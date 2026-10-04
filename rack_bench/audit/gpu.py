"""Passive NVIDIA inventory; XML parsing lives with the GPU checks."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from rack_bench.common.host import Unavailable, collect_check, read_text, run_command

SMI = "nvidia-smi -q -x"


def _clean(value):
    if value is None or value.strip().lower() in ("", "n/a", "not supported", "[not supported]"):
        return None
    return value.strip()


def _gpus():
    devices = ET.fromstring(run_command(["nvidia-smi", "-q", "-x"])).findall("gpu")
    if not devices:
        raise Unavailable(SMI, "No NVIDIA GPUs reported by nvidia-smi.")
    return devices


def _fields(name, fields):
    def collect():
        values = {}
        for index, gpu in enumerate(_gpus()):
            key = gpu.findtext("uuid") or gpu.get("id") or str(index)
            values[key] = {label: next((v for path in paths if (v := _clean(gpu.findtext(path))) is not None), None)
                           for label, paths in fields.items()}
        if not any(v is not None for row in values.values() for v in row.values()):
            raise Unavailable(SMI, "Requested fields are not supported/exposed by these GPUs or this driver.")
        return values
    check = collect_check(name, collect, [SMI])
    if check.status == "pass" and any(all(v is None for v in row.values()) for row in check.value.values()):
        check.status, check.detail = "warn", "Some GPUs do not expose the requested fields; null values are unverified."
    return check


def inventory():
    def collect():
        devices = []
        for index, gpu in enumerate(_gpus()):
            devices.append({"index": index, "uuid": _clean(gpu.findtext("uuid")),
                            "model": _clean(gpu.findtext("product_name")), "serial": _clean(gpu.findtext("serial")),
                            "architecture": _clean(gpu.findtext("product_architecture")),
                            "pci_bus_id": gpu.findtext("pci/pci_bus_id") or gpu.get("id"),
                            "memory_total": _clean(gpu.findtext("fb_memory_usage/total"))})
        return {"count": len(devices), "devices": devices}
    return collect_check("gpu.inventory", collect, [SMI])


def ecc():
    return _fields("gpu.ecc", {"current": ["ecc_mode/current_ecc"], "pending": ["ecc_mode/pending_ecc"],
                               "uncorrected_volatile_total": ["ecc_errors/volatile/uncorrected/total"]})


def mig():
    return _fields("gpu.mig", {"current": ["mig_mode/current_mig"], "pending": ["mig_mode/pending_mig"]})


def firmware():
    return _fields("gpu.firmware", {"vbios": ["vbios_version"], "gsp": ["gsp_firmware_version"]})


def board_firmware():
    return _fields("gpu.board_firmware", {"sbt": ["sbt_firmware_version", "sbt_version"],
                                          "sfw": ["sfw_firmware_version", "sfw_version"],
                                          "fmc": ["fmc_firmware_version", "fmc_version"]})


def clocks():
    return _fields("gpu.clocks", {"graphics": ["clocks/graphics_clock"], "sm": ["clocks/sm_clock"],
                                  "memory": ["clocks/mem_clock"], "max_sm": ["max_clocks/sm_clock"]})


def power_limits():
    return _fields("gpu.power_limits", {key: [f"gpu_power_readings/{field}", f"power_readings/{field}"] + (["power_readings/power_limit"] if key == "current" else [])
                   for key, field in (("current", "current_power_limit"), ("default", "default_power_limit"),
                                       ("min", "min_power_limit"), ("max", "max_power_limit"),
                                       ("draw", "power_draw"), ("instant_draw", "instant_power_draw"))})


def thermals():
    check = _fields("gpu.thermals", {"gpu": ["temperature/gpu_temp"], "memory": ["temperature/memory_temp"],
                                     "slowdown_threshold": ["temperature/gpu_temp_slow_threshold"],
                                     "utilization": ["utilization/gpu_util"]})
    if check.status == "pass":
        check.detail = "Instantaneous sample with driver-reported units; no idle qualification or profile grading."
    return check


def idle_thermals():
    check = _fields("gpu.idle_thermals", {"gpu": ["temperature/gpu_temp"]})
    if check.status != "skip":
        check.status = "skip"
        check.detail = "Instantaneous sample only: five-minute quiescence and a rack median have not been established."
    return check


def io_locality():
    commands = [["nvidia-smi", "topo", "-m"], ["nvidia-smi", "topo", "-p2p", "r"], ["nvidia-smi", "topo", "-p2p", "w"]]
    sources = [SMI]
    def collect():
        _gpus()
        value = {}
        labels = ("gpu_nic_topology", "p2p_read", "p2p_write")
        for index, (label, command) in enumerate(zip(labels, commands)):
            sources.append(" ".join(command))
            try:
                value[label] = re.sub(r"\x1b\[[0-9;]*m", "", run_command(command))
            except Unavailable as exc:
                value[label] = {"unavailable": str(exc)}
                if "timed out" in str(exc):
                    for remaining in labels[index + 1:]:
                        value[remaining] = {"unavailable": "Not attempted after NVIDIA topology timeout."}
                    break
        value["nvme"] = {}
        sources.append("/sys/class/nvme/*/device")
        for path in sorted(Path("/sys/class/nvme").glob("nvme[0-9]*")):
            device = (path / "device").resolve()
            numa = device / "numa_node"
            value["nvme"][path.name] = {"pci_path": str(device), "numa_node": read_text(numa) if numa.exists() else None}
        return value
    check = collect_check("gpu.io_locality", collect, sources)
    if check.status == "pass":
        if all(isinstance(check.value[key], dict) for key in ("gpu_nic_topology", "p2p_read", "p2p_write")):
            check.status = "skip"
        elif any(isinstance(check.value[key], dict) for key in ("gpu_nic_topology", "p2p_read", "p2p_write")):
            check.status = "warn"
        check.detail = "Passive topology/P2P capabilities, not an I/O test; no expected locality map configured."
        missing = [f"{key}: {check.value[key]['unavailable']}" for key in ("gpu_nic_topology", "p2p_read", "p2p_write")
                   if isinstance(check.value[key], dict)]
        if missing:
            check.detail += " Unavailable: " + "; ".join(missing)
    return check


CHECKS = {
    "gpu.inventory": inventory, "gpu.ecc": ecc, "gpu.mig": mig,
    "gpu.firmware": firmware, "gpu.board_firmware": board_firmware,
    "gpu.clocks": clocks, "gpu.power_limits": power_limits, "gpu.thermals": thermals,
    "gpu.idle_thermals": idle_thermals, "gpu.io_locality": io_locality,
}
