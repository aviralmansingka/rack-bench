"""Passive NIC/RDMA inspection; no packets or QPs created."""
import json
from pathlib import Path
import re
import shlex
import shutil

from rack_bench.common.host import Unavailable, collect_check, read_text, run_command
from rack_bench.common.models import Check

from . import nccl


def nic_inventory():
    def collect():
        devices = {}
        for path in sorted(Path("/sys/class/net").glob("*")):
            if path.name == "lo":
                continue
            record = {"physical": (path / "device").exists(), "fields": {}, "unavailable": {}}
            for field in ("address", "operstate", "mtu", "speed", "duplex", "device/vendor", "device/device", "device/numa_node"):
                if "/" in field and not record["physical"]:
                    continue
                try:
                    record["fields"][field] = read_text(path / field)
                except Unavailable as exc:
                    record["fields"][field] = None
                    record["unavailable"][field] = str(exc)
            devices[path.name] = record
        if not devices:
            raise Unavailable("/sys/class/net", "No non-loopback NICs exposed.")
        try:
            links = json.loads(run_command(["ip", "-j", "link"]))
        except Unavailable as exc:
            links = {"unavailable": str(exc)}
        return {"interfaces": devices, "ip_links": links}
    return collect_check("network.nic_inventory", collect, ["/sys/class/net/*", "ip -j link"])


def nic_firmware():
    sources = ["/sys/class/net/*/device"]
    def collect():
        values, errors = {}, {}
        for path in sorted(Path("/sys/class/net").glob("*/device")):
            name = path.parent.name
            sources.append(f"ethtool -i {name}")
            try:
                text = run_command(["ethtool", "-i", name])
                values[name] = {k.strip(): v.strip() for line in text.splitlines() if ":" in line for k, v in [line.split(":", 1)]}
            except Unavailable as exc:
                errors[name] = str(exc)
        if not values:
            raise Unavailable("ethtool -i <interface>", "; ".join(errors.values()) or "No physical NIC firmware sources exposed.")
        return {"devices": values, "unavailable": errors}
    check = collect_check("network.nic_firmware", collect, sources)
    if check.status == "pass" and check.value["unavailable"]:
        check.status, check.detail = "warn", "Some NICs could not be queried; missing firmware is not verified."
    return check


def rdma_ports():
    def collect():
        values, errors = {}, {}
        for command in ("ibstat", "ibv_devinfo"):
            try:
                text = run_command([command])
                if not text or re.search(r"no (?:IB|RDMA) devices", text, re.I):
                    raise Unavailable(command, "No RDMA devices reported.")
                values[command] = text
            except Unavailable as exc:
                errors[command] = str(exc)
        if not values:
            raise Unavailable("ibstat; ibv_devinfo", "; ".join(errors.values()))
        return {"ports": values, "unavailable": errors}
    return collect_check("network.rdma_ports", collect, ["ibstat", "ibv_devinfo"])


def gpudirect_rdma():
    sources = ["/sys/class/infiniband", "/sys/module/nvidia_peermem", "/sys/module/gdrdrv"]
    def collect():
        devices = sorted(p.name for p in Path(sources[0]).glob("*"))
        if not devices:
            raise Unavailable(sources[0], "No RDMA devices exposed in sysfs.")
        return {"rdma_devices": devices, "nvidia_peermem": Path(sources[1]).exists(),
                "gdrdrv": Path(sources[2]).exists()}
    check = collect_check("network.gpudirect_rdma", collect, sources)
    if check.status == "pass":
        check.detail = "Passive module presence only; GDRCopy observation is the gdrdrv module. No RDMA work launched."
        if not check.value["nvidia_peermem"]:
            check.status = "warn"
            check.detail += " GPUDirect RDMA not enabled alongside RDMA devices."
    return check


def congestion_control():
    def collect():
        data = {}
        for pattern in ("*/ecn/**/*", "*/roce_cc/**/*"):
            for path in Path("/sys/class/net").glob(pattern):
                if path.is_file():
                    data[str(path)] = read_text(path)
        if not data:
            raise Unavailable("/sys/class/net/*/{ecn,roce_cc}", "No driver-exposed RoCE congestion/ECN settings; TCP settings are separate.")
        return data
    return collect_check("network.congestion_control", collect, ["/sys/class/net/*/ecn", "/sys/class/net/*/roce_cc"])


def pkeys():
    source = "/sys/class/infiniband"
    def table(path):
        return {entry.name: f"0x{int(read_text(entry), 16):04x}" for entry in sorted(path.glob("[0-9]*"))}
    def collect():
        devices = sorted(Path(source).glob("*"))
        if not devices:
            raise Unavailable(source, "No IB devices exposed in sysfs.")
        values = {}
        for device in devices:
            direct = table(device / "pkeys")
            ports = {path.parent.name: table(path) for path in sorted(device.glob("ports/*/pkeys"))}
            if not direct and not any(ports.values()):
                raise Unavailable(str(device), "No readable PKey tables exposed; access may require root.")
            values[device.name] = {"default_index": 0, "pkeys": direct, "ports": ports}
        return values
    check = collect_check("network.pkeys", collect, [source + "/*/{pkeys,ports/*/pkeys}/*"])
    if check.status == "pass":
        check.detail = "Observed hexadecimal IB partition keys; default index is 0. No partition membership inferred."
    return check


def tcp_config():
    paths = {name: f"/proc/sys/net/{directory}/{name}"
             for directory, names in (
                 ("ipv4", ("tcp_congestion_control", "tcp_ecn", "tcp_rmem", "tcp_wmem", "ip_local_port_range",
                           "tcp_window_scaling", "tcp_mtu_probing", "tcp_available_congestion_control")),
                 ("core", ("rmem_max", "wmem_max"))) for name in names}
    command = ["tc", "qdisc", "show"]
    sources = [*paths.values(), shlex.join(command)]
    def collect():
        values, errors = {}, {}
        for name, path in paths.items():
            try:
                value = read_text(path)
                if name in ("tcp_rmem", "tcp_wmem", "ip_local_port_range"):
                    value = [int(part) for part in value.split()]
                    count = 2 if name == "ip_local_port_range" else 3
                    if len(value) != count:
                        raise ValueError(f"Expected {count} integers for {name}.")
                elif name == "tcp_available_congestion_control":
                    value = value.split()
                elif name not in ("tcp_congestion_control", "tcp_ecn"):
                    value = int(value)
                values[name] = value
            except (Unavailable, ValueError) as exc:
                errors[name] = str(exc)
        try:
            values["qdisc"] = run_command(command)
        except Unavailable as exc:
            errors["qdisc"] = str(exc)
        if not values:
            raise Unavailable(sources[0], "; ".join(f"{name}: {reason}" for name, reason in errors.items()))
        return {**values, "unavailable": errors}
    check = collect_check("network.tcp_config", collect, sources)
    if check.status == "pass":
        check.detail = ("Host TCP configuration facts that bound single-stream throughput "
                        "(socket buffer maxima vs path RTT, congestion control, port range, qdisc); "
                        "not a circuit measurement. No certification profile applied.")
    return check


def switch():
    return Check("network.switch", "skip", detail="No authenticated switch CLI/API configured; use host RDMA counters as a fallback. No network probes sent.")


def ufm():
    sources = []
    def collect():
        command = None
        if shutil.which("dpkg-query"):
            command = ["dpkg-query", "-W", "-f=${db:Status-Abbrev}\t${binary:Package}\t${Version}\n", "ufm*"]
        elif shutil.which("rpm"):
            command = ["rpm", "-qa", "--qf", "%{NAME}\t%{VERSION}-%{RELEASE}\n"]
        if command:
            sources.append(shlex.join(command))
            try:
                packages = {}
                for line in run_command(command, ok_codes=(0, 1)).splitlines():
                    parts = line.split("\t")
                    if command[0] == "dpkg-query":
                        if len(parts) != 3 or len(parts[0]) < 2 or parts[0][1] != "i":
                            continue
                        parts = parts[1:]
                    if len(parts) == 2 and parts[0].startswith("ufm") and parts[1].strip():
                        packages[parts[0]] = parts[1].strip()
                if packages:
                    package = next((name for name in ("ufm-enterprise", "ufm") if name in packages), sorted(packages)[0])
                    return {"present": True, "via": "package metadata", "package": package,
                            "version": packages[package], "packages": packages}
            except Unavailable:
                pass
        found = None
        for name in ("ufmcli", "ufmctl"):
            binary = shutil.which(name)
            if not binary:
                continue
            found = {"present": True, "via": "binary", "binary": binary, "version": None}
            command = [binary, "--version"]
            sources.append(shlex.join(command))
            try:
                match = re.search(r"\b\d+\.\d+(?:\.\d+)*(?:[-+][\w.]+)?", run_command(command))
                if match:
                    return {**found, "version": match.group()}
            except Unavailable:
                pass
        if shutil.which("systemctl"):
            command = ["systemctl", "show", "ufm.service", "ufm-enterprise.service", "podman-ufm.service",
                       "-p", "Id", "-p", "LoadState", "-p", "ActiveState"]
            sources.append(shlex.join(command))
            try:
                for block in run_command(command).split("\n\n"):
                    unit = dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
                    if unit.get("LoadState") in ("loaded", "masked"):
                        return {"present": True, "via": "systemd unit", "unit": unit.get("Id"),
                                "active_state": unit.get("ActiveState"), "version": None}
            except Unavailable:
                pass
        if found:
            return found
        raise Unavailable("local UFM discovery", "UFM not present.")
    check = collect_check("network.ufm", collect, sources)
    if check.status == "pass":
        check.detail = ("UFM present; version not locally discoverable — version detail via the UFM API is credential-gated (profile)"
                        if check.value["version"] is None else
                        "UFM present; version belongs to the named local package/tool. UFM API verification is credential-gated (profile).")
    return check


def rdma_error_counters():
    def collect():
        values = {}
        for pattern in ("*/ports/*/counters/*", "*/ports/*/hw_counters/*"):
            for path in Path("/sys/class/infiniband").glob(pattern):
                if re.search(r"error|discard|drop|down|recovery", path.name, re.I):
                    values[str(path)] = int(read_text(path))
        return values
    return collect_check("network.rdma_error_counters", collect, ["/sys/class/infiniband/*/ports/*/{counters,hw_counters}/*"])


CHECKS = {
    "network.nic_inventory": nic_inventory, "network.nic_firmware": nic_firmware,
    "network.rdma_ports": rdma_ports, "network.gpudirect_rdma": gpudirect_rdma,
    "network.congestion_control": congestion_control, "network.pkeys": pkeys,
    "network.tcp_config": tcp_config, "network.switch": switch, "network.ufm": ufm,
    "network.rdma_error_counters": rdma_error_counters,
    **nccl.CHECKS,
}
