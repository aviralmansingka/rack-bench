"""Installed component versions; only detected versions enter the host manifest."""
from fnmatch import fnmatchcase
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


def fabric_manager():
    return _package("software.fabric_manager", "*fabricmanager*")


def docker():
    check = _version("software.docker", ["docker", "--version"])
    if check.status == "pass":
        check.detail = "Docker CLI version; does not establish the daemon version (security checks query the local daemon separately)."
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
    "software.os": os_version, "software.kernel": kernel, "software.driver": driver, "software.cuda": cuda,
    "software.cublas": cublas, "software.cudnn": cudnn, "software.cutiroc": cutiroc, "software.nccl": nccl,
    "software.nvshmem": nvshmem, "software.fabric_manager": fabric_manager, "software.docker": docker,
    "software.podman": podman, "software.enroot": enroot, "software.nvidia_container_toolkit": nvidia_container_toolkit,
    "software.runc": runc, "software.ofed": ofed, "software.rdma_core": rdma_core, "software.ibverbs": ibverbs,
    "software.nccl_plugins": nccl_plugins, "software.dcgm": dcgm, "software.dcgm_exporter": dcgm_exporter,
    "software.bmc": bmc, "software.glibc": glibc, "software.python": python, "software.mpi": mpi,
    "software.hpcx": hpcx, "software.gcc": gcc, "software.nvcc": nvcc,
}
