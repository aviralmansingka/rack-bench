"""Check/Result and rendering contracts extracted from the audit-stage tests."""
from contextlib import redirect_stdout
from dataclasses import asdict
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rack_bench.common.models import Check, Result
from rack_bench.common.output import emit, render_human, render_json, show_operation


class ModelsOutputTests(unittest.TestCase):
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

    def test_json_stdout_and_run_dir_artifacts(self):
        result = self.sample()
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(StringIO()) as output:
                emit([result], stage="audit", json_target="-", run_dir=tmp)
            self.assertEqual(json.loads(output.getvalue()), json.loads(render_json([result])))
            self.assertEqual((Path(tmp) / "audit.values.json").read_text(), output.getvalue())
            self.assertEqual((Path(tmp) / "audit.out").read_text(), render_human([result]))

    def test_json_file_keeps_human_stdout(self):
        result = self.sample()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "export.json"
            with redirect_stdout(StringIO()) as output:
                emit([result], stage="audit", json_target=str(target), run_dir=tmp)
            self.assertEqual(output.getvalue(), render_human([result]))
            self.assertEqual(target.read_text(), render_json([result]))

    def test_progress_flushes(self):
        with patch("builtins.print") as print_call:
            show_operation("example", "read /proc/test")
        print_call.assert_called_once_with("[example] read /proc/test", flush=True)


if __name__ == "__main__":
    unittest.main()
