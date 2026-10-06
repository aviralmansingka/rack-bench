"""Installed component versions; only detected versions enter the host manifest."""
from fnmatch import fnmatchcase
import os
import re
import shlex
import shutil

from rack_bench.common.host import Unavailable, collect_check, dist_versions, read_text, run_command


def _release(text):
    match = re.search(r"(?<![\d.])(\d+(?:\.\d+)+(?:[-+][\w.~-]+)?)", text)
    if not match:
        raise ValueError("No version in command output")
    return match.group(1)


def _version(name, command, parse=_release):
    return collect_check(name, lambda: parse(run_command(command)), [shlex.join(command)])


def _package(name, pattern, dists=()):
    """Package-manager packages, falling back to pip-installed distributions."""
    if shutil.which("dpkg-query"):
        command = ["dpkg-query", "-W", "-f=${db:Status-Abbrev}\t${binary:Package}\t${Version}\n", pattern]
        def parse(text):
            return {parts[1]: parts[2] for line in text.splitlines()
                    if len(parts := line.split("\t")) == 3 and parts[0].startswith("ii")}
    else:
        command = ["rpm", "-qa", "--qf", "%{NAME}\t%{VERSION}-%{RELEASE}\n"]
        def parse(text):
            return {key: value for line in text.splitlines() if "\t" in line
                    for key, value in [line.split("\t", 1)] if fnmatchcase(key, pattern)}
    source = [shlex.join(command)]

    def collect():
        try:
            packages = parse(run_command(command, ok_codes=(0, 1)))
        except Unavailable:
            packages = {}
        if not packages and dists:
            packages = dist_versions(dists)
            if packages:
                source.append(f"python distributions {dists!r}")
        if not packages:
            raise Unavailable(source[0], "No matching installed packages or distributions.")
        return packages
    return collect_check(name, collect, source)


def os_version():
    def collect():
        values = dict(line.split("=", 1) for line in read_text("/etc/os-release").splitlines() if "=" in line)
        return {key: values[key].strip('"') for key in ("ID", "VERSION_ID") if key in values}
    return collect_check("software.os", collect, ["/etc/os-release"])


def kernel():
    return _version("software.kernel", ["uname", "-r"], lambda value: value)


def staged_kernel():
    sources = []
    def newer(left, right):
        command = ["dpkg", "--compare-versions", left, "gt", right]
        sources.append(shlex.join(command))
        try:
            run_command(command)
            return True
        except Unavailable as exc:
            if str(exc).startswith("Command exited 1:"):
                return False
            raise
    def collect():
        if not (shutil.which("dpkg-query") and shutil.which("dpkg")):
            reason = ("RPM-native kernel-package comparison is not implemented."
                      if shutil.which("rpm") else "no supported package manager for kernel-package comparison")
            raise Unavailable("package manager discovery", reason)
        sources.append("uname -r")
        release = run_command(["uname", "-r"])
        command = ["dpkg-query", "-W", "-f=${db:Status-Abbrev}\t${binary:Package}\t${Version}\n", "linux-image*"]
        sources.append(shlex.join(command))
        installed, removed = [], set()
        for line in run_command(command, ok_codes=(0, 1)).splitlines():
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            status, name, version = parts
            name = name.split(":", 1)[0]
            match = re.fullmatch(r"linux-image-(?:unsigned-)?(\d.+)", name)
            if not match or name.endswith(("-dbg", "-dbgsym")):
                continue
            kernel_release = match.group(1)
            if len(status) > 1 and status[1] == "i":
                installed.append({"release": kernel_release, "package": name, "version": version})
            else:
                removed.add(kernel_release)
        running = [package for package in installed if package["release"] == release]
        if not running:
            reason = ("running kernel's package no longer installed" if release in removed else
                      "running kernel release cannot be mapped to an installed kernel package (purged or unmanaged)")
            raise Unavailable(sources[1], f"{reason}: {release}.")
        current = running[0]
        for package in running[1:]:
            if newer(package["version"], current["version"]):
                current = package
        newest = current
        for package in installed:
            if package != current and newer(package["version"], newest["version"]):
                newest = package
        return {"running": current, "newest_installed": newest, "pending_reboot": newest != current}
    check = collect_check("software.staged_kernel", collect, sources)
    if check.status == "pass":
        check.detail = "Kernel comparison is package-native (dpkg --compare-versions), not string-based."
        if check.value["pending_reboot"]:
            check.status = "warn"
            check.detail += " newer kernel installed than running (pending reboot)."
    return check


def driver():
    def parse(text):
        versions = sorted(set(line.strip() for line in text.splitlines() if re.fullmatch(r"\d+(?:\.\d+)+", line.strip())))
        return versions[0] if len(versions) == 1 else versions
    return _version("software.driver", ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], parse)


def cuda():
    def parse(text):
        match = re.search(r"release\s+([\d.]+)", text)
        if not match:
            raise ValueError("No CUDA toolkit release")
        return match.group(1)
    return _version("software.cuda", ["nvcc", "--version"], parse)


def cublas():
    return _package("software.cublas", "libcublas*", dists=("nvidia-cublas",))


def cudnn():
    return _package("software.cudnn", "libcudnn*", dists=("nvidia-cudnn*",))


def cutiroc():
    return _package("software.cutiroc", "*cutiroc*", dists=("nvidia-cutlass",))


def nccl():
    return _package("software.nccl", "libnccl*", dists=("nvidia-nccl*",))


def nvshmem():
    return _package("software.nvshmem", "*nvshmem*", dists=("nvidia-nvshmem*",))


def pytorch():
    return _package("software.pytorch", "python3-torch*", dists=("torch",))


def vllm():
    return _package("software.vllm", "python3-vllm*", dists=("vllm",))


def fabric_manager():
    return _package("software.fabric_manager", "*fabricmanager*")


def docker():
    check = _version("software.docker", ["docker", "--version"])
    if check.status == "pass":
        check.detail = "Docker CLI version; does not establish the daemon version (security checks query the local daemon separately)."
    return check


def runtime_identity():
    sources, errors = [], []
    def collect():
        path = shutil.which("docker")
        if not path:
            raise Unavailable("docker", "Docker CLI not found.")
        binary = os.path.realpath(path)
        sources.extend([path, "docker --version"])
        cli = run_command(["docker", "--version"])
        compat_link = (binary != os.path.abspath(path) and os.path.basename(binary) != "docker")
        compat_link = compat_link or bool(re.search(r"podman|nerdctl", binary + " " + cli, re.I))
        command = ["docker", "version", "--format", "{{.Server.Version}}"]
        sources.append(shlex.join(command))
        try:
            daemon = _release(run_command(command))
        except (Unavailable, ValueError) as exc:
            daemon = None
            errors.append(str(exc))
        return {"cli": cli, "daemon": daemon, "binary": binary, "compat_link": compat_link}
    check = collect_check("software.runtime_identity", collect, sources)
    if check.status == "pass":
        check.detail = "CLI version alone does not establish the daemon; server version uses the configured Docker endpoint."
        if check.value["compat_link"]:
            check.status = "warn"
            check.detail += " Compatibility link/shim detected; server response is not proof of dockerd."
        if check.value["daemon"] is None:
            check.status = "warn"
            check.detail += " Daemon version unavailable: " + "; ".join(errors)
    return check


def podman():
    return _version("software.podman", ["podman", "--version"])


def enroot():
    return _version("software.enroot", ["enroot", "version"])


def nvidia_container_toolkit():
    return _version("software.nvidia_container_toolkit", ["nvidia-ctk", "--version"])


def runc():
    return _version("software.runc", ["runc", "--version"])


def ofed():
    return _version("software.ofed", ["ofed_info", "-s"], lambda text: text.removeprefix("MLNX_OFED_LINUX-").rstrip(":"))


def rdma_core():
    return _package("software.rdma_core", "rdma-core")


def ibverbs():
    return _package("software.ibverbs", "libibverbs*")


def nccl_plugins():
    return _package("software.nccl_plugins", "*nccl*net*")


def dcgm():
    return _version("software.dcgm", ["dcgmi", "--version"])


def dcgm_exporter():
    return _package("software.dcgm_exporter", "*dcgm*exporter*")


def bmc():
    def parse(text):
        for line in text.splitlines():
            key, sep, value = line.partition(":")
            if sep and key.strip() == "Firmware Revision":
                return value.strip()
        raise Unavailable("ipmitool mc info", "BMC firmware revision not exposed.")
    return _version("software.bmc", ["ipmitool", "mc", "info"], parse)


def glibc():
    return _version("software.glibc", ["getconf", "GNU_LIBC_VERSION"])


def lmod():
    sources = []
    def collect():
        candidates = [os.environ.get("LMOD_CMD"),
                      os.path.join(os.environ["LMOD_DIR"], "lmod") if os.environ.get("LMOD_DIR") else None,
                      shutil.which("lmod"), "/usr/share/lmod/lmod/libexec/lmod",
                      "/usr/share/lmod/libexec/lmod", shutil.which("modulecmd")]
        binary = next((path for path in candidates if path and os.path.isfile(path)), None)
        if not binary:
            raise Unavailable("Lmod executable discovery", "Lmod not found.")
        # Lmod writes its version banner to stderr; positional arguments avoid shell interpolation.
        command = ["sh", "-c", 'exec "$@" 2>&1', "lmod-version", binary, "bash", "--version"]
        sources.append(shlex.join(command))
        match = re.search(r"Modules based on Lua:\s*Version\s+([0-9][\w.+~-]*)", run_command(command))
        if not match:
            raise Unavailable(sources[-1], "No Lmod version banner; modulecmd may be Tcl Environment Modules.")
        return match.group(1)
    return collect_check("software.lmod", collect, sources)


def python():
    return _version("software.python", ["python3", "--version"])


def mpi():
    return _version("software.mpi", ["mpirun", "--version"])


def hpcx():
    return _package("software.hpcx", "*hpcx*")


def gcc():
    return _version("software.gcc", ["gcc", "-dumpfullversion", "-dumpversion"])


def nvcc():
    def parse(text):
        match = re.search(r"\bV(\d+(?:\.\d+)+)", text)
        if not match:
            raise ValueError("No nvcc build version")
        return match.group(1)
    return _version("software.nvcc", ["nvcc", "--version"], parse)


CHECKS = {
    "software.os": os_version, "software.kernel": kernel, "software.staged_kernel": staged_kernel,
    "software.driver": driver, "software.cuda": cuda,
    "software.cublas": cublas, "software.cudnn": cudnn, "software.cutiroc": cutiroc, "software.nccl": nccl,
    "software.nvshmem": nvshmem, "software.pytorch": pytorch, "software.vllm": vllm,
    "software.fabric_manager": fabric_manager, "software.docker": docker, "software.runtime_identity": runtime_identity,
    "software.podman": podman, "software.enroot": enroot, "software.nvidia_container_toolkit": nvidia_container_toolkit,
    "software.runc": runc, "software.ofed": ofed, "software.rdma_core": rdma_core, "software.ibverbs": ibverbs,
    "software.nccl_plugins": nccl_plugins, "software.dcgm": dcgm, "software.dcgm_exporter": dcgm_exporter,
    "software.bmc": bmc, "software.glibc": glibc, "software.lmod": lmod,
    "software.python": python, "software.mpi": mpi,
    "software.hpcx": hpcx, "software.gcc": gcc, "software.nvcc": nvcc,
}
