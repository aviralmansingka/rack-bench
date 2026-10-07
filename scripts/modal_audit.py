"""Draft: run rack-bench audit on a Modal worker.

Usage (once reviewed):
    uv run modal run scripts/modal_audit.py            # default GPU
    uv run modal run scripts/modal_audit.py --gpu b200 # pick a GPU

Requires `modal` locally (uv add --dev modal) and modal token auth.
"""
import json
from pathlib import Path

import modal

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Image: base with Python 3.14 (pyproject requires >=3.14), then bake the
# local source in at build time and install with uv from source — the package
# is unpublished, so `uv pip install .` from the copied tree is the install path.
image = (
    modal.Image.debian_slim(python_version="3.14")
    .apt_install(
        "pciutils",           # lspci -> topology.pci/pci_names, security.pcie_acs
        "dmidecode",           # -> system.dram
        "rdma-core",           # ibv_devinfo -> network.rdma_ports, rdma_error_counters
        "ibverbs-utils",       # ibv_devinfo binary location on debian 12
        "infiniband-diags",    # ibstat -> network.rdma_ports
        "nvme-cli",            # -> storage.nvme_*
        "smartmontools",       # smartctl -> storage.smart_health, ssd_firmware
        "iproute2",            # ss -> security.dashboard_exposure
        "runc",                 # runc --version -> software.runc
        "ipmitool",            # -> software.bmc
        "openmpi-bin",         # mpirun -> software.mpi
        "lm-sensors",          # -> system.thermal_profile fallback
    )
    .pip_install("uv")
    .add_local_file(str(PROJECT_ROOT / "pyproject.toml"), "/src/pyproject.toml", copy=True)
    .add_local_file(str(PROJECT_ROOT / "README.md"), "/src/README.md", copy=True)  # pyproject references it
    .add_local_dir(str(PROJECT_ROOT / "rack_bench"), "/src/rack_bench", copy=True)
    # nvcc from the PyPI wheel (driver is CUDA-13 class); CUDA-13 wheels put
    # nvcc at nvidia/cu13/bin/nvcc. Use a wrapper (not a symlink) so nvcc can
    # resolve nvcc.profile/nvvm relative to its real location.
    .run_commands(
        "cd /src && uv pip install --system . nvidia-cuda-nvcc nvidia-cublas nvidia-cudnn-cu13 "
        "nvidia-nccl-cu13 nvidia-nvshmem-cu13 nvidia-cutlass "
        "&& printf '#!/bin/sh\\nexec /usr/local/lib/python3.14/site-packages/nvidia/cu13/bin/nvcc \"$@\"\\n' "
        "> /usr/local/bin/nvcc && chmod +x /usr/local/bin/nvcc "
        "&& nvcc --version | tail -1 && rack-bench --help"
    )
)

app = modal.App("rack-bench-audit", image=image)


@app.function(gpu="b200", timeout=600)
def run_audit() -> dict:
    """Run the full audit on the worker and return the JSON envelope.

    A non-zero rack-bench exit code is a valid result (1 = failed checks),
    so it is captured into the envelope instead of raising.
    """
    import subprocess

    out_dir = "/root/rack-bench-runs"
    proc = subprocess.run(
        ["rack-bench", "audit", "--run-dir", out_dir, "--json", f"{out_dir}/export.json"],
        timeout=540, capture_output=True, text=True,
    )
    print(proc.stdout)  # human-readable view in the Modal logs
    export = Path(f"{out_dir}/export.json")
    envelope = json.loads(export.read_text()) if export.exists() else {"schema_version": 1, "results": []}
    envelope["audit_exit_code"] = proc.returncode
    return envelope


@app.local_entrypoint()
def main(gpu: str = "b200"):
    """gpu: any Modal GPU spec (h100, h200, b200, b200:8, ...)."""
    audit_fn = run_audit.with_options(gpu=gpu)
    envelope = audit_fn.remote()
    Path("rack-bench-runs/modal").mkdir(parents=True, exist_ok=True)
    dest = Path("rack-bench-runs/modal") / "audit.values.json"
    dest.write_text(json.dumps(envelope, indent=2))
    print(f"saved {dest}")
    # quick console rollup
    for r in envelope["results"]:
        counts = {}
        for c in r["checks"]:
            counts[c["status"]] = counts.get(c["status"], 0) + 1
        print(f"{r['scope']:>8} @ {r['host']}: {counts}")
