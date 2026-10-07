"""Passive security grading and ARM SMMU observations."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rack_bench.audit import runner, security
from rack_bench.common.models import Check


class SecurityTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             redirect_stdout(StringIO()) as output:
            for name, probe in security.CHECKS.items():
                with self.subTest(name=name):
                    check = probe()
                    self.assertIsInstance(check, Check)
                    self.assertEqual(check.name, name)
                    self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")

    def test_placeholder_floors_fail_pass_and_prerelease(self):
        for value, status in (("1.1.11", "fail"), ("1.1.12", "pass"), ("1.10.0", "pass"),
                              ("1.1.12-rc1", "warn"), ("1.0.0-rc1", "fail")):
            with self.subTest(value=value):
                check = security._grade_floor(Check("security.runc_cve_floor", "pass", value), "runc")
                self.assertEqual(check.status, status)
                self.assertTrue(check.expected["placeholder"])
        check = security._grade_floor(Check("security.kernel_cve_floor", "pass", "6.8.1"), "kernel")
        self.assertEqual(check.status, "skip")
        self.assertEqual(check.value, "6.8.1")
        self.assertIsNone(check.expected)

    def test_docker_security_uses_local_daemon_not_cli_version(self):
        with patch.object(security, "run_command", return_value="27.1.1") as command:
            self.assertEqual(security.docker_cve_floor().status, "pass")
        args = command.call_args.args[0]
        self.assertIn("unix:///var/run/docker.sock", args)
        self.assertIn("{{.Server.Version}}", args)

    def test_iommu_passthrough_and_runtime_identity_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            group = root / "0"
            group.mkdir()
            (group / "type").write_text("DMA")
            for cmdline, expected in (("amd_iommu=on iommu=pt", "fail"), ("iommu.passthrough=1", "fail"), ("amd_iommu=on", "pass")):
                def read(path):
                    return cmdline if str(path) == "/proc/cmdline" else Path(path).read_text()
                with patch.object(security, "Path", return_value=root), patch.object(security, "read_text", side_effect=read):
                    self.assertEqual(security.iommu().status, expected)
            (group / "type").write_text("identity")
            with patch.object(security, "Path", return_value=root), patch.object(security, "read_text", side_effect=lambda p: "" if str(p) == "/proc/cmdline" else Path(p).read_text()):
                self.assertEqual(security.iommu().status, "fail")

    def test_smmu_is_arm_only(self):
        with patch.object(security.platform, "machine", return_value="x86_64"), patch.object(security, "Path") as path:
            check = security.smmu()
        self.assertEqual(check.status, "skip")
        self.assertIn("SMMU is ARM-only", check.detail)
        path.assert_not_called()

    def test_smmu_arm_bindings_and_default_domains(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            driver = root / "sys/bus/platform/drivers/arm-smmu-v3"
            device = root / "sys/devices/platform/arm-smmu-v3.0.auto"
            driver.mkdir(parents=True)
            device.mkdir(parents=True)
            (driver / device.name).symlink_to(device, target_is_directory=True)
            (device / "driver").symlink_to(driver, target_is_directory=True)
            with patch.object(security.platform, "machine", return_value="aarch64"), \
                 patch.object(security, "Path", side_effect=lambda path: root / str(path).lstrip("/")):
                check = security.smmu()
                self.assertEqual(check.status, "skip")
                self.assertIn("No IOMMU groups", check.detail)
                group = root / "sys/kernel/iommu_groups/0"
                group.mkdir(parents=True)
                for domain, status in (("DMA", "pass"), ("DMA-FQ", "pass"), ("blocked", "pass"),
                                       ("identity", "warn"), ("unmanaged", "skip")):
                    with self.subTest(domain=domain):
                        (group / "type").write_text(domain + "\n")
                        check = security.smmu()
                        self.assertEqual(check.status, status)
                        self.assertEqual(check.value["smmu_bindings"], {"arm-smmu-v3": [device.name]})
                        self.assertEqual(check.value["default_domain_types"], {"0": domain})
                        if status == "pass":
                            self.assertIn("VM/stage-2 isolation are not verified", check.detail)
                with patch("pathlib.Path.read_text", side_effect=PermissionError("Permission denied")):
                    check = security.smmu()
                self.assertEqual(check.status, "skip")
                self.assertIn("Permission denied", check.detail)
                (group / "type").unlink()
                check = security.smmu()
                self.assertEqual(check.status, "skip")
                self.assertIn("missing or unsupported", check.detail)
                self.assertIsNone(check.value["default_domain_types"]["0"])

    def test_smmu_groups_or_driver_registration_alone_are_not_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            group = root / "sys/kernel/iommu_groups/0"
            group.mkdir(parents=True)
            (group / "type").write_text("DMA")
            driver = root / "sys/bus/platform/drivers/arm-smmu-v3"
            with patch.object(security.platform, "machine", return_value="arm64"), \
                 patch.object(security, "Path", side_effect=lambda path: root / str(path).lstrip("/")):
                for create_driver in (False, True):
                    with self.subTest(driver_registered=create_driver):
                        if create_driver:
                            driver.mkdir(parents=True)
                        check = security.smmu()
                        self.assertEqual(check.status, "skip")
                        self.assertIn("No ARM SMMU driver bindings", check.detail)

    def test_security_registration_keeps_passive_gpu_permissions_only(self):
        self.assertIs(runner.SCOPES["security"], security)
        self.assertIs(security.CHECKS["security.smmu"], security.smmu)
        self.assertIs(security.CHECKS["security.gpu_permissions"], security.gpu_permissions)
        self.assertNotIn("security.cuda_nonroot", security.CHECKS)
        self.assertFalse(hasattr(security, "cuda_nonroot"))

    def test_acs_permission_absence_and_disabled_controls(self):
        with patch.object(security, "run_command", return_value="0000:01:00.0 Bridge\n Capabilities: <access denied>"):
            self.assertEqual(security.pcie_acs().status, "skip")
        with patch.object(security, "run_command", return_value="0000:01:00.0 Bridge\n ACSCtl: SrcValid+ ReqRedir- CmpltRedir+"):
            self.assertEqual(security.pcie_acs().status, "warn")

    def test_secrets_scan_never_exports_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cluster.conf"
            path.write_text("api_token=DO-NOT-EXPORT\n")
            path.chmod(0o644)
            with patch.object(security, "SECRET_PATHS", (str(path),)):
                check = security.secrets()
                self.assertEqual(check.status, "warn")
                self.assertNotIn("DO-NOT-EXPORT", repr(check))
                path.write_text("-----BEGIN PRIVATE KEY-----\nDO-NOT-EXPORT\n")
                self.assertEqual(security.secrets().status, "fail")


if __name__ == "__main__":
    unittest.main()
