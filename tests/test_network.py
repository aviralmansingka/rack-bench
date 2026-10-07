"""NIC scope contracts and passive GPUDirect, PKey and UFM observations."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rack_bench.audit import network, runner
from rack_bench.common.host import Unavailable
from rack_bench.common.models import Check


class NetworkTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             redirect_stdout(StringIO()) as output:
            for name, probe in network.CHECKS.items():
                with self.subTest(name=name):
                    check = probe()
                    self.assertIsInstance(check, Check)
                    self.assertEqual(check.name, name)
                    self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")

    def test_gpudirect_rdma_sysfs_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(network, "Path", side_effect=lambda path: root / str(path).lstrip("/")):
                check = network.gpudirect_rdma()
                self.assertEqual(check.status, "skip")
                self.assertIn("No RDMA devices", check.detail)
                (root / "sys/class/infiniband/mlx5_0").mkdir(parents=True)
                check = network.gpudirect_rdma()
                self.assertEqual(check.status, "warn")
                self.assertIn("GPUDirect RDMA not enabled alongside RDMA devices", check.detail)
                self.assertFalse(check.value["nvidia_peermem"])
                self.assertFalse(check.value["gdrdrv"])
                (root / "sys/module/nvidia_peermem").mkdir(parents=True)
                (root / "sys/module/gdrdrv").mkdir()
                check = network.gpudirect_rdma()
                self.assertEqual(check.status, "pass")
                self.assertEqual(check.value, {"rdma_devices": ["mlx5_0"], "nvidia_peermem": True, "gdrdrv": True})

    def test_pkeys_readable_unreadable_and_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(network, "Path", side_effect=lambda path: root / str(path).lstrip("/")):
                check = network.pkeys()
                self.assertEqual(check.status, "skip")
                self.assertIn("No IB devices", check.detail)
                direct = root / "sys/class/infiniband/mlx5_0/pkeys"
                port = root / "sys/class/infiniband/mlx5_0/ports/1/pkeys"
                direct.mkdir(parents=True)
                port.mkdir(parents=True)
                (direct / "0").write_text("0xFFFF\n")
                (port / "0").write_text("0x8001\n")
                (port / "1").write_text("0x0000\n")
                check = network.pkeys()
                self.assertEqual(check.status, "pass")
                self.assertEqual(check.value["mlx5_0"], {"default_index": 0, "pkeys": {"0": "0xffff"},
                                                         "ports": {"1": {"0": "0x8001", "1": "0x0000"}}})
                with patch("pathlib.Path.read_text", side_effect=PermissionError("Permission denied")):
                    check = network.pkeys()
                self.assertEqual(check.status, "skip")
                self.assertIn("Permission denied", check.detail)
                for path in (direct / "0", port / "0", port / "1"):
                    path.unlink()
                check = network.pkeys()
                self.assertEqual(check.status, "skip")
                self.assertIn("No readable PKey tables", check.detail)

    def test_ufm_package_version_takes_precedence(self):
        tools = {"dpkg-query": "/usr/bin/dpkg-query", "ufmcli": "/usr/bin/ufmcli", "systemctl": "/usr/bin/systemctl"}
        text = "ii \tufm-enterprise\t6.24.2\nrc \tufm-old\t1.0\nii \tufm-versions-mgr\t1.2.0\n"
        with patch.object(network.shutil, "which", side_effect=tools.get), \
             patch.object(network, "run_command", return_value=text) as command:
            check = network.ufm()
        self.assertEqual(check.status, "pass")
        self.assertTrue(check.value["present"])
        self.assertEqual(check.value["via"], "package metadata")
        self.assertEqual(check.value["version"], "6.24.2")
        self.assertNotIn("ufm-old", check.value["packages"])
        self.assertEqual(command.call_count, 1)
        self.assertEqual(command.call_args.args[0][0], "dpkg-query")
        self.assertIn("credential-gated", check.detail)

    def test_ufm_rpm_version(self):
        with patch.object(network.shutil, "which", side_effect={"rpm": "/usr/bin/rpm"}.get), \
             patch.object(network, "run_command", return_value="ufm-enterprise\t6.24.2-1\nother\t1.0\n"):
            check = network.ufm()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value["version"], "6.24.2-1")
        self.assertEqual(check.value["packages"], {"ufm-enterprise": "6.24.2-1"})

    def test_ufm_binary_version_and_versionless_presence(self):
        for response, version in (("ufmcli version 1.8.2", "1.8.2"),
                                  (Unavailable("ufmcli --version", "Unknown option"), None)):
            with self.subTest(version=version), \
                 patch.object(network.shutil, "which", side_effect={"ufmcli": "/usr/bin/ufmcli"}.get), \
                 patch.object(network, "run_command", side_effect=[response]) as command:
                check = network.ufm()
                self.assertEqual(check.status, "pass")
                self.assertEqual(check.value, {"present": True, "via": "binary", "binary": "/usr/bin/ufmcli", "version": version})
                command.assert_called_once_with(["/usr/bin/ufmcli", "--version"])

    def test_ufm_unit_presence_without_version_passes(self):
        tools = {"dpkg-query": "/usr/bin/dpkg-query", "systemctl": "/usr/bin/systemctl"}
        unit = "Id=ufm.service\nLoadState=not-found\nActiveState=inactive\n\nId=ufm-enterprise.service\nLoadState=loaded\nActiveState=active"
        with patch.object(network.shutil, "which", side_effect=tools.get), \
             patch.object(network, "run_command", side_effect=["", unit]):
            check = network.ufm()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value, {"present": True, "via": "systemd unit", "unit": "ufm-enterprise.service",
                                       "active_state": "active", "version": None})
        self.assertIn("UFM present; version not locally discoverable", check.detail)
        self.assertIn("credential-gated (profile)", check.detail)

    def test_ufm_absent_skips(self):
        with patch.object(network.shutil, "which", return_value=None), patch.object(network, "run_command") as command:
            check = network.ufm()
        self.assertEqual(check.status, "skip")
        self.assertIn("UFM not present", check.detail)
        command.assert_not_called()
        with patch.object(network.shutil, "which", side_effect={"systemctl": "/usr/bin/systemctl"}.get), \
             patch.object(network, "run_command", return_value="Id=ufm.service\nLoadState=not-found\nActiveState=inactive"):
            self.assertEqual(network.ufm().status, "skip")

    def test_nic_registration_order_and_nccl_deferred(self):
        self.assertIs(runner.SCOPES["network"], network)
        names = list(network.CHECKS)
        self.assertEqual(names[names.index("network.rdma_ports") + 1], "network.gpudirect_rdma")
        self.assertEqual(names[names.index("network.congestion_control") + 1], "network.pkeys")
        self.assertEqual(names[names.index("network.switch") + 1], "network.ufm")
        self.assertFalse(any(name.startswith("nccl.") for module in runner.SCOPES.values() for name in module.CHECKS))

    def test_no_rdma_devices(self):
        with patch.object(network, "run_command", return_value="No IB devices found"):
            self.assertEqual(network.rdma_ports().status, "skip")


if __name__ == "__main__":
    unittest.main()
