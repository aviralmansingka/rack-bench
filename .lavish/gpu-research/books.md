# Canonical books and guides for GPU diagnosis: the ranked reading order

Research date: 2026-10-11. All claims below carry a source URL.

Scope: N07 only.
This node asks which books and guides help a team measure device-level GPU quality.
The measurement uses a two-hour `bench gpu` window.
The target is an 18-tray, GB300/NVL72-class rack in Chennai. [observed]
The parent research index defines this rack, the two-hour question, and the exclusions. [observed] <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/README.md>

[observed] The scope includes DOA/degraded units, ECC and row remapping, XIDs, and SDC.
The scope also includes power/thermal throttling, clocks, HBM, and software/firmware mismatch.
The scope also includes correctness, MIG, and per-GPU NVLink health.
The scope excludes east-west fabric performance. [observed] <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/research.md>

Conventions: Each claim has one label.
**[observed]** means that a source/document or local code states it.
**[calculated]** means arithmetic from reported measurements.
**[inference]** means a recommendation or interpretation.

“PASS” means that a measured property meets a declared, SKU/workload-specific profile criterion.
A vendor claim alone never makes a PASS.
Sometimes the GPU/driver does not show a field.
Sometimes a diagnostic plugin cannot run.
In those cases, report `SKIP` with the exact reason.
A null or `N/A` value is not a pass.

[observed] The existing audit code explicitly treats unsupported fields as unverified.
The audit code records passive observations, not active tests. [observed] <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L24-L37>
[observed] Local project policy says that permission-gated checks skip with a reason.
The project plans GPU bench for short device-compute checks. [observed] <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L130-L148> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L320-L325>

## 1. Executive answer: ranked task-based canon

| Rank | Source | What to use it for | Verdict for rack-bench |
|---|---|---|---|
| 1 | Brendan Gregg, *Systems Performance*, 2e (2020), especially methodology / USE / benchmarking | Test design, saturation-vs-error reasoning, counters/deltas, baselines, outliers, observability discipline | MUST. It is the methodological canon. It is not a GPU test recipe. [observed] <https://www.brendangregg.com/systems-performance-2nd-edition-book.html> |
| 2 | NVIDIA DCGM Diagnostics + DCGM release notes (current matched release) | Production active diagnostics, plugins, calibrated results, health semantics, supported GPU/driver combinations | MUST. It is the operational canon. It is more current than any book. [observed] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html> |
| 3 | NVIDIA `nvidia-smi` / NVML documentation and NVIDIA GPU Operational Events catalog | Exact passive telemetry, ECC/row-remap/XID/recovery semantics, clocks, temperatures, power and NVLink errors | MUST. It gives authoritative field definitions. Use version-matched docs and live `--help-query-*`. [observed] <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/deploy/gpu-operational-events/latest/> |
| 4 | CUDA C++ Programming Guide + CUDA Best Practices Guide + Compute Sanitizer docs | Build correctness workloads. Interpret runtime/tool limitations. Use it for kernel-level correctness and memory checks. | MUST reference for implementation. It does not replace hardware qualification. [observed] <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/> <https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html> |
| 5 | Kirk & Hwu et al., *Programming Massively Parallel Processors* (PMPP), 4e (2022) | CUDA/GPU architecture and memory hierarchy underlying test kernels | SKIM/select chapters. It gives architecture education. It does not give field diagnosis or Blackwell calibration. [observed] <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0> |
| 6 | Brendan Gregg, *BPF Performance Tools* (2019), plus modern Nsight Systems / CUPTI | Optional attribution of kernel/runtime stalls and timeline evidence | OPTIONAL. GPU tracing is not a universal BPF feature. eBPF alone does not prove device arithmetic correctness. [observed] <https://www.brendangregg.com/bpf-performance-tools-book.html> <https://docs.nvidia.com/nsight-systems/UserGuide/index.html> |
| 7 | NVIDIA Field Diagnostic / Extended Utility Diagnostic and RMA guidance | Escalation on suspected hardware fault. It is the provider/OEM-approved deep test and repair route. | Keep it out of the automatic two-hour routine. The exception is a site that explicitly provisions and authorizes it. [observed] <https://docs.nvidia.com/deploy/hw-field-diag/index.html> <https://docs.nvidia.com/deploy/rma-process/index.html> |

[inference] The shortest credible reading path starts with Gregg methodology.
Next, read the versioned DCGM diagnostics reference and `nvidia-smi` / NVML field semantics.
Then read the CUDA correctness/tool docs.
[inference] Read PMPP to learn how to write representative kernels.
Do not use PMPP as a live Blackwell RAS, firmware, or acceptance-test manual.

[inference] Current product docs and release notes beat books on exact flags, plugin availability, and GB300 support.
Peer-reviewed reliability papers beat both on prevalence and SDC detection limits.

## 2. #1 methodology: *Systems Performance*, 2nd edition — Brendan Gregg

### Why this book ranks first

- **[observed]** Gregg's 2e is the 2020 Addison-Wesley edition.
  It includes methodology, observability, benchmarking, and systems-performance chapters.
  Its publisher/author book page gives edition and contents. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>
- **[inference]** Its most transferable device-level lesson is the USE discipline.
  For each resource, ask about utilization, saturation, and errors.
  Then use a workload that makes those observations meaningful.
  For a GPU, those observations include measured compute/memory activity and requested-versus-realized performance.
  They also include time spent throttled and ECC/XID/row-remap/error deltas.
  A single “GPU utilization” snapshot is not enough. <https://www.brendangregg.com/usemethod.html> <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>
- **[inference]** Apply the method per GPU UUID.
  Keep raw observations, timestamps, driver/runtime versions, workload parameters, and the comparison basis.
  A mean across 72 GPUs can conceal one degraded device.
  Report per-device values and distribution/rank as well as the rack summary. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>
- **[inference]** The book gives methodology, not a GB300 validation script.
  It does not give Blackwell acceptable TFLOP/s, HBM bandwidth, ECC rate, temperature, wattage, or NVLink error thresholds.
  Derive those thresholds only from a declared profile and applicable product docs or a measured cohort baseline. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>

### How to port Gregg into a two-hour GPU test

1. **Show denominator and identity. [inference]** Enumerate all expected devices.
   Map stable GPU UUID/PCI BDF to tray/host/module.
   Fail completeness separately from performance.

   Driver enumeration indexes are not stable across reboots.
   The `nvidia-smi` guide recommends UUID or PCI bus ID for stable targeting. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
2. **Capture a before snapshot. [inference]** Store device identity, PCI BDF, product/architecture, driver/KMD, and CUDA UMD.
   Store VBIOS/GSP and platform firmware.
   Store ECC current/pending mode, volatile and aggregate error counters, retired pages, remapped rows, and recovery action.

   Store MIG state/instances, power limit/profile, supported/current clocks, and temperatures.
   Store per-link NVLink state/counters.
   The exposed subset depends on SKU, driver, platform privilege, and current tool. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html>
3. **Run a declared active workload. [inference]** Run diagnostic correctness/memory/compute/power checks on isolated devices.
   Capture telemetry during execution.
   Record achieved values and elapsed duration per device.
   A counter snapshot before/after separates new events from lifetime totals. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>
4. **Capture after and compute deltas. [inference]** Report volatile ECC changes and counter increments as window events.
   Keep aggregate ECC/row-remap history as lifetime context.

   On Linux, a driver unload/reload can reset volatile counts.
   Aggregate counts persist.
   Ampere+ does not support aggregate ECC reset. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
5. **Classify, do not conceal. [inference]** Separate hard failures, warnings, pass, and unavailable/skipped probes.
   Keep the exact diagnostic error ID, plugin status, raw values, and cause.
   A DCGM error can identify a GPU entity, severity, category, and recovery advice. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
6. **Use no universal threshold. [inference]** A performance threshold is defensible only with pinned conditions.
   Pin the exact GPU product, device count, workload/precision, and clocks/power policy.
   Also pin the software stack, contention state, and threshold source.

   DCGM offers relative-to-system-mean tolerance parameters.
   Those parameters are comparison rules, not universal GB300 guarantees. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>

## 3. #2 operational canon: NVIDIA DCGM Diagnostics

### Canonical run levels, semantics and time

- **[observed]** The current DCGM CLI reference defines four `dcgmi diag --run` levels.
  Level `1` runs quick deployment checks (normally seconds).
  Level `2` runs medium validation (normally about two minutes).
  Level `3` runs long hardware diagnostics (normally about 15 minutes).
  Level `4` runs extended/longer hardware diagnostics.
  An operator can select a single named test or comma-separated tests. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>
- **[observed]** The current suite composition is cumulative.
  Level 1 runs software/deployment checks.
  Level 2 adds memory and PCIe.
  Level 3 adds diagnostic, memory bandwidth, targeted stress, targeted power, and conditional tests.
  Level 4 adds memtest and pulse test to the level-3 set.
  Actual inclusion depends on host-loaded plugins and applicability. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>
- **[observed]** `--timeout` defaults to zero (unlimited).
  So a certification harness must set an explicit bound.
  `--iterations` repeats suites.
  `--json` is available.
  `--expectedNumEntities gpu:N` checks expected entity count only with default/all-GPU selection. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>
- **[inference]** Consider a ~15-minute level 3 run plus snapshots and a small independent correctness check.
  By nominal documentation runtime, that run fits easily within a two-hour category slot.
  The team must still time the actual rack runtime.
  Diagnostics across 72 GPUs can have a different wall-clock duration from the single-GPU estimates.
  They can also have a different power/thermal footprint.
  NVIDIA publishes no fixed total wall-clock guarantee. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** DCGM says that active diagnostics can consume substantial GPU, CPU, memory, power, and fabric resources.
  DCGM asks operators to coordinate with workload owners.
  DCGM diagnostics are not comprehensive hardware diagnostics.
  They do not repair faults, and they do not replace field diagnostic tools.
  They are not an RMA process. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[inference]** For certification, use level 1 and then run selected useful named tests.
  Alternatively, run a site-reviewed level 2/3 suite.
  In both cases, use a hard timeout and no active tenant workload.
  Do not blindly run `-r 4` as a quick check.
  Its default memory soak is 10 minutes, plus pulse-test and preceding tests.
  It can also be intrusive. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

### Plugins mapped to GPU failure modes

| Failure mode | DCGM mechanism | Bench interpretation |
|---|---|---|
| Dead, missing, inaccessible, incompatible software | `software` deployment prologue. Entity count. Library, permissions, driver/CUDA checks. | A missing expected GPU is FAIL. An unsupported/missing driver capability is SKIP/WARN with the exact reason. It is never an empty PASS. [observed] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> |
| ECC, row remap, memory data faults | `software`, `memory`, `memtest`. DBE/UCE, mismatch and row-remap checks. | Capture pre/post counters and pending/failure states. The memory test actively writes and verifies a significant memory allocation. [observed] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> |
| Compute correctness / gross degradation | `diagnostic` | The test runs large matrix products plus framebuffer write/read validation. Standard errors include XIDs, temperature and uncorrectable memory errors. [observed] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> |
| HBM bandwidth / sustained memory path | `memory_bandwidth` (STREAM-like TRIAD) and `memtest` | The measurement is per device. Enforce a profile/reference, not a generic threshold. In current docs, the plugin allocates a default fixed 756 MB working set. That set may not give a full-HBM bandwidth test on GB300. [observed] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> |
| Clock/power delivery / thermal response | `targeted_power`, `targeted_stress`, `diagnostic`. Telemetry and clock-event counters. | Run a specified workload. Correlate achieved performance, clocks, power, temperature, power caps and reason/time counters. [inference] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html> |
| Per-GPU NVLink health (only fabric scope retained) | DCGM health/NVLink telemetry. `nvidia-smi nvlink --status` and `--errorcounters`. | Query state and error deltas per GPU/link. This N07 GPU-quality scope excludes collective, pairwise bandwidth, and east-west fabric certification. Do not run them here. [observed] <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html> |
| SDC | DCGM data-pattern checks plus independent deterministic CUDA kernel/reference comparison | A pass covers only the tested operations, data types, input patterns, duration and error-detection method. No short screen proves zero SDC. [inference] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model> |

### Specific DCGM plugin semantics and calibration caveats

- **[observed]** The diagnostic plugin (level 3) performs a large matrix multiply.
  It copies data to different framebuffer addresses.
  Then it checks write/read correctness.
  The documented default stress is five minutes.
  The plugin monitors XIDs, temperature violations, uncorrectable memory and correctness. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** On Blackwell+, the diagnostic default matrix dimension is 8192.
  Tensor Core use defaults to true.
  Available parameters include precision, `gflops_tolerance_pcnt`, clock/power tolerance and `always_use_tensor`.
  Current docs describe comparison to the mean across GPUs in the system. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[inference]** Relative-to-rack-mean detection is valuable to find one outlier among nominally identical devices.
  It may miss a rack-wide degradation where all GPUs are equally slow.
  Pair the relative detector with SKU-specific absolute acceptance criteria from an approved profile.
  If no such criteria exist, label absolute-performance acceptance `SKIP`. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** The memory plugin tests allocation/write/read with five patterns.
  By default, it uses a significant fraction (documented as 75%) of total GPU memory.
  It reports allocation failure, mismatch, CUDA DBE, and L1 cache miscompare. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** Level-4 memtest uses pattern algorithms.
  Documentation runtimes are explicitly average seconds per iteration on a single A100 40GB.
  For example, bit-fade takes about 244 seconds, and 32-bit moving inversions take about 155 seconds.
  By default, memtest alternates tests 7 and 10 for 10 minutes.
  Those figures are not GB300 runtime guarantees. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** Targeted power attempts sustained near-TDP use.
  Its default minimum target ratio is 75%.
  It fails on memory errors, temperature violations, or XIDs.
  Targeted stress has a documented default target-performance minimum ratio of 95% (and additional error conditions). <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[inference]** These ratios are plugin-internal acceptance ratios, not vendor-independent GPU-quality thresholds.
  To interpret results, record the exact DCGM release/SKU configuration and plugin parameters.
  Also record the GPU’s applicable power policy. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** Hardware/SKU, CUDA libraries, an external executable, environment, permissions or privilege conditions can make plugins unavailable.
  An explicit request for unavailable tests returns errors.
  It does not guarantee a runnable check.
  The CLI docs show no public `dcgmi` operation to list all tests runnable on the runtime host. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>
- **[inference]** At initialization, record DCGM/driver/CUDA versions.
  Run the required named test under a fixed timeout.
  If the plugin says unsupported/missing, emit a reasoned SKIP and keep the diagnostic output.
  Never transform “plugin not loaded” into PASS. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>

### GB300 support: pin the release, not just the tool name

- **[observed]** DCGM 4.4.0 adds active diagnostic support for B300 (device 3182, subsystem 20E610DE).
  The same release also adds GB300 NVL Bianca (device 31c2).
  DCGM 4.4.2 adds GB300 NVL Galaxy (31C220E5) and GB300 MaxQ (31a1). <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>
- **[observed]** The current release history includes later DCGM releases than 4.4.2.
  Do not treat those early support additions as proof that every plugin works on every GB300 SKU.
  Check the current release’s per-plugin supported products and driver pairing.
  Also check the packaging lane and the locally installed host-engine version. <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html> <https://docs.nvidia.com/datacenter/dcgm/latest/installation.html>
- **[observed]** The NVBandwidth plugin’s published supported-products list includes B300 (20e6).
  Its scope is single-host GPU copy paths.
  It is an inter-GPU/PCIe bandwidth validation, not a standalone GPU arithmetic quality check. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[inference]** If requested, mention NVBandwidth in N07 only as a separately-scoped per-GPU link diagnostic option.
  Exclude its peer-pair/east-west throughput result from the `bench gpu` certificate in this document. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** DCGM installation docs identify NVSDM as the NVSwitch monitoring dependency for Blackwell and later systems.
  Fabric Manager dependencies differ by architecture generation. <https://docs.nvidia.com/datacenter/dcgm/latest/installation.html>
- **[inference]** A missing NVSDM/telemetry backend makes Blackwell NVSwitch readings unavailable, not healthy.
  For the in-scope device-level NVLink check, report per-GPU link status/counter acquisition explicitly.
  Do not infer device health from a missing switch backend. <https://docs.nvidia.com/datacenter/dcgm/latest/installation.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## 4. #3 command reference: `nvidia-smi`, NVML and NVIDIA event semantics

### Safe, read-only evidence collection

The following commands are queries.
Run them with a stable UUID/BDF mapping.
Save stdout/stderr, the UTC timestamp, and command/tool versions.
Fields vary.
Check the local driver’s `--help-query-gpu`, `--help-query-retired-pages`, `--help-query-remapped-rows`.

**[observed]** `nvidia-smi` explicitly states that many fields are unsupported in some environments and appear as N/A.
Its CLI text output has no guarantee of backward compatibility.
NVIDIA prefers NVML for maintained automation. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

```sh
# Identity and installed versions; use UUIDs/BDFs, not enumeration index alone.
nvidia-smi -L
nvidia-smi --version
nvidia-smi --query-gpu=uuid,pci.bus_id,name,serial,driver_version,vbios_version,gsp_firmware_version --format=csv

# Full structured inventory/snapshot; preserve XML output.
nvidia-smi -q -x > nvidia-smi-before.xml

# Human-readable RAS, temperature, power, performance and MIG state.
nvidia-smi -q -d ECC,ROW_REMAPPER,PAGE_RETIREMENT,PERFORMANCE,TEMPERATURE,POWER,CLOCK,COMPUTE

# Explicit ECC and row-remap records. Availability of query fields is version/SKU dependent.
nvidia-smi --query-gpu=ecc.errors.corrected.aggregate.device_memory,ecc.errors.uncorrected.aggregate.device_memory --format=csv
nvidia-smi --query-remapped-rows=gpu_bus_id,bank_count,bank_needs_remapping --format=csv
nvidia-smi --query-retired-pages=address,cause,pending --format=csv

# Current state, sampled during device compute (store full samples, not a lone reading).
nvidia-smi dmon -s pucvme -d 1 -c 600

# Per-GPU NVLink state and error counters; these queries do not inject traffic.
nvidia-smi nvlink --status
nvidia-smi nvlink --errorcounters
```

**[observed]** `nvidia-smi -q -d` supports ECC, row remapper, page retirement, performance, temperature, power and clock sections.
Selective query and loop formats support scripted capture.
Unsupported requested values may be N/A. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

**[observed]** `dmon` supports 1-second samples and a `-c` count.
It has groups for power/temperature, utilization, clocks, violation metrics, memory and ECC.
Some metrics may be unavailable for a particular GPU/platform. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

### ECC, page retirement and row remapping are not interchangeable

- **[observed]** ECC volatile counters count errors since the last driver load.
  Linux can unload/reload the driver more often when no persistent driver clients exist.
  Aggregate counters persist indefinitely.
  Hardware corrects single-bit errors.
  Hardware detects double-bit errors but does not correct them. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** Page retirement hides unreliable pages from later driver/application allocations.
  A DBE or multiple SBEs on a page can cause retirement.
  `Pending` means that the driver has not yet blacklisted the pages at reboot.
  Before that transition, the pages may remain allocatable. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** Row remapping moves an unreliable memory row to a reserved row.
  One uncorrectable error or multiple correctable errors in one row may trigger it.
  `Pending` means that the remap needs a GPU reset to take effect.
  `Remapping Failure Occurred` records a historical failure.
  The bank availability histogram shows the remaining reserved-row capacity.
  Row remapping is available on Ampere and later. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** Report at minimum the ECC current/pending state and volatile/aggregate SBE/DBE.
  Report retired pages and pending retirement.
  Report correctable/uncorrectable remapped-row totals, pending remap, failure flag, and bank availability.
  Report the recovery action.
  Do not reduce these to one “ECC count.” <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** `nvidia-smi --reset-ecc-errors` changes counters (requires root).
  Ampere+ does not support aggregate reset.
  Avoid it in certification.
  Take snapshots and calculate differences instead. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

### XIDs, SDC, and recovery decisions

- **[observed]** XIDs are driver event codes, not a single universal failure severity.
  NVIDIA’s DCGM health docs map XID classes to memory/PCIe/thermal/power/NVLink.
  The docs give examples such as XID 63 pending page retirement and 64 row-remap failure.
  Other examples are 94 contained error and 95 uncontained error. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>
- **[observed]** NVIDIA’s GPU Operational Events catalog separates detailed events and recovery scope/severity.
  For example, a pending row-remapping event (legacy XID 63) is recoverable.
  That event takes effect on the next reset.
  Remap-failure events (legacy XID 64) are fatal/resource failure cases. <https://docs.nvidia.com/deploy/gpu-operational-events/latest/>
- **[observed]** `nvidia-smi -q` shows the GPU Recovery Action, such as None, Reset, Reboot, Drain P2P, or Drain and Reset.
  The action is remediation guidance.
  The action alone does not explain the originating fault. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** Keep the kernel log/journal XID timestamp and BDF.
  Keep them with the DCGM entity/error ID and GPU recovery action.
  Escalate/reset only through the documented site runbook.
  Do not auto-reset from a certification script.
  A recoverable event still belongs in the report.
  It may invalidate a clean pass for the affected check. <https://docs.nvidia.com/deploy/gpu-operational-events/latest/> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** SDC is incorrect computation without an explicit hardware error signal.
  The NVIDIA research reliability model estimates application-level SDC.
  It uses fault injection plus error-propagation modeling. <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>
- **[inference]** ECC counters, DCGM’s tested data paths, and finite deterministic reference comparisons can detect some faults.
  They cannot prove the absence of SDC.
  Where feasible, use CPU-side independent verification of deterministic test output.
  Include nontrivial patterns and multiple precisions.
  Describe the scope as “no mismatch observed in these checks,” not “SDC-free.” <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>

### Clocks, power, limits and thermals: interpret under workload

- **[observed]** `nvidia-smi` reports current clocks, supported/max clocks, power draw, and power limit.
  It also reports temperature readings and clock event reasons/counters.
  Event reasons separate software power cap, thermal slowdown, and hardware thermal slowdown.
  They also separate external hardware power brake, sync boost, and other caps. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** Current/average/instant power and module-power fields differ.
  The module may include the GPU, a supported NVIDIA CPU, and other components.
  Module power limits may govern several components.
  Hopper+ data-center products support module fields. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** Temperature telemetry is not uniform.
  Not all products expose all sensor types.
  Module form factors that rely on enclosure cooling may omit sensors.
  T.Limit is a margin, not an absolute temperature. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** Quiesce the rack, and then capture a short idle baseline.
  Then sample under the same declared sustained workload.
  Use `clock_event_reasons`, the corresponding time counters, and achieved throughput together.
  They show whether idle, policy/power cap, thermal slowdown, or external brake causes a low clock.
  A current clock alone cannot diagnose quality. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** Do not impose one temperature, watts, or clock threshold across module SKUs, firmware and cooling configurations.
  Compare against the device’s exposed operating limits and the approved platform profile.
  Also compare against homogeneous-peer measurements with documented thermal/power controls.
  Missing sensor support is SKIP for that field, not zero. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** `nvidia-smi dmon` aggregates ECC counters in its documented ECC group.
  `nvidia-smi -q` supplies detailed error locations and timescales.
  **[inference]** Prefer detailed snapshots for RAS acceptance.
  Prefer sampled telemetry for temporal association during load. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

### Per-GPU NVLink health only

- **[observed]** `nvidia-smi nvlink --status` reports link state (active, inactive, sleep; bandwidth if active).
  `--errorcounters` lists link errors and recoveries.
  Counter names differ between NVLink generations.
  The current CLI guide lists NVLink 4 replay/recovery/CRC fields.
  It lists NVLink 5 packet, integrity, recovery, discard, and BER/FEC-style fields. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** Blackwell and later links can enter Sleep.
  Sleep does not mean a failed link.
  Blackwell+ deprecates the NVLink bandwidth mode switch.
  Do not use old bandwidth-mode configuration assumptions as a health probe. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** Record the links of each physical GPU while the GPU test runs.
  Record before/after error-counter deltas for those links.
  Interpret sleep/inactive against topology and current utilization.
  Do not run NVLink bandwidth, collective, or rack-fabric tests within this book node.
  The exception is a test that another bench category explicitly owns. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## 5. #4 CUDA programming and correctness guides

### CUDA C++ Programming Guide + Best Practices Guide

- **[observed]** NVIDIA’s CUDA C++ Programming Guide documents the execution model, memory spaces, and synchronization.
  It also documents arithmetic, streams, and device capabilities.
  The CUDA Best Practices Guide describes performance measurement and optimization practices. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>
- **[inference]** Read the execution, memory hierarchy, numerical behavior, and error-checking sections.
  These sections help you build an independently checked GPU health workload.
  In a certification kernel, check every CUDA API result.
  Synchronize before you evaluate completion.
  Compare outputs to known deterministic CPU references.
  Alternatively, compare outputs to vetted expected hashes/tolerances for the arithmetic mode. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>
- **[inference]** “Bit-exact” only applies when the operation and build are deterministic.
  That determinism must hold under the chosen device/compiler/library versions.
  Floating-point reduction order and fused operations can change rounding.
  Some library GEMM algorithm/precision modes do not promise bitwise equality.
  For such a GEMM, do not make bitwise equality a blanket rule.
  Pin operands, library versions, math mode, algorithm, seed, and comparison contract.

  When exact identity has no guarantee, use a mathematically justified tolerance. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cuda/cublas/index.html>
- **[inference]** A two-hour CPU-reference comparison can verify selected kernels and data sizes.
  It is sampling, not exhaustive validation.
  It does not cover every instruction, HBM address, thermal transient, or rare fault.
  Pair correctness with DCGM memory/ECC/RAS telemetry, and publish coverage. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

### Compute Sanitizer: useful, but not a hardware acceptance suite

- **[observed]** NVIDIA Compute Sanitizer offers `memcheck`, `racecheck`, `initcheck`, and `synccheck` tools.
  These tools find memory access, race, initialization and synchronization errors in CUDA applications. <https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html>
- **[inference]** Use it during development and optionally on a compact test binary.
  Do not use it as the routine production rack-wide two-hour default.
  Instrumentation changes runtime and workload behavior.
  It checks software-visible classes of errors.
  It does not certify HBM margin, power delivery, cooling, or field reliability. <https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html>

## 6. #5 CUDA architecture book: *Programming Massively Parallel Processors* (PMPP)

- **[observed]** *Programming Massively Parallel Processors: A Hands-on Approach* is a textbook.
  The 4th edition has these details: Wen-mei Hwu, David Kirk, Izzat El Hajj; 2022.
  It covers CUDA and parallel architecture.
  It is not a DCGM/NVML troubleshooting handbook. <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0>
- **[inference]** Read selected parts on SIMT execution, occupancy, memory hierarchy/coalescing, and synchronization.
  Also read parts on reductions and performance measurement.
  These parts help the team understand why distinct memory and compute tests probe distinct resources.
  They also show why utilization alone is not performance. <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0>
- **[inference]** Its version horizon prevents it from replacing current sources.
  It cannot replace the current GB300 architecture/product spec or current CUDA 13/driver behavior.
  It cannot replace DCGM plugin calibration, XID event definitions, row-remap state, or Blackwell MIG details.
  Pair it with live NVIDIA CUDA/architecture docs and matched release notes. <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>
- **Verdict [inference]:** SKIM for test authors.
  Operators do not need it to run the bench.
  It is stronger than a cookbook for understanding custom CUDA checks.
  It is weaker than primary NVIDIA documentation on what NVIDIA supports.
  It is also weaker on how to read current hardware health. <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0>

## 7. #6 Tracing: BPF book versus GPU-specific tracing

### Gregg, *BPF Performance Tools* (2019)

- **[observed]** Gregg’s book covers Linux eBPF performance tools and tracing practices.
  Its author page includes the table of contents and edition metadata. <https://www.brendangregg.com/bpf-performance-tools-book.html>
- **[inference]** Use the method for low-overhead host-kernel context around GPU runs.
  That context includes launch latency, CPU scheduling, and driver ioctl/kernel activity.
  It also includes memory pressure and host contention.
  The method helps attribute delays to host software.
  It does not prove GPU arithmetic correctness or HBM health. <https://www.brendangregg.com/bpf-performance-tools-book.html>
- **[observed]** NVIDIA Nsight Systems and the CUDA Profiling Tools Interface (CUPTI) document GPU activity timelines.
  They also document CUDA API/kernel tracing.
  A general eBPF book does not document them. <https://docs.nvidia.com/nsight-systems/UserGuide/index.html> <https://docs.nvidia.com/cupti/>
- **[inference]** For CUDA API, kernel, memcpy and synchronization timelines, Nsight Systems/CUPTI is the current primary source.
  For kernel microarchitecture counters, use Nsight Compute’s supported metrics and profiling guidance.
  Shared production systems may restrict profiling permissions/collection. <https://docs.nvidia.com/nsight-systems/UserGuide/index.html> <https://docs.nvidia.com/cuda/nsight-compute/index.html>
- **[inference]** eBPF-driven “GPU tracing” can mean tracing host-side calls or a vendor-specific integration.
  Do not imply that standard eBPF directly observes GPU SM instructions, HBM transactions or NVLink PHY health.
  Before you treat a trace as evidence, establish the provider, event source, privilege and data semantics. <https://www.brendangregg.com/bpf-performance-tools-book.html> <https://docs.nvidia.com/cupti/>
- **Verdict [inference]:** OPTIONAL/debug only.
  Record whether the team runs tracing and whether permissions prevent it.
  Do not let tracing gate a basic GPU certificate.
  The exception is a profile that explicitly requires trace-based diagnosis. <https://docs.nvidia.com/nsight-systems/UserGuide/index.html>

## 8. Blackwell MIG and NVLink: platform restrictions and “hygiene”

### MIG state is configuration evidence, not an invitation to reconfigure

- **[observed]** The NVIDIA MIG User Guide says to use only supported GPUs/systems and the latest datacenter driver.
  NVML or `nvidia-smi` can manage MIG. <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/getting-started-with-mig.html>
- **[observed]** NVIDIA release information reports new MIG profiles for HGX GB300 NVL72 in GPU Operator documentation.
  The profiles include 1g.35gb, 1g.35gb+me, 1g.70gb, 2g.70gb, 3g.139gb, 4g.139gb, and 7g.278gb.
  Exact profile availability remains platform/driver dependent. <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/release-notes.html>
- **[observed]** `nvidia-smi` can read the current and pending MIG mode.
  It can also list GI/CI profiles and instances.
  MIG enable/disable and instance create/destroy actions change privileged configuration.
  NVIDIA explains that MIG mode may involve a GPU reset, depending on product/state.
  Active driver clients may block changes. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/getting-started-with-mig.html>
- **[inference]** In a certification bench, query the MIG current/pending mode, existing instances, and profile geometry.
  Compare them to the rack’s expected policy.
  Keep them unchanged.
  Do not run `nvidia-smi -mig 1`, `-mig 0`, `mig -cgi`, `-dgi` or `-dci` during certification.
  A test that changes MIG can disturb tenants and require a reset.
  It can also alter visibility and leave the instance configuration changed. <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/getting-started-with-mig.html>
- **[observed]** `nvidia-smi` docs warn that several NVML interfaces do not support GPU/MEM/engine utilization attribution in MIG mode.
  MIG-specific telemetry support depends on the version and metric.
  So `N/A` is not zero. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/getting-started-with-mig.html>
- **[observed]** NVIDIA’s MIG platform support tables do not establish universal support for every Blackwell SKU by architecture alone.
  The supported GPU/platform table and driver requirements are normative. <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/supported-gpus.html>

### MIG and NVLink conflict: describe by product/platform, not blanket folklore

- **[observed]** NVIDIA Fabric Manager documentation covers MIG and NVLink.
  On some products, MIG enablement disables/does not use GPU NVLinks and P2P.
  The documentation also explicitly notes that NVLinks remain active during MIG mode on supported newer platforms. <https://docs.nvidia.com/datacenter/tesla/fabric-manager-user-guide/index.html>
- **[observed]** The MIG user guide reports profile tables and feature restrictions per supported product.
  GPU Operator release notes explicitly include MIG profiles for HGX GB300 NVL72. <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/supported-gpus.html> <https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/release-notes.html>
- **[inference]** Do not repeat the old blanket claim “MIG turns off NVLink” for all Blackwell/GB300 platforms.
  Also, do not infer from one generic statement that MIG preserves every NVLink use case.
  Pin the actual HGX GB300/NVL72 platform docs.
  Also pin the driver/Fabric Manager/NVSDM and MIG profile docs.
  A MIG geometry check is distinct from a per-GPU link status/error check. <https://docs.nvidia.com/datacenter/tesla/fabric-manager-user-guide/index.html> <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/supported-gpus.html>
- **[inference]** The expected NVLink-state policy for a given profile can remain unclear in platform-specific documentation.
  In that case, mark that policy comparison SKIP until the system OEM/NVIDIA platform guide settles it.
  Still capture the available physical per-GPU NVLink telemetry. <https://docs.nvidia.com/datacenter/tesla/fabric-manager-user-guide/index.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## 9. Proposed two-hour `bench gpu` measurement plan

This plan is a time budget proposal.
It does not claim that a complete manufacturing-quality test fits within two hours.
**[inference]** Parallelism across devices can shorten wall time.
It can also alter cooling and rack power.
So record the actual parallelism and the simultaneous test policy. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>

| Elapsed | Check | Evidence / interpretation |
|---|---|---|
| 0–10 min | Identity, topology mapping, version/firmware inventory, expected GPU count, process/tenant quiescence, baseline RAS/ECC/remaps/MIG/power/clocks/thermal/NVLink | Detect a missing/DOA or misidentified device. Save stable IDs and before counters. [inference] <https://docs.nvidia.com/deploy/nvidia-smi/index.html> |
| 10–15 min | DCGM level 1 / software deployment checks | Check CUDA/NVML/library/access issues. Check pending retirement/remap/software issues. Actual time varies. [observed] <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html> |
| 15–35 min | DCGM level 2 or explicit memory + PCIe as profile allows | Check memory pattern correctness and device-host integration. Gate/omit PCIe peer/fabric components if they are outside category scope. [inference] <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html> |
| 35–55 min | DCGM `diagnostic` or calibrated short variant; independent deterministic arithmetic correctness smoke | Check per-device GEMM/copy correctness and achieved performance. Record XID/ECC/temperature events. Use the vendor-documented default or a recorded parameter override. [inference] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> |
| 55–75 min | Memory bandwidth and short HBM pattern test | Record per-GPU throughput, working set, patterns, and errors. Do not treat the default 756MB STREAM buffer as full HBM capacity/bandwidth coverage. [inference] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> |
| 75–100 min | Sustained targeted power/compute under continuous telemetry | Find throttling, an underperforming outlier, and power/thermal instability. Keep clock/power/thermal samples and reason deltas. [inference] <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html> |
| 100–110 min | Take after snapshots. Calculate RAS/NVLink deltas. Inspect the XID/kernel log and errors. | Classify new events vs lifetime state. Note unavailable counters. [inference] <https://docs.nvidia.com/deploy/nvidia-smi/index.html> |
| 110–120 min | Report and policy evaluation | Report PASS/FAIL/WARN/SKIP per check. Include actual duration, raw values, versions, profile source and limitations. [inference] <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L130-L148> |

**[calculated]** This proposed allocation sums to 120 minutes (10+5+20+20+20+25+10+10).
It is a scheduling envelope.
It is not a measured duration or a claim of full memory/device coverage.
**[inference]** In practice, select either a site-calibrated DCGM suite or component plugins.
This choice prevents an unintended second run of overlapping tests.
Set an explicit command timeout below the category limit to leave reporting time. <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>

### Minimum useful bench-gpu outputs

1. **[inference]** Per physical GPU: UUID/BDF, tray/host/module, and expected/observed presence.
   Also report SKU, driver and firmware versions.
   Attach the raw command output. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
2. **[inference]** Per GPU: ECC state and SBE/DBE volatile/aggregate counts.
   Also report retired-page and pending state.
   Also report row-remap corrected/uncorrected/pending/failure/availability and recovery action.
   Give before/after values and the delta. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
3. **[inference]** DCGM per-plugin status/error ID/details, elapsed time and test parameters.
   Also report the compute correctness result and measured workload rate.
   Also report precision, clocks and sample distributions. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
4. **[inference]** Under load: per-GPU SM/memory clocks and board/module power.
   Also report the configured/enforced limit if available, and the GPU/HBM temperature if exposed.
   Also report clock-event causes and counters. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
5. **[inference]** Per-GPU NVLink state and error counters before/after.
   This scope gives no fabric bandwidth/collective grade. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
6. **[inference]** Explicit coverage caveat: short tests cannot guarantee the absence of intermittent, extremely rare SDC.
   Each unavailable metric/test must have a reasoned skip. <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L31-L36>

### No universal performance threshold

- **[observed]** DCGM diagnostic tolerance options can compare performance, clock and power across GPUs in the running system.
  Blackwell settings and SKU calibration matter. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[inference]** This brief asserts no single threshold across every GB300 system.
  This applies to TFLOP/s, HBM GB/s, watts, clock MHz, temperature, ECC counts, remap availability, and NVLink errors.
  A threshold needs a primary source tied to the exact supported SKU/configuration.
  Alternatively, it needs a rack certification profile.
  Another option is a documented measured baseline with its uncertainty and workload conditions. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** If only peer-relative comparison is available, report it as “relative outlier screen,” not absolute acceptance.
  A cohort-wide failure can make the mean a misleading reference. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

## 10. Commands and actions: safe queries versus change/reset operations

### Safe observational commands (normally read-only)

These commands are observational/query actions: `nvidia-smi -L`, `nvidia-smi -q -x`, `nvidia-smi --version`, `nvidia-smi --help-query-gpu`.
These commands are also observational/query actions: `nvidia-smi --query-gpu=... --format=csv`, `nvidia-smi --query-retired-pages=...`, `nvidia-smi --query-remapped-rows=...`.
These commands are also observational/query actions: `nvidia-smi dmon ...`, `nvidia-smi nvlink --status`, `nvidia-smi nvlink --errorcounters`.
`dcgmi diag ...` is a test action (active workload, not read-only).
Exact field support depends on version and target. **[observed]** <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>

### Never silently change certification state

- **[observed]** `nvidia-smi -e` changes ECC mode, and the change applies after reboot.
  `-p` clears ECC counts and requires root.
  `-r` resets GPU(s) and requires quiescing all users.
  NVIDIA does not recommend GPU reset for production and does not guarantee it.
  Depending on platform/NVLink/FM state, a reset may require peer GPUs. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[observed]** These actions modify device state: MIG enable/disable, instance creation/destruction, and clock locks/resets.
  Power-limit changes and temperature-target changes also modify device state.
  These actions may require privilege or reset. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/getting-started-with-mig.html>
- **[inference]** Keep N07’s certification implementation read-only for device configuration.
  As a routine check, never run `-e`, ECC counter reset, or `-r`.
  As a routine check, never run MIG setters, `-lgc`/`-lmc`, `-pl`, or `-gtt`.
  Also never run clock resets, NVLink counter resets, firmware update, or a power-profile setter as a routine check. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** If a GPU needs recovery, record it and fail/warn the relevant check.
  Then hand off the printed recovery action to an authorized maintenance procedure.
  That procedure needs tenant drain and operator approval.
  Certification is evidence collection, not automatic repair. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

## 11. Local rack-bench evidence and precise boundary

- **[observed]** The GPU audit in this checkout uses `nvidia-smi -q -x` and stable UUID keys.
  It extracts ECC, MIG mode, VBIOS/GSP/SBT/SFW/FMC, clocks, and power limits.
  It also extracts temperature and utilization fields.
  It treats unsupported fields as null/unverified. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L8-L36> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L40-L90>
- **[observed]** The local audit only takes an instantaneous thermal sample.
  It labels that sample “no idle qualification or profile grading”.
  It is not an active stress test. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L84-L90>
- **[observed]** Local `gpu.io_locality` queries `nvidia-smi topo` capability/topology.
  It explicitly says that it is passive, not an I/O test. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L93-L128>
- **[observed]** The project README lists the intended GPU bench checks.
  They are GEMM/FP4/FP8/FP16/FP32 throughput, memory bandwidth, NVLink bandwidth, and SM clock stability under load.
  The present task’s boundary excludes east-west fabric performance.
  The boundary keeps per-GPU NVLink health. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L320-L325> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/README.md>
- **[inference]** A useful implementation split has three parts.
  Audit gathers read-only inventory and lifetime RAS/configuration.
  `bench gpu` runs measured and time-boxed compute/memory/power checks plus before/after health telemetry.
  `smoke gpu` owns longer burn-in.
  Do not relabel audit metadata as bench performance evidence. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L159-L165> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L320-L325> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L484-L491>

## 12. Why books are insufficient; source priority

1. **[inference]** Gregg is the best general diagnostic method book.
   It predates the GB300 launch ecosystem.
   It cannot specify current DCGM support tables, Blackwell plugin bugs, GB300 NVL profile behavior, or CLI syntax.
   Check release notes and matched DCGM docs. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>
2. **[inference]** PMPP teaches CUDA architecture and coding.
   It does not teach vendor RAS counters, GPU recovery actions, platform firmware compatibility, or qualified thresholds.
   NVIDIA’s current programmer and management docs take precedence on those claims. <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
3. **[inference]** DCGM is a broad system-readiness suite.
   It is not comprehensive device diagnosis and not a repair/RMA tool.
   NVIDIA explicitly says so.
   OEM/NVIDIA field diagnostics and RMA process documents become primary for suspected device fault escalation. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/hw-field-diag/index.html> <https://docs.nvidia.com/deploy/rma-process/index.html>
4. **[inference]** Current docs are mutable “latest” pages.
   Pin each certificate to the installed DCGM, driver and firmware versions.
   Keep the matching release notes/document snapshot.
   The `nvidia-smi` command-line guide warns that it does not guarantee backward-compatible output. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>
5. **[inference]** Peer-reviewed GPU fault and SDC papers are superior sources for mechanisms, prevalence and statistical limits.
   They generally do not define current safe command semantics or a site acceptance limit for a product.
   Use them to describe what a two-hour screen cannot prove.
   Use product docs for the executable procedure. <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>

## 13. Ranked reading sequence (task-based, no prerequisites)

1. **[inference] Gregg, *Systems Performance*, 2e:** read the methodology/USE, observability and benchmarking chapters.
   Focus on controlled workload, saturation/errors, deltas, distributions and experimental confounders.
   This book is the diagnostic reasoning spine. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>
2. **[inference] NVIDIA DCGM Diagnostics guide + `dcgmi diag` reference:** read the current suite levels and plugin-specific failures/parameters.
   Also read JSON output, runtime prerequisites, and resource warnings.
   Then read current release notes back to the specific GB300 support addition and later fixes. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>
3. **[inference] NVIDIA `nvidia-smi` manual + NVML API + GPU Operational Events:** read ECC, retirement, row remapper, and XID/recovery action.
   Also read performance reasons, temperatures/power, MIG, and `nvlink` sections.
   Record live driver `--help-query-*`, because the CLI and fields change. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/deploy/nvml-api/index.html> <https://docs.nvidia.com/deploy/gpu-operational-events/latest/>
4. **[inference] CUDA Programming Guide, Best Practices, cuBLAS docs:** read only the sections that the bench’s correctness kernel needs.
   These sections cover the determinism/tolerance contract, API errors, synchronization, and workload arithmetic. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/> <https://docs.nvidia.com/cublas/index.html>
5. **[inference] PMPP 4e:** read selected chapters on execution/memory hierarchy, performance and implementation.
   It is a resource for engineers who write tests, not a gate for operators. <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0>
6. **[inference] Compute Sanitizer + Nsight Systems/CUPTI (as needed):** use the sanitizer for development correctness.
   Use tracing for unexplained runtime/driver/kernel timeline behavior.
   Use tracing only when privileges and certification policy allow. <https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html> <https://docs.nvidia.com/nsight-systems/UserGuide/index.html> <https://docs.nvidia.com/cupti/>
7. **[inference] NVIDIA Field Diagnostic / RMA docs:** use them for escalation only, not as routine two-hour bench instructions. <https://docs.nvidia.com/deploy/hw-field-diag/index.html> <https://docs.nvidia.com/deploy/rma-process/index.html>

## 14. O'Reilly supplement: edition checks and new measurement reading

### 14.1 Edition and format decisions

[observed] The source pass checks ten catalog records against public evidence.
O'Reilly access fails.
Full text does not form the evidence base for this supplement.
[Complete supplement](oreilly.md) · [Source notes](oreilly/README.md).

[observed] InformIT confirms Gregg's second edition and 928 pages.
Its copyright field gives 2021.
Gregg's author page identifies the edition as 2020.
Keep publication and copyright fields separate.
[Publisher](https://www.informit.com/store/systems-performance-9780136821649) · [Source note](oreilly/gregg2.md).

[inference] Keep Gregg 2e rather than require both Gregg editions.
The first-edition note confirms durable methods.
It does not change this brief's preferred edition.
[Edition comparison](oreilly/gregg1.md).

[observed] PMPP 4e remains the verified architecture reference in this pass.
The note corrects the second-edition product identifier to 9780124159921.
The supplied fourth-edition catalog identifier has an unverified format relationship.
Later-edition status remains unverified.
This pass does not prove that 4e is the latest edition.
[Edition evidence](oreilly/pmpp.md).

### 14.2 New test-author reference

[observed] Fregly's public companion lists twenty chapters and a November 2025 publication statement.
Its checklist gives matched inputs, warmup, event timing, independent output checks, and raw artifacts.
[Companion](https://github.com/cfregly/ai-performance-engineering) · [Checklist](https://raw.githubusercontent.com/cfregly/ai-performance-engineering/main/docs/appendix.md).

[inference] Add Fregly's AI Systems Performance Engineering as practical GPU measurement reading for test authors.
Use chapters 6–12 for kernel/memory topics.
Use chapters 13–14 for framework/compiler topics.
Keep Gregg for general methods, current NVIDIA guides for RAS and platform support, and PMPP for architecture.
The public companion does not establish verified full-book procedures or measured GB300 diagnostic coverage.
[Source assessment](oreilly/fregly.md).

[inference] Do not copy clock, power, MIG, persistence, OS tuning, or recovery changes into `bench gpu`.
Use approved active workloads without configuration changes.
Require exclusive allocation and approved power/cooling policy.
Keep living companion revision information separate from book-edition information.
[Safety contract](docs/gpu-bench-research.md) · [Source limits](oreilly/fregly.md).

### 14.3 Optional sources and gaps

[inference] Cook, Professional CUDA C, CUDA by Example, and Python/CUDA supply optional implementation topics.
Bondi supplies optional requirements and test-planning methods.
Motta remains pending because this pass cannot verify its contents.
None replaces the current operational references or supplies universal GB300 acceptance rules.
[Source decisions and complete notes](oreilly.md).

## Sources

- **Kept — [observed]** Brendan Gregg, *Systems Performance*, 2e book page (<https://www.brendangregg.com/systems-performance-2nd-edition-book.html>).
  It is the source for the ranked methodology book and TOC/edition.
- **Kept — [observed]** Gregg USE method (<https://www.brendangregg.com/usemethod.html>).
  It gives a practical device-resource diagnostic method.
- **Kept — [observed]** NVIDIA DCGM Diagnostics guide (<https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>).
  It documents plugin behavior, failure modes, parameters and limitations.
- **Kept — [observed]** DCGM CLI reference (<https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>).
  It documents exact run-level, selector, timeout and output semantics.
- **Kept — [observed]** DCGM release notes (<https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>).
  It documents GB300-specific support and later compatibility fixes.
- **Kept — [observed]** NVIDIA `nvidia-smi` guide (<https://docs.nvidia.com/deploy/nvidia-smi/index.html>).
  It documents current query semantics, RAS, row remap, and ECC.
  It also documents clocks, power/thermal, MIG and NVLink CLI.
- **Kept — [observed]** NVIDIA GPU Operational Events (<https://docs.nvidia.com/deploy/gpu-operational-events/latest/>).
  It documents detailed event severity and recovery semantics beyond numeric XID shorthand.
- **Kept — [observed]** NVIDIA MIG User Guide (<https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/>) and Fabric Manager guide (<https://docs.nvidia.com/datacenter/tesla/fabric-manager-user-guide/index.html>).
  They document product/system support and configuration side-effects.
  They also show non-universal MIG/NVLink behavior.
- **Kept — [observed]** NVIDIA CUDA Programming Guide, Best Practices, cuBLAS, and Compute Sanitizer docs (<https://docs.nvidia.com/cuda/cuda-c-programming-guide/>; <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>; <https://docs.nvidia.com/cublas/index.html>; <https://docs.nvidia.com/compute-sanitizer/ComputeSanitizer/index.html>).
  This entry also keeps Nsight Systems, Nsight Compute and CUPTI docs (<https://docs.nvidia.com/nsight-systems/UserGuide/index.html>; <https://docs.nvidia.com/cuda/nsight-compute/index.html>; <https://docs.nvidia.com/cupti/>).
  They are the primary software test and tracing references.
- **Kept — [observed]** Elsevier PMPP 4e publisher entry (<https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0>).
  It confirms book identity and the architecture-oriented role.
- **Kept — [observed]** NVIDIA SDC modeling study (<https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>).
  It supports an important limit.
  Finite correctness checks cannot establish an SDC-free device.
- **Kept — [observed]** rack-bench local GPU audit and project contract (<file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py>; <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md>; <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/research.md>).
  They give precise local evidence for current passive probes, project policy and scope.
- **Dropped — [inference]** Generic GPU benchmark roundups, unaffiliated tuning blogs, cloud-provider claims and forum anecdotes.
  They lack authority for GB300 RAS semantics or certified universal limits. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **Dropped — [inference]** NCCL, NVBandwidth and multi-node collective performance suites as GPU-quality canon.
  They test communication paths outside N07.
  The exception is the narrowly retained per-GPU NVLink health query. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/README.md>

## Gaps

- **[observed]** Public DCGM pages and release notes document specific GB300/B300 device IDs and support additions.
  The local evidence examined does not include a complete bill of materials for the rack.
  It also does not include the exact module revision or a driver/firmware compatibility matrix.
  It also does not include OEM-qualified thresholds. <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/research.md>
- **[inference]** Before certifying, verify the actual HGX GB300 NVL72 SKU (including Galaxy/Bianca variant).
  Also verify the NVIDIA driver branch, CUDA runtime, DCGM package lane/version, NVSDM, and platform firmware.
  Check them against the official support matrix of the deployed system.
  Do not infer support from “Blackwell” alone. <https://docs.nvidia.com/datacenter/dcgm/latest/installation.html> <https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html>
- **[observed]** `nvidia-smi` output/field exposure varies by version.
  DCGM plugin presence depends on the host.
  This research has no command output from the actual certified rack.
  So it cannot show which fields/plugins are operational there. <https://docs.nvidia.com/deploy/nvidia-smi/index.html> <https://docs.nvidia.com/datacenter/dcgm/latest/reference/command-line-reference/dcgmi/dcgmi-diag.html>
- **[inference]** First, run read-only field-discovery and timed pilot diagnostics on one representative rack GPU.
  Record actual durations, observed contention, N/A fields, and plugin errors.
  Record the exact DCGM/driver versions.
  Revise the two-hour schedule from these measurements, not from published single-A100 runtimes. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **[observed]** The sources cited here give no universal public performance threshold for all GB300-class systems.
  This gap covers all workload precisions and power profiles. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- **[inference]** The profile owner must select an authoritative SKU-specific performance limit.
  Alternatively, the owner must derive a reproducible rack baseline with an explicit statistical rule.
  Until then, publish measured values and mark absolute performance certification SKIP, not PASS. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>
- **[inference]** N07 does not establish defect prevalence or the expected SDC rate.
  It also does not establish what a two-hour negative sample implies statistically.
  Those answers require the primary research of the sibling GPU reliability study and an explicit confidence model. <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>
- **[inference]** MIG/NVLink coexistence is platform- and generation-specific.
  Use the exact GB300 NVL72 system guide to set policy for the deployed partition profile.
  Without that guide, certify the observed device state.
  Do not assert unsupported MIG/NVLink compatibility. <https://docs.nvidia.com/datacenter/tesla/fabric-manager-user-guide/index.html> <https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/supported-gpus.html>
- **[observed]** This research makes no live measurements on the Chennai rack.
  All runtime and support claims are documentation claims, not rack observations. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/README.md>
- [observed] The O'Reilly supplement has access, TOC, edition, and format gaps.
  Companion evidence does not establish full-book review.
  [Exact source gaps](oreilly.md#gaps).

