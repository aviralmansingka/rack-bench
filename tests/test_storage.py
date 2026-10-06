"""Storage scope contracts, including passive RAID, LVM and multipath topology."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from rack_bench.audit import storage
from rack_bench.common.host import Unavailable
from rack_bench.common.models import Check

MULTIPATH = """mpatha (3600508b400105e210000900000490000) dm-0 HP,HSV200
size=20G features='1 queue_if_no_path' hwhandler='1 alua' wp=rw
|-+- policy='service-time 0' prio=50 status=active
| `- 2:0:0:1 sda 8:0 active ready running
`-+- policy='service-time 0' prio=10 status=enabled
  `- 3:0:0:1 sdb 8:16 active ghost running
"""


class StorageTests(unittest.TestCase):
    def test_all_checks_return_data_when_hardware_and_tools_are_absent(self):
        with patch("subprocess.Popen", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.read_text", side_effect=FileNotFoundError()), \
             patch("pathlib.Path.exists", return_value=False), patch("pathlib.Path.glob", return_value=[]), \
             redirect_stdout(StringIO()) as output:
            for name, probe in storage.CHECKS.items():
                with self.subTest(name=name):
                    check = probe()
                    self.assertIsInstance(check, Check)
                    self.assertEqual(check.name, name)
                    self.assertIn(check.status, ("pass", "warn", "fail", "skip"))
        self.assertEqual(output.getvalue(), "")

    def test_mount_decoding_and_redaction(self):
        data = storage._mounts(r"//user:private@host/share /mnt/my\040share cifs rw,password=one\054two,credentials=/private 0 0")
        self.assertEqual(data[0]["target"], "/mnt/my share")
        self.assertEqual(data[0]["storage_class"], "shared")
        self.assertNotIn("private", repr(data))
        self.assertNotIn("one", repr(data))
        self.assertNotIn("two", repr(data))

    def test_software_raid_sysfs_states(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(storage, "Path", return_value=Path(tmp)):
            check = storage.software_raid()
            self.assertEqual(check.status, "skip")
            self.assertIn("no md arrays", check.detail)
            array = Path(tmp) / "md0"
            (array / "md").mkdir(parents=True)
            (array / "slaves" / "sda1").mkdir(parents=True)
            (array / "slaves" / "sdb1").mkdir()
            (array / "md" / "level").write_text("raid1\n")
            (array / "md" / "raid_disks").write_text("2\n")
            for degraded, action, status in ((0, "idle", "pass"), (1, "idle", "warn"),
                                              (0, "recover", "warn"), (0, "resync", "warn")):
                with self.subTest(degraded=degraded, action=action):
                    (array / "md" / "degraded").write_text(f"{degraded}\n")
                    (array / "md" / "sync_action").write_text(action + "\n")
                    check = storage.software_raid()
                    self.assertEqual(check.name, "storage.software_raid")
                    self.assertEqual(check.status, status)
                    self.assertEqual(check.value["md0"], {
                        "level": "raid1", "raid_disks": 2, "degraded": degraded,
                        "sync_action": action, "members": ["sda1", "sdb1"],
                    })
            (array / "md" / "degraded").unlink()
            (array / "md" / "sync_action").unlink()
            for level in ("raid0", "linear"):
                with self.subTest(level=level):
                    (array / "md" / "level").write_text(level)
                    check = storage.software_raid()
                    self.assertEqual(check.status, "pass")
                    self.assertIsNone(check.value["md0"]["degraded"])
                    self.assertIsNone(check.value["md0"]["sync_action"])

    def test_lvm_json_topology(self):
        pvs = [{"pv_name": "/dev/sda2", "vg_name": "vg0", "pv_size": "2147483648B"}]
        vgs = [{"vg_name": "vg0", "vg_size": "2143289344B"}]
        lvs = [{"lv_name": "root", "vg_name": "vg0", "lv_size": "1073741824B",
                "devices": "/dev/sda2(0)"}]
        reports = [json.dumps({"report": [{section: rows}]})
                   for section, rows in (("pv", pvs), ("vg", vgs), ("lv", lvs))]
        with patch.object(storage, "run_command", side_effect=reports) as command:
            check = storage.lvm()
        self.assertEqual(check.name, "storage.lvm")
        self.assertEqual(check.status, "pass")
        self.assertEqual(check.value, {"pvs": pvs, "vgs": vgs, "lvs": lvs})
        self.assertEqual([args.args[0][0] for args in command.call_args_list], ["pvs", "vgs", "lvs"])
        for args in command.call_args_list:
            argv = args.args[0]
            self.assertIn("--readonly", argv)
            self.assertEqual(argv[argv.index("--reportformat") + 1], "json")
            self.assertEqual(argv[argv.index("--units") + 1], "b")

    def test_lvm_absent_tools_or_pvs(self):
        with patch.object(storage, "run_command", side_effect=Unavailable("pvs", "Command not found: pvs.")):
            check = storage.lvm()
        self.assertEqual(check.status, "skip")
        self.assertIn("Command not found", check.detail)
        with patch.object(storage, "run_command", return_value='{"report": [{"pv": []}]}') as command:
            check = storage.lvm()
        self.assertEqual(check.status, "skip")
        self.assertIn("No LVM PVs", check.detail)
        self.assertEqual(command.call_count, 1)

    def test_lvm_malformed_report_skips(self):
        for text in ("not JSON", '{"report": [{"pv": [{}]}]}'):
            with self.subTest(text=text), patch.object(storage, "run_command", return_value=text):
                check = storage.lvm()
            self.assertEqual(check.status, "skip")
            self.assertIn("Cannot decode source", check.detail)

    def test_multipath_healthy_paths_and_aliases(self):
        for header, alias in (("mpatha (3600508b400105e210000900000490000)", "mpatha"),
                              ("3600508b400105e210000900000490000", None)):
            text = MULTIPATH.replace("mpatha (3600508b400105e210000900000490000)", header)
            with self.subTest(alias=alias), patch.object(storage, "run_command", return_value=text) as command:
                check = storage.multipath()
            self.assertEqual(check.name, "storage.multipath")
            self.assertEqual(check.status, "pass")
            device = check.value["dm-0"]
            self.assertEqual(device["alias"], alias)
            self.assertEqual(device["wwn"], "3600508b400105e210000900000490000")
            self.assertEqual(device["dm_device"], "dm-0")
            self.assertEqual((device["usable_paths"], device["total_paths"]), (2, 2))
            self.assertEqual([p["device"] for p in device["paths"]], ["sda", "sdb"])
            self.assertEqual([p["state"] for p in device["paths"]], ["ready", "ghost"])
            self.assertIn("configured path count is verified against the certification profile, not probed", check.detail)
            command.assert_called_once_with(["multipath", "-ll"])

    def test_multipath_faulty_undefined_and_offline_paths_warn(self):
        for state in ("failed faulty running", "active undef running", "active ready offline"):
            text = MULTIPATH.replace("active ghost running", state)
            with self.subTest(state=state), patch.object(storage, "run_command", return_value=text):
                check = storage.multipath()
            self.assertEqual(check.status, "warn")
            self.assertEqual(check.value["dm-0"]["usable_paths"], 1)
            self.assertEqual(check.value["dm-0"]["total_paths"], 2)

    def test_multipath_faulty_path_warns_even_with_two_usable_paths(self):
        text = MULTIPATH + "  `- 4:0:0:1 sdc 8:32 failed faulty running\n"
        with patch.object(storage, "run_command", return_value=text):
            check = storage.multipath()
        self.assertEqual(check.status, "warn")
        self.assertEqual(check.value["dm-0"]["usable_paths"], 2)
        self.assertEqual(check.value["dm-0"]["total_paths"], 3)

    def test_multipath_single_or_zero_paths_warn(self):
        for text, count in (("\n".join(MULTIPATH.splitlines()[:4]), 1), (MULTIPATH.splitlines()[0], 0)):
            with self.subTest(count=count), patch.object(storage, "run_command", return_value=text):
                check = storage.multipath()
            self.assertEqual(check.status, "warn")
            self.assertEqual(check.value["dm-0"]["usable_paths"], count)
            self.assertEqual(check.value["dm-0"]["total_paths"], count)

    def test_multipath_absent_tools_or_devices(self):
        with patch.object(storage, "run_command", side_effect=Unavailable("multipath -ll", "Command not found: multipath.")):
            check = storage.multipath()
        self.assertEqual(check.status, "skip")
        self.assertIn("multipath not present", check.detail)
        with patch.object(storage, "run_command", return_value=""):
            check = storage.multipath()
        self.assertEqual(check.status, "skip")
        self.assertIn("multipath not present", check.detail)

    def test_topology_checks_registration_order(self):
        self.assertEqual(list(storage.CHECKS)[1:6], [
            "storage.mounts", "storage.software_raid", "storage.lvm", "storage.multipath", "storage.nvme_controllers",
        ])

    def test_smart_health_bitmask_and_partial_coverage(self):
        with patch("subprocess.Popen", return_value=Mock(returncode=8, communicate=Mock(return_value=('{"smart_status":{"passed":false}}', '')))):
            check = storage._smart("storage.smart_health", ["/dev/test"])
        self.assertEqual(check.status, "fail")
        with patch.object(storage, "run_command", side_effect=[json.dumps({"smart_status": {"passed": True}}), Unavailable("smartctl /dev/b", "Permission denied")]):
            check = storage._smart("storage.smart_health", ["/dev/a", "/dev/b"])
        self.assertEqual(check.status, "skip")
        self.assertIn("/dev/a", check.value["devices"])
        self.assertIn("/dev/b", check.value["unavailable"])


if __name__ == "__main__":
    unittest.main()
