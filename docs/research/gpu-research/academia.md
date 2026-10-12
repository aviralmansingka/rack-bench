# GPU failures in field studies: evidence and two-hour screening
Research date: 2026-10-11. All claims below carry a source URL.

## 1. Executive answer

### 1.1 What research supports
- [observed] Field studies show many different kinds of accelerator failures in production. These include HBM ECC events, recovery exhaustion, GPU control/firmware faults, and device disappearance/off-bus.
  They also include NVLink device errors, driver/software mismatch, system integration, thermal, power, workload, and manufacturing-batch effects.
  The studied cohorts differ in generation and definition. Their event frequencies do not estimate GB300 failure rates ([Delta A100/H100 study](https://arxiv.org/html/2503.11901v3); [Titan lifetime study](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf); [Tsubame multi-generation study](https://www.osti.gov/servlets/purl/2204463)).
- [inference] For a two-hour device-level acceptance bench, capture baseline state and historical counters.
  Then run a vendor-supported DCGM diagnostic for memory integrity, compute correctness, memory bandwidth, and controlled sustained power/stress.
  Continuously collect per-GPU ECC/XID/temperature/power/clock/throttle telemetry.
  Then rerun state/counters and report each GPU independently.
  These checks can reveal present defects and weak performance. They cannot forecast fleet failure rates or prove that rare SDC is absent.
- [observed] NVIDIA describes DCGM Diagnostics as deployment-readiness tests. NVIDIA says they are not comprehensive hardware diagnostics or a replacement for field diagnosis/RMA tooling ([DCGM Diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] Keep collection status separate from quality assessment.
  A measurement counts as collected when the declared probe runs and produces attributable data.
  This rule applies whether or not the data indicates failure.
  Keep measurements from failed devices.
  A separate assessment may compare collected values with thresholds.
  A “no event in two hours” result does not certify reliability ([rack-bench contract and stages](../../../README.md#L7-L15)).

### 1.2 Research date and evidence policy
- [observed] This brief follows the requested date and claim markers.
  It separates primary studies, official NVIDIA documentation, and local repository evidence from interpretations.
- [inference] Do not pool study denominators.
  A system-level failure share, per-GPU MTBE, per-GPU-hour event rate, and job-failure probability answer different questions.

## 2. What populations and generations establish

### 2.1 Delta: modern A100 and H100 operational logs
- [observed] Patke et al. analyze Delta at NCSA.
  The study covers 1,056 GPUs: 448 A100 40-GB GPUs and 608 H100 96-GB GPUs in GH200 nodes.
  The study spans 2.5 years and totals 11.7 million GPU-hours.
  The A100 cohort contributes 9.6M GPU-hours / 895 days. The H100 cohort contributes 2.1M / 146 days ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] The authors select high-impact XID/recovery events from system logs.
  They correlate Slurm job failures with those events.
  They use DCGM utilization samples at one-minute granularity.
  The selected events do not include every GPU fault.
  The authors exclude XID 13 and 43 because these usually indicate user-job errors ([paper methodology](https://arxiv.org/html/2503.11901v3)).
- [observed] The authors report 14,821 selected critical errors on A100 and 1,821 on H100.
  System-wide MTBE measures 1.4 and 1.9 hours, respectively.
  Per-node MTBE measures 154 and 292 hours, respectively.
  These values describe system event rates across the studied nodes.
  They do not give the probability that one GPU fails during a short test ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] The cohorts differ in exposure, GPU count, maturity, and hardware packaging.
  The authors caution against direct comparison with older Titan/Summit systems because of the generation gap ([paper](https://arxiv.org/html/2503.11901v3)).

### 2.2 Titan: K20X board lifetimes and batch-specific pathology
- [observed] The paper reports 18,688 NVIDIA GPU-accelerated nodes/GPUs in Titan's Cray XK7.
  The lifetime analysis covers over 100,000 collective GPU-years in a six-year productive epoch.
  It focuses on units installed after the early rework period.
  The analysis uses inventory and DBE/off-the-bus logs ([Ostrouchov et al.](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf)).
- [observed] The paper reports three major rework cycles for Titan.
  It reports a late-2016 failure surge and replacement of roughly 11,000 GPU boards.
  The analysis links this unusual mode to silver-sulfide corrosion of a resistor on one GPU circuit-board batch.
  The analysis does not link it to a general GPU-chip defect (paper introduction, p. 1, and conclusion, p. 12; [Ostrouchov et al. PDF](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf)).
- [observed] The paper cites earlier Titan DBE MTBE around 160 hours.
  GPU memory accounts for 86% of those events. The register file accounts for the remainder.
  The paper links early Titan “off the bus” events to a system integration problem and reports its fix ([Ostrouchov et al.](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf)).
- [observed] Titan’s survival analysis identifies hazard differences associated with location and cooling.
  It also identifies workload and scheduling influences.
  The investigators report no matching extreme batch failure mode at similar-component facilities ([Ostrouchov et al.](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf)).
- [inference] Titan shows why a rack screen must compare same-rack GPU peers.
  The screen must also capture placement and thermal context.
  Do not project Titan’s K20X rate or resistor failure mode to GB300.

### 2.3 Summit and LLNL-related multi-GPU evidence
- [observed] Summit DBE work studies 27,648 Tesla V100 GPUs with HBM2.
  The study reports that prior-DBE GPUs face greater recurrence.
  Placement and workload matter.
  In the general population, DBEs correlate with short- and long-term high power modes but not significantly with higher temperature.
  Oles et al. publish this study in *Proceedings of the 38th ACM International Conference on Supercomputing* in 2024.
  The primary ORNL publication abstract appears in the linked [record](https://impact.ornl.gov/en/publications/understanding-gpu-memory-corruption-at-extreme-scale-the-summit-c).
- [observed] Taherin et al. study Tsubame-2 (K20X, 3 GPUs/node) and Tsubame-3 (P100, 4 GPUs/node).
  The study records 897 and 338 system failure records over stated periods.
  GPU category accounts for 44.37% of Tsubame-2 recorded failures and about 28% of Tsubame-3 recorded failures.
  These shares cover categorized system failure records. They are not GPU failure probabilities per device-hour ([LLNL-hosted paper](https://www.osti.gov/servlets/purl/2204463)).
- [observed] Tsubame-3 software failures form 50.59% of failure records.
  GPU-driver problems account for about 43% of software failures.
  The records include an unknown-cause category and limits from operational classification ([paper](https://www.osti.gov/servlets/purl/2204463)).
- [observed] The Tsubame study reports a nonuniform distribution of GPU failures within nodes.
  About 70% of listed GPU failures on Tsubame-2 involve simultaneous multi-GPU events.
  Multi-GPU involvement is uncommon on Tsubame-3: 7.4% of failures involve >1 GPU.
  System hardware, generation, operations, and failure definitions differ ([paper](https://www.osti.gov/servlets/purl/2204463)).
- [inference] These studies show the value of per-device outcomes over a rack-wide aggregate PASS.
  An average can hide one weak GPU.
  Software stack compatibility also affects readiness.

## 3. Mechanisms and field-study rates

### 3.1 ECC, HBM errors, and their limits
- [observed] In the Delta study, the system automatically corrects individual single-bit ECC events.
  The study data does not log those events.
  The study treats DBEs and consecutive single-bit errors as uncorrectable events.
  Those events trigger recovery paths ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] Delta records 34 inferred uncorrectable ECC events on A100 (per-GPU MTBE 283,271 hours).
  Delta records 24 on H100 (per-GPU MTBE 88,768 hours).
  The authors calculate per-GB MTBE of ~11.33M hours A100 versus ~8.52M H100.
  They hypothesize that the lower H100 memory resilience relates to its larger capacity.
  Voltage/stack/thermal explanations remain hypotheses, not known causes ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] These denominators cover operational GPU-hours and memory capacity within one site.
  They do not cover controlled device tests.
  GPU workload and configuration matter.
  Do not convert the H100 estimate into a GB300 expected rate ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] Delta observes H100 row-remapping recovery (RRE) success probability 0.59.
  The study reports 33% of row-remapping events as failures (RRF).
  Overall recovery/containment alleviates impact in 92% of uncorrectable-event paths.
  Error containment can still terminate a job.
  Containment does not equal data correctness or uninterrupted workload ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] NVIDIA says Ampere+ row remapping replaces degraded DRAM rows with spare rows.
  The remap takes effect after GPU reset and persists.
  NVIDIA's Blackwell RMA guidance adds HBM channel repair in some recovery attempts.
  It defines remap-failure conditions and reporting through NVML/nvidia-smi/SMBPBI ([row remapping documentation](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/row-remapping.html); [RMA thresholds](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/rma-policy-thresholds-for-row-remapping.html)).
- [inference] In a brief bench, record pending page retirement and row-remap pending/failure.
  Record remap counts/spares where the driver exposes them.
  Record volatile and aggregate ECC counters before/after.
  Do not intentionally induce DBE or claim repair without reboot.
  A clean memory-pattern test does not verify spare-row exhaustion history.

### 3.2 XIDs and hardware/control faults
- [observed] Delta selects XID 31 MMU, 48 DBE, 63 row-remap event, and 64 row-remap failure events.
  Delta also selects 74 NVLink, 79 GPU off bus, 94 contained memory, and 95 uncontained memory events.
  The study further selects 119/120 GSP and 122/123 PMU SPI events.
  XID counts and interpretations remain specific to that driver/logging cohort ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] The study reports 3,857 GSP errors and 10 off-bus events on A100.
  It reports three GSP errors and no observed off-bus or NVLink errors on H100.
  The H100 data covers its shorter 146-day period.
  The authors attribute improvements plausibly to packaging/driver changes.
  They cannot prove causality from observational data ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] Delta associates off-bus behavior with a driver that cannot reach the GPU across the system bus.
  Prior work links such failures to loose GPU-board connection/contact issues and thermal cycles.
  An XID is a diagnostic signal, not necessarily a root-cause verdict ([paper](https://arxiv.org/html/2503.11901v3)).
- [observed] The study reports that 88% of A100 PMU SPI errors propagate to MMU errors.
  It reports that 90% of those MMU errors associate with job failure.
  The authors report 98% job-failure probability for observed PMU SPI events.
  Sample sizes and study-specific job association constrain these percentages ([paper](https://arxiv.org/html/2503.11901v3)).
- [inference] Capture kernel journal and driver XIDs around the run.
  Distinguish pre-existing from new counters.
  Preserve raw event text.
  Classify unknown XIDs as evidence.
  Do not silently suppress them.

### 3.3 Silent data corruption: what ECC cannot guarantee
- [observed] SDC is, by definition, incorrect computation without a corresponding hardware indication.
  An ECC counter-only monitor cannot detect an error that neither ECC nor telemetry flags ([OCP SDC whitepaper](https://www.opencompute.org/documents/sdc-in-ai-ocp-whitepaper-final-pdf)).
- [observed] The OCP whitepaper discusses model/training-level consequences.
  It notes that fault propagation depends on architecture and workload.
  No generic application-level detector covers all silent corruptions ([OCP SDC whitepaper](https://www.opencompute.org/documents/sdc-in-ai-ocp-whitepaper-final-pdf)).
- [observed] Delta shows bitwise data write/read checks in diagnostic workloads.
  Delta notes that error containment may catch H100 uncorrectable memory errors.
  Containment still causes the affected job to fail ([Delta study](https://arxiv.org/html/2503.11901v3)).
- [inference] Include deterministic known-answer tests: integer/FP32/FP64 or applicable low-precision GEMM against trusted references.
  Include repeatability, checksums, and memory write/read patterns.
  Compare per GPU.
  Do not rely only on fleet throughput.
  This detects some execution and data-path faults, not arbitrary SDC in untested operations.
- [observed] Published fault-injection modeling work explicitly separates low-level fault manifestation from propagation to application output.
  Using only one level can misestimate application SDC ([NVIDIA Research](https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model)).

### 3.4 Thermal, power, clocks, and performance degradation
- [observed] Titan’s large observational cohort links GPU lifetimes to heat dissipation.
  The study correlates lifetimes with cooling layout and job scheduling.
  Summit’s V100 DBE study finds power-mode associations.
  It finds no significant general-population correlation with higher temperature.
  These findings conflict only superficially.
  The studies examine distinct mechanisms, workloads, populations, and outcomes ([Titan study](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf); [Summit study](https://impact.ornl.gov/en/publications/understanding-gpu-memory-corruption-at-extreme-scale-the-summit-c)).
- [observed] NVIDIA DCGM diagnostics include targeted power and stress tests.
  They monitor temperature violations, XIDs, and memory errors.
  Targeted power fails if it cannot reach the configured fraction of target power.
  The tests support temperature ceilings ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] Measure clock, power draw/limit, temperature, and throttle-reason state throughout load.
  Compare achieved sustained performance and power per GPU to identical SKU peers.
  Compare them to declared measured thresholds.
  A snapshot of clocks/power limits is configuration evidence, not proof under load.
- [inference] Do not impose H100 thermal thresholds on GB300.
  Use device-reported slowdown/shutdown thresholds and GB300-specific supported DCGM/firmware data.
  Record unsupported metrics as skip with reason.

### 3.5 Driver, firmware, and workload interaction
- [observed] The Tsubame-3 study attributes approximately 43% of software failure records to GPU-driver-related problems.
  The records include frequent driver updates/upgrades and software-driver mismatch.
  The study warns that root causes are often ambiguous ([LLNL-hosted paper](https://www.osti.gov/servlets/purl/2204463)).
- [observed] DCGM Diagnostics includes NVML/CUDA access, software conflicts, driver and permission checks as deployment diagnostics ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] Audit exact driver, CUDA, DCGM, firmware, and VBIOS/GSP versions.
  Compare them with an approved compatibility manifest.
  Then execute kernels from the deployed runtime.
  A compatible version string alone does not show measured execution success.

## 4. Two-hour bench design supported by evidence

### 4.1 Proposed sequence and evidence returned
- [inference] **0–10 min: baseline and identity.**
  Capture UUID/serial/model/memory, driver/runtime/DCGM versions, and ECC/MIG mode.
  Capture clocks/power limits, thermal thresholds, and pending retire/remap status.
  Capture ECC counters, the XID/kernel log window, and per-GPU NVLink health.
  Validate all expected GPU identities.
  A missing/duplicate device is a fail, not a skipped benchmark.
- [inference] **10–20 min: deployment and correctness preflight.**
  Run supported DCGM level 1/readiness checks on each GPU.
  Run kernel/runtime load and short deterministic known-answer compute on each GPU.
  Record each return code and output.
  No vendor declaration substitutes for actual execution.
- [inference] **20–65 min: memory and compute integrity.**
  Run DCGM diagnostic/memory test patterns plus compute diagnostic.
  Capture per-device mismatches, CUDA errors, XIDs, ECC deltas, and performance.
  Ensure non-overlapping exclusive devices.
  Do not permit tenant jobs to contaminate test results.
- [inference] **65–100 min: sustained power/thermal and clocks.**
  Run targeted power or targeted stress at a profile-defined target.
  Run it concurrently only if platform limits and rack power budget permit.
  Monitor achieved watts, clocks, temperature, throttle reasons, and performance at regular intervals.
  Stop safely on vendor thresholds.
  Preserve a partial result as failure/aborted, not pass.
- [inference] **100–115 min: measured HBM bandwidth and NVLink per-GPU health.**
  Run per-GPU memory bandwidth measurement.
  Inspect NVLink health/error deltas.
  Omit collective/all-reduce performance because east-west fabric is out of scope.
  NVLink stays only for device/link health as requested.
- [inference] **115–120 min: final snapshot and report.**
  Re-read counters and XIDs.
  Report deltas, benchmark values, telemetry completeness, tool versions, thresholds, exclusions, and reasoned skips.
  Individual GPU rows plus rack summary prevent a high performer masking a low outlier.
- [observed] DCGM provides parseable JSON output and configurable test duration.
  Its diagnostic plugin checks large matrix multiplies and framebuffer read/write correctness.
  It also checks standard errors, XIDs, and temperature violations.
  The docs show a five-minute default diagnostic example ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [observed] DCGM level-4 memtest documentation describes address/walking-bit, moving inversion, random-pattern, bit-fade, and memory-stress tests.
  On an A100 reference, several tests take seconds to minutes.
  Default memory stress alternates selected tests for ten minutes.
  That timing is not a GB300 runtime guarantee ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] A full DCGM level 4 is a candidate only after timing and compatibility validation on GB300.
  Selecting a subset plus runtime headroom is safer than assuming full-suite runtime scales linearly across 72 GPUs.

### 4.2 Feasibility and important caveats
- [observed] DCGM diagnostics provide levels and individual plugins.
  Official docs say they are not comprehensive diagnostics.
  The docs say they do not replace vendor field diagnosis ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] For 72 GPUs, run the supported tests concurrently where safe.
  Enforce rack-level power/cooling envelopes.
  Avoid multiplying a single-GPU test time by 72.
  Contention, synchronization, platform firmware, and thermal behavior can change results.
  Measure GB300 rack timing empirically.
- [inference] A two-hour GPU bench can detect a DOA GPU.
  It can detect reproducible memory/compute mismatch, counter increments, and missing links.
  It can detect throttling under the tested load and relative performance outliers.
  It cannot show long-term component lifetime.
  It cannot exercise every address/operation/temperature or prove that rare SDC is absent.
- [inference] Preserve failure evidence.
  Do not automatically reset devices during evidence collection.
  Row remapping may require reset to take effect.
  A reset can alter state and erase useful before/after context.

## 5. Statistical limits of short no-event tests

### 5.1 Zero observed failures is weak rate evidence
- [calculated] An ideal homogeneous Poisson event model assumes a constant independent event rate and complete detection.
  Zero events in exposure E give a one-sided 95% upper rate bound of approximately 3/E.
  The bound uses -ln(0.05) ≈ 2.996.
  This “rule of three” assumes stationarity and perfect event detection.
  The derivation follows the exact zero-count Poisson probability: P(N=0|λE)=exp(-λE), set equal to 0.05, yielding λ=-ln(0.05)/E.
  The derivation implies no empirical GPU source ([NIST/SEMATECH e-Handbook, Poisson distribution](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366j.htm)).
- [calculated] If the bench observes all 72 GPUs for 2 hours, total exposure equals 144 GPU-hours.
  Zero events yield an approximate upper 95% bound of 3/144 = 0.0208 events/GPU-hour.
  This equals one event per 48 GPU-hours.
  Field studies report tens of thousands of GPU-hours per uncorrectable event.
  The two-hour bound is far too weak to substantiate those rates ([Delta study](https://arxiv.org/html/2503.11901v3)).
- [calculated] At the single-device level, two event-free hours give an upper bound of 1.5 events/GPU-hour under the same model.
  A clean short bench therefore says little about rare field failures.
- [inference] The calculation is illustrative, not a GB300 reliability estimate.
  Shared rack faults violate independence.
  Failure rates are not necessarily stationary.
  Induced diagnostics differ from production workloads.
  Logs may miss silent errors.

### 5.2 Exposure and test coverage are distinct
- [observed] Delta’s 11.7M GPU-hours provide operational exposure.
  The study restricts error extraction to selected logged events.
  Proprietary/inconsistent driver logging can affect that extraction ([Delta study](https://arxiv.org/html/2503.11901v3)).
- [inference] Report both exercised duration and measured work.
  Report GPU-hours, bytes/addresses touched, pattern count, and compute operations/precision.
  Report achieved bandwidth/power, telemetry sampling interval, and monitor coverage.
  “Two hours passed” without workload coverage is not meaningful evidence.

## 6. Practical checks and grading proposals

### 6.1 Device identity, readiness, and software
- [observed] The repository audit currently reads model, serial, UUID, architecture, and framebuffer capacity in `gpu.inventory` (`rack_bench/audit/gpu.py:40-50`).
  It collects ECC and MIG mode in `gpu.ecc` and `gpu.mig` (`rack_bench/audit/gpu.py:53-59`).
  It collects firmware versions at lines 62-70 ([local evidence](../../../rack_bench/audit/gpu.py#L40-L70)).
- [observed] Existing code gathers clocks, max SM clock, power-limit/readings, and thermal fields (`rack_bench/audit/gpu.py:72-90`).
  The code explicitly records thermals as a single instantaneous sample.
  The code does no idle qualification or profile grading ([local evidence](../../../rack_bench/audit/gpu.py#L72-L90)).
- [observed] The local profile schema declares expected GPU model/count/memory, ECC/MIG states, and NVLink link count.
  `bench.gpu` presently declares GEMM FP8 and memory-bandwidth percentages (`docs/profile-schema.md:38-50,70-79`) ([local evidence](../../profile-schema.md#L38-L50)).
- [inference] Reuse the audited UUID identity in the proposed bench-gpu.
  Add dynamic DCGM tests.
  Treat unsupported counter fields as explicit skip with reason, not a fabricated zero.

### 6.2 Error, ECC, row-remap and SDC evidence
- [inference] Distinguish volatile versus lifetime totals in baseline and post-run counter deltas where the driver exposes them.
  Fail on new uncorrectable ECC, row-remap failure, memory mismatch, or fatal XID.
  Also fail on unexplained device disappearance.
  Warn/record correctable ECC increments with threshold and context.
  Do not erase them.
- [inference] Any pending row remap means the memory repair may not yet be effective.
  Report “pending repair”.
  Require a controlled reset/maintenance workflow.
  Do not mark it fully remediated within the bench.
- [inference] Include exact arithmetic/reference checks and byte-for-byte memory checks.
  State that these checks cover tested operations only.
  Use repeated independent seeds and checksums.
  Check NaN/Inf as a useful but incomplete signal.
- [observed] NVIDIA documents row remap as reset-activated and persistent.
  Blackwell support and thresholds need GPU-generation-specific interpretation ([NVIDIA row remapping](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/row-remapping.html); [RMA thresholds](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/rma-policy-thresholds-for-row-remapping.html)).

### 6.3 Throttling, clocks, and relative performance
- [inference] Compare measured per-GPU FP8 GEMM and HBM bandwidth against an explicit GB300 profile and peer distribution.
  Record absolute rates and percentage-of-target.
  The profile schema already has these two threshold slots.
  Research does not provide a defensible universal GB300 percentage threshold.
- [inference] During stress, record actual clock/power/temperature and throttle-reason time series.
  A low benchmark score without telemetry is a failure signal but a weak diagnosis.
  Achieved clocks below expected values during an active power/thermal cap show the likely constraint.
- [observed] DCGM's targeted stress/power plugins provide adjustable target thresholds.
  The plugins monitor thermal/errors.
  DCGM output can be JSON ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

### 6.4 NVLink health only, not fabric benchmark
- [inference] Read per-GPU NVLink state and link error/recovery counter deltas before and after compute stress.
  Report missing/unhealthy links and new errors.
  This is device-level link health, not east-west bandwidth or collective performance.
- [observed] The Delta study defines NVLink errors as link integrity/connection issues.
  These issues can reduce throughput and need reset/SRE intervention.
  A100 logs 1,922 errors.
  H100 logs none during its shorter study window ([Delta study](https://arxiv.org/html/2503.11901v3)).

## 7. Implications for `bench gpu`

### 7.1 Recommendation
- [inference] Make the two-hour category a measured screen, not burn-in.
  The screen includes baseline + supported readiness diagnostics + deterministic correctness + memory test.
  It adds sustained power/stress + HBM bandwidth + per-GPU telemetry and post-state comparison ([DCGM diagnostic goals and test plugins](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] Store per-GPU UUID, test/config version, start/end timestamps, measurements, counter deltas, thresholds, and status.
  Aggregate collection completeness separately from quality grading.
  Preserve measurements and failures for every device, including failed devices ([DCGM JSON output](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html); [local collection contract](../../../README.md#L7-L15)).
- [inference] Include stable signatures of test output and binary/tool versions.
  These signatures make the same GPU generation/profile reproducible ([DCGM JSON output and configurable diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
  Never call a vendor “healthy” flag alone measured certification.
- [observed] The local README defines audit as inventory/topology.
  It defines bench as a short per-component quick pass/fail.
  It defines smoke as long-duration stress.
  The GPU bench remains planned, not yet available ([README](../../../README.md#L3-L20)).

### 7.2 Failure semantics
- [inference] **Fail quality assessment:** absent/incorrect expected device; new DBE/uncorrectable ECC; row-remap failure; correctness mismatch; fatal/new XID.
  Fail also on DCGM diagnostic failure, unexpected throttle, and sustained performance below declared profile.
  Fail on NVLink health failure where the profile declares expected links ([DCGM failure conditions](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
  Keep any successfully captured measurements attached to the failed result.
- [inference] **Warn quality assessment:** corrected ECC delta, degraded but still within threshold performance.
  Also warn on thermal/power headroom concern and pre-existing historical XID.
  Warn on pending remap requiring maintenance ([NVIDIA row-remapping behavior](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/row-remapping.html)).
- [inference] **Skip with reason:** unsupported metric/plugin on GB300 driver; inaccessible counter; incompatible DCGM package.
  Also skip on unavailable trusted threshold or a test blocked by production workload or safety budget.
  Skip means not collected.
  Skip must not silently satisfy collection completeness ([DCGM plugin support and prerequisites](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] Define failure thresholds in a measured GB300 acceptance profile.
  Neither Titan K20X, Summit V100, Delta A100/H100, nor older DCGM timing/spec thresholds justify inventing GB300 rates or limits.

## 8. Sources and confidence

### 8.1 High-confidence primary sources
- [observed] Delta GPU resilience paper, full text and tables: [arXiv HTML](https://arxiv.org/html/2503.11901v3).
  It shows a strong operational dataset and methods.
  Limitations include one site, selected event classes, unequal cohort durations, and driver-log uncertainty.
- [observed] Titan GPU lifetime paper and data context: [PDF](https://christian-engelmann.de/publications/ostrouchov20gpu.pdf).
  It shows strong survival analysis and cohort history.
  The unique board batch and cooling environment affect the K20X-era cohort.
- [observed] Summit V100/HBM2 DBE study record: [ORNL publication page](https://impact.ornl.gov/en/publications/understanding-gpu-memory-corruption-at-extreme-scale-the-summit-c).
  The record gives a primary lab study summary.
  This pass does not retrieve full methods/results access.
- [observed] Tsubame / LLNL-hosted multi-generation failure study: [OSTI PDF](https://www.osti.gov/servlets/purl/2204463).
  It is primary research.
  Its failure shares are system-log category shares, not device-hour rates.
- [observed] NVIDIA DCGM Diagnostics and memory management documentation: [DCGM Diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html), [Row Remapping](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/row-remapping.html), [RMA thresholds](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/rma-policy-thresholds-for-row-remapping.html).
  The documentation gives the best available operational check semantics.
  The documentation is not independent validation of GB300 performance.

### 8.2 Sourcing confidence
- [inference] Confidence is high for the reported cohort sizes, study-defined rates, failure examples, and official DCGM test behavior.
  Confidence is medium for mechanisms inferred from observational associations.
  Confidence is low for direct applicability to GB300-class Blackwell Ultra.
  This brief does not establish field failure cohorts or public test timing for the exact rack SKU.
- [inference] This brief makes no ungrounded GB300 failure-rate extrapolation.
  Thresholds require rack/vendor-specific measured baselines and acceptance agreement.

## Gaps
- [observed] The Summit publication landing page provides abstract-level findings.
  This pass does not fetch the full paper.
  Verify effect sizes, exact denominators, and detailed model covariates from the publisher paper.
  Quote them operationally only after that verification ([ORNL record](https://impact.ornl.gov/en/publications/understanding-gpu-memory-corruption-at-extreme-scale-the-summit-c)).
- [observed] No primary field reliability study located here reports GB300 GPU-hour denominators or error rates.
  None reports row-remap exhaustion frequency or two-hour diagnostic sensitivity.
  Therefore this brief claims none.
- [observed] DCGM documentation contains A100 runtime examples and current plugin descriptions.
  It lists B300 support for NVBandwidth.
  It does not show complete GB300 NVL72 DCGM level-4 support.
  It does not show end-to-end 72-GPU runtime under rack limits ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- [inference] Validate exact GB300 SKU, driver/DCGM versions, diagnostic plugin availability, counter names, and runtime on the certification rack.
  Publish the resulting local measured thresholds and explicit unsupported-field skips.
- [observed] Public evidence does not provide an exhaustive SDC denominator for current GPU fleets.
  Short deterministic correctness workloads can reveal tested errors.
  They cannot prove absence of silent data corruption ([OCP SDC whitepaper](https://www.opencompute.org/documents/sdc-in-ai-ocp-whitepaper-final-pdf)).
