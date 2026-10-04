"""Passive security checks. Historical placeholder floors are NOT a certification baseline."""
from pathlib import Path
import os
import re
import shlex
import stat

from rack_bench.common.host import Unavailable, collect_check, read_text, run_command
from rack_bench.common.models import Check

# Deliberately small historical examples, not an exhaustive/current advisory table.
# Numeric upstream comparisons do not recognize distro backports or fixed older branches.
MINIMUM_VERSIONS = {
    "runc": {"minimum": "1.1.12", "placeholder": True, "advisory": "https://nvd.nist.gov/vuln/detail/CVE-2024-21626"},
    "nvidia_container_toolkit": {"minimum": "1.16.2", "placeholder": True,
        "advisory": "https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/release-notes.html#nvidia-container-toolkit-1-16-2"},
    "docker": {"minimum": "27.1.1", "placeholder": True, "advisory": "https://docs.docker.com/engine/release-notes/27/#2711"},
}


def _version(text):
    match = re.search(r"(?<![\d.])(\d+(?:\.\d+)+)([-+][\w.~-]+)?", text)
    if not match:
        raise ValueError("No dotted version in source")
    return match.group(0)


def _numeric(version):
    return tuple(int(part) for part in re.match(r"\d+(?:\.\d+)+", version).group(0).split("."))


def _grade_floor(check, component):
    rule = MINIMUM_VERSIONS.get(component)
    check.expected = rule
    if rule:
        check.source.append(rule["advisory"])
    if check.status == "skip":
        return check
    if not rule:
        check.status, check.detail = "skip", "Observed version, but no reviewed minimum for this component in the placeholder table."
        return check
    versions = check.value.values() if isinstance(check.value, dict) else [check.value]
    comparisons = []
    for value in versions:
        actual, floor = _numeric(value), _numeric(rule["minimum"])
        size = max(len(actual), len(floor))
        comparisons.append((actual + (0,) * (size - len(actual))) >= (floor + (0,) * (size - len(floor))))
    if all(comparisons) and any(re.search(r"(?:rc|alpha|beta|pre)", value, re.I) for value in versions):
        check.status, check.detail = "warn", "Prerelease version cannot be certified against a stable release floor."
    else:
        check.status = "pass" if all(comparisons) else "fail"
        check.detail = "Meets" if check.status == "pass" else "Below"
        check.detail += " the historical PLACEHOLDER upstream floor only; not a current CVE safety verdict. Distro backports/other fixed branches are not modeled."
    return check


def _floor(name, component, command, parse=_version):
    check = collect_check(name, lambda: parse(run_command(command)), [shlex.join(command)])
    return _grade_floor(check, component)


def driver_cve_floor():
    return _floor("security.driver_cve_floor", "driver", ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"])


def container_toolkit_cve_floor():
    return _floor("security.container_toolkit_cve_floor", "nvidia_container_toolkit", ["nvidia-ctk", "--version"])


def cuda_cve_floor():
    return _floor("security.cuda_cve_floor", "cuda", ["nvcc", "--version"])


def runc_cve_floor():
    return _floor("security.runc_cve_floor", "runc", ["runc", "--version"])


def docker_cve_floor():
    # A CLI version is not a daemon security version. Do not follow remote Docker contexts.
    return _floor("security.docker_cve_floor", "docker",
                  ["docker", "--host", "unix:///var/run/docker.sock", "version", "--format", "{{.Server.Version}}"])


def podman_cve_floor():
    return _floor("security.podman_cve_floor", "podman", ["podman", "--version"])


def connectx_cve_floor():
    check = collect_check("security.connectx_cve_floor", lambda: {p.parent.name: _version(read_text(p))
                          for p in Path("/sys/class/infiniband").glob("*/fw_ver")}, ["/sys/class/infiniband/*/fw_ver"])
    return _grade_floor(check, "connectx")


def dcgm_cve_floor():
    return _floor("security.dcgm_cve_floor", "dcgm", ["dcgmi", "--version"])


def dcgm_exporter_cve_floor():
    return _floor("security.dcgm_exporter_cve_floor", "dcgm_exporter",
                  ["dpkg-query", "-W", "-f=${Version}", "dcgm-exporter"])


def bluefield_cve_floor():
    return Check("security.bluefield_cve_floor", "skip", detail="No authenticated BlueField firmware source; DPU OS version cannot be inferred from NIC firmware.")


def kernel_cve_floor():
    return _floor("security.kernel_cve_floor", "kernel", ["uname", "-r"])


def known_bad_kernels():
    check = collect_check("security.known_bad_kernels", lambda: run_command(["uname", "-r"]), ["uname -r"])
    if check.status == "pass":
        check.status, check.detail = "skip", "Kernel recorded; no branch/distro-specific known-bad advisory list configured."
    return check


def iommu():
    def collect():
        params = [p for p in read_text("/proc/cmdline").split()
                  if p.startswith(("iommu=", "iommu.passthrough=", "intel_iommu=", "amd_iommu="))]
        groups = {p.name: read_text(p / "type") if (p / "type").exists() else None
                  for p in sorted(Path("/sys/kernel/iommu_groups").glob("[0-9]*"))}
        return {"parameters": params, "domain_types": groups}
    check = collect_check("security.iommu", collect, ["/proc/cmdline", "/sys/kernel/iommu_groups/*/type"])
    check.expected = {"passthrough": False, "identity_domains": False}
    if check.status != "pass":
        return check
    params, groups = check.value["parameters"], check.value["domain_types"]
    bad = any(p in ("iommu=off", "iommu=soft", "intel_iommu=off", "amd_iommu=off")
              or (p.startswith("iommu=") and "pt" in p.split("=", 1)[1].split(","))
              or p in ("iommu.passthrough=1", "iommu.passthrough=y", "iommu.passthrough=on", "iommu.passthrough=true") for p in params)
    if bad or any(value and value.lower() == "identity" for value in groups.values()):
        check.status, check.detail = "fail", "IOMMU disabled/software-only, passthrough boot mode, or identity domains observed."
    elif not groups or any(value not in ("DMA", "DMA-FQ", "blocked") for value in groups.values()):
        check.status, check.detail = "warn", "Translated isolation cannot be verified for all visible domains."
    else:
        check.detail = "Translated/blocked IOMMU domains observed; no explicit passthrough mode."
    return check


def pcie_acs():
    def collect():
        text = run_command(["lspci", "-D", "-vv"])
        values = {}
        for block in text.split("\n\n"):
            controls = [line.strip() for line in block.splitlines() if "ACSCtl:" in line]
            if controls:
                values[block.splitlines()[0].split()[0]] = controls
        if not values:
            raise Unavailable("lspci -D -vv", "No PCIe ACS controls readable; capabilities may be unsupported or access-denied without root.")
        return values
    check = collect_check("security.pcie_acs", collect, ["lspci -D -vv"])
    if check.status == "pass":
        disabled = any(re.search(r"(?:SrcValid|ReqRedir|CmpltRedir)-", line) for rows in check.value.values() for line in rows)
        check.status = "warn" if disabled else "pass"
        check.detail = "Some ACS protections are disabled." if disabled else "Observed ACS redirect/source-validation controls; expected bridge coverage is not configured."
    return check


def dpu_host_isolation():
    return Check("security.dpu_host_isolation", "skip", detail="No authenticated BlueField management inventory; host-isolation policy cannot be established locally.")


def bmc_exposure():
    return Check("security.bmc_exposure", "skip", detail="No tenant/BMC network definitions or management credentials; passive localhost inspection cannot prove reachability isolation.")


def gpu_permissions():
    def collect():
        devices = {str(p): {"mode": oct(stat.S_IMODE(p.stat().st_mode)), "readable": os.access(p, os.R_OK),
                            "writable": os.access(p, os.W_OK)} for p in sorted(Path("/dev").glob("nvidia[0-9]*"))
                   if re.fullmatch(r"nvidia\d+", p.name)}
        if not devices:
            raise Unavailable("/dev/nvidia[0-9]*", "No NVIDIA device nodes available.")
        return {"euid": os.geteuid(), "devices": devices}
    check = collect_check("security.gpu_permissions", collect, ["stat/access /dev/nvidia[0-9]*"])
    if check.status == "pass":
        accessible = all(v["readable"] and v["writable"] for v in check.value["devices"].values())
        check.status = "pass" if accessible and check.value["euid"] != 0 else "warn"
        check.detail = "Audit-user access only; root access does not establish non-root access. Scheduler/CUDA usability is not tested."
    return check


def cuda_nonroot():
    return Check("security.cuda_nonroot", "skip", detail="CUDA context creation is an active GPU operation; only passive device permissions are audited.")


def profiling_counters():
    def collect():
        match = re.search(r"RmProfilingAdminOnly:\s*(\d+)", read_text("/proc/driver/nvidia/params"))
        if not match:
            raise Unavailable("/proc/driver/nvidia/params", "Driver does not expose RmProfilingAdminOnly.")
        return int(match.group(1))
    check = collect_check("security.profiling_counters", collect, ["/proc/driver/nvidia/params"])
    check.expected = 0
    if check.status == "pass":
        check.status = "warn" if check.value else "pass"
        check.detail = "Profiling restricted to administrators." if check.value else "Non-admin profiling counters permitted."
    return check


def kmsg_access():
    if not Path("/dev/kmsg").exists():
        return Check("security.kmsg_access", "skip", detail="/dev/kmsg is not exposed.", source=["/dev/kmsg"])
    writable = os.access("/dev/kmsg", os.W_OK)
    return Check("security.kmsg_access", "warn" if writable else "pass",
                 {"euid": os.geteuid(), "writable": writable},
                 detail="Writable kernel log needs an explicit error-injection policy." if writable else "Kernel log not writable by audit user; no write attempted.",
                 source=["access /dev/kmsg"])


SECRET_PATHS = ("/etc/nccl.conf", "/etc/slurm/slurm.conf", "/etc/nvidia-container-runtime/config.toml", "/etc/docker/daemon.json")


def secrets():
    values, suspect, private_key, errors = {}, False, False, False
    for filename in SECRET_PATHS:
        path = Path(filename)
        if not path.exists():
            continue
        try:
            info = path.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_size > 1024 * 1024:
                raise Unavailable(filename, "Not a regular file or exceeds 1 MiB scan limit.")
            world_readable = bool(info.st_mode & stat.S_IROTH)
            text = read_text(path) if world_readable else ""
            text = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith(("#", ";")))
            keys = re.findall(r'''(?i)["']?([\w.-]*(?:token|password|secret|api[_-]?key)[\w.-]*)["']?\s*[:=]\s*["']?[^\s"',}]+''', text)
            has_key = bool(re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", text))
            values[filename] = {"world_readable": world_readable, "suspect_keys": sorted(set(keys)), "private_key": has_key}
            suspect |= bool(keys)
            private_key |= has_key
        except (Unavailable, OSError) as exc:
            values[filename] = {"unavailable": str(exc)}
            errors = True
    status = "skip" if not values else "fail" if private_key else "warn" if suspect or errors else "pass"
    return Check("security.secrets", status, values or None,
                 detail="Bounded heuristic scan of fixed cluster-config paths only; secret values are never exported. Missing paths are not scanned, suspect keys need review.", source=list(SECRET_PATHS))


def dashboard_exposure():
    def collect():
        return {"tcp_listeners": [parts[3] for line in run_command(["ss", "-H", "-ltn"]).splitlines()
                                  if len(parts := line.split()) >= 4]}
    check = collect_check("security.dashboard_exposure", collect, ["ss -H -ltn"])
    if check.status == "pass":
        check.status = "warn" if check.value["tcp_listeners"] else "pass"
        check.detail = "Passive TCP listeners do not establish dashboard identity/authentication; no HTTP probes sent."
    return check


CHECKS = {
    "security.driver_cve_floor": driver_cve_floor, "security.container_toolkit_cve_floor": container_toolkit_cve_floor,
    "security.cuda_cve_floor": cuda_cve_floor, "security.runc_cve_floor": runc_cve_floor,
    "security.docker_cve_floor": docker_cve_floor, "security.podman_cve_floor": podman_cve_floor,
    "security.connectx_cve_floor": connectx_cve_floor, "security.dcgm_cve_floor": dcgm_cve_floor,
    "security.dcgm_exporter_cve_floor": dcgm_exporter_cve_floor, "security.bluefield_cve_floor": bluefield_cve_floor,
    "security.kernel_cve_floor": kernel_cve_floor, "security.known_bad_kernels": known_bad_kernels,
    "security.iommu": iommu, "security.pcie_acs": pcie_acs, "security.dpu_host_isolation": dpu_host_isolation,
    "security.bmc_exposure": bmc_exposure, "security.gpu_permissions": gpu_permissions,
    "security.cuda_nonroot": cuda_nonroot, "security.profiling_counters": profiling_counters,
    "security.kmsg_access": kmsg_access, "security.secrets": secrets, "security.dashboard_exposure": dashboard_exposure,
}
