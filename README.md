# rack-bench

Certification CLI for GB300-class datacenter clusters. `rack-bench` runs a
three-stage pipeline — **audit → bench → smoke** — that takes a rack from
"hardware just racked" to "certified for fleet use."

- **`audit`** — inventory & topology. Read-only. Captures hardware configuration
  and any system specs that impact performance (power limits, firmware versions,
  thermal profiles, BIOS settings).
- **`bench`** — per-component quick pass/fail. Short-duration single-component
  tests across six categories: `gpu`, `network`, `storage`, `training`,
  `inference`, `lifecycle`.
- **`smoke`** — burn-in. Long-duration stress testing per component, plus
  combined stressors (notably GPU compute + interconnect together) to catch
  failures that only appear under sustained, concurrent load.

> **Implementation status:** the `audit` stage (all seven scopes, 108 checks) is
> implemented and merged. `bench`, `smoke`, `report`, the certification profile
> (`--config`), and multi-host fan-out (`--hosts`) are specified here as the
> design target and are not yet implemented.

## CLI shape

    rack-bench <stage> [category] [test] [options]

Every stage can run at three scopes — a single test, a whole category, or the
full stage. The most common certification flow is just three commands:

    rack-bench audit                       # full inventory of this node
    rack-bench bench                      # all categories, quick pass/fail
    rack-bench smoke --duration 4h        # burn-in everything

### Global options

| Flag | Description |
| --- | --- |
| `--json <file>` | Machine-readable results (also written to the run dir) |
| `--run-dir <dir>` | Artifact directory (default `./rack-bench-runs/<ts>/`) |
| `--hosts <list\|file\|group>` | SSH fan-out to certification-unit nodes |
| `--config <file>` | Certification profile (spec, thresholds, durations) |
| `--continue-on-fail` | Don't abort the run when a test fails |
| `--only <pattern>` / `--skip <pattern>` | Filter tests by name glob |
| `--show-command` | Echo each command/file read to stdout, with check name |

### Multi-node execution (`--hosts`)

`--hosts` accepts a literal host list, a `@hostfile` path, or a named group
from the certification profile; the default is `localhost`. `all-nodes`
resolves to the certification unit's node manifest — the trays this
acceptance covers, declared in the profile (the 18 trays of an NVL72, or a
multi-rack acceptance batch).

Resolution is manifest-driven, not discovery-driven:

1. The profile declares the expected nodes (literal list or pattern).
2. If rack-manager (BMC/Redfish) credentials are configured, rack-bench
   enumerates what the rack itself reports and diffs it against the
   manifest — declared-but-unreachable or present-but-undeclared trays
   are findings in the rollup.
3. The audit ssh-fans-out (key-based, the certification user) to every
   host in parallel, collects one envelope per host, and rolls up per-tray
   results, cross-tray version-manifest drift, and per-tray NVLink health.
   Unreachable or hung hosts are recorded as loud failures — an acceptance
   run can never pass on a partial rack.

rack-bench never scans subnets or sweeps for whatever answers; fleet
discovery is out of scope.

**Bootstrapping an NVL72** (first contact, before any profile exists):

1. Run `rack-bench audit` on one tray (localhost mode) — this captures the
   fabric domain UUID and topology that identify the rack.
2. Pull the node manifest from the rack manager, or take it from the order
   spec (18 trays).
3. Write the profile: node manifest, ssh user/key, BMC credentials.
4. Run `rack-bench audit --hosts all-nodes` — manifest/BMC cross-check
   plus the full 18-tray fan-out with rollup.

Coordinated multi-node tests (bench-network collectives, cross-rack smoke)
do not use the ssh fan-out: rack-bench generates a rankfile from the
audited topology (GPU/NIC/NUMA locality per tray) and delegates rendezvous
to `mpirun`. Independent per-node tests use the fan-out above.
| `--verbose` / `--quiet` | Output verbosity |

### Command tree

    rack-bench audit                      # everything below
      rack-bench audit topology           # NUMA, PCIe, NVLink fabric map
      rack-bench audit gpu  # GPU inventory, ECC, firmware, power limits
      rack-bench audit network  # NICs, link state, congestion control config
      rack-bench audit storage  # Disks, NVMe namespaces, filesystems
      rack-bench audit system             # CPU, memory, BIOS, thermal profile
      rack-bench audit software  # OS, kernel, drivers, runtimes, libraries
      rack-bench audit security  # CVE floors, isolation, exposure

    rack-bench bench                      # everything below
      rack-bench bench gpu                # per-GPU compute quick check
      rack-bench bench network            # link + bandwidth quick check
      rack-bench bench storage            # I/O quick check
      rack-bench bench training           # single-node training sanity
      rack-bench bench inference          # inference server sanity
      rack-bench bench lifecycle          # power cycle timing
      rack-bench bench <category> <test>  # one test, e.g. bench gpu gemm

    rack-bench smoke                      # everything below
      rack-bench smoke gpu                # sustained GPU compute burn-in
      rack-bench smoke network            # sustained network burn-in
      rack-bench smoke storage            # sustained storage burn-in
      rack-bench smoke gpu-network        # GPU compute + interconnect together
      rack-bench smoke full               # all stressors concurrently
      rack-bench smoke <category> --duration 8h

Each `bench` test prints `PASS`/`FAIL` plus the measured metric against the
configured threshold; `smoke` reports errors/ECC events/thermal throttling
observed during the soak.

## Stage 1 — audit (read-only inventory)

No benchmarks. Gathers everything needed to (a) verify the rack matches its
ordered spec and (b) explain later bench/smoke results.

Expected values come from the certification profile (`--config`): the ordered
rack spec (GPU count & model, NVLink fabric map, NIC count/speed, drive
model/count, memory sizes) plus pinned software versions. Every audit field is
scored `PASS` (matches spec) / `WARN` (off-spec but non-gating, recorded for
later explanation) / `FAIL` (spec mismatch) / `SKIP` (source unavailable — e.g.
no DCGM, no switch credentials). A `SKIP` on a gated field counts as a failure:
"couldn't verify" is not "verified."

**Unprivileged by design**

- `rack-bench audit` is read-only and designed for a normal (non-root) cluster
  user; permission-gated probes report `SKIP` with a reason rather than failing
  the probe (certification gating still applies).
- Most checks work unprivileged: GPU probes via `nvidia-smi`, `/sys` and `/proc`
  reads, the version manifest, and NCCL config.
- `system.dram` (`dmidecode`), some `smartctl` paths, and local `ipmitool` need
  root or group membership and skip honestly without it; Redfish needs
  credentials, not root.
- For certification, audit as a regular cluster user to validate non-root GPU
  usability; optionally re-run only root-gated probes, e.g. `sudo rack-bench
  audit --only 'system.dram'`.
- Running everything as root weakens the `gpu_permissions` finding; non-root
  CUDA usability is functionally verified in bench.

**Topology**

- NUMA domains & CPU affinity map (GB300 dual-socket Grace)
- PCIe enumeration: devices, lane width/speed vs. expected
- NVLink/NVSwitch fabric: per-GPU link count & width, fabric topology (NVL72
  ladder), degraded-link detection — a link is degraded when its width or the
  GPU's link count is below the profile's fabric map; any degraded link
  hard-fails certification (step 1 of the flow)

**GPU**

- Inventory: GPU count, model, serials, RAS/ECC mode, MIG config
- Firmware (SBT, SFW, FMC versions), clocks & power limits, thermals as observed
  — the quiesced idle-thermal baseline belongs to smoke (recorded after 5 min
  quiesced; a GPU running >10°C hotter than the rack median at idle is a `WARN`,
  usually a seated/cooling issue)
- GPU↔NIC and GPU↔NVMe locality: each GPU's NICs and NVMe devices must sit on
  the same PCIe switch / NUMA domain as the profile's expected map, so bench I/O
  tests can pin to the right local path

**Network**

- NIC inventory (model, firmware, link speed/state per port)
- RoCE/IB config: congestion control algorithm, MTU, ECN settings
- GPUDirect RDMA enablement: `nvidia-peermem`/GDRCopy modules loaded and usable
  whenever RDMA devices exist (RDMA present but peer-memory support missing →
  WARN — the classic "GPUDirect never enabled" acceptance failure)
- IB partition keys (PKeys) where readable: fabric partition sanity for
  partitioned InfiniBand subnets
- UFM (Ultra Fabric Manager) presence & version on InfiniBand-managed fabrics;
  subnet-manager API detail is gated on fabric credentials in the profile
- Switch-facing info where reachable: via the switch vendor's CLI/API from the
  management network, only when switch credentials are configured in the
  profile; unreachable switches are recorded as `SKIP` (non-gating), with
  host-side RDMA error counters used as the fallback signal

**NCCL configuration**

- Fabric topology & adapter naming: expected HCA names per rail, plane mapping
  on multiplanar networks (e.g. 4x 200G ports per GB300 tray → one
  `rdma_vf_railN` per GPU), flagging non-standard device names that break stock
  launch scripts
- Environment & config files: `NCCL_IB_HCA`, `NCCL_IB_GID_INDEX`,
  `NCCL_SOCKET_IFNAME`, `NCCL_NET_GDR_LEVEL`, system `nccl.conf` — verifying a
  working default so jobs don't hang on bad GID selection (a real-world GB300
  failure: auto GID pick chose an unroutable link-local address and hung NCCL)
- NCCL plugins present & loaded (internal SHARP/UMD, provider-specific like
  gIB/SPCX), versions vs. the software manifest
- Multi-node NVLink path: IMEX daemon state and host-level NVLink fabric config;
  jobs must not silently cross the NVLink domain onto RDMA

Active validation of the NCCL fabric belongs to bench, not audit: `bench
network` runs the queue-pair sanity per rail (QP creation mutates RDMA state)
and the 2-rank all-reduce canary that validates the config end-to-end.

NCCL misconfiguration is the single richest source of "cluster mysteriously
slow" bugs — wrong HCA pinning, missing plugins, or jobs spilling across the
scale-up boundary can silently halve bandwidth without failing loudly.

**Storage**

- Drive inventory: model, firmware, capacity, health (SMART), media errors
- Software RAID (`/sys/block/md*/md/`): array level, member devices, state —
  degraded or rebuilding arrays are flagged
- LVM topology (`pvs`/`vgs`/`lvs`): PV→VG→LV layout and sizes, so volume
  configuration is spec-checkable
- Multipath topology (`multipath -ll`, read-only): mpath devices, path counts
  and path states — single-path or faulty-path devices are flagged
- Local vs. shared storage, filesystem types & mount options
- NVMe namespace + controller config

**System**

- CPU model/cores/SNC mode, DRAM size/type (device memory size/type is captured
  per GPU by `gpu.inventory` and verified against the certification profile)
- BIOS settings that affect performance (power profiles, resizable BAR, IOMMU
  state), thermal/acoustic profile
- Kernel boot parameters (hugepages, isolcpus, IOMMU mode, cgroup settings)
- Direct liquid cooling telemetry via BMC (GB300 is DLC-mandatory): coolant
  inlet/outlet temperature per tray, flow rate, and differential pressure vs.
  vendor thresholds — thermal throttling explains a large share of burn-in
  failures, and elevated inlet temps across a rack point at facility-side
  (CDU/piping) problems rather than node faults

**Software**

- OS: distribution, release, kernel version — plus staged-but-unbooted kernel
  detection (newer kernel package installed than the running one →
  pending-reboot WARN)
- NVIDIA stack: driver version, CUDA toolkit, cuBLAS/cuDNN/cuTIROC/NCCL/NVSHMEM
  versions, Fabric Manager
- Container stack: Docker/Podman/Enroot versions, nvidia-container-toolkit —
  plus runtime identity: real `dockerd` vs a compatibility link (e.g. podman's
  docker shim), daemon version vs CLI
- Networking: OFED or rdma-core version, `ibverbs`/`nccl` plugin versions
- Telemetry & management: DCGM version, BMC firmware
- Base libraries: glibc, Python, MPI (OpenMPI/HPC-X), module system (Lmod)
  versions
- Workload frameworks: PyTorch, vLLM (anchors the training/inference benches)
- Toolchain pins: compiler (gcc/nvcc) versions for reproducible bench binaries

The software audit produces a single version manifest per host so any
bench/smoke result can be traced back to the exact stack it ran on; a mismatch
across nodes on any pinned field (driver, CUDA, cuBLAS/cuDNN/NCCL/NVSHMEM, OFED,
glibc, kernel, Fabric Manager) is flagged as a certification failure. Unpinned
fields (e.g. Python minor version) are recorded for traceability only.

**Security**

- Version-vs-CVE minimums: NVIDIA driver, nvidia-container-toolkit, CUDA
  toolkit, runc, Docker/Podman, ConnectX firmware, DCGM/dcgm-exporter, BlueField
  DPU firmware — each compared against a published minimum-version table (e.g.
  ClusterMAX's `minimum-versions.json`), FAIL when below the floor
- Kernel hygiene: kernel newer than the minimum patched version, known-bad
  kernel versions flagged (e.g. kernels missing the inode-writeback fix that
  soft-locks NUMA nodes when large cgroups exit — observed killing nodes during
  ordinary job teardown)
- Virtualization & isolation: IOMMU/SMMU enabled and configured (no passthrough
  mode on GPU nodes), PCIe ACS state, DPU host-isolation on BlueField-managed
  frontend networks, BMC/IPMI interfaces not reachable from tenant/workload
  networks
- GPU access & permissions: devices schedulable, CUDA usable by non-root users
  (functionally verified in bench), Nsight Compute profiling counters not
  administratively blocked (RmProfilingAdminOnly), `/dev/kmsg` writable where
  synthetic error injection is required
- Secrets & exposure scan: no tokens/keys in world-readable cluster configs, no
  exposed dashboards without auth

Security checks report PASS/WARN/FAIL like bench (not just inventory): a node
below the CVE floor fails certification even if all performance tests pass.

## Stage 2 — bench (quick pass/fail, minutes not hours)

Short single-component tests with binary pass/fail against thresholds from the
certification profile. Default profile targets GB300 NVL72-class nodes.

**gpu** — single-GPU and all-GPU compute checks: GEMM/FP4/FP8/FP16/FP32
throughput vs. spec, memory bandwidth, NVLink bandwidth per pair, collective
latency (all-reduce), SM clock stability under load.

**network** — port-to-port link check, single-pair bandwidth (TCP & RDMA),
intra-rack bandwidth matrix sample, small-message latency, packet-loss counter
check.

**storage** — sequential/random read+write IOPS and bandwidth, fsync latency,
short-duration sustained-write check for burst caches.

**training** — a time-boxed (minutes) single-node training step: known-good
model config, tokens/sec vs. threshold, loss decreasing (data plumbing sane),
multi-GPU data-parallel sanity via NCCL collectives.

**inference** — model load time, time-to-first-token, tokens/sec single- and
multi-stream, KV-cache/throughput stability over a short burst.

**lifecycle** — power-cycle timing: BMC-driven cold boot → GPU ready → CUDA
usable, measured end-to-end; NIC link-up time; time-to-job-ready.

## Stage 3 — smoke (burn-in)

Long-duration (`--duration`, default 4h) sustained stress, watching for errors
that only surface over time: ECC correctable/uncorrectable events, XIDs, thermal
throttling, link retrains, clock drops, packet loss.

**gpu** — sustained compute (GEMM loop) + memory traffic on all GPUs.

**network** — sustained RDMA/TCP mesh across all NICs and intra-rack pairs.

**storage** — sustained mixed read/write workload, watching for media errors,
latency spikes, and cache-flush stalls.

**gpu-network** — the headline stressor: all GPUs at full compute _while_ NVLink
fabric and network links run sustained traffic. Catches thermal, power-sharing,
and interference failures invisible to single-component tests.

**full** — all of the above concurrently; the final gate before certification.

## Certification flow

1. `rack-bench audit --hosts all-nodes --json audit.json` — verify spec match;
   abort certification if topology is degraded (missing NVLink lanes etc.)
2. `rack-bench bench --hosts all-nodes` — quick pass/fail on every category;
   investigate any FAIL before burning time in smoke
3. `rack-bench smoke full --duration 4h --hosts all-nodes` — burn-in
4. `rack-bench report --run-dir ./rack-bench-runs/<ts>/` — summary rollup across
   all nodes and stages, exit code reflects certification verdict

Exit codes: `0` all pass · `1` test failures · `2` infrastructure error (host
unreachable, missing tooling).
