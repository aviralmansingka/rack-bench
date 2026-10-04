"""Passive NIC/RDMA and NCCL configuration inspection; no packets or QPs created."""
import ipaddress
import json
import os
from pathlib import Path
import re

from rack_bench.common.host import Unavailable, collect_check, read_text, run_command
from rack_bench.common.models import Check

NCCL_KEYS = ("NCCL_IB_HCA", "NCCL_IB_GID_INDEX", "NCCL_SOCKET_IFNAME", "NCCL_NET_GDR_LEVEL")
PLUGIN = re.compile(r"lib(?:nccl[-_](?:net|tuner)[\w-]*|sharp_coll|sharp|spcx[\w-]*|gib[\w-]*)\.so")


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


def tcp_config():
    return collect_check("network.tcp_config", lambda: {name: read_text(f"/proc/sys/net/ipv4/{name}")
                         for name in ("tcp_congestion_control", "tcp_ecn")},
                         ["/proc/sys/net/ipv4/tcp_congestion_control", "/proc/sys/net/ipv4/tcp_ecn"])


def switch():
    return Check("network.switch", "skip", detail="No authenticated switch CLI/API configured; use host RDMA counters as a fallback. No network probes sent.")


def rdma_error_counters():
    def collect():
        values = {}
        for pattern in ("*/ports/*/counters/*", "*/ports/*/hw_counters/*"):
            for path in Path("/sys/class/infiniband").glob(pattern):
                if re.search(r"error|discard|drop|down|recovery", path.name, re.I):
                    values[str(path)] = int(read_text(path))
        return values
    return collect_check("network.rdma_error_counters", collect, ["/sys/class/infiniband/*/ports/*/{counters,hw_counters}/*"])


def hca_names():
    return collect_check("nccl.hca_names", lambda: sorted(p.name for p in Path("/sys/class/infiniband").glob("*")), ["/sys/class/infiniband"])


def rail_map():
    def collect():
        return {p.name: {"pci_path": str((p / "device").resolve()),
                         "numa_node": read_text(p / "device/numa_node") if (p / "device/numa_node").exists() else None,
                         "netdevs": sorted(n.name for n in (p / "device/net").glob("*"))}
                for p in sorted(Path("/sys/class/infiniband").glob("*"))}
    check = collect_check("nccl.rail_map", collect, ["/sys/class/infiniband/*/device"])
    if check.status == "pass":
        check.detail = "Observed HCA/PCI/NUMA associations; rail and plane expectations require a future fabric profile."
    return check


def _nccl_config(paths):
    files = {}
    for path in paths:
        if path.exists():
            entries = {}
            for line in read_text(path).splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() in NCCL_KEYS:
                    entries[key.strip()] = value.strip()
            files[str(path)] = entries
    env = {key: os.environ[key] for key in NCCL_KEYS if key in os.environ}
    effective = {}
    for values in files.values():
        effective.update(values)
    effective.update(env)
    if not effective:
        raise Unavailable("NCCL environment/config files", "No allowlisted NCCL defaults present in environment or config files.")
    return {"environment": env, "files": files, "effective": effective}


def env_defaults():
    paths = [Path("/etc/nccl.conf"), Path(os.environ.get("NCCL_CONF_FILE", str(Path.home() / ".nccl.conf")))]
    check = collect_check("nccl.env_defaults", lambda: _nccl_config(paths), ["environment: " + ", ".join(NCCL_KEYS), *map(str, paths)])
    if check.status == "pass":
        check.detail = "Allowlisted settings only; environment wins. User-file selection follows NCCL_CONF_FILE or legacy ~/.nccl.conf. No routability validation."
    return check


def gid_selection():
    def collect():
        return {str(p): read_text(p) for p in sorted(Path("/sys/class/infiniband").glob("*/ports/*/gids/*"))}
    check = collect_check("nccl.gid_selection", collect, ["/sys/class/infiniband/*/ports/*/gids/*"])
    if check.status == "pass":
        try:
            local = any(ipaddress.IPv6Address(value).is_link_local for value in check.value.values())
        except ipaddress.AddressValueError:
            check.status, check.detail = "skip", "Cannot decode GID addresses."
            return check
        check.status = "warn" if local else "pass"
        check.detail = "GID inventory only; link-local entries need explicit selection review. End-to-end routability is not tested."
    return check


def plugins_present():
    def collect():
        return [line.strip() for line in run_command(["ldconfig", "-p"]).splitlines() if PLUGIN.search(line)]
    check = collect_check("nccl.plugins_present", collect, ["ldconfig -p"])
    if check.status == "pass":
        check.detail = "Loader-cache presence, not proof a future NCCL job will load the plugin; versions are in the software manifest when packaged."
    return check


def plugins_loaded():
    def collect():
        found = {}
        for path in sorted(Path("/proc").glob("[0-9]*/maps")):
            try:
                libraries = sorted({parts[5] for line in read_text(path).splitlines()
                                    if len(parts := line.split(maxsplit=5)) == 6 and PLUGIN.search(parts[5])})
            except Unavailable:
                continue
            if libraries:
                found[path.parent.name] = libraries
        if not found:
            raise Unavailable("/proc/[0-9]*/maps", "No loaded NCCL/SHARP plugins visible in readable process maps; other users' processes may be inaccessible.")
        return found
    return collect_check("nccl.plugins_loaded", collect, ["/proc/[0-9]*/maps"])


def queue_pairs():
    return Check("nccl.queue_pairs", "skip", detail="QP creation changes RDMA state and is excluded from read-only audit; ACTIVE ports alone do not verify it.")


def imex():
    def collect():
        text = run_command(["systemctl", "show", "nvidia-imex.service", "-p", "LoadState", "-p", "ActiveState"])
        values = dict(line.split("=", 1) for line in text.splitlines() if "=" in line)
        if values.get("LoadState") == "not-found":
            raise Unavailable("systemctl show nvidia-imex.service", "IMEX service is not installed.")
        return values
    check = collect_check("nccl.imex", collect, ["systemctl show nvidia-imex.service -p LoadState -p ActiveState"])
    if check.status == "pass" and check.value.get("ActiveState") != "active":
        check.status, check.detail = "warn", "IMEX service is installed but not active."
    return check


def imex_config():
    def collect():
        channels = sorted(p.name for p in Path("/dev/nvidia-caps-imex-channels").glob("*"))
        settings = {}
        path = Path("/etc/nvidia-imex/config.cfg")
        if path.exists():
            for line in read_text(path).splitlines():
                key, sep, value = line.partition("=")
                if sep and key.strip() in ("IMEX_SERVER_PORT", "IMEX_DOMAIN_ID", "IMEX_CHANNEL_COUNT"):
                    settings[key.strip()] = value.strip()
        if not channels and not settings:
            raise Unavailable(str(path), "No IMEX channel devices or allowlisted fabric settings exposed.")
        return {"channels": channels, "settings": settings}
    return collect_check("nccl.imex_config", collect, ["/dev/nvidia-caps-imex-channels", "/etc/nvidia-imex/config.cfg"])


def all_reduce_canary():
    return Check("nccl.all_reduce_canary", "skip", detail="An active two-rank GPU all-reduce is outside read-only audit; no workload is launched.")


CHECKS = {
    "network.nic_inventory": nic_inventory, "network.nic_firmware": nic_firmware,
    "network.rdma_ports": rdma_ports, "network.congestion_control": congestion_control,
    "network.tcp_config": tcp_config, "network.switch": switch, "network.rdma_error_counters": rdma_error_counters,
    "nccl.hca_names": hca_names, "nccl.rail_map": rail_map, "nccl.env_defaults": env_defaults,
    "nccl.gid_selection": gid_selection, "nccl.plugins_present": plugins_present, "nccl.plugins_loaded": plugins_loaded,
    "nccl.queue_pairs": queue_pairs, "nccl.imex": imex, "nccl.imex_config": imex_config,
    "nccl.all_reduce_canary": all_reduce_canary,
}
