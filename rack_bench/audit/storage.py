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
    "storage.inventory": inventory, "storage.mounts": mounts, "storage.nvme_controllers": nvme_controllers,
    "storage.nvme_namespaces": nvme_namespaces, "storage.nvme_health": nvme_health,
    "storage.smart_health": smart_health, "storage.ssd_firmware": ssd_firmware,
}
