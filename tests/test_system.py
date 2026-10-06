"""Source parsing and graceful absence, without requiring privileged hardware."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rack_bench.audit import system
from rack_bench.common.host import Unavailable
from rack_bench.common.models import Check


class SystemTests(unittest.TestCase):
    def test_cpu_fields_and_snc_not_inferred(self):
        text = json.dumps({"lscpu": [{"field": key + ":", "data": value} for key, value in {
            "Model name": "Example CPU", "Architecture": "aarch64", "CPU(s)": "16",
            "Socket(s)": "2", "Core(s) per socket": "8", "Thread(s) per core": "1",
            "NUMA node(s)": "2", "NUMA node0 CPU(s)": "0-7", "NUMA node1 CPU(s)": "8-15",
            "On-line CPU(s) list": "0-15",
        }.items()]})
        with patch.object(system, "run_command", return_value=text):
            cpu = system.cpu()
            self.assertEqual(cpu.status, "pass")
            self.assertEqual(cpu.value["logical_cpus"], 16)
            self.assertEqual(cpu.value["numa_cpus"], {"NUMA node0": "0-7", "NUMA node1": "8-15"})
            self.assertEqual(system.snc().status, "skip")
            self.assertIsNone(cpu.expected)
            self.assertEqual(cpu.source, ["lscpu --json"])

    def test_missing_and_malformed_lscpu(self):
        with patch.object(system, "run_command", side_effect=Unavailable("lscpu --json", "Command not found.")):
            self.assertEqual(system.cpu().status, "skip")
        with patch.object(system, "run_command", return_value="not JSON"):
            self.assertEqual(system.cpu().status, "skip")

    def test_meminfo_units(self):
        text = "MemTotal: 2048 kB\nSwapTotal: 1024 kB\nHugePages_Total: 2\nHugepagesize: 2048 kB"
        with patch.object(system, "read_text", return_value=text):
            memory = system.memory()
        self.assertEqual(memory.value, {"mem_total_bytes": 2097152, "swap_total_bytes": 1048576,
                                        "hugepages_total": 2, "hugepage_size_bytes": 2097152})
        self.assertEqual(memory.source, ["/proc/meminfo"])

    def test_dram_permission_and_parsing(self):
        with patch.object(system, "run_command", side_effect=Unavailable("dmidecode --type memory", "Permission denied")):
            check = system.dram()
            self.assertEqual(check.status, "skip")
            self.assertIn("Permission denied", check.detail)
        text = "Handle 0x01\nMemory Device\n\tSize: 32 GB\n\tType: DDR5\n\tLocator: DIMM_A\n\tSpeed: 4800 MT/s\n\nHandle 0x02\nMemory Device\n\tSize: No Module Installed"
        with patch.object(system, "run_command", return_value=text):
            check = system.dram()
        self.assertEqual(len(check.value), 1)
        self.assertEqual(check.value[0]["type"], "DDR5")

    def test_boot_only_exports_relevant_options(self):
        with patch.object(system, "read_text", return_value="root=UUID=x api_token=secret iommu=pt hugepages=4 quiet"):
            check = system.boot_parameters()
        self.assertEqual(check.value["parameters"], ["iommu=pt", "hugepages=4"])
        self.assertNotIn("secret", repr(check))
        self.assertEqual(check.status, "pass")  # Inventory, not a security verdict.

    def test_absent_and_available_thermal_zones(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(system, "Path", return_value=root):
                self.assertEqual(system.thermal_profile().status, "skip")
            zone = root / "thermal_zone0"
            zone.mkdir()
            for name, value in {"type": "cpu-thermal", "temp": "42500", "policy": "step_wise"}.items():
                (zone / name).write_text(value)
            with patch.object(system, "Path", return_value=root):
                check = system.thermal_profile()
            self.assertEqual(check.status, "pass")
            self.assertEqual(check.value["thermal_zone0"]["temperature_c"], 42.5)

    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             patch("pathlib.Path.iterdir", return_value=iter(())), redirect_stdout(StringIO()) as output:
            for name, probe in system.CHECKS.items():
                with self.subTest(name=name):
                    check = probe()
                    self.assertIsInstance(check, Check)
                    self.assertEqual(check.name, name)
                    self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
