"""Representative vendor outputs, absence paths and passive security grading."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from rack_bench.audit import gpu, network, security, software, storage, topology
from rack_bench.audit.runner import SCOPES
from rack_bench.common.host import Unavailable, collect_check, run_command
from rack_bench.common.models import Check
from rack_bench.common.output import show_operation

GPU_XML = '''<nvidia_smi_log><gpu id="00000000:01:00.0">
<product_name>NVIDIA Example</product_name><uuid>GPU-test</uuid><serial>N/A</serial>
<fb_memory_usage><total>81920 MiB</total></fb_memory_usage>
<ecc_mode><current_ecc>Enabled</current_ecc><pending_ecc>Enabled</pending_ecc></ecc_mode>
<mig_mode><current_mig>N/A</current_mig><pending_mig>N/A</pending_mig></mig_mode>
<vbios_version>99.01</vbios_version><gsp_firmware_version>570.133.20</gsp_firmware_version>
<clocks><sm_clock>1980 MHz</sm_clock></clocks>
<power_readings><power_limit>700.00 W</power_limit><default_power_limit>700.00 W</default_power_limit></power_readings>
<temperature><gpu_temp>31 C</gpu_temp></temperature>
<fabric><state>Completed</state><status>Success</status><cliqueId>1</cliqueId></fabric>
</gpu></nvidia_smi_log>'''


class ScopeTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             redirect_stdout(StringIO()) as output:
            for module in SCOPES.values():
                for name, probe in module.CHECKS.items():
                    with self.subTest(name=name):
                        check = probe()
                        self.assertIsInstance(check, Check)
                        self.assertEqual(check.name, name)
                        self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")

    def test_gpu_timeout_does_not_issue_more_topology_queries(self):
        with patch.object(gpu, "run_command", side_effect=[GPU_XML, Unavailable("nvidia-smi topo -m", "Command timed out after 10s.")]) as command, \
             patch("pathlib.Path.glob", return_value=[]):
            check = gpu.io_locality()
        self.assertEqual(command.call_count, 2)
        self.assertEqual(check.status, "skip")
        self.assertIn("timed out", check.detail)
        self.assertNotIn("nvidia-smi topo -p2p r", check.source)

    def test_gpu_xml_inventory_and_supported_fields(self):
        with patch.object(gpu, "run_command", return_value=GPU_XML):
            check = gpu.inventory()
            self.assertEqual(check.value["count"], 1)
            self.assertIsNone(check.value["devices"][0]["serial"])
            self.assertEqual(gpu.ecc().value["GPU-test"]["current"], "Enabled")
            self.assertEqual(gpu.mig().status, "skip")
            self.assertEqual(gpu.power_limits().value["GPU-test"]["current"], "700.00 W")
            self.assertEqual(gpu.thermals().value["GPU-test"]["gpu"], "31 C")
            self.assertEqual(gpu.idle_thermals().status, "skip")
            self.assertEqual(gpu.board_firmware().status, "skip")

    def test_every_gpu_check_skips_without_gpus_or_command(self):
        for text in ("<nvidia_smi_log><attached_gpus>0</attached_gpus></nvidia_smi_log>", "not XML"):
            with patch.object(gpu, "run_command", return_value=text):
                for name, probe in gpu.CHECKS.items():
                    with self.subTest(name=name, text=text):
                        check = probe()
                        self.assertEqual(check.name, name)
                        self.assertEqual(check.status, "skip")
                        self.assertTrue(check.source)
        with patch.object(gpu, "run_command", side_effect=Unavailable(gpu.SMI, "Command not found: nvidia-smi.")):
            for probe in gpu.CHECKS.values():
                self.assertIn("Command not found", probe().detail)

    def test_pci_machine_readable_parser_preserves_repeated_fields(self):
        records = topology._parse_pci("Slot:\t0000:01:00.0\nClass:\tVGA\nModule:\tnvidia\nModule:\tnouveau\n\nSlot:\t0000:02:00.0\nClass:\tEthernet")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["Module"], ["nvidia", "nouveau"])

    def test_nvlink_counts_and_unsupported_host(self):
        text = "GPU 0: Test\n Link 0: 50 GB/s\n Link 1: <inactive>\nGPU 1: Test\n Link 0: 50 GB/s\n Link 1: 50 GB/s"
        with patch.object(topology, "run_command", return_value=text):
            self.assertEqual(topology.links_per_gpu().value, {"0": 1, "1": 2})
        with patch.object(topology, "run_command", return_value="GPU 0: NVLink is not supported"):
            self.assertEqual(topology.links_per_gpu().status, "skip")
            self.assertEqual(topology.link_width().status, "skip")
        with patch.object(topology, "run_command", return_value="GPU 0: Test\n Current Link Width: 2") as command:
            self.assertEqual(topology.link_width().status, "pass")
            command.assert_called_once_with(["nvidia-smi", "nvlink", "--getLinkWidth"])

    def test_real_fabric_query_path(self):
        with patch.object(topology, "run_command", side_effect=[GPU_XML, "GPU0 GPU1 NV18", "LoadState=loaded\nActiveState=active"]) as command:
            check = topology.fabric()
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value["devices"]["GPU-test"]["state"], "Completed")
        self.assertEqual(command.call_count, 3)

    def test_nccl_env_precedence_and_no_secret_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            system = Path(tmp) / "nccl.conf"
            user = Path(tmp) / "user.conf"
            system.write_text("NCCL_IB_GID_INDEX=1\nNCCL_SOCKET_IFNAME==ens1f0\nPASSWORD=never-export\n")
            user.write_text("NCCL_IB_GID_INDEX=2\n")
            with patch.dict("os.environ", {"NCCL_IB_GID_INDEX": "3"}, clear=True):
                result = network._nccl_config([system, user])
            self.assertEqual(result["effective"]["NCCL_IB_GID_INDEX"], "3")
            self.assertEqual(result["effective"]["NCCL_SOCKET_IFNAME"], "=ens1f0")
            self.assertNotIn("never-export", repr(result))
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaises(Unavailable):
                    network._nccl_config([])

    def test_no_rdma_devices_and_sharpyuv_is_not_plugin(self):
        with patch.object(network, "run_command", return_value="No IB devices found"):
            self.assertEqual(network.rdma_ports().status, "skip")
        with patch.object(network, "run_command", return_value="libsharpyuv.so.0 => /lib/libsharpyuv.so.0"):
            self.assertEqual(network.plugins_present().status, "skip")
        with patch.object(network, "run_command", return_value="libnccl-net.so => /lib/libnccl-net.so"):
            self.assertEqual(network.plugins_present().status, "pass")

    def test_loaded_plugins_preserve_deleted_mapping_paths(self):
        with patch("pathlib.Path.glob", return_value=[Path("/proc/123/maps")]), \
             patch.object(network, "read_text", return_value="7f00-7f10 r-xp 0000 08:01 5 /usr/lib/libnccl-net.so (deleted)"):
            check = network.plugins_loaded()
        self.assertEqual(check.value, {"123": ["/usr/lib/libnccl-net.so (deleted)"]})

    def test_mount_decoding_and_redaction(self):
        data = storage._mounts(r"//user:private@host/share /mnt/my\040share cifs rw,password=one\054two,credentials=/private 0 0")
        self.assertEqual(data[0]["target"], "/mnt/my share")
        self.assertEqual(data[0]["storage_class"], "shared")
        self.assertNotIn("private", repr(data))
        self.assertNotIn("one", repr(data))
        self.assertNotIn("two", repr(data))

    def test_smart_health_bitmask_and_partial_coverage(self):
        with patch("subprocess.Popen", return_value=Mock(returncode=8, communicate=Mock(return_value=('{"smart_status":{"passed":false}}', '')))):
            check = storage._smart("storage.smart_health", ["/dev/test"])
        self.assertEqual(check.status, "fail")
        with patch.object(storage, "run_command", side_effect=[json.dumps({"smart_status": {"passed": True}}), Unavailable("smartctl /dev/b", "Permission denied")]):
            check = storage._smart("storage.smart_health", ["/dev/a", "/dev/b"])
        self.assertEqual(check.status, "skip")
        self.assertIn("/dev/a", check.value["devices"])
        self.assertIn("/dev/b", check.value["unavailable"])

    def test_software_versions_and_installed_package_filter(self):
        with patch.object(software, "run_command", return_value="Cuda compilation tools, release 13.1, V13.1.80"):
            self.assertEqual(software.cuda().value, "13.1")
            self.assertEqual(software.nvcc().value, "13.1.80")
        with patch.object(software, "run_command", return_value="glibc 2.39"):
            self.assertEqual(software.glibc().value, "2.39")
        with patch.object(software.shutil, "which", return_value="/usr/bin/dpkg-query"), patch.object(software, "run_command", return_value="ii \tlibnccl2\t2.26.2-1\nrc \tlibnccl-old\t1.0\n"):
            self.assertEqual(software.nccl().value, {"libnccl2": "2.26.2-1"})

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

    def test_timeout_cleanup_is_bounded_even_if_sigkill_cannot_reap_child(self):
        proc = Mock(pid=123456)
        proc.communicate.side_effect = subprocess.TimeoutExpired("example", 1)
        with patch("subprocess.Popen", return_value=proc), patch("os.killpg"):
            with self.assertRaises(Unavailable) as caught:
                run_command(["example"], timeout=1)
        self.assertIn("remained unresponsive", str(caught.exception))
        self.assertEqual(proc.communicate.call_count, 2)
        proc.wait.assert_not_called()
        proc.stdout.close.assert_called_once()

    def test_collect_check_handles_parse_errors_and_progress_flushes(self):
        def parse():
            raise ValueError("bad source")
        check = collect_check("example", parse, ["example source"])
        self.assertEqual(check.status, "skip")
        with patch("builtins.print") as print_call:
            show_operation("example", "read /proc/test")
        print_call.assert_called_once_with("[example] read /proc/test", flush=True)


if __name__ == "__main__":
    unittest.main()
