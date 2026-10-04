"""Public names, runner filtering and Check/Result serialization contracts."""
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from io import StringIO
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from rack_bench.audit import runner
from rack_bench.cli import main
from rack_bench.common.host import operation_echo, read_text, run_command
from rack_bench.common.models import Check, Result
from rack_bench.common.output import render_human, render_json


class CliTests(unittest.TestCase):
    def sample(self):
        return Result("system", "test-host", ts="2026-01-01T00:00:00+00:00", checks=[
            Check("system.cpu", "pass", {"cores": 16}, expected=None, detail="Observed.", source=["lscpu --json"]),
            Check("system.hbm", "skip", detail="No supported source."),
        ], manifest={"example": "1.0"})

    def test_result_json_round_trip(self):
        original = self.sample()
        document = json.loads(render_json([original]))
        self.assertEqual(set(document), {"schema_version", "results"})
        self.assertEqual(document["schema_version"], 1)
        entry = document["results"][0]
        self.assertEqual(set(entry), {"scope", "host", "ts", "checks", "manifest"})
        self.assertEqual(set(entry["checks"][0]), {"name", "status", "value", "expected", "detail", "source"})
        restored = Result(**{**entry, "checks": [Check(**check) for check in entry["checks"]]})
        self.assertEqual(restored, original)
        self.assertEqual(json.loads(json.dumps(asdict(original.checks[0]))), entry["checks"][0])

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            Check("system.cpu", "unknown")

    def test_filters_run_only_selected_checks_in_registration_order(self):
        calls = []
        def probe(name):
            def run():
                calls.append(name)
                return Check(name, "pass", value=1)
            return run
        names = ["system.cpu", "system.memory", "system.bios", "system.hbm"]
        module = SimpleNamespace(CHECKS={name: probe(name) for name in names})
        with patch.dict(runner.SCOPES, {"system": module}, clear=True):
            results = runner.collect("system", only=["system.c*", "system.b*", "system.mem*"], skip=["*.memory"])
        self.assertEqual(calls, ["system.cpu", "system.bios"])
        self.assertEqual([c.name for c in results[0].checks], calls)
        self.assertEqual(results[0].manifest, {})

    def test_empty_selection_is_error(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(StringIO()) as error:
            target = Path(tmp) / "unused"
            self.assertEqual(main(["audit", "system", "--only", "does.not.exist", "--run-dir", str(target)]), 2)
            self.assertIn("No audit checks matched", error.getvalue())
            self.assertFalse(target.exists())

    def test_globals_accumulate_before_and_after_stage(self):
        with patch.object(runner, "run", return_value=0) as run:
            self.assertEqual(main(["--only", "system.c*", "audit", "system", "--only", "system.b*",
                                   "--skip", "*.bios_settings", "--json"]), 0)
        self.assertEqual(run.call_args.kwargs["only"], ["system.c*", "system.b*"])
        self.assertEqual(run.call_args.kwargs["skip"], ["*.bios_settings"])
        self.assertEqual(run.call_args.kwargs["json_target"], "-")

    def test_json_stdout_and_run_dir_artifacts(self):
        result = self.sample()
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "collect", return_value=[result]):
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["audit", "system", "--json", "--run-dir", tmp]), 0)
            self.assertEqual(json.loads(output.getvalue()), json.loads(render_json([result])))
            self.assertEqual((Path(tmp) / "audit.values.json").read_text(), output.getvalue())
            self.assertEqual((Path(tmp) / "audit.out").read_text(), render_human([result]))

    def test_json_file_keeps_human_stdout(self):
        result = self.sample()
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "collect", return_value=[result]):
            target = Path(tmp) / "export.json"
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["audit", "system", "--json", str(target), "--run-dir", tmp]), 0)
            self.assertEqual(output.getvalue(), render_human([result]))
            self.assertEqual(target.read_text(), render_json([result]))

    def test_fail_verdict_sets_exit_one(self):
        result = self.sample()
        result.checks[0].status = "fail"
        with patch.object(runner, "collect", return_value=[result]), patch.object(runner, "emit"):
            self.assertEqual(runner.run("system"), 1)

    def test_scope_registry_has_explicit_named_functions(self):
        self.assertNotIn("firmware", runner.SCOPES)
        names = []
        for module in runner.SCOPES.values():
            self.assertIsInstance(module.CHECKS, dict)
            for name, probe in module.CHECKS.items():
                names.append(name)
                self.assertTrue(callable(probe))
                self.assertNotEqual(probe.__name__, "<lambda>")
        self.assertEqual(len(names), len(set(names)))
        for scope, name in (("gpu", "gpu.firmware"), ("network", "network.nic_firmware"),
                            ("software", "software.bmc"), ("storage", "storage.ssd_firmware")):
            self.assertIn(name, runner.SCOPES[scope].CHECKS)

    def test_software_manifest_contains_selected_detected_versions_only(self):
        module = SimpleNamespace(CHECKS={
            "software.kernel": lambda: Check("software.kernel", "pass", "6.8.1"),
            "software.gcc": lambda: Check("software.gcc", "pass", "13.3.0"),
            "software.cuda": lambda: Check("software.cuda", "skip", detail="Missing."),
        })
        with patch.dict(runner.SCOPES, {"software": module}, clear=True):
            result = runner.collect("software", skip=["*.gcc"])[0]
        self.assertEqual(result.manifest, {"kernel": "6.8.1"})

    def test_show_command_precedes_table_and_quiet_wins(self):
        def probe():
            run_command(["example", "argument with spaces"])
            read_text("/proc/example")
            return Check("system.example", "pass", 1)
        module = SimpleNamespace(CHECKS={"system.example": probe})
        with tempfile.TemporaryDirectory() as tmp, patch.dict(runner.SCOPES, {"system": module}, clear=True), \
             patch("subprocess.Popen", return_value=Mock(returncode=0, communicate=Mock(return_value=("ok", "")))), \
             patch("pathlib.Path.read_text", return_value="ok"):
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["audit", "system", "--show-command", "--run-dir", tmp]), 0)
            text = output.getvalue()
            self.assertIn("[system.example] example 'argument with spaces'", text)
            self.assertIn("[system.example] read /proc/example", text)
            self.assertLess(text.index("[system.example]"), text.index("STATUS"))
            self.assertIsNone(operation_echo.get())
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["audit", "system", "--show-command", "--quiet", "--run-dir", tmp]), 0)
            self.assertNotIn("[system.example]", output.getvalue())

    def test_echo_context_is_reset_when_probe_raises(self):
        def broken():
            raise ValueError("broken")
        with patch.dict(runner.SCOPES, {"system": SimpleNamespace(CHECKS={"system.broken": broken})}, clear=True):
            with self.assertRaises(ValueError):
                runner.collect("system", show_command=True)
        self.assertIsNone(operation_echo.get())


if __name__ == "__main__":
    unittest.main()
