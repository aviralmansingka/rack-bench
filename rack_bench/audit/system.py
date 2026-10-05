"""Read-only system inventory. No inferred platform settings or default thresholds."""
import json
from pathlib import Path
import re

from rack_bench.common.host import Unavailable, read_text, run_command
from rack_bench.common.models import Check


def _skip(name, error):
    return Check(name, "skip", detail=str(error), source=[error.source])


def _lscpu():
    text = run_command(["lscpu", "--json"])
    try:
        return {item["field"].rstrip(":"): item["data"] for item in json.loads(text)["lscpu"]}
    except (ValueError, KeyError, TypeError) as exc:
        raise Unavailable("lscpu --json", "Cannot decode lscpu JSON fields.") from exc


def cpu():
    name = "system.cpu"
    try:
        fields = _lscpu()
        value = {"model": fields.get("Model name"), "architecture": fields.get("Architecture")}
        for field, key in (("CPU(s)", "logical_cpus"), ("Socket(s)", "sockets"),
                           ("Core(s) per socket", "cores_per_socket"),
                           ("Thread(s) per core", "threads_per_core"), ("NUMA node(s)", "numa_nodes")):
            value[key] = int(fields[field]) if fields.get(field) is not None else None
        value["online_cpus"] = fields.get("On-line CPU(s) list")
        value["offline_cpus"] = fields.get("Off-line CPU(s) list")
        value["numa_cpus"] = {key.removesuffix(" CPU(s)"): val for key, val in fields.items()
                              if re.fullmatch(r"NUMA node\d+ CPU\(s\)", key)}
        if not value["model"] or value["logical_cpus"] is None:
            raise Unavailable("lscpu --json", "CPU model/count absent from lscpu output.")
    except Unavailable as exc:
        return _skip(name, exc)
    except (ValueError, TypeError) as exc:
        return _skip(name, Unavailable("lscpu --json", f"Invalid CPU count fields ({type(exc).__name__})."))
    return Check(name, "pass", value, detail="Observed topology; logical_cpus includes offline CPUs. No expected hardware profile configured.",
                 source=["lscpu --json"])


def memory():
    name, source = "system.memory", "/proc/meminfo"
    try:
        fields = dict(line.split(":", 1) for line in read_text(source).splitlines() if ":" in line)
        if "MemTotal" not in fields:
            raise Unavailable(source, "MemTotal is absent from /proc/meminfo.")
        value = {}
        for field, key, factor in (("MemTotal", "mem_total_bytes", 1024),
                                   ("SwapTotal", "swap_total_bytes", 1024),
                                   ("HugePages_Total", "hugepages_total", 1),
                                   ("Hugepagesize", "hugepage_size_bytes", 1024)):
            value[key] = int(fields[field].split()[0]) * factor if field in fields else None
    except Unavailable as exc:
        return _skip(name, exc)
    except (ValueError, KeyError, IndexError) as exc:
        return _skip(name, Unavailable(source, f"Cannot decode memory fields ({type(exc).__name__})."))
    return Check(name, "pass", value, detail="Kernel-visible memory, not installed DIMM capacity; see system.dram.",
                 source=[source])


def dram():
    name, source = "system.dram", "dmidecode --type memory"
    try:
        text = run_command(["dmidecode", "--type", "memory"])
    except Unavailable as exc:
        return _skip(name, exc)
    devices = []
    for block in text.split("\n\n"):
        if "Memory Device" not in [line.strip() for line in block.splitlines()]:
            continue
        fields = {key.strip(): val.strip() for line in block.splitlines() if ":" in line
                  for key, val in [line.split(":", 1)]}
        if fields.get("Size") in (None, "No Module Installed"):
            continue
        devices.append({key: fields.get(label) for key, label in (
            ("locator", "Locator"), ("size", "Size"), ("type", "Type"),
            ("speed", "Speed"), ("configured_speed", "Configured Memory Speed"))})
    if not devices:
        return Check(name, "skip", detail="No populated DIMM records available from dmidecode.", source=[source])
    return Check(name, "pass", devices, detail="Installed DIMM sizes/types; firmware-reported units retained.",
                 source=[source])


def snc():
    name = "system.snc"
    try:
        fields = _lscpu()
    except Unavailable as exc:
        return _skip(name, exc)
    value = {key: val for key, val in fields.items()
             if "snc" in key.lower() or "sub-numa" in key.lower() or "sub numa" in key.lower()}
    if not value:
        return Check(name, "skip", detail="lscpu does not expose SNC mode; NUMA node count is not proof of a firmware setting.",
                     source=["lscpu --json"])
    return Check(name, "pass", value, source=["lscpu --json"])


def bios():
    value, sources, errors = {}, [], []
    for field in ("bios_vendor", "bios_version", "bios_date"):
        path = f"/sys/class/dmi/id/{field}"
        sources.append(path)
        try:
            value[field] = read_text(path)
        except Unavailable as exc:
            errors.append(str(exc))
    return Check("system.bios", "skip" if not value else "warn" if errors else "pass", value or None,
                 detail="; ".join(errors) if errors else "BIOS identity only; performance settings are a separate check.",
                 source=sources)


def bios_settings():
    return Check("system.bios_settings", "skip", detail="No platform BIOS-settings reader implemented; identity/boot flags do not verify firmware settings.")


def boot_parameters():
    source = "/proc/cmdline"
    try:
        words = read_text(source).split()
    except Unavailable as exc:
        return _skip("system.boot_parameters", exc)
    # Limit exports to performance/isolation options, avoiding unrelated boot secrets.
    prefixes = ("hugepages", "default_hugepagesz", "isolcpus", "nohz_full", "rcu_nocbs",
                "iommu", "intel_iommu", "amd_iommu", "cgroup", "systemd.unified_cgroup_hierarchy",
                "numa_balancing", "transparent_hugepage")
    parameters = [word for word in words if word.split("=", 1)[0].startswith(prefixes)]
    return Check("system.boot_parameters", "pass", {"parameters": parameters},
                 detail="Performance/isolation boot options only; other boot arguments omitted.", source=[source])


def thermal_profile():
    name, root = "system.thermal_profile", Path("/sys/class/thermal")
    sources = [str(root)]
    try:
        paths = sorted(root.iterdir())
    except OSError as exc:
        return _skip(name, Unavailable(str(root), f"Cannot enumerate thermal zones: {exc}."))
    zones, errors = {}, []
    for path in paths:
        if not path.name.startswith("thermal_zone"):
            continue
        try:
            for field in ("type", "temp", "policy"):
                sources.append(str(path / field))
            zones[path.name] = {"type": read_text(path / "type"),
                                "temperature_c": int(read_text(path / "temp")) / 1000,
                                "policy": read_text(path / "policy") if (path / "policy").exists() else None}
        except (Unavailable, ValueError) as exc:
            errors.append(f"{path.name}: {exc}")
    detail = "; ".join(errors) if errors else "Thermal zone temperatures in Celsius and kernel cooling policy; not a BIOS/acoustic profile."
    if not zones:
        detail = "; ".join(errors) or "No thermal_zone devices exposed in /sys/class/thermal."
    return Check(name, "skip" if not zones else "warn" if errors else "pass", zones or None,
                 detail=detail, source=sources)


def dlc_telemetry():
    return Check("system.dlc_telemetry", "skip", detail="No BMC telemetry source configured; coolant temperature, flow and pressure were not queried.")


CHECKS = {
    "system.cpu": cpu,
    "system.memory": memory,
    "system.dram": dram,
    "system.snc": snc,
    "system.bios": bios,
    "system.bios_settings": bios_settings,
    "system.boot_parameters": boot_parameters,
    "system.thermal_profile": thermal_profile,
    "system.dlc_telemetry": dlc_telemetry,
}
