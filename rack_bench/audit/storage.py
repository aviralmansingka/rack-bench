"""Block/namespace metadata, mount options, and read-only SMART requests."""
import json
from pathlib import Path
import re

from rack_bench.common.host import Unavailable, collect_check, read_text, run_command
from rack_bench.common.models import Check


def inventory():
    command = ["lsblk", "-J", "-b", "-o", "NAME,TYPE,SIZE,MODEL,SERIAL,REV,TRAN,ROTA"]
    return collect_check("storage.inventory", lambda: json.loads(run_command(command))["blockdevices"], [" ".join(command)])


def _unescape(value):
    return re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), value)


def _mounts(text):
    values = []
    for line in text.splitlines():
        fields = line.split()
        if len(fields) < 6:
            raise ValueError("Invalid /proc/mounts record")
        source, target, fs = map(_unescape, fields[:3])
        options = fields[3]
        source = re.sub(r"(//)[^/@\s]+:[^/@\s]+@", r"\1<redacted>@", source)
        safe_options = []
        for raw_option in options.split(","):
            option = _unescape(raw_option)
            key = option.split("=", 1)[0]
            if any(token in key.lower() for token in ("password", "passwd", "secret", "token", "credentials")):
                option = key + "=<redacted>"
            safe_options.append(option)
        values.append({"source": source, "target": target, "fstype": fs, "options": safe_options,
                       "storage_class": "shared" if fs in ("nfs", "nfs4", "cifs", "lustre", "ceph", "glusterfs", "fuse.sshfs") else "local_or_virtual"})
    return values


def mounts():
    return collect_check("storage.mounts", lambda: _mounts(read_text("/proc/mounts")), ["/proc/mounts"])


def software_raid():
    source = "/sys/block/md*/md"
    def collect():
        arrays = {}
        for md in sorted(Path("/sys/block").glob("md*/md")):
            level = read_text(md / "level")
            redundant = level not in ("raid0", "linear")
            arrays[md.parent.name] = {
                "level": level,
                "raid_disks": int(read_text(md / "raid_disks")),
                "degraded": int(read_text(md / "degraded")) if redundant else None,
                "sync_action": read_text(md / "sync_action") if redundant else None,
                "members": sorted(p.name for p in (md.parent / "slaves").iterdir()),
            }
        if not arrays:
            raise Unavailable(source, "no md arrays exposed in sysfs.")
        return arrays
    check = collect_check("storage.software_raid", collect, [source, "/sys/block/md*/slaves"])
    if check.status == "pass":
        check.detail = "md sysfs inventory; redundancy fields are null for RAID0/linear arrays."
        affected = [name for name, array in check.value.items()
                    if array["degraded"] or array["sync_action"] not in (None, "idle", "frozen")]
        if affected:
            check.status = "warn"
            check.detail = "Degraded array or active synchronization: " + ", ".join(affected)
    return check


def lvm():
    sources = []
    def collect():
        values = {}
        for tool, section, fields in (("pvs", "pv", "pv_name,vg_name,pv_size"),
                                      ("vgs", "vg", "vg_name,vg_size"),
                                      ("lvs", "lv", "lv_name,vg_name,lv_size,devices")):
            command = [tool, "--readonly", "--reportformat", "json", "--units", "b", "-o", fields]
            sources.append(" ".join(command))
            document = json.loads(run_command(command))
            values[tool] = [{field: row[field] for field in fields.split(",")}
                            for report in document["report"] for row in report[section]]
            if tool == "pvs" and not values[tool]:
                raise Unavailable(sources[-1], "No LVM PVs reported.")
        return values
    check = collect_check("storage.lvm", collect, sources)
    if check.status == "pass":
        check.detail = "LVM sizes in bytes; vg_name joins PV/VG/LV records and devices reports LV backing PVs."
    return check


def multipath():
    source = "multipath -ll"
    def collect():
        devices, current = {}, None
        for line in run_command(["multipath", "-ll"]).splitlines():
            header = re.match(r"^(\S+)(?:\s+\(([^)]+)\))?\s+(dm-\d+)\b", line)
            if header:
                name, wwn, dm = header.groups()
                current = {"alias": name if wwn else None, "wwn": wwn or name,
                           "dm_device": dm, "paths": []}
                devices[dm] = current
                continue
            path = re.match(r"^[|`+\\\-\s]*(\S+)\s+(\S+)\s+(\d+:\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$", line)
            if path and current is not None:
                address, device, major_minor, dm_state, state, device_state = path.groups()
                current["paths"].append({"address": address, "device": device, "major_minor": major_minor,
                                         "dm_state": dm_state, "state": state, "device_state": device_state,
                                         "usable": dm_state == "active" and state in ("ready", "ghost")
                                         and device_state == "running"})
        if not devices:
            raise Unavailable(source, "multipath not present: no multipath devices listed.")
        for device in devices.values():
            device["total_paths"] = len(device["paths"])
            device["usable_paths"] = sum(path["usable"] for path in device["paths"])
        return devices
    check = collect_check("storage.multipath", collect, [source])
    if check.status == "pass":
        check.detail = "observed paths only; configured path count is verified against the certification profile, not probed."
        affected = [name for name, device in check.value.items()
                    if device["usable_paths"] < 2 or device["usable_paths"] < device["total_paths"]]
        if affected:
            check.status = "warn"
            check.detail += " Unusable paths or fewer than two usable paths: " + ", ".join(affected)
    elif check.detail.startswith("Command not found:"):
        check.detail = "multipath not present: " + check.detail
    return check


def nvme_controllers():
    def collect():
        return {p.name: {field: read_text(p / field) if (p / field).exists() else None
                         for field in ("model", "serial", "firmware_rev", "state", "transport")}
                for p in sorted(Path("/sys/class/nvme").glob("nvme[0-9]*"))}
    return collect_check("storage.nvme_controllers", collect, ["/sys/class/nvme/nvme*/{model,serial,firmware_rev,state,transport}"])


def nvme_namespaces():
    def collect():
        return {p.name: {field: read_text(p / field) if (p / field).exists() else None
                         for field in ("nsid", "size", "queue/logical_block_size", "queue/physical_block_size", "device/model")}
                for p in sorted(Path("/sys/block").glob("nvme*n*"))}
    check = collect_check("storage.nvme_namespaces", collect, ["/sys/block/nvme*n*/{nsid,size,queue/logical_block_size,queue/physical_block_size,device/model}"])
    if check.status == "pass":
        check.detail = "Namespace size is in 512-byte sectors; logical/physical block sizes are bytes."
    return check


def _smart(name, devices):
    sources, values, errors = [], {}, {}
    for device in devices:
        command = ["smartctl", "--json", "--health", "--attributes", device]
        sources.append(" ".join(command))
        try:
            # Bits 3..7 are health/error-history findings, not command execution failures.
            data = json.loads(run_command(command, ok_codes=tuple(range(0, 256, 8))))
            if not isinstance(data, dict) or not isinstance(data.get("smart_status", {}).get("passed"), bool):
                raise Unavailable(sources[-1], "SMART health status not supported/exposed.")
            values[device] = {key: data[key] for key in ("smart_status", "nvme_smart_health_information_log",
                              "ata_smart_attributes", "scsi_error_counter_log", "temperature", "power_on_time") if key in data}
        except (Unavailable, ValueError, TypeError) as exc:
            errors[device] = str(exc)
    if not devices:
        return Check(name, "skip", detail="No matching disk/controller devices exposed in sysfs.", source=["/sys/block", "/sys/class/nvme"])
    status = "skip" if errors or not values else "pass"
    detail = "Read-only SMART health/attributes; no self-tests started."
    if errors:
        detail += " Incomplete: " + "; ".join(f"{device}: {reason}" for device, reason in errors.items())
    for data in values.values():
        if data["smart_status"]["passed"] is False:
            status = "fail"
            detail += " A device explicitly reports failed SMART health."
    return Check(name, status, {"devices": values, "unavailable": errors}, detail=detail, source=sources)


def nvme_health():
    return _smart("storage.nvme_health", [f"/dev/{p.name}" for p in sorted(Path("/sys/class/nvme").glob("nvme[0-9]*"))])


def smart_health():
    return _smart("storage.smart_health", [f"/dev/{p.name}" for p in sorted(Path("/sys/block").glob("sd*"))])


def ssd_firmware():
    def collect():
        values = {}
        for p in sorted(Path("/sys/block").glob("*")):
            if p.name.startswith("nvme"):
                path = p / "device/firmware_rev"
            elif p.name.startswith("sd"):
                # SCSI revision is inventory only: SATA/SAS device may be an HDD.
                path = p / "device/rev"
            else:
                continue
            if path.exists():
                values[p.name] = {"revision": read_text(path), "model": read_text(p / "device/model") if (p / "device/model").exists() else None}
        return values
    check = collect_check("storage.ssd_firmware", collect, ["/sys/block/nvme*/device/firmware_rev", "/sys/block/sd*/device/rev"])
    if check.status == "pass":
        check.detail = "NVMe firmware and SCSI revision inventory; SCSI media is not assumed to be SSD."
    return check


CHECKS = {
    "storage.inventory": inventory, "storage.mounts": mounts,
    "storage.software_raid": software_raid, "storage.lvm": lvm, "storage.multipath": multipath,
    "storage.nvme_controllers": nvme_controllers,
    "storage.nvme_namespaces": nvme_namespaces, "storage.nvme_health": nvme_health,
    "storage.smart_health": smart_health, "storage.ssd_firmware": ssd_firmware,
}
