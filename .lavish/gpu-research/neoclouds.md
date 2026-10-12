# N01 — Neocloud GPU-health evidence and two-hour device screening

Research date: 2026-10-11. All claims below carry a source URL.

Claims use **[observed]** for source-reported facts, **[calculated]** for arithmetic, and **[inference]** for recommendations or conclusions.
Provider statements show a control or visibility commitment.
They do not prove a particular rack’s state.

## 1. Executive answer

### 1.1 What cloud providers actually show or promise

- **[observed]** Public neocloud documentation is uneven.
  CoreWeave publishes the strongest active screening description.
  The description names idle-node verification for silent data corruption (SDC), numerical performance regression, and thermal deficiency.
  The documented test runs 20–30 minutes hourly when idle and exercises all GPUs.
  CoreWeave does not publish test thresholds, per-device pass records, or fleet SDC rates ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).
- **[observed]** Lambda describes automated node-health checks every few minutes.
  Lambda removes failed nodes from Slurm automatically and runs remediation.
  Lambda runs background GPU diagnostics on idle capacity.
  Its Slurm console shows users per-node GPU temperature, memory, and power.
  These are service descriptions, not tenant-facing ECC/XID/row-remap history or published test outcomes ([Lambda Managed Slurm quickstart](https://docs.lambda.ai/managed-slurm/quickstart)).
- **[observed]** Runpod Instant Clusters gives a Grafana observability engine at five-second granularity.
  GPU metrics come from NVIDIA DCGM, and host metrics come from Node Exporter.
  The documented metric inventory includes ECC, remapping, and fan metrics.
  This evidence applies to Instant Clusters, not necessarily every Runpod product or a general health API ([Runpod Cluster observability](https://docs.runpod.io/instant-clusters/cluster-observability)).
- **[observed]** Modal publishes operational guidance for XID interpretation and mitigation.
  The guide includes GPU reset/drain decisions for serious ECC events.
  It is a health/troubleshooting guide.
  It does not promise customers a raw per-GPU RAS history or a pre-rental certification artifact ([Modal GPU Health](https://modal.com/docs/guide/gpu-health)).
- **[inference]** The realistic tenant baseline is workload-visible telemetry plus provider-side detection/repair.
  Raw persistent counters, screening thresholds, device identity/history, and individual screening results are usually not public.
  A rack-bench certificate must measure the rack itself.
  It must not infer health from provider SLA language.

### 1.2 Highest-value conclusion for rack-bench

- **[inference]** DCGM documents mechanisms that teams can select and schedule within a two-hour bench window.
  NVIDIA does not promise that a full-rack suite finishes within two hours.
  DCGM distinguishes passive health summaries from active tests.
  NVIDIA says online diagnostics do not provide complete field diagnostics or RMA evidence ([DCGM health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html); [DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- **[inference]** For an idle, administratively controlled rack, bench-gpu captures a per-GPU baseline and runs a short active diagnostic/memory correctness test.
  It measures comparable kernel and HBM performance under load.
  It samples throttle/clock/power and ECC/XID deltas and checks per-GPU NVLink errors.
  If the rack is not drained, mark active checks SKIP with that exact reason.
  If required permissions/driver support are absent, mark active checks SKIP with that exact reason.
  Do not call telemetry-only checks a performance PASS.

## 2. Neocloud/provider evidence catalog

### 2.1 CoreWeave: explicit idle-node SDC and regression screening

- **[observed]** CoreWeave says HPC Verification is an on-node framework.
  The framework tests hardware and driver integrity beyond passive monitoring.
  It runs automatically on idle compute nodes.

  Its first stated target is SDC that standard alerts do not trigger.
  Its second target is numerical performance regression in common deep-learning kernels in FP8, FP16, and BF16.
  Its third target is thermal deficiencies.
  It tests them with all SMs at 100% load for approximately 20 minutes ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).

- **[observed]** CoreWeave publishes an hourly cadence at the top of the hour.
  An idle node receives a 20–30 minute test that uses all GPUs and available InfiniBand resources.
  Busy nodes skip the test and retry the next hour.
  CoreWeave documents on-demand verification as approximately 35 minutes.
  On-demand verification requires an idle node ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).

- **[observed]** The tests stop when the scheduler starts customer work.
  CoreWeave documents exceptions for third-party schedulers and Pods pinned with `.spec.nodeName`.
  It also documents an exception for work that runs outside Slurm on SUNK.
  The tests are distinct from Node Health Check (NHC).
  CoreWeave describes drain/undrain behavior.
  It shows test presence through transient Pods, GPU utilization/memory metrics, and a Node Details dashboard ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).

- **[inference]** The declared test duration fits a two-hour per-category budget.
  But a rack-wide certification cannot assume CoreWeave's scheduler or receive its internal verifier artifacts.
  The public page does not quantify FP result tolerance, SDC error rate, or regression cutoff.
  It also does not quantify per-GPU outcomes, false-positive rate, or what a tenant can export.

- **[observed]** CoreWeave has a separate NCCL troubleshooting article.
  The article tells users to diagnose whether errors stay in one Pod or occur simultaneously across nodes.
  It tells users to isolate a failing node by bisection.
  It tells users to submit exact NCCL output, node names, error strings, and `ibstat`.
  Its examples include active link flap/vendor error and a down/disabled InfiniBand port ([CoreWeave NCCL error diagnosis](https://docs.coreweave.com/support/sunk/articles/what-do-nccl-errors-mean)).

- **[inference]** That NCCL guidance helps triage of a GPU/rack failure report.
  It is not a device-level GPU health test.
  Much of it concerns east-west fabric.
  This brief excludes those fabric checks except GPU NVLink health.

### 2.2 Lambda: background checks, diagnostics, and limited console telemetry

- **[observed]** Lambda Managed Slurm says continuous node health checks run on every node every few minutes.
  Lambda removes a failed node from scheduling.
  Automated remediation then attempts recovery.
  Deep GPU diagnostics and stress tests run continuously on idle capacity.
  They run in a low-priority partition that yields to customer jobs ([Lambda Managed Slurm quickstart](https://docs.lambda.ai/managed-slurm/quickstart)).

- **[observed]** Lambda says its Slurm console shows per-node GPU temperature, memory, and power.
  Lambda says it collects hardware, GPU, and scheduler telemetry.
  This quickstart does not name public ECC counters, XID history, row-remap totals, or diagnostic thresholds.
  It also does not name an API for device health ([Lambda Managed Slurm quickstart](https://docs.lambda.ai/managed-slurm/quickstart)).

- **[observed]** Lambda restricts system-level access to cluster administrators/support.
  Tenants must not assume that they can run privileged field diagnostics or change driver/Firmware configuration ([Lambda Managed Slurm quickstart](https://docs.lambda.ai/managed-slurm/quickstart)).

- **[inference]** The available evidence supports health automation and basic performance telemetry.
  It does not support a customer-verifiable device-by-device quality guarantee.
  This research does not find published GB300-specific applicability, remediation SLA by fault class, or result export.

### 2.3 Runpod: DCGM metrics for Instant Clusters

- **[observed]** Runpod states that Instant Clusters send built-in observability metrics to Grafana at five-second granularity.
  GPU metrics come from NVIDIA DCGM.
  Host metrics come from Node Exporter.
  Users need no configuration ([Runpod Cluster observability](https://docs.runpod.io/instant-clusters/cluster-observability)).

- **[observed]** The documented metric catalogue lists ECC single-/double-bit aggregate and volatile double-bit errors.
  It lists correctable/uncorrectable/pending/failed row remapping and fan speed.
  It also lists thermal and power information.
  Runpod advises that ECC DBE indicates an uncorrectable GPU-memory error.
  For that error, Runpod tells users to contact support ([Runpod Cluster observability](https://docs.runpod.io/instant-clusters/cluster-observability)).

- **[inference]** Five-second Grafana samples help a tenant-side time series and before/after deltas.
  They are not equivalent to full raw XID logs, lifetime counters, or a field diagnostic.
  They are also not equivalent to a published screen/repair guarantee.
  The scope is explicitly Instant Clusters.
  Do not generalize availability to all Runpod Pods or bare-metal products.

- **[observed]** Runpod documentation marks the observability page last modified September 2, 2026 ([Runpod Cluster observability](https://docs.runpod.io/instant-clusters/cluster-observability)).

### 2.4 Modal: public XID interpretation and remediation practice

- **[observed]** Modal's GPU-health guide distinguishes user/application-attributable errors from hardware/driver-significant conditions.
  It gives practical action guidance for ECC events and XIDs.
  It describes XID 94 as a contained ECC error that affects one application.
  It describes XID 95 as uncontained.
  That uncontained error affects multiple applications and requires a GPU reset before applications restart ([Modal GPU Health](https://modal.com/docs/guide/gpu-health)).

- **[observed]** The guide describes XID 63 as successful ECC page-retirement/row-remap recording.
  It describes XID 64 as row-remap recording failure on A100-and-later GPUs.
  It advises a prompt reboot for XID 64 and escalation if the error recurs.
  It describes XID 79 as a GPU lost from the bus.
  It describes XID 48 as uncorrectable double-bit ECC ([Modal GPU Health](https://modal.com/docs/guide/gpu-health)).

- **[observed]** Modal cautions that XID 13 and XID 31 have multiple possible causes.
  The causes include application, driver, and occasionally hardware issues.
  Thus a blanket “any XID = bad GPU” rule misclassifies workload faults ([Modal GPU Health](https://modal.com/docs/guide/gpu-health)).

- **[inference]** Modal gives a useful provider-operated policy example.
  It does not show that every Modal tenant can query raw persistent health counters.
  Its guide is architecture-general.
  It does not establish GB300-specific screening or public pass records.

### 2.5 Provider evidence not found / not safely generalizable

- **[observed]** The cited public material describes no universal neocloud health API across providers.
  No API gives stable per-device UUID/serial, cumulative ECC and row-remap history, or an XID event log.
  No API gives screening timestamps/results or a repair/retirement ledger.
  CoreWeave gives a dashboard/test description.
  Lambda gives a Slurm console/service description, and Runpod gives an Instant Clusters Grafana view.
  Modal gives a guide ([CoreWeave](https://docs.coreweave.com/platform/fleet-management/hpc-verification); [Lambda](https://docs.lambda.ai/managed-slurm/quickstart); [Runpod](https://docs.runpod.io/instant-clusters/cluster-observability); [Modal](https://modal.com/docs/guide/gpu-health)).

- **[inference]** Missing public evidence does not mean that a provider lacks internal diagnostics.
  It means that a tenant cannot independently assert that the provider applied those controls to a particular GPU.
  A tenant can make that assertion only when the provider supplies per-device records.

## 3. DCGM: measured evidence available at device level

### 3.1 Health watches versus active validation

- **[observed]** DCGM health monitoring uses passive field watches.
  The watches cover PCIe, memory, InfoROM, thermal/power, NVLink, driver, and additional systems.
  Health rules translate retained measurements/events into incidents.
  Health watches do not apply a workload.
  A Healthy summary only means that no enabled rule finds an incident in retained data ([DCGM health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html)).

- **[observed]** NVIDIA's example enables PCIe, memory, InfoROM, thermal/power, NVLink, and driver watches with `dcgmi health --set pmitnd`.
  The example then fetches/checks group health.
  NVIDIA warns about some watches.
  They need around 60 seconds of samples before an initial check is meaningful ([DCGM health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html)).

- **[observed]** DCGM Diagnostics run active tests when operators can remove GPUs from normal service.
  NVIDIA positions levels 1–2 for readiness/epilogue.
  NVIDIA positions levels 3–4 for administrator/post-mortem use.
  NVIDIA says DCGM is not comprehensive hardware diagnosis or the field diagnostic/RMA process ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

- **[inference]** Use both mechanisms.
  Passive watch deltas detect in-test events.
  Active tests show that a GPU can execute/copy/read correctly under load.
  A health PASS alone is not a functional PASS.

### 3.2 ECC, remapping, and retirement

- **[observed]** DCGM field identifiers include volatile and aggregate/persistent SBE/DBE counters.
  The counters include device-memory, L1/L2, register, texture, and SRAM categories.
  DCGM documents aggregate fields as monotonically increasing.
  DCGM also shows retired SBE/DBE page totals and pending-page-retirement state ([DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html)).

- **[observed]** Row-remap fields include correctable and uncorrectable remap totals, pending state, and failed state.
  They also include historical remap availability histogram buckets.
  These fields are direct, per-GPU evidence sources when the installed GPU/driver supports and reports them ([DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html)).

- **[observed]** NVIDIA says GPUs support row remapping from Ampere onward.
  On Blackwell, a third remapping attempt can occur for an uncorrectable error in a bank.
  That attempt starts HBM channel repair if a spare channel exists.

  Row-remap failure can occur after eight uncorrectable rows in a bank.
  It can also occur after a repeated already-remapped row or 512 total uncorrectable remaps.
  Field Diagnostic validates RMA qualification.
  NVML/`nvidia-smi` shows the failure flag in-band, and SMBPBI shows it out-of-band ([NVIDIA GPU Memory Error Management: RMA thresholds](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/rma-policy-thresholds-for-row-remapping.html)).

- **[inference]** Do not grade any nonzero remap count as automatic failure.
  The count records managed degradation/remediation history.
  Report counts, pending/failure booleans, and deltas separately.
  A failed or pending remap is a high-severity finding.
  The vendor field diagnostic—not rack-bench—decides RMA.

- **[observed]** DCGM health policy includes configurable page-retirement limits.
  It also includes fixed rules for severe ECC, row-remap failure, XIDs, and performance excursion types.
  Exact defaults follow versioned policy behavior, not a universal pass threshold ([DCGM feature overview](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html); [health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html)).

### 3.3 XID evidence and causal caution

- **[observed]** DCGM shows the current XID as `DCGM_FI_DEV_XID_ERROR` (field 230).
  DCGM health rules include MMU/PBDMA/reset-channel XID incidents and contained/uncontained ECC cases.
  They also include remap failure and GPU recovery needs ([DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html); [DCGM health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html)).

- **[observed]** NVIDIA's published XID guide explains individual XIDs and recommended diagnosis.
  Its examples are XID 48 DBE, XID 63/64 remap record success/failure, and XID 74 NVLink error.
  Further examples are XID 79 GPU inaccessible over PCIe and XID 94 contained ECC.
  The last example is XID 95 uncontained ECC ([NVIDIA Xid Errors](https://docs.nvidia.com/deploy/xid-errors/index.html)).

- **[inference]** Capture the kernel/NVRM event log as well as DCGM's point-in-time XID field.
  A current-value field is not by itself a durable event history.
  Before you assign fault responsibility, keep the raw code, GPU UUID/PCI bus ID, and timestamp.
  Also keep the contemporaneous test/workload.

- **[inference]** Categorize XIDs, rather than treating every XID equally.
  Fail or quarantine a GPU for hardware-significant/uncorrectable or recurring device events.
  Record application-attributable XIDs as workload/test failure.
  Change that grade only if the XID reproduces on a clean known-good workload.

### 3.4 DOA, silent corruption, and bit-exact correctness

- **[observed]** DCGM's level-3 Diagnostic plugin performs large matrix multiplications and framebuffer write/read checks.
  It runs for five minutes by default.
  It monitors XIDs, temperature violations, uncorrectable memory errors, and data correctness.
  Its memory plugin writes/reads patterns.
  The memory plugin reports allocation failure, memory mismatch, CUDA DBE, and L1-cache miscompare ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

- **[observed]** DCGM level-4 memtest includes walking bits/address checks, moving inversions, and random patterns.
  It also includes block moves, memory stress, and bit-fade.
  Some tests take seconds.
  On the documented A100 40GB reference, moving inversions 32-bit takes about 155 seconds per iteration.
  On the same reference, bit-fade takes about 244 seconds per iteration.
  Defaults alternate stress tests for 10 minutes ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

- **[observed]** CoreWeave's publicly named SDC check detects memory errors that do not raise standard alerts.
  CoreWeave runs it alongside FP8/FP16/BF16 performance regression screening ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).

- **[inference]** The strongest short correctness signal is reproducible deterministic output validation under memory and arithmetic stress.
  This validation uses checksums/reference comparison and per-GPU attribution.
  A finite test cannot establish zero SDC probability.
  A pass means that the test observes no discrepancy under the tested patterns/duration.

- **[observed]** DCGM's current documentation explicitly lists NVBandwidth support for B300.
  That particular plugin SKU list does not give an explicit GB300 NVL72 name.
  DCGM release notes separately list active-diagnostic support additions for GB300 variants ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html); [DCGM changelog](https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html)).

- **[inference]** Verify the installed DCGM build, driver, SKU detection, and supported tests on the actual GB300 system at runtime.
  A B300 or Blackwell-family listing does not prove that NVIDIA enables or calibrates every GB300-specific test.

### 3.5 Performance, clocks, power, and thermals

- **[observed]** DCGM Diagnostics includes relative performance, compute/memory bandwidth, power/thermal stress, and PCIe tests.
  The Diagnostic plugin compares GFLOPS among GPUs and has a configurable tolerance.
  The targeted-power plugin attempts near-TDP steady work.
  It fails if it cannot reach the configured fraction of target.
  It also fails if uncorrectable memory errors, thermal violations, or XIDs occur ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

- **[observed]** Current DCGM fields include GPU/memory temperatures and operating/slowdown limits.
  They include board power and requested/default/min/max/enforced limits.
  They include SM and memory clocks and clock event reasons.
  They also include cumulative seconds throttled by power, thermal, sync-boost, board, reliability, or application limits ([DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html)).

- **[inference]** A useful screen compares same-rack GPUs under the same workload.
  It records achieved throughput plus clock, power, temperature, and throttle-time deltas.
  A low clock or power draw alone is not a failure.
  An underfilled kernel, profile/power cap, workload mismatch, cooling policy, or shared power constraint can explain it.
  Grade observed performance against a predeclared GB300 workload baseline and explain outliers.

- **[observed]** DCGM's diagnostic parameter documentation lists Blackwell-and-newer behavior.
  Examples are an 8192 matrix dimension default and Tensor Core use.
  Thus do not carry legacy threshold/config assumptions forward unexamined ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

### 3.6 Per-GPU NVLink health only

- **[observed]** DCGM health watches include NVLink.
  The health rules document link error/recovery conditions, including Blackwell+ link-recovery events.
  DCGM fields give per-link status and per-link CRC/replay/recovery counts.
  They also give throughput and NVLink5+ error/recovery counters ([DCGM health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html); [DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html)).

- **[observed]** NVIDIA XID 74 guidance says that the event indicates an NVLink connection issue.
  The issue can start at the local link or at the remote endpoint.
  Before hardware escalation, review per-link details and repeatability after reset ([NVIDIA Xid Errors](https://docs.nvidia.com/deploy/xid-errors/index.html)).

- **[inference]** For this scope, check the expected active NVLink count/status of each GPU.
  Capture per-link error-counter baselines and deltas while the GPU runs its assigned GPU test.
  Report asymmetric throughput/error growth.
  Do not run NCCL/east-west fabric certification under this GPU-device brief.

## 4. Device health and allocation hygiene

### 4.1 MIG and whole-GPU identity

- **[observed]** DCGM inventories MIG mode, GPU-instance/compute-instance attributes, and related visibility fields.
  Its health and diagnostic APIs distinguish GPU entities from MIG entities.
  NVIDIA's fields explicitly mark MIG mode and instance metadata ([DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html)).

- **[observed]** Lambda documents MIG operation on a GH200 instance as an explicit administrator/user operation.
  The operation includes enabling MIG and creating instances.
  This is not GB300 evidence.
  Do not generalize it to an NVL72 rack ([Lambda MIG guide](https://docs.lambda.ai/education/using-mig)).

- **[inference]** Before testing, a whole-GPU certification run records MIG current/pending mode and enumerates GPU/GI/CI ownership.
  Policy can expect one exclusive whole GPU.
  Then non-empty MIG instances, unrelated processes, or uncertain partition ownership cause a reasoned SKIP/FAIL.
  They must not cause a misleading per-GPU PASS.
  For a MIG product, test/grade each instance and parent device separately.
  Do not assume that all counters are attributable at the MIG slice.

- **[observed]** DCGM's diagnostic deployment test fails when unrelated graphics processes use target GPUs.
  The tests require device access, CUDA/NVML libraries, and appropriate permissions ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

### 4.2 Driver, firmware, and evidence identity

- **[observed]** DCGM's deployment diagnostics test NVML/CUDA access, library versioning, and software conflicts.
  They also test permissions, driver, and cgroup integration.
  Telemetry fields show system driver/NVML/CUDA versions and GPU identifiers/firmware metadata ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html); [DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html)).

- **[inference]** Record GPU UUID, serial if visible, PCI bus ID, model, firmware, driver, and CUDA/DCGM versions.
  Also record whether the system supports each field/test.
  Compare node/tray software versions to the certification profile.
  Report a mismatch as a distinct software-configuration result.
  Do not silently call it a defective GPU.

- **[inference]** Keep the exact command, exit status, DCGM JSON, logs, metric samples, and node/tray identity.
  This record makes a PASS reproducible and allows later change detection.

### 4.3 Used / certified-pre-owned claims

- **[observed]** The primary provider sources in this review disclose active checks and monitoring in selected products.
  They do not publish a universal used-GPU lifecycle ledger.
  They also do not publish a per-serial CPO certificate.
  Such a certificate has prior ECC/remap/XID counts and test results ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification); [Lambda quickstart](https://docs.lambda.ai/managed-slurm/quickstart); [Runpod observability](https://docs.runpod.io/instant-clusters/cluster-observability)).

- **[inference]** A remap counter is useful history, not a complete provenance certificate.
  For refurbished/previously rented units, request serial-bound age/use history, firmware, and raw lifetime counters.
  Also request the last field diagnostic, replacements/repairs, and dated screening outputs.
  Label absent history unknown.
  Do not infer unused/new.

## 5. Proposed rack-bench GPU procedure (≤2 hours)

### 5.1 Suggested schedule for 18 trays

- **[inference]** If all 18 trays can run tests concurrently without contention, use a practical 105–115-minute schedule.
  Use 5–10 minutes for inventory/baselines and exclusive-allocation validation.
  Use 30–40 minutes for the active DCGM quick/level-3 diagnostic plus a targeted memory test.
  Use 20–30 minutes for concurrent per-GPU known-answer compute and memory bandwidth/correctness.
  Use 20–25 minutes for a sustained thermal/power workload while you collect health deltas.
  Use 5–10 minutes for final counter/log capture and the report.

  Keep at least 5–10 minutes contingency.
  This is a proposed schedule, not NVIDIA-published rack timing.

- **[calculated]** A GB300-class NVL72 rack has 72 GPUs.
  At 20 minutes per GPU, concurrent execution takes 20 minutes wall time.
  This holds only if the scheduler runs devices independently and the tests do not serialize.
  The host/rack topology can serialize tests, or power/cooling limits can require staggering.
  Then 72×20 minutes is 24 GPU-hours, so test wall time is no longer 20 minutes.
  Measure the actual DCGM run-time on GB300 NVL72 during commissioning.

- **[observed]** CoreWeave's idle-node test targets every GPU in 20–30 minutes.
  Its on-demand test allows approximately 35 minutes.
  These values give a real-world duration anchor.
  They do not guarantee equal execution on the target hardware ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).

### 5.2 Required measured checks and evidence

1. **Identity / dead-device / configuration — [inference].** Enumerate exactly the expected devices and serial/UUID/PCI ID.
   Read model, memory capacity, firmware, and driver.
   Validate that all devices respond and that no unexpected process/MIG partition exists.
   The existing local baseline collector reads inventory, ECC mode, MIG, firmware, clocks, power limits, thermals, and topology.
   See exact references in §7.

2. **Baseline RAS snapshot — [inference].** Capture ECC enabled/current/pending.
   Capture volatile and aggregate SBE/DBE by memory domain, and retired page totals/pending.
   Capture row remap correctable/uncorrectable totals/pending/failed/availability, XIDs, and kernel logs.
   Keep before/after snapshots.
   Then the report does not mistake persistent history for errors from this run.

3. **Active correctness and memory — [inference].** Run DCGM level-3 diagnostic/memory tests and a deterministic per-GPU known-answer kernel.
   The kernel uses an independent reference/checksum.
   The proposed rack-bench extension allocates as much available HBM as safely possible and records the actual bytes tested.

   This differs from DCGM memory plugin documentation, which specifies 75% allocation by default.
   Use supported DCGM level-4 memtest cases selectively within the budget.
   Do not claim exhaustive HBM screening if not all patterns run.

4. **Compute/performance parity — [inference].** Run a fixed, warmed FP8/FP16/BF16 Tensor Core workload and a conventional arithmetic kernel on every GPU.
   Compare achieved throughput against a versioned GB300 reference and the same-rack cohort median.
   CoreWeave confirms that it uses these precisions for fleet screening.
   CoreWeave gives no thresholds ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).
   Record clock, power, temperature, and utilization with each score to distinguish an underfed workload from a degraded GPU.

5. **HBM throughput — [inference].** Measure per-device local memory bandwidth with a stable streaming test and validate output.
   DCGM documents a memory-bandwidth plugin that uses STREAM TRIAD and a configurable minimum bandwidth.
   Use it only when the installed build/SKU supports it.
   Set the threshold from validated GB300 baselines ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

6. **Thermal/power/clock behavior — [inference].** Take a baseline first.
   Through sustained compute, sample power limit, draw, SM/memory clocks, GPU and memory temperatures, and thermal margin.
   During that compute, also sample event-reason bits and cumulative throttle seconds.

   Report temperature and throttle duration, not a single max-temperature PASS.
   Treat observed nonzero throttling as explanatory evidence.
   Fail only against a predeclared workload-specific bound, or if workload throughput falls outside spec.

7. **XID and health watch — [inference].** Start DCGM health watches (PCIe, memory, InfoROM, thermal/power, NVLink, driver) before active work.
   Allow at least the sampling warm-up, and check after the test.
   Save kernel logs and XID timestamps.
   Report new events separately from historical state ([DCGM health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html)).

8. **NVLink device edge health — [inference].** Capture expected per-GPU link count/status before/after load.
   Also capture per-link CRC/replay/recovery counters before/after load.
   Fail/report missing expected active links or counter growth according to profile.
   This check is device-link health, not east-west fabric throughput certification ([DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html)).

9. **Driver/firmware compatibility — [inference].** Capture exact driver/CUDA/DCGM/BMC/GPU firmware.
   Check supported field/test inventory and version-manifest consistency.
   Unsupported/null fields become explicit SKIP(reason), not zero.

10. **MIG hygiene — [inference].** Confirm whether the profile expects MIG on/off.
    Enumerate all GPU/GI/CI instances, assigned device visibility, and processes.
    Do not run whole-GPU stress while tenant or system processes are present.
    The only exception is scheduler isolation.

### 5.3 Non-mutating bench boundary

- **[inference]** The bench can apply active compute and memory load.
  The bench must not change device configuration.
  Do not toggle ECC or MIG, and do not change power limits/clocks/power profiles.
  Do not update firmware or drivers, clear counters, reset GPUs, or reboot nodes.
  Take before/after snapshots and report observed changes.
  Configuration changes or recovery belong to a separately authorized maintenance workflow.

### 5.4 Acceptance semantics

- **[inference]** PASS means that the declared measurement completes on every in-scope GPU.
  It also means that the output meets versioned thresholds.
  It also means that no disqualifying new RAS event occurs.
  A provider claim, absent error log, or static capability inventory alone cannot earn performance PASS.

- **[inference]** FAIL keeps full raw findings: device identity; old/new counters; XID/log evidence; exact test and output.
  FAIL also keeps performance; clocks/power/temperature; driver/firmware; reproducibility status.
  Do not auto-delete or average away one degraded GPU.

- **[inference]** SKIP requires a concrete reason.
  Example reasons are nonexclusive allocation, unauthorized diagnostic, unavailable DCGM/driver feature, and unsupported GPU/SKU.
  Other examples are missing GB300 threshold baseline and missing NVLink counters.
  A test that does not finish in the window is also an example.
  Distinguish “unsupported” from “tested, zero errors.”

- **[inference]** A clean 2-hour result is a screening certificate.
  It does not prove no future SDC, full life expectancy, complete physical integrity, or RMA eligibility.

## 6. What is not established

### 6.1 Honest misses

- **[observed]** The reviewed CoreWeave documentation does not publish SDC incidence rates or screening-result distribution.
  It also does not publish FP kernel tolerances/cutoffs or a per-GPU customer export ([CoreWeave HPC Verification](https://docs.coreweave.com/platform/fleet-management/hpc-verification)).

- **[observed]** Lambda's cited public page does not disclose diagnostic algorithms, failure thresholds, or XID/ECC/remap visibility.
  It also does not disclose per-device screening results or GB300-specific health behavior ([Lambda Managed Slurm quickstart](https://docs.lambda.ai/managed-slurm/quickstart)).

- **[observed]** Runpod documents specific Instant Cluster metrics.
  It does not document fleet screening outcome rates or a per-device repair/retirement policy.
  It does not guarantee that other product types show those same metrics ([Runpod Cluster observability](https://docs.runpod.io/instant-clusters/cluster-observability)).

- **[observed]** DCGM Diagnostics expressly disclaims comprehensive diagnosis, active remediation, and RMA adjudication.
  Full offline field diagnosis remains a separate NVIDIA process ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

- **[inference]** Two hours cannot estimate the rare-event SDC rate with useful statistical confidence.
  Two hours cannot validate lifetime durability.
  Two hours cannot prove the absence of intermittent thermal/power faults that require longer burn-in.
  The window can find reproducible correctness/performance anomalies and known RAS indicators.

- **[inference]** A green health dashboard can hide unenabled watches, expired retention, or inaccessible counters.
  It can also hide an idle/no-load sample, a recently reset baseline, or software mismatch.
  Archive watch configuration, support metadata, data age, and raw counter values.

- **[inference]** GB300-class limits vary by rack policy, clocks, firmware, cooling, power mode, and DCGM/driver version.
  Public docs do not supply universal limits for a GB300 NVL72 Chennai rack.
  The missing limits include expected throughput, temperature, throttle fraction, ECC acceptance policy, and per-model NVLink threshold.
  Establish and version a local golden baseline.

### 6.2 Conflicts and interpretation boundaries



## 7. Exact local evidence references

### 7.1 Existing rack-bench baseline checks

- **[observed]** [`gpu.py#L17-L21`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L17-L21) enumerates GPUs via `nvidia-smi -q -x`.
  [`gpu.py#L40-L50`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L40-L50) collects count, UUID, model, serial, architecture, PCI bus ID and memory capacity.
- **[observed]** [`gpu.py#L53-L59`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L53-L59) captures ECC mode/uncorrected volatile total and MIG mode.
  [`gpu.py#L62-L69`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L62-L69) captures firmware.
  [`gpu.py#L72-L81`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L72-L81) captures clocks and power limits/draw.
  [`gpu.py#L84-L90`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/gpu.py#L84-L90) captures thermals/utilization, explicitly instantaneous.
- **[observed]** [`topology.py#L105-L117`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/topology.py#L105-L117) reports per-GPU NVLink counts/state.
  [`topology.py#L110-L112`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/rack_bench/audit/topology.py#L110-L112) notes that missing-link detection needs an expected-map comparison.
- **[inference]** These audit collectors do not provide ECC lifetime/row-remap/XID history or active correctness testing.
  They also do not provide sustained thermal/performance data or per-link counter deltas.

### 7.2 Correct local scope and contract references

- **[observed]** [`research.md#L5-L16`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/research.md#L5-L16) states the device-level question, two-hour window, and rack context.
  It also states the measured evidence contract, NVLink scope, and node independence.
  [`research.md#L34`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/research.md#L34) gives N01's question and acceptance condition.
- **[observed]** [`.lavish/gpu-research/README.md#L5-L10`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/README.md#L5-L10) states the GPU research question, rack context and evidence contract.
  [`README.md#L34`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/README.md#L34) excludes east-west and retains per-GPU NVLink.
- **[observed]** The project [`README.md#L7-L15`](file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/README.md#L7-L15) describes read-only audit, quick per-component bench and sustained smoke.
  It does not itself state the detailed measured-PASS/reasoned-SKIP contract.
## 8. Source confidence

### 8.1 High confidence

- **[observed]** NVIDIA DCGM documentation and field identifiers are primary, detailed technical sources.
  They show what the framework measures and the distinction between active/passive mechanisms.
  They also show known limitations and Blackwell-related support.
  Verify the exact installed DCGM and GPU support on target hardware ([DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html); [health monitoring](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/health-monitoring.html); [fields](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html); [changelog](https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html)).
- **[observed]** NVIDIA GPU Memory Error Management is the primary source for Blackwell row-remap/HBM channel repair behavior.
  It is also the primary source for RMA thresholds ([NVIDIA RMA policy](https://docs.nvidia.com/deploy/a100-gpu-mem-error-mgmt/latest/rma-policy-thresholds-for-row-remapping.html)).
- **[observed]** CoreWeave, Lambda, Runpod, and Modal documentation are primary sources for their own stated product behavior.
  Confidence is high that the providers publish the descriptions.
  Confidence is not high that those controls guarantee any particular rack outcome ([CoreWeave](https://docs.coreweave.com/platform/fleet-management/hpc-verification); [Lambda](https://docs.lambda.ai/managed-slurm/quickstart); [Runpod](https://docs.runpod.io/instant-clusters/cluster-observability); [Modal](https://modal.com/docs/guide/gpu-health)).

### 8.2 Limits to confidence

- **[inference]** “Not published in pages reviewed” is deliberately weaker than “provider does not do this”.
  Private operational systems and support-only APIs can exist.
- **[inference]** Product/version changes can change provider-specific public claims.
  The Runpod page shows a September 2026 update.
  The other documentation pages are live documents.
  Their retrieved text does not give a stable revision record.
- **[inference]** This research has no GB300-class rack to execute/benchmark commands or confirm every field.
  It also cannot validate total diagnostic wall time.
  The test plan is source-grounded, but thresholds/runtime require rack commissioning.

## Gaps

- This research finds no public, serial-bound neocloud screening reports for individual GB300 GPUs.
  Ask CoreWeave/Lambda/Runpod for anonymized test outputs, exact thresholds, retention, and counter access.
  Also ask for remediation records.
  Get these records before you interpret their health language as a guarantee.
- No provider publishes an SDC incidence rate or screening sensitivity/false-negative rate in the cited public docs.
  Nobody can reconstruct these rates from hourly screening or short test duration.
- The cited primary provider sources establish no universal certified-pre-owned GPU protocol.
  They also establish no publicly verifiable used-GPU history.
  Request provenance and dated counters per device.
- Hardware tests must still verify exact DCGM/driver builds, field support, and NVLink5+/Blackwell counter availability.
  They must also verify GB300-specific calibration and complete DCGM test runtimes on an 18-tray NVL72 rack.
  Establish baseline thresholds locally before you produce PASS results.
- The cited HPC Verification page does not publish the exact CoreWeave FP8/FP16/BF16 kernels or SDC method.
  It also does not publish pass tolerances or the per-node customer-visible result format.
- The selected sources do not establish “GPU-per-VM” isolation guarantees across the providers.
  Validate actual UUID/device count, MIG/vGPU mode, and process ownership from the assigned workload.
  Do not rely on a product label.
