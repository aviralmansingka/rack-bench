# rack-bench

Certification CLI for GB300-class datacenter clusters. `rack-bench` runs a
three-stage pipeline — **audit → bench → smoke** — that takes a rack from
"hardware just racked" to "certified for fleet use."

- **`audit`** — inventory & topology. Read-only. Captures hardware configuration
  and any system specs that impact performance (power limits, firmware versions,
  thermal profiles, BIOS settings).
- **`bench`** — per-component quick pass/fail. Short-duration single-component
  tests across seven categories: `gpu`, `network`, `internet`, `storage`,
  `training`, `inference`, `lifecycle`.
- **`smoke`** — burn-in. Long-duration stress testing per component, plus
  combined stressors (notably GPU compute + interconnect together) to catch
  failures that only appear under sustained, concurrent load.

> **Implementation status:** the `audit` stage (all eight scopes, 122 checks) is
> implemented and merged. `bench internet` measures paths, DNS, idle/loaded
> latency, sustained and single-stream transfers, PMTUD, and TCP retransmits.
> Other `bench` categories, `smoke`, `report`, the certification profile
> (`--config`), and multi-host fan-out (`--hosts`) remain unimplemented design
> targets.

## CLI shape

    rack-bench <stage> [category] [test] [options]

Every stage can run at three scopes — a single test, a whole category, or the
full stage. The most common certification flow is just three commands:

    rack-bench audit                       # full inventory of this node
    rack-bench bench                      # all categories, quick pass/fail
    rack-bench smoke --duration 4h        # burn-in everything

### Global options

| Flag                                    | Description                                            |
| --------------------------------------- | ------------------------------------------------------ |
| `--json <file>`                         | Machine-readable results (also written to the run dir) |
| `--run-dir <dir>`                       | Artifact directory (default `./rack-bench-runs/<ts>/`) |
| `--hosts <list\|file\|group>`           | SSH fan-out to certification-unit nodes                |
| `--config <file>`                       | Certification profile (spec, thresholds, durations)    |
| `--continue-on-fail`                    | Don't abort the run when a test fails                  |
| `--only <pattern>` / `--skip <pattern>` | Filter tests by name glob                              |
| `--show-command`                        | Echo each command/file read to stdout, with check name |

### Multi-node execution (`--hosts`)

`--hosts` accepts a literal host list, a `@hostfile` path, or a named group from
the certification profile; the default is `localhost`. `all-nodes` resolves to
the certification unit's node manifest — the trays this acceptance covers,
declared in the profile (the 18 trays of an NVL72, or a multi-rack acceptance
batch).

Resolution is manifest-driven, not discovery-driven:

1. The profile declares the expected nodes (literal list or pattern).
2. If rack-manager (BMC/Redfish) credentials are configured, rack-bench
   enumerates what the rack itself reports and diffs it against the manifest —
   declared-but-unreachable or present-but-undeclared trays are findings in the
   rollup.
3. The audit ssh-fans-out (key-based, the certification user) to every host in
   parallel, collects one envelope per host, and rolls up per-tray results,
   cross-tray version-manifest drift, and per-tray NVLink health. Unreachable or
   hung hosts are recorded as loud failures — an acceptance run can never pass
   on a partial rack.

rack-bench never scans subnets or sweeps for whatever answers; fleet discovery
is out of scope.

**Bootstrapping an NVL72** (first contact, before any profile exists):

1. Run `rack-bench audit` on one tray (localhost mode) — this captures the
   fabric domain UUID and topology that identify the rack.
2. Pull the node manifest from the rack manager, or take it from the order spec
   (18 trays).
3. Write the profile: node manifest, ssh user/key, BMC credentials.
4. Run `rack-bench audit --hosts all-nodes` — manifest/BMC cross-check plus the
   full 18-tray fan-out with rollup.

Coordinated multi-node tests (bench-network collectives, cross-rack smoke) do
not use the ssh fan-out: rack-bench generates a rankfile from the audited
topology (GPU/NIC/NUMA locality per tray) and delegates rendezvous to `mpirun`.
Independent per-node tests use the fan-out above. | `--verbose` / `--quiet` |
Output verbosity |

### Command tree

    rack-bench audit                      # everything below
      rack-bench audit topology           # NUMA, PCIe, NVLink fabric map
      rack-bench audit gpu  # GPU inventory, ECC, firmware, power limits
      rack-bench audit network  # NICs, link state, congestion control config
      rack-bench audit connectivity       # routes, DNS, egress, ASN, ROA, RIS
      rack-bench audit storage  # Disks, NVMe namespaces, filesystems
      rack-bench audit system             # CPU, memory, BIOS, thermal profile
      rack-bench audit software  # OS, kernel, drivers, runtimes, libraries
      rack-bench audit security  # CVE floors, isolation, exposure

    rack-bench bench                      # everything below
      rack-bench bench gpu                # per-GPU compute quick check
      rack-bench bench network            # link + bandwidth quick check
      rack-bench bench internet           # external network measurements
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
  usability; optionally re-run only root-gated probes, e.g.
  `sudo rack-bench audit --only 'system.dram'`.
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

**Connectivity**

- `connectivity.routes`: default routes/gateways and kernel source-IP selection
  per family, plus VLAN/VRF interfaces and policy rules to explain table
  selection on multi-ISP/VRF nodes; passive `ip` reads, no probes sent
- `connectivity.resolver`: `/etc/resolv.conf`, systemd-resolved status when
  available, and locally reported DNSSEC state (not an active validation test)
- `connectivity.ipv6`: global-scope IPv6 addresses, default route, and libc AAAA
  query capability (`no-aaaa` setting); not proof of IPv6 Internet reachability
- `connectivity.proxies`: proxy environment, `/etc/environment`, and readable
  git/Docker configuration, with embedded URL credentials redacted; proxies may
  be part of the customer service path
- `connectivity.egress_ip`: public egress IP per family, preferring direct
  OpenDNS queries via optional `dig`, with HTTPS ipify fallback. The configured
  recursive resolver's whoami answer can describe the resolver, not this host;
  DNS and HTTPS paths (including proxies) can have different egress addresses
- `connectivity.asn`: RIPEstat announced prefix and origin ASNs for that egress
- `connectivity.roa`: covering ROA existence and RPKI origin/maxLength validity
  via RIPEstat `rpki-validation` (coverage does not imply authorization)
- `connectivity.ris`: exact prefix/origin visibility in RIPE RIS collectors,
  including routes seen by only one peer; not proof of global propagation

Connectivity makes **~4 external read-only queries** per available address
family (DNS/HTTPS to RIPEstat/OpenDNS/ipify); fallback attempts, dual-stack, and
multiple origin ASNs can add queries. Observations are shared within one audit
run, including filtered runs, not cached across runs. Every external query has a
hard 5-second deadline, including DNS/HTTPS resolution and response reads.
External checks **SKIP cleanly offline**, with reasons and exact endpoints in
`source`. Partial dual-stack observations also SKIP; successful-family values
remain in JSON alongside the unavailable-family reasons. No credentials are
required. Local routes/resolver/IPv6/proxy checks remain passive; use
`--skip 'connectivity.*'` for an audit without these external queries, or
`--only 'connectivity.routes'` for just passive routing facts.

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

Active validation of the NCCL fabric belongs to bench, not audit:
`bench network` runs the queue-pair sanity per rail (QP creation mutates RDMA
state) and the 2-rank all-reduce canary that validates the config end-to-end.

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
- Internet bench tools: `software.mtr`, `software.fping`, `software.traceroute`,
  `software.iperf3`, `software.flent`, `software.curl`; missing optional tools
  SKIP. This is version visibility only, not a dependency of the bench stage.

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

**network** — port-to-port link check, point-to-point RDMA perftest
(`ib_write_bw`/`ib_read_bw`), single-pair bandwidth (TCP & RDMA), intra-rack
bandwidth matrix sample, small-message latency, packet-loss counter check, and
the NCCL collective bandwidth sweep: allreduce, allgather, and alltoall across
message sizes from 8 B to 16 GB, launched through both MPI and
`torch.distributed`, reporting algbw/busbw as a percentage of line rate (untuned
RoCEv2 sits near 60%, tuned deployments near 98%) with a monotonicity check on
the busbw-vs-message-size curve — a jagged curve indicates misconfiguration
(e.g. automatic GID selection picking an unroutable address). Beyond the
intra-rack matrix sample, an N-node collective validates scale-out performance
across the audited topology via the `mpirun` rankfile path.

**storage** — sequential/random read+write IOPS and bandwidth, fsync latency,
short-duration sustained-write check for burst caches.

**training** — a time-boxed (minutes) single-node training step: known-good
model config, tokens/sec vs. threshold, loss decreasing (data plumbing sane),
multi-GPU data-parallel sanity via NCCL collectives.

**inference** — model load time, time-to-first-token, tokens/sec single- and
multi-stream, KV-cache/throughput stability over a short burst.

**lifecycle** — power-cycle timing: BMC-driven cold boot → GPU ready → CUDA
usable, measured end-to-end; NIC link-up time; time-to-job-ready.

### Internet — external network

`rack-bench bench internet` measures single-host north-south performance to S3
and R2 using an IPv4-only, stdlib S3 client. All 13 checks per provider are
wired: path AS/hops/RTT, DNS, idle TTFB, upload/download MiB/s and obj/s, loaded
TTFB, PMTUD, TCP retransmits, and summary. Single-stream rates live in
throughput detail, not a new check name. GCS interoperability and Warp execution
remain unsupported and SKIP explicitly.

**PASS means observed, not certified.** `expected` stays `null` until the
certification profile schema exists. Only path RTT sanity can WARN; instability,
asymmetry, loaded p95 inflation above 20 ms, BDP shortfalls, and retransmit
findings are diagnostic detail. Missing credentials/tools/buckets, failed
transfers, invalid timings, and checksum failures SKIP with reasons. A run
containing SKIPs can exit 0; inspect the checks, not just the exit code.

#### Workload and ownership

Path/DNS and a verified 100 KiB idle-TTFB baseline run first. Uploads use
seeded, checksummed ~1 GiB multipart objects with concurrent small-object GETs
for loaded TTFB. Downloads verify ranges from this run's completed uploads; they
never use pre-seeded data. All upload windows, including a separate unloaded
concurrency-1 test, finish before download windows start. TCP socket sampling
brackets these windows; PMTUD uses stepped DF pings.

Quick uses 32 streams for 60 seconds per sustained direction plus separate
concurrency-1 windows. Certify uses 1/8/32/64 streams, five minutes per window,
three runs per concurrency, dropping the best and worst by measured rate.
Dedicated single-stream windows also have three runs. The scalar rate is the
largest concurrency's retained run, not the fastest result. Scheduling stops at
a part/range boundary; actual elapsed time includes setup and the current
operation's overrun. Incomplete multipart uploads are aborted. A slow/short run
can measure uploaded parts without completing an object: download then SKIPs
rather than manufacturing data.

Quick targets S3 Mumbai and R2 apac. Certify adds Singapore and N. Virginia as
**light bands**, not two more full certifications: no sustained transfers or
loaded probes; one object at most 32 MiB each direction per far band. Including
the idle baseline, both far bands add at most 64 MiB uploaded and about 68 MiB
downloaded, plus setup/control traffic. `--regions` replaces this default
matrix. R2 placement hints do not prove a regional path, so unpinnable far bands
SKIP. S3 redirects at inaccessible regional endpoints also SKIP rather than
silently changing the measured region.

Supply `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` and optional
`AWS_SESSION_TOKEN`; R2 additionally needs `R2_ACCOUNT_ID`. These AWS-named
variables must contain the selected provider's credentials; separate provider
invocations are usually appropriate. There is no SDK/config/IMDS discovery. Use
an existing bucket with scoped read/write/delete/multipart permissions. Each
collection owns a fresh `rack-bench/<run-id>/...` prefix. Cleanup deletes only
exact owned keys, even when summary is filtered out; `--keep-data` retains keys
and seeds. Configure a 24-hour object-expiry and incomplete-upload abort
lifecycle rule as crash insurance. A lost initiation response can leave an
unknown upload ID that object listings cannot reclaim.

`--only`/`--skip` never launch hidden prerequisites. Download without an upload
manifest (including `--directions down`) SKIPs. Loaded latency without the idle
baseline or upload windows SKIPs. TCP retransmits without observable transfer
socket deltas SKIP. TCP detail describes sampling coverage: short-lived sockets
can be missed, and local counters cannot measure the remote download sender's
retransmits. BDP uses observed advertised window/RTT when available; `rcv_space`
is not treated as an advertised receive window. The client opens a connection
per request: concurrency 1 is sequential requests, not one persistent TCP flow.

#### Options and artifacts

Internet flags follow `bench internet`, not the `bench` parent.

| Flag                            | Description                                           |
| ------------------------------- | ----------------------------------------------------- |
| `--providers s3,r2`             | Unique providers: `s3`, `r2`, `gcs` (GCS unsupported) |
| `--directions up,down`          | Selected directions; down needs this run's uploads    |
| `--profile quick\|certify`      | Default `quick`; certify requires `--yes`             |
| `--regions s3=us-east-1,...`    | Override the tiered provider region matrix            |
| `--buckets s3=<name>,r2=<name>` | Existing buckets; required for object probes          |
| `--concurrent N`                | Override quick's 32 streams or certify's sweep        |
| `--duration 60s`                | Per-window duration; defaults: quick 60s, certify 5m  |
| `--tool stdlib\|warp`           | Default `stdlib`; Warp execution unsupported          |
| `--keep-data`                   | Retain completed objects under the run-owned prefix   |
| `--yes`                         | Accept the certify reference cost estimate            |

The default run selects 26 checks (S3 and R2); bare `rack-bench bench` runs only
implemented categories, currently internet. Generic flags match audit:
`--only`/`--skip` are repeatable globs (`--skip` wins); an empty selection
exits 2. `--json` prints the version-1 envelope; `--json FILE` exports it
alongside human stdout. `--run-dir DIR` receives `bench.out` and
`bench.values.json`. JSON-encoded detail retains all regions/runs, per-operation
timings, per-second throughput buckets, byte accounting, diagnostic signals, and
cleanup results. `--show-command` traces real operations; `--quiet` suppresses
traces and PASS rows, not SKIPs.

**Transfers incur charges.** Certify always prints its reference estimate to
stderr and requires `--yes`, even with JSON or `--quiet`. The spec's
nearest-band 10 Gbit/s references are quick ~75 GB (S3 ~$7, R2 $0, GCS
~$9) and certify
~2.2 TB (S3 ~$200, R2 $0, GCS ~$260), per provider. These are
not live quotes and are not adjusted for sweeps, overrides, filters, directions,
request fees, or operation overruns. Far bands stay within the light budget
above; they do not multiply the nearest-band reference by three. See the
[implementation spec](docs/bench-internet.md) for methodology and remaining
work.

#### Try it without cloud traffic

These commands were exercised from the repo root. They need no real credentials,
make no cloud requests, and write only temporary artifacts. The transfer tests
use fake clients, clocks, and commands; no real-duration benchmark was run.

    uv run rack-bench bench internet --help
    uv run python -m unittest tests.test_bench_internet_transfer -v
    (
      demo_dir="$(mktemp -d)"
      trap 'rm -rf "$demo_dir"' EXIT
      env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY \
        uv run rack-bench bench internet --json --run-dir "$demo_dir/default"
      env AWS_ACCESS_KEY_ID=fake AWS_SECRET_ACCESS_KEY=fake \
        uv run rack-bench bench internet --providers s3 \
        --buckets s3=example-bench --directions down --only '*.download.*' \
        --json --run-dir "$demo_dir/down"
    )

The first collection yields 26 credential SKIPs; the second yields two SKIPs
naming the missing upload objects. Live cloud interoperability and paid transfer
rates were not exercised here.

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

## ClusterMAX coverage

The security scope already consumes ClusterMAX's `minimum-versions.json` as its
CVE floor. For network performance specifically, ClusterMAX additionally tests
three things this spec does not yet cover; they are roadmap items, not part of
the first implementation:

- **Fabric fault injection** — link flap and node kill during running
  collectives, plus job-level failover, to measure how the fabric and jobs
  behave when a component dies (ClusterMAX 3.0 fault-tolerance testing).
- **Observability functional validation** — DCGM exporter and NCCL inspector
  actually emitting metrics while tests run; this spec audits their versions but
  never validates emission end-to-end.
- **Multi-tenant network isolation** — tenant-segmented networking (e.g. RoCE
  VPC isolation); the security scope covers host-level isolation, not tenant
  network segmentation.

Internet egress/ingress performance to public object stores (S3, R2, GCS) is
outside ClusterMAX's scope entirely. `bench internet` now measures it for S3 and
R2; the longer `smoke internet` soak remains future work.

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
