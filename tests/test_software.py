"""Software scope tests and end-to-end version manifest wiring."""
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rack_bench.audit import software
from rack_bench.cli import main
from rack_bench.common.host import Unavailable
from rack_bench.common.models import Check


class SoftwareTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             patch.object(software, "dist_versions", return_value={}), redirect_stdout(StringIO()) as output:
            for name, probe in software.CHECKS.items():
                with self.subTest(name=name):
                    check = probe()
                    self.assertIsInstance(check, Check)
                    self.assertEqual(check.name, name)
                    self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")

    def test_software_versions_and_installed_package_filter(self):
        with patch.object(software, "run_command", return_value="Cuda compilation tools, release 13.1, V13.1.80"):
            self.assertEqual(software.cuda().value, "13.1")
            self.assertEqual(software.nvcc().value, "13.1.80")
        with patch.object(software, "run_command", return_value="glibc 2.39"):
            self.assertEqual(software.glibc().value, "2.39")
        with patch.object(software.shutil, "which", return_value="/usr/bin/dpkg-query"), patch.object(software, "run_command", return_value="ii \tlibnccl2\t2.26.2-1\nrc \tlibnccl-old\t1.0\n"):
            self.assertEqual(software.nccl().value, {"libnccl2": "2.26.2-1"})

    def test_dpkg_empty_or_unavailable_falls_back_to_python_distributions(self):
        for response in ("", Unavailable("dpkg-query", "Command not found: dpkg-query.")):
            with self.subTest(response=response), \
                 patch.object(software.shutil, "which", return_value="/usr/bin/dpkg-query"), \
                 patch.object(software, "run_command", side_effect=[response]) as command, \
                 patch.object(software, "dist_versions", return_value={"nvidia-nccl-cu12": "2.26.2"}) as distributions:
                check = software.nccl()
                self.assertEqual(check.status, "pass")
                self.assertEqual(check.value, {"nvidia-nccl-cu12": "2.26.2"})
                self.assertEqual(command.call_args.kwargs["ok_codes"], (0, 1))
                distributions.assert_called_once_with(("nvidia-nccl*",))
                self.assertIn("python distributions", check.source[-1])

    def test_staged_kernel_native_ordering_warn_and_pass(self):
        packages = ("hi \tlinux-image-6.8.0-9-generic\t6.8.0-9.9\n"
                    "ii \tlinux-image-6.8.0-10-generic\t6.8.0-10.10\n"
                    "ii \tlinux-image-generic\t999.0\n"
                    "ii \tlinux-image-6.8.0-99-generic-dbgsym\t999.0\n")
        for running, result, status in (("6.8.0-9-generic", "", "warn"),
                                        ("6.8.0-10-generic", Unavailable("dpkg", "Command exited 1: false"), "pass")):
            with self.subTest(running=running), patch.object(software.shutil, "which", return_value="/usr/bin/dpkg"), \
                 patch.object(software, "run_command", side_effect=[running, packages, result]) as command:
                check = software.staged_kernel()
                self.assertEqual(check.status, status)
                self.assertEqual(check.value["running"]["release"], running)
                self.assertEqual(check.value["newest_installed"]["version"], "6.8.0-10.10")
                self.assertEqual(check.value["pending_reboot"], status == "warn")
                self.assertIn("package-native", check.detail)
                self.assertEqual(command.call_args.args[0][:2], ["dpkg", "--compare-versions"])
                self.assertEqual(command.call_args.args[0][3], "gt")
                if status == "warn":
                    self.assertIn("newer kernel installed than running (pending reboot)", check.detail)

    def test_staged_kernel_missing_or_removed_running_package_skips(self):
        for rows, reason in (("", "cannot be mapped"),
                             ("rc \tlinux-image-6.8.0-9-generic\t6.8.0-9.9\n", "no longer installed")):
            packages = rows + "ii \tlinux-image-6.8.0-10-generic\t6.8.0-10.10\n"
            with self.subTest(reason=reason), patch.object(software.shutil, "which", return_value="/usr/bin/dpkg"), \
                 patch.object(software, "run_command", side_effect=["6.8.0-9-generic", packages]) as command:
                check = software.staged_kernel()
                self.assertEqual(check.status, "skip")
                self.assertIn(reason, check.detail)
                self.assertEqual(command.call_count, 2)

    def test_staged_kernel_no_native_comparator_skips(self):
        for tools, reason in (({}, "no supported package manager for kernel-package comparison"),
                              ({"rpm": "/usr/bin/rpm"}, "RPM-native")):
            with self.subTest(tools=tools), patch.object(software.shutil, "which", side_effect=tools.get), \
                 patch.object(software, "run_command") as command:
                check = software.staged_kernel()
                self.assertEqual(check.status, "skip")
                self.assertIn(reason, check.detail)
                command.assert_not_called()

    def test_staged_kernel_comparison_error_is_not_a_pass(self):
        packages = "ii \tlinux-image-6.8.0-9-generic\t6.8.0-9.9\nii \tlinux-image-6.8.0-10-generic\t6.8.0-10.10\n"
        with patch.object(software.shutil, "which", return_value="/usr/bin/dpkg"), \
             patch.object(software, "run_command", side_effect=["6.8.0-9-generic", packages,
                          Unavailable("dpkg", "Command exited 2: bad version")]):
            check = software.staged_kernel()
        self.assertEqual(check.status, "skip")
        self.assertIn("Command exited 2", check.detail)

    def test_runtime_identity_daemon_and_compat_link(self):
        for binary, cli, daemon, status in (("/usr/bin/docker", "Docker version 27.1.1", "27.1.1", "pass"),
                                            ("/usr/bin/podman", "podman version 5.0.0", "5.0.0", "warn")):
            with self.subTest(binary=binary), patch.object(software.shutil, "which", return_value="/usr/bin/docker"), \
                 patch.object(software.os.path, "realpath", return_value=binary), \
                 patch.object(software, "run_command", side_effect=[cli, daemon]) as command:
                check = software.runtime_identity()
                self.assertEqual(check.status, status)
                self.assertEqual(check.value, {"cli": cli, "daemon": daemon, "binary": binary,
                                               "compat_link": status == "warn"})
                self.assertIn("CLI version alone does not establish the daemon", check.detail)
                self.assertEqual(command.call_args.args[0], ["docker", "version", "--format", "{{.Server.Version}}"])

    def test_runtime_identity_absent_cli_or_unavailable_daemon(self):
        with patch.object(software.shutil, "which", return_value=None):
            check = software.runtime_identity()
        self.assertEqual(check.status, "skip")
        self.assertIn("Docker CLI not found", check.detail)
        with patch.object(software.shutil, "which", return_value="/usr/bin/docker"), \
             patch.object(software.os.path, "realpath", return_value="/usr/bin/docker"), \
             patch.object(software, "run_command", side_effect=["Docker version 27.1.1", Unavailable("docker version", "Permission denied")]):
            check = software.runtime_identity()
        self.assertEqual(check.status, "warn")
        self.assertIsNone(check.value["daemon"])
        self.assertIn("Permission denied", check.detail)

    def test_lmod_absent_or_tcl_modules_skips(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(software.shutil, "which", return_value=None), \
             patch.object(software.os.path, "isfile", return_value=False):
            check = software.lmod()
        self.assertEqual(check.status, "skip")
        self.assertIn("Lmod not found", check.detail)
        with patch.dict(os.environ, {"LMOD_CMD": "/usr/bin/modulecmd"}), \
             patch.object(software.os.path, "isfile", return_value=True), \
             patch.object(software, "run_command", return_value="Modules Release 5.4.0"):
            check = software.lmod()
        self.assertEqual(check.status, "skip")
        self.assertIn("No Lmod version banner", check.detail)

    def test_lmod_version_banner_on_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "lmod"
            binary.write_text("#!/bin/sh\nprintf 'Modules based on Lua: Version 8.7.24\\n' >&2\n")
            binary.chmod(0o755)
            with patch.dict(os.environ, {"LMOD_CMD": str(binary)}):
                check = software.lmod()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value, "8.7.24")

    def test_pytorch_and_vllm_distributions_present_or_absent(self):
        for probe, distribution in ((software.pytorch, "torch"), (software.vllm, "vllm")):
            for versions, status in (({distribution: "2.6.0"}, "pass"), ({}, "skip")):
                with self.subTest(distribution=distribution, status=status), \
                     patch.object(software.shutil, "which", return_value="/usr/bin/dpkg-query"), \
                     patch.object(software, "run_command", return_value=""), \
                     patch.object(software, "dist_versions", return_value=versions) as distributions:
                    check = probe()
                    self.assertEqual(check.status, status)
                    if status == "pass":
                        self.assertEqual(check.value, versions)
                    distributions.assert_called_once_with((distribution,))

    def test_new_checks_registration_order(self):
        names = list(software.CHECKS)
        self.assertEqual(names[names.index("software.kernel") + 1], "software.staged_kernel")
        self.assertEqual(names[names.index("software.docker") + 1], "software.runtime_identity")
        self.assertEqual(names[names.index("software.glibc") + 1], "software.lmod")
        self.assertLess(names.index("software.nvshmem"), names.index("software.pytorch"))
        self.assertEqual(names[names.index("software.pytorch") + 1], "software.vllm")

    def test_cli_envelope_contains_selected_software_manifest(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(software, "run_command", side_effect=[
            "6.8.1", "Cuda compilation tools, release 13.1, V13.1.80",
        ]) as command:
            with redirect_stdout(StringIO()) as output:
                self.assertEqual(main(["audit", "software", "--only", "software.kernel", "--only", "software.cuda",
                                       "--only", "software.gcc", "--skip", "*.gcc", "--json", "--run-dir", tmp]), 0)
            document = json.loads(output.getvalue())
            self.assertEqual(document["schema_version"], 1)
            result, = document["results"]
            self.assertEqual(result["scope"], "software")
            self.assertEqual(result["manifest"], {"kernel": "6.8.1", "cuda": "13.1"})
            self.assertEqual([check["status"] for check in result["checks"]], ["pass", "pass"])
            self.assertEqual(json.loads((Path(tmp) / "audit.values.json").read_text()), document)
            self.assertEqual(command.call_count, 2)


if __name__ == "__main__":
    unittest.main()
