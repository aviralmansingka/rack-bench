"""Bench dispatch and internet CLI contracts; no credentials or network required."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from rack_bench.bench import internet, runner
from rack_bench.cli import main
from rack_bench.common.host import operation_echo, read_text
from rack_bench.common.models import Check, Result
from rack_bench.common.output import render_human


class BenchTests(unittest.TestCase):
    def test_registry_and_stub_envelope(self):
        self.assertEqual(runner.CATEGORIES, {"internet": internet})
        self.assertEqual(list(internet.CHECKS), [f"internet.{p}.summary" for p in internet.PROVIDERS])
        result = runner.collect("internet")[0]
        self.assertEqual(result.scope, "internet")
        self.assertTrue(result.host)
        self.assertTrue(result.ts)
        self.assertEqual(result.manifest, {})
        self.assertEqual(result.checks, [Check(f"internet.{p}.summary", "skip", detail="not implemented")
                                         for p in ("s3", "r2")])
        self.assertEqual([r.checks for r in runner.collect()], [result.checks])

    def test_default_flags(self):
        with patch.object(runner, "run", return_value=0) as run:
            self.assertEqual(main(["bench", "internet"]), 0)
        self.assertEqual(run.call_args.args, ("internet",))
        self.assertEqual(run.call_args.kwargs["options"], internet.Options())

    def test_all_flags_are_forwarded(self):
        with patch.object(runner, "run", return_value=0) as run:
            self.assertEqual(main([
                "bench", "internet", "--providers", "gcs,s3", "--directions", "down",
                "--profile", "certify", "--regions", "s3=us-east-1,gcs=us-central1",
                "--concurrent", "8", "--duration", "2m", "--tool", "warp", "--keep-data", "--yes",
                "--json", "export.json", "--run-dir", "artifacts", "--show-command", "--quiet",
            ]), 0)
        self.assertEqual(run.call_args.kwargs["options"], internet.Options(
            providers=("gcs", "s3"), directions=("down",), profile="certify",
            regions={"s3": "us-east-1", "gcs": "us-central1"}, concurrent=8, duration=120,
            tool="warp", keep_data=True, yes=True))
        self.assertEqual(run.call_args.kwargs["json_target"], "export.json")
        self.assertEqual(run.call_args.kwargs["run_dir"], "artifacts")
        self.assertTrue(run.call_args.kwargs["show_command"])
        self.assertTrue(run.call_args.kwargs["quiet"])

    def test_profile_duration_defaults_and_units(self):
        for flags, seconds in [([], 60), (["--profile", "certify"], 300),
                               (["--duration", "90"], 90), (["--duration", "1h"], 3600),
                               (["--duration", "15s"], 15)]:
            with self.subTest(flags=flags), patch.object(runner, "run", return_value=0) as run:
                main(["bench", "internet", *flags])
                self.assertEqual(run.call_args.kwargs["options"].duration, seconds)

    def test_invalid_flags_rejected_before_dispatch(self):
        cases = [
            ("--providers", "azure"), ("--providers", "s3,s3"), ("--providers", "s3,"),
            ("--providers", ""), ("--directions", "both"), ("--directions", "up,up"),
            ("--directions", ""), ("--profile", "slow"), ("--tool", "curl"),
            ("--concurrent", "0"), ("--concurrent", "-1"), ("--concurrent", "1.5"),
            ("--duration", "0s"), ("--duration", "-2"), ("--duration", "1.5s"),
            ("--duration", "nan"), ("--duration", "2d"), ("--regions", "us-east-1"),
            ("--regions", "azure=east"), ("--regions", "s3="),
            ("--regions", "s3=east,s3=west"), ("--regions", "s3=a=b"),
            ("--regions", "s3=east,"), ("--regions", ""), ("--unknown", "x"),
        ]
        for flags in cases:
            with self.subTest(flags=flags), patch.object(runner, "run") as run, \
                 redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
                main(["bench", "internet", *flags])
            self.assertEqual(error.exception.code, 2)
            run.assert_not_called()

    def test_help_lists_surface(self):
        with redirect_stdout(StringIO()) as output, self.assertRaises(SystemExit) as exit_status:
            main(["bench", "internet", "--help"])
        self.assertEqual(exit_status.exception.code, 0)
        for flag in ("providers", "directions", "profile", "regions", "concurrent", "duration",
                     "tool", "keep-data", "yes", "json", "run-dir", "only", "skip", "show-command", "quiet"):
            self.assertIn("--" + flag, output.getvalue())

    def test_globals_accumulate_before_and_after_stage(self):
        with patch.object(runner, "run", return_value=0) as run:
            main(["--only", "internet.s3.*", "--skip", "*.path.*", "bench", "internet",
                  "--only", "internet.r2.*", "--skip", "*.tcp.*", "--json"])
        self.assertEqual(run.call_args.kwargs["only"], ["internet.s3.*", "internet.r2.*"])
        self.assertEqual(run.call_args.kwargs["skip"], ["*.path.*", "*.tcp.*"])
        self.assertEqual(run.call_args.kwargs["json_target"], "-")

    def test_provider_selection_in_registration_order(self):
        result = runner.collect(options=internet.Options(providers=("gcs", "r2")))[0]
        self.assertEqual([c.name for c in result.checks], ["internet.r2.summary", "internet.gcs.summary"])

    def test_filters_prevent_probe_calls(self):
        checks = {name: Mock(return_value=Check(name, "skip")) for name in internet.CHECKS}
        with patch.dict(internet.CHECKS, checks, clear=True):
            result = runner.collect(only=["internet.*"], skip=["internet.r2.*"])[0]
        self.assertEqual([c.name for c in result.checks], ["internet.s3.summary"])
        checks["internet.s3.summary"].assert_called_once()
        checks["internet.r2.summary"].assert_not_called()
        checks["internet.gcs.summary"].assert_not_called()

    def test_empty_selection_is_error_without_artifacts(self):
        for flags in (["--only", "no.such.check"], ["--skip", "*"],
                      ["--providers", "r2", "--only", "internet.s3.*"]):
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as tmp, \
                 redirect_stderr(StringIO()) as error:
                target = Path(tmp) / "unused"
                self.assertEqual(main(["bench", "internet", *flags, "--run-dir", str(target)]), 2)
                self.assertIn("No bench checks matched", error.getvalue())
                self.assertFalse(target.exists())

    def test_json_stdout_shape_and_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(StringIO()) as output:
            self.assertEqual(main(["bench", "internet", "--json", "--run-dir", tmp]), 0)
            document = json.loads(output.getvalue())
            self.assertEqual(set(document), {"schema_version", "results"})
            self.assertEqual(document["schema_version"], 1)
            self.assertEqual(len(document["results"]), 1)
            result = document["results"][0]
            self.assertEqual(set(result), {"scope", "host", "ts", "checks", "manifest"})
            self.assertEqual(result["scope"], "internet")
            self.assertEqual(result["manifest"], {})
            self.assertEqual(result["checks"], [
                {"name": f"internet.{p}.summary", "status": "skip", "value": None,
                 "expected": None, "detail": "not implemented", "source": []} for p in ("s3", "r2")])
            self.assertEqual((Path(tmp) / "bench.values.json").read_text(), output.getvalue())
            self.assertIn("SKIP=2", (Path(tmp) / "bench.out").read_text())

    def test_json_file_and_full_stage_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(StringIO()) as output:
            target = Path(tmp) / "export.json"
            self.assertEqual(main(["bench", "--json", str(target), "--run-dir", tmp]), 0)
            self.assertIn("internet.s3.summary", output.getvalue())
            self.assertEqual(target.read_text(), (Path(tmp) / "bench.values.json").read_text())
            self.assertEqual(output.getvalue(), (Path(tmp) / "bench.out").read_text())

    def test_certify_gate_before_collection_even_when_quiet(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, "collect") as collect, \
             redirect_stderr(StringIO()) as error, redirect_stdout(StringIO()) as output:
            target = Path(tmp) / "unused"
            self.assertEqual(main(["bench", "internet", "--profile", "certify", "--quiet",
                                   "--json", "--run-dir", str(target)]), 2)
            collect.assert_not_called()
            self.assertFalse(target.exists())
        self.assertEqual(output.getvalue(), "")
        for expected in ("10 Gbit/s", "2.2 TB", "S3 ~$200", "R2 ~$0", "requires --yes"):
            self.assertIn(expected, error.getvalue())

    def test_certify_yes_keeps_json_clean_and_estimates_selected_providers(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(StringIO()) as error, \
             redirect_stdout(StringIO()) as output:
            self.assertEqual(main(["bench", "internet", "--profile", "certify", "--yes",
                                   "--providers", "gcs,r2", "--json", "--run-dir", tmp]), 0)
        self.assertEqual(len(json.loads(output.getvalue())["results"][0]["checks"]), 2)
        self.assertIn("GCS ~$260, R2 ~$0", error.getvalue())
        self.assertNotIn("S3 ~$200", error.getvalue())
        self.assertIn("no transfers or charges", error.getvalue())

    def test_quick_does_not_require_acceptance(self):
        with patch.object(runner, "emit"), redirect_stderr(StringIO()) as error:
            self.assertEqual(main(["bench", "internet"]), 0)
        self.assertEqual(error.getvalue(), "")

    def test_show_command_and_quiet_match_audit(self):
        def probe(options):
            read_text("/proc/example")
            return Check("internet.s3.summary", "pass", 1)
        with tempfile.TemporaryDirectory() as tmp, \
             patch.dict(internet.CHECKS, {"internet.s3.summary": probe}, clear=True), \
             patch("pathlib.Path.read_text", return_value="ok"):
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["bench", "internet", "--show-command", "--run-dir", tmp]), 0)
            self.assertIn("[internet.s3.summary] read /proc/example", output.getvalue())
            self.assertLess(output.getvalue().index("[internet.s3"), output.getvalue().index("STATUS"))
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["bench", "internet", "--show-command", "--quiet", "--run-dir", tmp]), 0)
            self.assertNotIn("[internet.s3.summary]", output.getvalue())
            self.assertNotIn("internet.s3.summary", output.getvalue())
        self.assertIsNone(operation_echo.get())

    def test_echo_reset_on_exception(self):
        probe = Mock(side_effect=ValueError("broken"))
        with patch.dict(internet.CHECKS, {"internet.s3.summary": probe}, clear=True):
            with self.assertRaisesRegex(ValueError, "broken"):
                runner.collect(show_command=True)
        self.assertIsNone(operation_echo.get())

    def test_mismatched_check_name_rejected(self):
        with patch.dict(internet.CHECKS, {"internet.s3.summary": lambda options: Check("wrong", "skip")}, clear=True):
            with self.assertRaisesRegex(ValueError, "mismatched name"):
                runner.collect()

    def test_failure_sets_exit_one(self):
        result = Result("internet", "test-host", checks=[Check("internet.s3.summary", "fail")])
        with patch.object(runner, "collect", return_value=[result]), patch.object(runner, "emit"):
            self.assertEqual(main(["bench", "internet"]), 1)

    def test_empty_registry_emits_empty_envelope(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(runner.CATEGORIES, {}, clear=True), \
             redirect_stdout(StringIO()) as output:
            self.assertEqual(main(["bench", "--json", "--run-dir", tmp]), 0)
            self.assertEqual(json.loads(output.getvalue()), {"schema_version": 1, "results": []})
            self.assertEqual((Path(tmp) / "bench.out").read_text(), render_human([]))


if __name__ == "__main__":
    unittest.main()
