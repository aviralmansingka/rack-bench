"""Passive NCCL cases extracted from the audit-stage scope tests."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rack_bench.audit import nccl
from rack_bench.cli import main
from rack_bench.common.host import Unavailable
from rack_bench.common.models import Check


class NcclTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             patch.dict("os.environ", {}, clear=True), redirect_stdout(StringIO()) as output:
            for name, probe in nccl.CHECKS.items():
                with self.subTest(name=name):
                    check = probe()
                    self.assertIsInstance(check, Check)
                    self.assertEqual(check.name, name)
                    self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")

    def test_nccl_env_precedence_and_no_secret_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            system = Path(tmp) / "nccl.conf"
            user = Path(tmp) / "user.conf"
            system.write_text("NCCL_IB_GID_INDEX=1\nNCCL_SOCKET_IFNAME==ens1f0\nPASSWORD=never-export\n")
            user.write_text("NCCL_IB_GID_INDEX=2\n")
            with patch.dict("os.environ", {"NCCL_IB_GID_INDEX": "3"}, clear=True):
                result = nccl._nccl_config([system, user])
            self.assertEqual(result["effective"]["NCCL_IB_GID_INDEX"], "3")
            self.assertEqual(result["effective"]["NCCL_SOCKET_IFNAME"], "=ens1f0")
            self.assertNotIn("never-export", repr(result))
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(Unavailable):
                    nccl._nccl_config([])

    def test_sharpyuv_is_not_plugin(self):
        with patch.object(nccl, "run_command", return_value="libsharpyuv.so.0 => /lib/libsharpyuv.so.0"):
            self.assertEqual(nccl.plugins_present().status, "skip")
        with patch.object(nccl, "run_command", return_value="libnccl-net.so => /lib/libnccl-net.so"):
            self.assertEqual(nccl.plugins_present().status, "pass")

    def test_loaded_plugins_preserve_deleted_mapping_paths(self):
        with patch("pathlib.Path.glob", return_value=[Path("/proc/123/maps")]), \
             patch.object(nccl, "read_text", return_value="7f00-7f10 r-xp 0000 08:01 5 /usr/lib/libnccl-net.so (deleted)"):
            check = nccl.plugins_loaded()
        self.assertEqual(check.value, {"123": ["/usr/lib/libnccl-net.so (deleted)"]})

    def test_nccl_cli_checks_keep_network_envelope_scope(self):
        with tempfile.TemporaryDirectory() as tmp, patch("pathlib.Path.exists", return_value=False), \
             patch.dict("os.environ", {"NCCL_SOCKET_IFNAME": "=eth0"}, clear=True):
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["audit", "network", "--only", "nccl.env_defaults", "--json", "--run-dir", tmp]), 0)
            document = json.loads(output.getvalue())
            self.assertEqual(document["schema_version"], 1)
            result, = document["results"]
            self.assertEqual(result["scope"], "network")
            check, = result["checks"]
            self.assertEqual(check["name"], "nccl.env_defaults")
            self.assertEqual(check["status"], "pass")
            self.assertEqual(check["value"]["effective"], {"NCCL_SOCKET_IFNAME": "=eth0"})
            self.assertEqual(json.loads((Path(tmp) / "audit.values.json").read_text()), document)


if __name__ == "__main__":
    unittest.main()
