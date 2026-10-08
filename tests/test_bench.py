"""Bench dispatch and internet CLI contracts; no credentials or network required."""
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from rack_bench.bench import internet, runner
from rack_bench.cli import main
from rack_bench.common.host import operation_echo, read_text
from rack_bench.common.models import Check, Result
from rack_bench.common.output import render_human


SUFFIXES = ("path.as_path", "path.hops", "path.rtt_sanity", "dns.resolve", "latency.ttfb",
            "upload.throughput", "upload.objs_per_sec", "latency.loaded", "download.throughput",
            "download.objs_per_sec", "tcp.pmtud", "tcp.retransmit_ratio", "summary")


def names(providers):
    return [f"internet.{p}.{suffix}" for p in providers for suffix in SUFFIXES]


class BenchTests(unittest.TestCase):
    def setUp(self):
        # Default CLI runs must remain offline even on a developer's credentialed host.
        environment = patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)

    def test_registry_and_missing_credentials_envelope(self):
        self.assertEqual(runner.CATEGORIES, {"internet": internet})
        self.assertEqual(list(internet.CHECKS), names(internet.PROVIDERS))
        result = runner.collect("internet")[0]
        self.assertEqual(result.scope, "internet")
        self.assertTrue(result.host)
        self.assertTrue(result.ts)
        self.assertEqual(result.manifest, {})
        self.assertEqual(result.checks, [Check(name, "skip", detail=
            "credentials not set: missing environment variable: AWS_ACCESS_KEY_ID")
            for name in names(("s3", "r2"))])
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
                "--buckets", "s3=bench-s3,gcs=bench-gcs",
                "--concurrent", "8", "--duration", "2m", "--tool", "warp", "--keep-data", "--yes",
                "--json", "export.json", "--run-dir", "artifacts", "--show-command", "--quiet",
            ]), 0)
        self.assertEqual(run.call_args.kwargs["options"], internet.Options(
            providers=("gcs", "s3"), directions=("down",), profile="certify",
            regions={"s3": "us-east-1", "gcs": "us-central1"},
            buckets={"s3": "bench-s3", "gcs": "bench-gcs"}, concurrent=8, duration=120,
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
            ("--buckets", ""), ("--buckets", "azure=bench"), ("--buckets", "s3="),
            ("--buckets", "s3=bench,s3=other"), ("--buckets", "s3=ab"),
            ("--buckets", "s3=dotted.bucket"), ("--buckets", "r2=bad..bucket"),
            ("--buckets", "r2=127.0.0.1"), ("--buckets", "s3=bench,"),
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
        for flag in ("providers", "directions", "profile", "regions", "buckets", "concurrent", "duration",
                     "tool", "keep-data", "yes", "json", "run-dir", "only", "skip", "show-command", "quiet"):
            self.assertIn("--" + flag, output.getvalue())

    def test_globals_accumulate_at_all_parser_levels(self):
        with patch.object(runner, "run", return_value=0) as run:
            main(["--only", "internet.s3.*", "--skip", "*.path.*", "bench",
                  "--only", "internet.gcs.*", "--skip", "*.upload.*", "internet",
                  "--only", "internet.r2.*", "--skip", "*.tcp.*", "--json"])
        self.assertEqual(run.call_args.kwargs["only"], ["internet.s3.*", "internet.gcs.*", "internet.r2.*"])
        self.assertEqual(run.call_args.kwargs["skip"], ["*.path.*", "*.upload.*", "*.tcp.*"])
        self.assertEqual(run.call_args.kwargs["json_target"], "-")

    def test_provider_selection_in_registration_order(self):
        result = runner.collect("internet", options=internet.Options(providers=("gcs", "r2")))[0]
        self.assertEqual([c.name for c in result.checks], names(("r2", "gcs")))

    def test_filters_prevent_probe_calls(self):
        checks = {name: Mock(return_value=Check(name, "skip")) for name in internet.CHECKS}
        with patch.dict(internet.CHECKS, checks, clear=True):
            result = runner.collect(only=["internet.*"], skip=["internet.r2.*"])[0]
        self.assertEqual([c.name for c in result.checks], names(("s3",)))
        for name, probe in checks.items():
            if name.startswith("internet.s3."):
                probe.assert_called_once()
            else:
                probe.assert_not_called()

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
                {"name": name, "status": "skip", "value": None, "expected": None,
                 "detail": "credentials not set: missing environment variable: AWS_ACCESS_KEY_ID",
                 "source": []} for name in names(("s3", "r2"))])
            self.assertEqual((Path(tmp) / "bench.values.json").read_text(), output.getvalue())
            self.assertIn("SKIP=26", (Path(tmp) / "bench.out").read_text())

    def test_json_file_and_full_stage_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(StringIO()) as output:
            target = Path(tmp) / "export.json"
            self.assertEqual(main(["bench", "--json", str(target), "--run-dir", tmp]), 0)
            self.assertIn("internet.s3.summary", output.getvalue())
            self.assertEqual(target.read_text(), (Path(tmp) / "bench.values.json").read_text())
            self.assertEqual(output.getvalue(), (Path(tmp) / "bench.out").read_text())

    def test_certify_gate_before_probes_even_when_quiet(self):
        probe = Mock()
        with tempfile.TemporaryDirectory() as tmp, \
             patch.dict(internet.CHECKS, {"internet.s3.summary": probe}, clear=True), \
             redirect_stderr(StringIO()) as error, redirect_stdout(StringIO()) as output:
            target = Path(tmp) / "unused"
            self.assertEqual(main(["bench", "internet", "--profile", "certify", "--quiet",
                                   "--json", "--run-dir", str(target)]), 2)
            probe.assert_not_called()
            self.assertFalse(target.exists())
        self.assertEqual(output.getvalue(), "")
        for expected in ("10 Gbit/s", "2.2 TB", "S3 ~$200", "R2 ~$0", "requires --yes"):
            self.assertIn(expected, error.getvalue())

    def test_certify_yes_keeps_json_clean_and_estimates_selected_providers(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stderr(StringIO()) as error, \
             redirect_stdout(StringIO()) as output:
            self.assertEqual(main(["bench", "internet", "--profile", "certify", "--yes",
                                   "--providers", "gcs,r2", "--json", "--run-dir", tmp]), 0)
        self.assertEqual(len(json.loads(output.getvalue())["results"][0]["checks"]), 26)
        self.assertIn("GCS ~$260, R2 ~$0", error.getvalue())
        self.assertNotIn("S3 ~$200", error.getvalue())
        self.assertIn("small-object requests may incur charges", error.getvalue())

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

    def dummy_category(self):
        @dataclass
        class Options:
            duration: str = "forever"
            tool: str = "native"
            device: str = "test-device"
            profile: str = "certify"  # Must not trigger the internet cost gate.

        def add_arguments(parser):
            parser.add_argument("--duration", choices=("forever", "short"), default="forever")
            parser.add_argument("--tool", choices=("native", "other"), default="native")
            parser.add_argument("--device", default="test-device")

        return SimpleNamespace(
            Options=Options, add_arguments=add_arguments,
            options_from_args=lambda args: Options(duration=args.duration, tool=args.tool, device=args.device),
            CHECKS={"dummy.summary": Mock(return_value=Check("dummy.summary", "pass", value=1))})

    def test_bench_parent_help_has_only_generic_flags(self):
        with redirect_stdout(StringIO()) as output, self.assertRaises(SystemExit) as exit_status:
            main(["bench", "--help"])
        self.assertEqual(exit_status.exception.code, 0)
        self.assertIn("internet", output.getvalue())
        for flag in ("json", "run-dir", "only", "skip", "show-command", "quiet"):
            self.assertIn("--" + flag, output.getvalue())
        for flag in ("providers", "directions", "profile", "regions", "buckets", "concurrent", "duration",
                     "tool", "keep-data", "yes"):
            self.assertNotIn("--" + flag, output.getvalue())

    def test_category_flags_are_not_accepted_on_parent(self):
        for arguments in (["--providers", "s3"], ["--providers", "s3", "internet"],
                          ["--duration", "60s", "internet"], ["--yes", "internet"]):
            with self.subTest(arguments=arguments), redirect_stderr(StringIO()), \
                 patch.object(runner, "run") as run, self.assertRaises(SystemExit) as error:
                main(["bench", *arguments])
            self.assertEqual(error.exception.code, 2)
            run.assert_not_called()

    def test_dummy_category_owns_colliding_flag_names_and_policy(self):
        dummy = self.dummy_category()
        with patch.dict(runner.CATEGORIES, {"dummy": dummy}), patch.object(runner, "emit"), \
             patch.object(internet, "Options", side_effect=AssertionError("internet default used")), \
             patch.object(internet, "before_run", side_effect=AssertionError("internet gate used")), \
             patch.object(internet, "selected_checks", side_effect=AssertionError("internet filter used")):
            self.assertEqual(main(["bench", "dummy", "--duration", "short", "--tool", "other",
                                   "--device", "example"]), 0)
        dummy.CHECKS["dummy.summary"].assert_called_once_with(
            dummy.Options(duration="short", tool="other", device="example"))

    def test_category_flags_do_not_leak_to_siblings(self):
        dummy = self.dummy_category()
        cases = [("dummy", "--providers", "s3"), ("dummy", "--regions", "s3=us-east-1"),
                 ("dummy", "--duration", "60s"), ("internet", "--duration", "forever"),
                 ("internet", "--device", "example")]
        with patch.dict(runner.CATEGORIES, {"dummy": dummy}):
            for arguments in cases:
                with self.subTest(arguments=arguments), redirect_stderr(StringIO()), \
                     self.assertRaises(SystemExit) as error:
                    main(["bench", *arguments])
                self.assertEqual(error.exception.code, 2)
        dummy.CHECKS["dummy.summary"].assert_not_called()

    def test_full_stage_uses_each_category_defaults_and_optional_hooks(self):
        dummy = self.dummy_category()  # No before_run or selected_checks required.
        with patch.dict(runner.CATEGORIES, {"dummy": dummy}), patch.object(runner, "emit") as emit:
            self.assertEqual(main(["bench"]), 0)
        dummy.CHECKS["dummy.summary"].assert_called_once_with(dummy.Options())
        results = emit.call_args.args[0]
        self.assertEqual([result.scope for result in results], ["internet", "dummy"])
        self.assertEqual([c.name for c in results[0].checks], names(("s3", "r2")))

    def test_full_stage_globs_can_select_just_one_category(self):
        dummy = self.dummy_category()
        with patch.dict(runner.CATEGORIES, {"dummy": dummy}), patch.object(runner, "emit") as emit:
            self.assertEqual(main(["bench", "--only", "dummy.*"]), 0)
        results = emit.call_args.args[0]
        self.assertEqual(results[0].checks, [])
        self.assertEqual([c.name for c in results[1].checks], ["dummy.summary"])

    def test_all_category_gates_run_before_any_probe(self):
        dummy = self.dummy_category()
        dummy.before_run = Mock(side_effect=ValueError("dummy gate"))
        probe = Mock()
        with patch.dict(runner.CATEGORIES, {"dummy": dummy}), \
             patch.dict(internet.CHECKS, {"internet.s3.summary": probe}, clear=True), \
             patch.object(runner, "emit") as emit, redirect_stderr(StringIO()) as error:
            self.assertEqual(main(["bench"]), 2)
        self.assertIn("dummy gate", error.getvalue())
        dummy.before_run.assert_called_once_with(dummy.Options())
        probe.assert_not_called()
        dummy.CHECKS["dummy.summary"].assert_not_called()
        emit.assert_not_called()

    def test_category_options_cannot_be_shared_across_full_stage(self):
        with self.assertRaisesRegex(ValueError, "Category-specific options require a category"):
            runner.collect(options=internet.Options())

    def test_empty_registry_emits_empty_envelope(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(runner.CATEGORIES, {}, clear=True), \
             redirect_stdout(StringIO()) as output:
            self.assertEqual(main(["bench", "--json", "--run-dir", tmp]), 0)
            self.assertEqual(json.loads(output.getvalue()), {"schema_version": 1, "results": []})
            self.assertEqual((Path(tmp) / "bench.out").read_text(), render_human([]))


if __name__ == "__main__":
    unittest.main()
