"""GPU tests extracted from the audit-stage scope tests."""
from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

from rack_bench.audit import gpu
from rack_bench.common.host import Unavailable
from rack_bench.common.models import Check

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


class GpuTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             redirect_stdout(StringIO()) as output:
            for name, probe in gpu.CHECKS.items():
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


if __name__ == "__main__":
    unittest.main()
