"""Passive NCCL configuration inspection; no packets or QPs created."""
import ipaddress
import os
from pathlib import Path
import re

from rack_bench.common.host import Unavailable, collect_check, read_text, run_command

NCCL_KEYS = ("NCCL_IB_HCA", "NCCL_IB_GID_INDEX", "NCCL_SOCKET_IFNAME", "NCCL_NET_GDR_LEVEL")
PLUGIN = re.compile(r"lib(?:nccl[-_](?:net|tuner)[\w-]*|sharp_coll|sharp|spcx[\w-]*|gib[\w-]*)\.so")


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


CHECKS = {
    "nccl.hca_names": hca_names, "nccl.rail_map": rail_map, "nccl.env_defaults": env_defaults,
    "nccl.gid_selection": gid_selection, "nccl.plugins_present": plugins_present, "nccl.plugins_loaded": plugins_loaded,
    "nccl.imex": imex, "nccl.imex_config": imex_config,
}
