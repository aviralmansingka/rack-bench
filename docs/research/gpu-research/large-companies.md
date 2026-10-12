# N04 — Large-company GPU fleet screening

Research date: 2026-10-11. All claims below carry a source URL.

This brief marks claims **[observed]** when a source states/shows them, **[calculated]** for arithmetic, and **[inference]** for recommendations or interpretation. It covers device-level GPU quality for rack-bench's approximately two-hour per-category certification. It separates CPU evidence. It prefers primary vendor documentation and company engineering disclosures. Public descriptions do not reveal complete proprietary runbooks.

## 1. Executive findings

### 1.1 What transfers to a two-hour GPU bench

1. **[observed]** Google documents GPU-specific health policy. It uses passive health checks, Xid classification, and ECC/page-retirement signals. It repairs selected Xids that indicate hardware faults (including 74, 79, 140). Some Xids need pattern matching because software and hardware causes overlap. [Google Compute Engine GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)
2. **[observed]** Meta describes fleet SDC defense as complementary layers. Fleetscanner runs targeted microbenchmarks on a maintenance cadence (whole fleet every 45–60 days). Ripple runs short tests beside workloads. Hardware Sentinel analyzes application exceptions. These are fleet programs; they do not show that a two-hour one-shot test proves GPU correctness. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)
3. **[observed]** NVIDIA's current `nvidia-smi` reference lists ECC, retired pages, row remapping, clocks, and power/thermal throttle reasons. It also lists recovery action, NVLink link state/counters, and Blackwell+ PRM interfaces. These readings support fast evidence gathering. Availability depends on driver/device. Some counters are cumulative, not test-window deltas. [NVIDIA nvidia-smi reference](https://docs.nvidia.com/deploy/nvidia-smi/index.html)
4. **[inference]** A useful two-hour screen combines a measured baseline with concurrent per-GPU memory/compute/correctness exercise. It also captures telemetry and log deltas. It is not a single “stress passed” boolean. A two-hour pass detects reproducible faults under chosen inputs and operating conditions. It does not rule out data-dependent, rare, aging, or weeks-long SDCs.
5. **[observed]** `stress-ng` is a CPU/system stress tool. It does not provide evidence of GPU silicon correctness. Do not convert CPU silent-error rates or CPU stress results into GPU failure rates. Meta's CPU SDC mechanism history informs fleet methodology. It remains distinct from Meta's direct accelerator/HBM/SRAM statements. [stress-ng manual](https://manpages.ubuntu.com/manpages/jammy/man1/stress-ng.1.html) [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

## 2. Meta: SDC program in depth

### 2.1 Three fault classes and why a short test has limits

**[observed]** Meta groups faults into three classes. Static faults stop a device from powering on or enumerating. Transient faults depend on conditions or load; they include thermal runaway and random uncorrectable-error crashes. Silent faults make hardware miscompute without detectable traces. Static checks are comparatively easy; transient faults need condition reproduction. SDC can persist undetected; attribution to a device needs telemetry and engineering. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

**[observed]** Meta says SDC manifestation can depend on data, voltage, frequency, temperature, and lifecycle. Exhaustive input testing is impractical. A defect may emerge only after months. Meta therefore calls for consistent, periodic testing over random state space. It says not to treat one qualification run as conclusive. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

**[observed]** Meta reports accelerator-relevant failure locations in Llama 3 training incidents. These include SRAM, HBM, processing grids, and switch hardware. The broader statement says hardware failures caused over 66% of training interruptions. That figure is cluster-level and includes components beyond GPUs. It is not a GPU defect probability. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable) [Llama 3 paper](https://arxiv.org/abs/2407.21783)

### 2.2 Fleetscanner, Ripple, Hardware Sentinel

- **Fleetscanner — targeted active tests. [observed]** Meta says Fleetscanner captures performance outliers through targeted microbenchmarks. It records their signatures in telemetry for later detection without running the benchmark. It schedules directed tests during maintenance events, such as firmware upgrades and repairs. Full-fleet coverage occurs every 45–60 days; Meta warns that this cadence can be too slow for some SDCs. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable) The primary paper is [Detecting Silent Errors in the Wild](https://arxiv.org/abs/2203.08989).
- **Ripple — short online tests. [observed]** Meta says Ripple tests run in milliseconds to seconds alongside workloads. The tests overlap instructions across cores/threads to achieve fleet coverage in days. The source frames the technique around fleet compute hardware/core anomalies. It does not publish a GPU-specific error-detection rate. It does not certify that Ripple alone identifies GPU SDC. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable) [paper](https://arxiv.org/abs/2203.08989)
- **Hardware Sentinel — analytical signal. [observed]** Meta describes a test- and architecture-agnostic method. It analyzes application exceptions in kernel space without dedicated test allocation. Meta reports 41% improvement over testing-based methods across architectures, applications, and datacenters. This is not a GPU benchmark throughput result. The public abstract/source does not establish GB300-specific sensitivity. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable) [ACM paper](https://dl.acm.org/doi/10.1145/3676641.3716258)

**[inference]** The practical contribution is the architecture. It combines directed tests, opportunistic in-band signals, telemetry signatures, and exception analytics. A certification CLI can use the directed test and before/after telemetry slice. It cannot reproduce Meta's years of fleet baselines or cross-host anomaly models in a two-hour isolated rack test.

### 2.3 GPU-specific correctness mechanisms and examples

**[observed]** Meta distinguishes two training SDC manifestations. NaNs can propagate widely. Corrupted-but-in-range gradient variance can silently cause divergence/local minima. Meta notes that the latter can take weeks or months to appear in training. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

**[observed]** Meta's GPU/AI strategy includes deterministic training on a known model for several iterations. This checks specific values for NaNs/divergence. The strategy also uses reductive triage: teams bisect mini-training across smaller node sets. Hyper-checkpointing shortens attribution. These methods need workload/model/checkpoint context. They do not provide generic proof of all operations. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

**[observed]** Meta lists stack resilience methods. These include gradient clipping/NaN checks, algorithmic fault tolerance, shadow-node redundant training, parameter vulnerability factors, and sampled inference divergence detection. These methods need application integration and/or substantial duplicate compute. They are not suitable as a universal two-hour device-only pass criterion. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

**[inference]** For bench-gpu, use reproducible known-answer kernels. Compare each GPU's output with an independent CPU/high-precision reference or trusted GPU implementation. Use multiple data patterns and precision modes. Keep tolerances explicit. Use bit-exact comparison only for deterministic integer/bitwise or deliberately reproducible operations. Floating-point reduction order can legitimately differ.

The source documents deterministic training as a strategy. It does not provide a ready-made test corpus or universal tolerance.

### 2.4 CPU versus GPU SDC evidence — do not conflate

**[observed]** Meta's foundational 2021 study, *Silent Data Corruptions at Scale*, concerns production CPU cores. It reports approximately 1 in 1,000 cores with SDC-inducing defects at fleet scale. This is CPU evidence, not a GPU/HBM rate. [Meta SDC paper](https://arxiv.org/abs/2102.11245)

**[observed]** Meta's Ripple/Fleetscanner descriptions cover fleet microbenchmarking and short co-located tests. The public 2025 write-up discusses AI and non-AI infrastructure. It does not publish GPU-specific per-device SDC prevalence or test sensitivity. Do not apply the CPU SDC paper's denominator to accelerators. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable) [Ripple paper](https://arxiv.org/abs/2203.08989)

**[observed]** Meta separately identifies GPU AI hardware faults in SRAM/HBM/processing grids. It describes AI training/inference detection. This is qualitatively GPU-relevant evidence. It does not quantify per-GPU screening yield or establish a GPU error rate comparable to the CPU paper. [Meta Engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

**[inference]** Do not use CPU rates to derive GPU acceptance thresholds, expected GPU failures, or confidence intervals. Report CPU-derived fleet methods only as methodological context.

## 3. Google / DeepMind and GPU fleet validation

### 3.1 Google Cloud GPU health operations

**[observed]** Google Compute Engine says it uses passive GPU health checks. It can initiate emergency maintenance/replacement when hardware signals warrant it. Xids 74, 79, and 140 are examples with high probability of hardware failure. Other Xids may come from software or hardware. Google handles these by pattern matching. A single code does not always imply replacement. [Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)

**[observed]** Google distinguishes application Xids (for example 13/31/137, often illegal access) from driver and firmware/hardware recoverable cases. It explicitly says illegal memory access is not ECC unless Xid 48 is also present. Xid 48 indicates double-bit ECC; Xid 63 records retirement/remap. Xid 64 can mean remap failure/exhausted reserved rows. Xid 92 indicates a high single-bit rate. Xids 94/95 indicate contained/uncontained errors and need co-occurring evidence. [Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)

**[observed]** Google says to use DCGM diagnostic levels 3–4 to investigate some rare cases. In these cases, degradation may appear as illegal memory access. Its public guide gives `dcgmi diag -r memory -j` as an example of a GPU-memory diagnostic returning pending-retirement/DBE evidence. NVIDIA characterizes Level 1 as a readiness metric, not an active thermal stress test. [Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)

**[inference]** For a 2-hour window, include passive evidence: event logs/Xids, ECC, retired pages, and remap state. Also run a controlled active diagnostic. “No Xid found” is only a clean observed log interval, not proof of correctness. Capture historical counters and reset boundaries.

### 3.2 Google hardware validation specifics and applicability

**[observed]** Google's public fleet policies prioritize repair automation from historical/passive health and error-code patterns. They do not claim a publicly described two-hour burn-in for each accelerator before every customer use. The public documentation does not disclose the internal test schedule, exact threshold logic, or GB300 qualification recipe. [Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)

**[observed]** Google's A3 performance triage procedure uses NCCL `all_reduce_perf` and recursive node-set bisection to locate a straggler. That method assesses nodes/collectives and includes fabric/software effects. This brief excludes east-west fabric as a GPU category. This brief does not propose it as device-level GPU proof. [Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)

### 3.3 DeepMind / Google SDC evidence limit

**[observed]** Google/DeepMind public SDC material often cited as *Cores That Don’t Count* shows mercurial CPU cores and CPU computation errors. It does not show GPU device-level SDC screening. Do not present it as GPU validation evidence. [Google Research publication record](https://research.google/pubs/cores-that-dont-count/)

**[inference]** In this N04 evidence set, Google's strongest directly applicable operational source is Google Cloud's GPU-specific DCGM/Xid/ECC troubleshooting guidance. It shows production triage and repair behavior. It is not a published DeepMind GPU correctness screening suite or quantitative GB300 acceptance test.

## 4. Microsoft GPU fleet operations

### 4.1 What public evidence supports

**[observed]** The OCP source reports Microsoft's participation with Meta, Google, ARM, AMD, NVIDIA, and Intel. They participate in the Open Compute Project server resilience initiative. The effort addresses SDC research and test architectures across the industry. This is evidence of cross-company resilience work, not a Microsoft-specific GPU screening command or threshold. [OCP server resilience initiative](https://www.opencompute.org/blog/computings-hidden-menace-the-ocp-takes-action-against-silent-data-corruption-sdc)

**[observed]** The Azure Monitor supported-metrics reference cited here does not establish guest-based GPU telemetry or DCGM Exporter collection. It is not evidence of Microsoft GPU screening. Public Microsoft sources reviewed do not substantiate that specific operational claim. [Azure Monitor supported metrics](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-compute-virtualmachines-metrics)

**[inference]** This brief reviews public, primary Microsoft sources. They do not disclose a comparable GPU-specific fleet screening regimen, SDC rate, acceptance workload, or GB300 burn-in duration. Do not infer such a program from generic Azure monitoring or OCP participation.

### 4.2 Limits and unresolved identity claims

**[observed]** No verified primary-source evidence in this brief establishes that Microsoft uses a tool called “Florence” for GPU health screening. The searches show unrelated/ambiguous Florence references, not an identifiable Microsoft GPU validation product. [Microsoft Azure GPU documentation](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated)

**[inference]** Treat “Florence” as unverified in this fleet-screening context. Do not conflate it with unrelated Microsoft AI model names or internal tooling. A first-party document must first define the tool and its role.

## 5. Stress-screening tools and what they really prove

### 5.1 NVIDIA DCGM diagnostics

**[observed]** NVIDIA DCGM includes diagnostics for GPU health checks, with increasing levels of coverage. Google publicly recommends levels 3–4 for deep investigation. Google treats level 1 as a readiness metric. GPU-memory diagnostic output can report allocation coverage, pending retirements and DBE-related warnings. [Google DCGM guidance](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus) [NVIDIA DCGM documentation](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)

**[inference]** DCGM is the best-supported quick-start diagnostic suite for bench-gpu. First check the installed DCGM version and its supported tests on GB300. Full diagnostic levels may exceed two hours. The duration depends on device count, version, platform, and test configuration. No public source located guarantees a duration for an 18-tray GB300 rack. Time the run and preserve per-test outcomes; do not assume a fixed runtime.

**[observed]** Diagnostics can consume GPU resources. Depending on deployment, they can require host-engine access/permissions. Invasive or privileged diagnostics during tenant workloads are unsafe. The bench must require a drained, exclusive maintenance window. [NVIDIA DCGM documentation](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/getting-started.html)

### 5.2 gpu-burn identity and limits

**[observed]** `gpu-burn` is an open-source CUDA GPU stress utility maintained at [wilicc/gpu-burn](https://github.com/wilicc/gpu-burn). It repeatedly performs dense matrix multiplication to load GPUs and checks output for errors. Its README describes selectable duration and GPU selection. It also notes substantial power/thermal load. [gpu-burn README](https://github.com/wilicc/gpu-burn)

**[inference]** It is a useful sustained compute/thermal/power screen and can reveal gross instability. Its single workload family is not broad SDC coverage. It is not an exhaustive HBM address-pattern test. Use a known verified build compatible with the installed CUDA/driver and Blackwell. The public project does not establish GB300/Grace platform certification. Run it only with rack operator approval.

Monitor power/temperature during the run. Stop on Xid, uncorrectable ECC, abnormal throttle, or thermal limit.

**[observed]** No public evidence located verifies “Florence” as an established GPU burn-in tool. No located evidence identifies its authoritative upstream, version, Blackwell support, privileges, or destructive behavior. [NVIDIA GPU deployment tools index](https://developer.nvidia.com/gpu-deployment-kit)

### 5.3 stress-ng: CPU stress is not GPU validation

**[observed]** `stress-ng` provides CPU, memory, I/O and system stressors. Its documented stressors do not constitute CUDA GPU arithmetic or HBM validation. Its `--verify` option is stressor-specific and is not a general GPU SDC detector. [stress-ng manual](https://manpages.ubuntu.com/manpages/jammy/man1/stress-ng.1.html) [upstream project](https://github.com/ColinIanKing/stress-ng)

**[inference]** CPU stress may help expose host CPU, RAM, cooling, or power-delivery interactions under GPU load. A clean stress-ng run cannot certify GPU correctness. A combined CPU+GPU stress run can confound attribution. It can also perturb rack-level power/thermal conditions. Keep it separate from the device-level GPU result, or label it a system test.

### 5.4 “Florence” verification

**[observed]** This brief does not verify “Florence” as a GPU fleet screening tool. The searched results do not provide a primary-source software repository, vendor manual, or version history. They also give no GPU workload description, permissions, or data-loss/reset warnings. [Microsoft Florence model announcement (unrelated model identity)](https://www.microsoft.com/en-us/research/project/florence/)

**[inference]** Do not add a tool named `florence` to a certification checklist yet. First, someone must supply its exact project/vendor identity and executable documentation. The name alone is insufficient evidence.

## 6. NVIDIA telemetry and Blackwell/GB300 relevance

### 6.1 Fast, low-risk device evidence

**[observed]** `nvidia-smi` supports machine-readable query/loop modes and UUID/PCI bus identity. Its documentation recommends stable UUID or PCI bus IDs over enumeration indexes. It exposes ECC, clocks, power, temperature, page retirement, row remapping, recovery action, and process/MIG state where supported. [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

**[observed]** Current docs describe row remapping on Ampere+, including correctable/uncorrectable remap counts, pending remap, failure history, and per-bank availability histogram. Page retirement can report pending blacklisting and retired pages. Lifetime aggregate counts differ from volatile counters. [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

**[observed]** Power/thermal telemetry includes average/instant draw, GPU/module limits, and temperature/operating thresholds. It also includes clock event reasons/counters for thermal slowdown, power cap, and external power brake. Readings and fields differ by product and may be unavailable (`N/A`). [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

**[observed]** The NVIDIA tool queries NVLink status and error counters per link. The docs list replay/recovery/CRC counters. For NVLink 5, they also list packet, malformed, buffer-overrun, integrity, BER/FEC and recovery counters. The docs list NVLink 5 counter reset as unsupported. Timestamped before/after readings of cumulative counters still allow deltas. This holds only if counters do not wrap or reset independently. [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

### 6.2 Blackwell / GB300 caution

**[observed]** NVIDIA's reference explicitly marks `nvidia-smi prm` as Blackwell-or-newer. It describes Blackwell-specific GPU hostname support only on compatible GB200 platforms. The manual is rolling documentation. Some features are architecture-specific, and NVIDIA marks some counters as deprecated. Check exact installed driver support locally. [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

**[inference]** GB300-class rack presence alone does not guarantee a given queried field or DCGM test works. Record driver, firmware, DCGM, CUDA, and tool versions at runtime. Record feature absence as a skip with reason, never a PASS or a fabricated zero.

### 6.3 Privilege and destructive-operation boundaries

**[observed]** NVIDIA documents read-only queries separately from operations requiring root/admin. ECC-mode changes require reboot. Resetting counters changes evidence. GPU reset requires root and no active users. NVIDIA explicitly does not recommend reset for production, and reset may not succeed.

MIG create/destroy and mode changes alter device partitioning and may require privilege. Clock/power settings changes require root and can distort certification. [NVIDIA nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

**[inference]** Keep configuration and recovery operations read-only by default. Do not reset counters or change ECC/MIG/clocks/power profiles. Do not reset GPUs or run repair/remap actions. The bench itself is active; it allocates HBM and consumes power. Run it only in an exclusive, operator-approved window. Capture pre-run and post-run cumulative values with timestamps.

If no clean baseline exists, report lifetime values and classify attribution as limited.

## 7. Two-hour GPU screen proposal

### 7.1 Suggested bounded sequence

**[inference]** Organize a practical two-hour bench in five steps:
(a) 5–10 min identity/software/health baseline;
(b) 10 min passive per-GPU NVML/DCGM/ECC/Xid/NVLink snapshot;
(c) 60–80 min concurrent per-GPU compute and HBM exercise with deterministic known-answer checks;
(d) 10–15 min cooldown/second telemetry snapshot and event-log diff;
(e) reserve 10–20 min for diagnostics, output flush, or graceful abort.
Parallel scheduling across GPUs is essential. A long sequential test for each device cannot fit 72 GPUs into two hours.

**[inference]** Use at least two workload families. The first is dense compute (stress/known-answer matrix multiply). The second is memory-focused allocation/read-write/verification over a high fraction of allocatable HBM. Use varied deterministic patterns and checksums.

First verify supported DCGM/CUDA paths on GB300 and safe rack power limits. Then select the exact operations and percentage of memory. A single `gpu-burn` run does not cover all units or input patterns.

**[inference]** Capture these items for each GPU:
UUID, PCI ID, model, serial, driver and VBIOS/GSP/board firmware;
ECC mode and volatile/aggregate errors;
retired pages/remap state;
Xids and kernel event interval;
clocks/utilization/power/temperature/throttle counters at regular intervals;
HBM allocation tested;
checksums/error counts;
NVLink state and counter changes;
test command, version, exit status, and skip reason.

### 7.2 PASS / FAIL / WARN / SKIP semantics

- **PASS [inference]:** The bench identifies and tests every expected GPU. Correctness checks match defined expectations. The run shows no new uncorrectable ECC, actionable Xid, failed remap, or unexpected NVLink health event. The workload completes. Thermal/power behavior stays within the configured vendor/platform envelope. “Measured pass” does not claim zero SDC probability.
- **FAIL [inference]:** A missing expected device, kernel mismatch, or reproducible wrong result causes FAIL. New DBE/UCE, severe Xid/fallen-off-bus, failed remap, or GPU reset/hang also causes FAIL. Sustained abnormal throttling or a performance outlier under a valid comparable workload also causes FAIL. Preserve evidence and avoid automatic recovery that erases state.
- **WARN [inference]:** A correctable ECC increase causes WARN. Historical remap/retirement causes WARN. A performance outlier without known-good baseline causes WARN. Unsupported telemetry or a benign/ambiguous Xid requiring investigation causes WARN. Do not silently convert warning to pass.
- **SKIP [inference]:** An unavailable/unsupported test causes SKIP. Permission denied, device occupied, incompatible build, or insufficient safe isolation also causes SKIP. Include the exact reason and source/tool version.

## 8. Local implementation evidence (exact paths and lines)

### 8.1 What rack-bench currently measures

**[observed]** Local audit GPU collection is passive `nvidia-smi -q -x`. It inventories model/serial/architecture/PCI ID/memory. It probes ECC, MIG, firmware, clocks, power limits, thermals, and topology/P2P capability. It does not execute CUDA correctness, HBM stress, DCGM diagnostics, or GPU-burn. See [`rack_bench/audit/gpu.py` lines 8–9](../../../rack_bench/audit/gpu.py#L8-L9), [17–21](../../../rack_bench/audit/gpu.py#L17-L21), [40–50](../../../rack_bench/audit/gpu.py#L40-L50), [53–90](../../../rack_bench/audit/gpu.py#L53-L90), [93–128](../../../rack_bench/audit/gpu.py#L93-L128), and [131–136](../../../rack_bench/audit/gpu.py#L131-L136).

**[observed]** The local thermal check explicitly labels its data an instantaneous sample. It says there is no idle qualification or profile grading ([`rack_bench/audit/gpu.py` lines 84–90](../../../rack_bench/audit/gpu.py#L84-L90)). Topology/P2P is explicitly passive capability data, not an I/O test, with no expected locality map ([`rack_bench/audit/gpu.py` lines 93–128](../../../rack_bench/audit/gpu.py#L93-L128)).

**[observed]** Local tests encode these limits. [`tests/test_gpu.py` lines 38–45](../../../tests/test_gpu.py#L38-L45) verify that topology timeout stops further probes and skips. [`tests/test_gpu.py` lines 47–56](../../../tests/test_gpu.py#L47-L56) cover passive inventory/fields. [`tests/test_gpu.py` lines 58–70](../../../tests/test_gpu.py#L58-L70) require unsupported/no-GPU outcomes to skip and preserve source. These tests do not validate GPU stress or correctness screening.

### 8.2 Implication for bench-gpu

**[inference]** Keep the audit snapshot as provenance and build an active bench stage separately. Add checks only when they execute a measured workload or explicitly report a passive observation. Distinguish lifetime counters from test-window deltas. Keep NVLink per-GPU status in this category, but do not add east-west fabric throughput testing.

## 9. Source confidence and evidence quality

1. **High confidence:** NVIDIA's official `nvidia-smi` reference covers supported fields, architectural caveats, privileges, reset and NVLink counter semantics. Google Cloud's first-party GPU troubleshooting guide covers its own Xid/repair and DCGM workflows. [NVIDIA](https://docs.nvidia.com/deploy/nvidia-smi/index.html) [Google](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)
2. **High confidence for Meta's stated methodology; medium for reproducibility:** Meta Engineering is first-party and detailed, with linked research papers. The public article does not release test binaries, thresholds, GPU-specific sensitivity, or all operational parameters. [Meta](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)
3. **Medium/low confidence for tools outside primary vendor documentation:** gpu-burn is an identifiable open-source project. Its own README is not vendor qualification for Blackwell/GB300. `stress-ng` identity and CPU scope are clear from upstream/manual. It provides no GPU pass evidence. “Florence” remains unverified as a GPU test identity. [gpu-burn](https://github.com/wilicc/gpu-burn) [stress-ng](https://github.com/ColinIanKing/stress-ng)
4. **Limited Microsoft-specific evidence:** OCP participation and Azure telemetry documentation show broad resilience/monitoring context. They do not show a publicly documented Microsoft GPU acceptance test. [OCP](https://www.opencompute.org/blog/computings-hidden-menace-the-ocp-takes-action-against-silent-data-corruption-sdc)  [Azure Monitor supported metrics (scope limited)](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-compute-virtualmachines-metrics)

## Gaps

- The reviewed sources do not publish Meta's exact GPU Fleetscanner workloads, thresholds, or sampling policies. They do not publish fleet GPU-specific sensitivity/false-positive rates or GB300 qualification procedures.
- Google Cloud shows operational GPU health and DCGM diagnosis. It does not show internal pre-deployment burn-in duration, acceptance thresholds, or DeepMind-specific GPU correctness tests. Its A3 examples include H100/H200, not a GB300 rack recipe.
- Microsoft public sources reviewed do not show its GPU hardware screening cadence, GPU SDC statistics, or internal tools. “Florence” stays unverified as a GPU test tool. Resolving the name requires a first-party URL/repository and version.
- The public gpu-burn project does not guarantee current Blackwell/GB300 or Grace compatibility, diagnostic coverage, or two-hour rack-scale runtime. Validate the exact commit/build, CUDA, driver, and test behavior on a sacrificial/approved system before certification use.
- Public documentation does not establish DCGM diagnostic durations or exact test support on the rack's installed GB300 driver/firmware. Time each diagnostic in situ. Preserve skips and unsupported test output.
- A two-hour screen cannot exclude rare, data-dependent, voltage/frequency/temperature-sensitive or aging SDC. Meta's methodology itself emphasizes repeated periodic screening and workload-time telemetry as necessary complements.
- CPU SDC studies and CPU stress tools provide no valid numerical GPU defect-rate estimate. This brief infers no GPU rate here.
