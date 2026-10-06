"""Topology tests extracted from the audit-stage scope tests."""
from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

from rack_bench.audit import topology
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


class TopologyTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             redirect_stdout(StringIO()) as output:
            for name, probe in topology.CHECKS.items():
                with self.subTest(name=name):
                    check = probe()
                    self.assertIsInstance(check, Check)
                    self.assertEqual(check.name, name)
                    self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")

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


if __name__ == "__main__":
    unittest.main()
