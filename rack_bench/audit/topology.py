"""NUMA/PCIe inventory and passive NVLink/NVSwitch probing."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from rack_bench.common.host import Unavailable, collect_check, read_text, run_command


def numa():
    def collect():
        nodes = {p.name: {"cpulist": read_text(p / "cpulist"), "distance": read_text(p / "distance")}
                 for p in sorted(Path("/sys/devices/system/node").glob("node[0-9]*"))}
        cpus = {p.name: [n.name for n in sorted(p.glob("node[0-9]*"))]
                for p in sorted(Path("/sys/devices/system/cpu").glob("cpu[0-9]*"))}
        if not nodes and not cpus:
            raise Unavailable("/sys/devices/system/cpu", "No CPU/NUMA sysfs maps exposed.")
        return {"nodes": nodes, "cpu_nodes": cpus, "online": read_text("/sys/devices/system/cpu/online")}
    return collect_check("topology.numa", collect, ["/sys/devices/system/node/node*", "/sys/devices/system/cpu/cpu*/node*", "/sys/devices/system/cpu/online"])


def pcie():
    def collect():
        data = {}
        for path in sorted(Path("/sys/bus/pci/devices").glob("*")):
            fields = {}
            for field in ("numa_node", "current_link_speed", "current_link_width", "max_link_speed", "max_link_width"):
                fields[field] = read_text(path / field) if (path / field).exists() else None
            data[path.name] = fields
        if not any(row["current_link_width"] is not None for row in data.values()):
            raise Unavailable("/sys/bus/pci/devices", "PCIe link width/speed not exposed; device enumeration is in topology.pci_names.")
        return data
    check = collect_check("topology.pcie", collect, ["/sys/bus/pci/devices/*/{numa_node,current_link_speed,current_link_width,max_link_speed,max_link_width}"])
    if check.status == "pass":
        check.detail = "Reported PCIe link attributes; null means not exposed on that function. No expected lane/speed profile applied."
    return check


def _parse_pci(text):
    devices = []
    for block in text.split("\n\n"):
        record = {}
        for line in block.splitlines():
            key, sep, value = line.partition(":")
            if sep:
                if key in record:
                    record[key] = [*record[key], value.strip()] if isinstance(record[key], list) else [record[key], value.strip()]
                else:
                    record[key] = value.strip()
        if "Slot" in record:
            devices.append(record)
    return devices


def pci_names():
    return collect_check("topology.pci_names", lambda: _parse_pci(run_command(["lspci", "-D", "-vmm"])), ["lspci -D -vmm"])


def fabric():
    sources = ["nvidia-smi -q -x"]
    def collect():
        root = ET.fromstring(run_command(["nvidia-smi", "-q", "-x"]))
        devices = {}
        for gpu in root.findall("gpu"):
            section = gpu.find("fabric")
            if section is None:
                section = gpu.find("gpu_fabric")
            if section is None:
                continue
            values = {field.tag: field.text.strip() for field in section.iter()
                      if field.text and not list(field) and field.text.strip().lower() not in ("", "n/a", "not supported")}
            if values:
                devices[gpu.findtext("uuid") or gpu.get("id")] = values
        if not devices:
            raise Unavailable("nvidia-smi -q -x", "No supported NVLink fabric fields; GPU/NVSwitch fabric unavailable on this host.")
        sources.append("nvidia-smi topo -m")
        value = {"devices": devices, "topology": run_command(["nvidia-smi", "topo", "-m"])}
        sources.append("systemctl show nvidia-fabricmanager.service -p LoadState -p ActiveState")
        try:
            value["fabric_manager"] = run_command(["systemctl", "show", "nvidia-fabricmanager.service", "-p", "LoadState", "-p", "ActiveState"])
        except Unavailable as exc:
            value["fabric_manager"] = {"unavailable": str(exc)}
        return value
    return collect_check("nvlink.fabric", collect, sources)


def _links(text):
    data, gpu = {}, None
    for line in text.splitlines():
        match = re.match(r"GPU\s+(\d+):", line.strip())
        if match:
            gpu = match.group(1)
            data[gpu] = {}
        link = re.search(r"Link\s+(\d+):\s*(.*)", line)
        if link and gpu is not None:
            state = link.group(2).strip()
            rate = re.search(r"(\d+(?:\.\d+)?)\s*GB/s", state)
            active = (float(rate.group(1)) > 0) if rate else state.lower() == "active"
            data[gpu][link.group(1)] = {"active": active, "reported": state,
                                      "bandwidth_gb_s": float(rate.group(1)) if rate else None}
    if not any(data.values()):
        raise Unavailable("nvidia-smi nvlink --status", "No NVLink link records; NVLink is unsupported or unavailable on this host.")
    return data


def links_per_gpu():
    def collect():
        return {gpu: sum(link["active"] for link in ports.values())
                for gpu, ports in _links(run_command(["nvidia-smi", "nvlink", "--status"])).items()}
    check = collect_check("nvlink.links_per_gpu", collect, ["nvidia-smi nvlink --status"])
    if check.status == "pass":
        check.detail = "Active NVLink counts; an expected fabric map is needed to distinguish disabled and missing links."
    return check


def link_state():
    return collect_check("nvlink.link_state", lambda: _links(run_command(["nvidia-smi", "nvlink", "--status"])), ["nvidia-smi nvlink --status"])


def link_width():
    def collect():
        text = run_command(["nvidia-smi", "nvlink", "--getLinkWidth"])
        if not re.search(r"(?:width|lanes)[^\n]*\d", text, re.I) or re.search(r"not supported|unsupported", text, re.I):
            raise Unavailable("nvidia-smi nvlink --getLinkWidth", "Physical NVLink width is not exposed by this GPU/driver; GB/s is not a lane count.")
        return text
    return collect_check("nvlink.link_width", collect, ["nvidia-smi nvlink --getLinkWidth"])


CHECKS = {
    "topology.numa": numa, "topology.pcie": pcie, "topology.pci_names": pci_names,
    "nvlink.fabric": fabric, "nvlink.links_per_gpu": links_per_gpu,
    "nvlink.link_state": link_state, "nvlink.link_width": link_width,
}
