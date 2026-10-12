# Hyperscaler GPU Diagnosis: Customer Checks and Recovery

Research date: 2026-10-11. All claims below carry a source URL.

The label **[observed]** marks a claim that a primary source states.
The label **[calculated]** marks arithmetic.
The label **[inference]** marks recommendations or deductions.
This brief covers N02 only: hyperscaler-published GPU diagnosis and operational limits.
This brief does not claim that every provider applies the same acceptance standard.

## 1. Executive answer: what a two-hour GPU bench can substantiate

### 1.1 Minimum measured device-level package

1. **[observed] Inventory and DOA screen:** List the UUID, PCI bus address, model, serial, memory capacity, and architecture of each GPU.
   Compare the GPU count and identity with the rack map.
   Then run a CUDA workload.

   AWS tells customers to use `nvidia-smi -q` and verify the attached-GPU count.
   The Azure extension reports GPU-not-found and unsupported-size failures.
   Google names installed-driver and DCGM validation ([AWS EC2 Xid troubleshooting](https://repost.aws/knowledge-center/ec2-linux-troubleshoot-xid-errors), [Azure Linux driver extension](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/hpccompute-gpu-linux), [Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).

2. **[observed] ECC / HBM remap state:** Capture ECC counters, retired pages, pending page retirement/remap, remap failures, and XIDs.
   Capture them both before and after you exercise memory.
   DCGM software diagnostics explicitly fail pending or failed remaps.
   Google documents DBE, row remapping, and remediation ([DCGM Diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html), [Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).

3. **[observed] Fast diagnostic plus bounded stress:** DCGM levels are cumulative.
   Level 1 is quick.
   Level 2 is medium.
   Level 3 is long system hardware diagnosis.
   Level 4 is extended.

   Google publishes `dcgmi diag -r 1` for the thermal check.
   Google notes levels 3/4 for deeper suspected hardware faults.
   NVIDIA's timing table estimates that level-4 on Hopper eight-GPU systems can exceed 2 hours.
   That estimate shows no guaranteed fit ([Google](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus), [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

4. **[inference]** A sound two-hour category puts full-rack inventory and snapshots first.
   Next, it runs targeted level-1/2 diagnostics on all 72 GPUs.
   Next, it runs one carefully bounded GPU memory/correctness and compute stress pass.
   Then it captures per-GPU NVLink health counters and post-test deltas.
   Do not promise a full DCGM level-4 suite over all 72 devices inside the window.

### 1.2 What hyperscalers require versus what they repair themselves

- **[observed]** Google gives the most explicit customer runbook.
  It covers `nvidia-smi`/DCGM thermal checks, XID interpretation, and GPU reset where supported.
  Google requires logs and bug reports for support.
  Google separately uses passive health checks.
  These checks automatically send high-risk failures such as XID 74/79/140 for repair ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[observed]** AWS material describes instance-level health and customer diagnosis.
  AWS EC2 infrastructure checks do not replace the tenant's device-level diagnosis.
  The ParallelCluster GPU health feature runs checks before Slurm jobs.
  It drains/deprovisions impaired nodes ([AWS ParallelCluster GPU health checks](https://aws.amazon.com/blogs/hpc/introducing-gpu-health-checks-in-aws-parallelcluster-3-6), [AWS re:Post indexed snippet; direct fetch failed](https://repost.aws/knowledge-center/ec2-linux-troubleshoot-xid-errors)).
- **[observed]** The cited Azure N-series NVIDIA extension is an installer/driver-management mechanism.
  It is not a hardware-health suite.
  It may reboot at installation.
  It does not automatically update drivers after installation.
  It requires internet access.
  Azure recommends VM Assist for guest-agent/overall VM-health diagnosis ([Azure Linux extension](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/hpccompute-gpu-linux)).

## 2. DCGM / DCGG terminology and exact diagnostic levels

### 2.1 Correct tool name

- **[observed]** The NVIDIA/Google tool is **DCGM** (NVIDIA Data Center GPU Manager).
  Operators invoke it through **`dcgmi`**.
  DCGM Diagnostics is the current name for diagnostic executable functionality formerly called NVVS.
  Google's docs and GKE metrics use DCGM, not “DCGG” ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html), [GKE DCGM metrics](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/dcgm-metrics)).
- **[inference]** “DCGG” in task notes appears to be a typo or conflation.
  Keep the exact terms `DCGM`, `dcgmi`, and optionally `dcgm-exporter` in rack-bench UI.

### 2.2 Levels, diagnostic purpose, and runtime

- **[observed]** NVIDIA defines these run levels.
  `dcgmi diag -r 1` is quick system validation.
  `-r 2` is medium/extended validation.
  `-r 3` is long system HW diagnostics.
  `-r 4` is extended/longer-running HW diagnostics.
  Higher numbered levels include lower-level tests ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- **[observed]** Google uses `dcgmi diag -r 1` to check thermal violations.
  A `Warn` or `Fail` under Thermal means a violation occurred.
  Concurrent clock throttling suggests overheating ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[observed]** NVIDIA's current diagnostics docs give Hopper example runtime bounds.
  r1 runs under 2.5 seconds.
  r2 runs under 2.5 minutes for four GPUs / 10.5 minutes for eight.
  r3 runs under 10 / 35 minutes respectively.
  r4 runs under 45 minutes / 2.25 hours respectively.
  These values come from the table's test timings and are not a guarantee for GB300 ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- **[calculated]** Suppose you apply the eight-GPU Hopper r4 runtime of 2.25 hours literally.
  That runtime exceeds the two-hour GPU-category budget by 15 minutes.
  This source does not publish a GB300 rack-wide aggregate runtime.
- **[observed]** `dcgmi diag -r memory -j` emits machine-readable JSON and actionable error metadata.
  `dcgmi diag -r diagnostic -p diagnostic.test_duration=300.0` runs the named diagnostic plugin for five minutes.
  `dcgmi diag -r targeted_power -p targeted_power.test_duration=300.0` runs the named targeted-power plugin for five minutes.
  These commands do not bound a full level-3 run ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- **[observed]** NVIDIA says that DCGM diagnostics are not comprehensive hardware diagnostics.
  They do not actively fix problems.
  They do not replace field diagnosis.
  They do not perform RMA ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

### 2.3 GB300 / Blackwell compatibility caveat

- **[observed]** DCGM release notes mention B300 diagnostic improvements.
  They list NVBandwidth support for B300 device ID `20e6`.
  Level-3/4 diagnostics can use `-p "generic_mode=True"` on GPUs that lack SKU-specific calibration.
  Generic mode makes the affected tests stability checks.
  They are then not calibrated performance/power threshold checks ([DCGM changelog](https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html), [diagnostics guide](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- **[inference]** Screen GB300 NVL72-class systems against installed DCGM/driver support and actual device IDs.
  Do not use a blanket “Blackwell supported” assumption.
  Generic mode may test function/stability.
  Do not report generic mode as calibrated performance PASS.
- **[observed]** Google A3 examples and thresholds are H100/H200-specific, not GB300.
  Google separately identifies A4X Max as GB300 and bare metal.
  A4X Max is not equivalent to A3 guest/VM behavior ([Google troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus), [Google accelerator-optimized machines](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines)).

## 3. Exact command and evidence catalog

### 3.1 Inventory, logs, and support package

```bash
nvidia-smi -L
nvidia-smi -q
nvidia-smi -q -x > nvidia-smi-q.xml
nvidia-smi --query-gpu=timestamp,name,pci.bus_id,uuid,temperature.gpu,clocks_throttle_reasons.hw_slowdown --format=csv
sudo dmesg -T | grep -iE 'NVRM|Xid|nvidia'
sudo nvidia-bug-report.sh
```

- **[observed]** AWS re:Post search indexing exposed guidance to run `sudo nvidia-smi -q`.
  The guidance compares the attached-GPU count with the instance type.
  The direct page fetch failed.
  Treat that page-specific claim as provisional ([AWS re:Post search-index result](https://repost.aws/knowledge-center/ec2-linux-troubleshoot-xid-errors)).
- **[observed]** Google support asks for project/instance IDs, suspect nodes, and full non-interleaved NCCL logs.
  It also asks for DCGM/`nvidia-smi` health-check output and the exact failing workload command.
  It also asks for logs, `nvidia-bug-report.sh`, and changes before failure ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[inference]** The `nvidia-smi -L`, XML capture, dmesg, and bug-report commands above are an operational collection recipe.
  They are not a verbatim requirement in every provider document.
  Keep raw output, tool versions, UTC timestamps, and GPU UUID mapping in bench evidence.

### 3.2 DCGM checks

```bash
dcgmi discovery -l
dcgmi diag -r 1
dcgmi diag -r 2 -j
dcgmi diag -r memory -j
dcgmi health -c
dcgmi dmon -e 100,101,102,150,155,156,157
```

- **[observed]** `dcgmi diag -r 1` is Google's documented thermal check.
  `dcgmi diag -r memory -j` is the published actionable-memory example.
  Google indicates levels 3/4 for deeper investigation where it suspects hardware degradation ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[observed]** NVIDIA documents diagnostic JSON and diagnostic level commands.
  The exact field-ID selection for `dcgmi dmon -e` varies by DCGM version.
  The list above is not a provider-prescribed fixed field list ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html), [DCGM field IDs](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-api/dcgm-api-field-ids.html)).
- **[inference]** `dcgmi health -c` gives a useful health-watch snapshot only when an operator configures DCGM health watches.
  Record `dcgmi health -h` and `dcgmi --version`.
  Treat unsupported fields/commands as reasoned skips, not green results.

### 3.3 Diagnostic customization and timing

```bash
# quick system validation
dcgmi diag -r 1
# medium checks, machine-readable result
dcgmi diag -r 2 -j
# named diagnostic plugin only (5 min; not total level-3 runtime)
dcgmi diag -r diagnostic -p diagnostic.test_duration=300.0
# named targeted-power plugin only (5 min; not total level-3 runtime)
dcgmi diag -r targeted_power -p targeted_power.test_duration=300.0
# generic stability mode only where SKU calibration is unavailable
dcgmi diag -r 3 -p 'generic_mode=True'
```

- **[observed]** NVIDIA documents custom run duration parameters, iterations, YAML config overrides, and specific test selection.
  The level 3 diagnostic plugin stresses the GPU for five minutes by default.
  It checks XIDs, temperature violations, uncorrectable memory errors, and data correctness ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- **[inference]** Do not blindly run full `-r 3` or `-r 4` over 72 simultaneous GPUs.
  GPU/power/thermal workload, cooling headroom, and DCGM engine load affect runtime and observability.
  Parallel resource contention and diagnostic calibration also affect runtime and observability.
  Pilot and measure on one tray.
  Then define concurrency and preserve per-GPU status.

### 3.4 `nvidia-smi -q` fields worth capturing

- **[observed]** Google explicitly queries `timestamp,name,pci.bus_id,temperature.gpu,clocks_throttle_reasons.hw_slowdown`.
  In this A3 guidance, Google interprets `hw_slowdown=Active` as temperature-related throttling.
  NVIDIA defines generic HW slowdown as either HW thermal slowdown or external power brake.
  So do not infer temperature outside the Google-specific context ([NVIDIA nvidia-smi manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html)) ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[observed]** NVIDIA `nvidia-smi` documents queryable ECC errors, retired pages, and row remapper counters/status.
  It also documents power limits/draw, clocks, and throttle reasons.
  DCGM field IDs include XID errors, retired-page counts, pending retirement, and remapped rows (correctable/uncorrectable).
  They also include remap failure/pending, thermal/power violation time, and PCIe link generation/width ([NVIDIA nvidia-smi manual](https://docs.nvidia.com/deploy/nvidia-smi/index.html), [DCGM fields](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-api/dcgm-api-field-ids.html)).
- **[inference]** Capture `nvidia-smi -q -x` wholesale rather than hard-coding XML paths.
  Query support and XML structure vary by GPU, driver, and version.
  At minimum, inspect `Attached GPUs`, UUID/serial/product, PCIe, and ECC current/pending.
  Also inspect volatile/aggregate errors, retired pages/remapped rows, and temperature thresholds.
  Also inspect clocks/current and max clocks, and power draw/default/current limits.
  Also inspect throttle reasons, MIG mode, GPU utilization, and NVLink error counters.

## 4. Failure classification and recovery rules

### 4.1 XID rules that must not be collapsed into generic failure

| Event | Provider/NVIDIA meaning and supported action |
|---|---|
| **XID 79** | **[observed]** NVIDIA defines this event as GPU fallen off PCI bus. The NVIDIA catalog classifies it as bus access failure. The catalog recommends contacting support. Google says its managed workflow detects it and repairs host hardware. In the rack bench, fail/isolate the device and collect PCI/kernel logs. AWS XID-specific re:Post recovery text remains unverified because the page fetch failed ([NVIDIA](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html), [Google](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)). |
| **XID 94** | **[observed]** Contained error: restart the affected application. Other applications remain unaffected. NVIDIA recommends a GPU reset when convenient. Interpret it alongside co-occurring XIDs. This event alone does not establish cause ([NVIDIA](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html), [Google](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)). |
| **XID 95** | **[observed]** Uncontained error: stop workloads. Reset the GPU or reboot before you restart workloads. Investigate related XIDs ([NVIDIA](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html), [Google](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)). |
| **XID 48 / 63 / 64** | **[observed]** XID 48 is uncorrectable DBE. XID 63 records retirement/remap. XID 64 indicates remap recording failure. Stop the workload, and reset/reboot as appropriate. Repeated remap-bank exhaustion or SRAM thresholds may warrant replacement/field diagnosis ([NVIDIA catalog](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html), [Google](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)). |
| **XID 154** | **[observed]** This event summarizes a changed recovery action: none, drain P2P, drain/reset, GPU reset, or node reboot. It is not an independent root cause. Retain adjacent XIDs and the recovery transition ([NVIDIA catalog](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html)). |
| **XID 13/31/137** | **[observed]** These events usually show application illegal memory access, not ECC by itself. Debug them with Compute Sanitizer or cuda-gdb. Google allows DCGM level 3/4 when it suspects rare hardware degradation ([Google](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus), [NVIDIA](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html)). |

- **[inference]** An XID event is evidence, not automatically a physical defect.
  Use XID text plus associated counters to classify application and driver signals.
  Use the same evidence to classify contained/uncontained and hardware/remap signals.
  Preserve the event timeline.
  Do not erase counters with a reset before collection.

### 4.2 Reset operations are disruptive and platform-dependent

- **[observed]** Google says A3/A4/A4X/A4X Max support `sudo nvidia-smi --gpu-reset`.
  Other listed VM families may require a VM reboot.
  A reset also occurs on VM reset or stop/start.
  For GKE paths, utility locations differ (`/home/kubernetes/bin/nvidia`).
  The GPU reset tool is an option ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[observed]** AWS generic EC2 guidance recommends stop/start if system recovery fails or system checks persist.
  This step is infrastructure recovery, not a validated XID-79-specific remedy.
  It is disruptive ([AWS automatic recovery](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html)).
- **[observed]** GPU reset is not universally available or safe with active clients.
  NVIDIA's XID catalog recommends reset where appropriate.
  DCGM itself explicitly does not actively repair issues ([NVIDIA XID catalog](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html), [DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).
- **[inference]** Certification must never silently reset or reboot.
  Require explicit maintenance authorization.
  Drain workloads and record pre-reset evidence.
  Reset only one GPU, and only if the platform supports the reset and the GPU is isolated.
  Then re-enumerate and re-test.
  Otherwise mark recovery “not attempted: disruptive / unsupported”.

## 5. Hyperscaler platform and placement constraints

### 5.1 AWS EC2

- **[observed]** AWS EC2 runs automated system, instance, and attached-EBS status checks.
  These checks catch instance infrastructure/software/network reachability faults.
  They do not represent the rack-bench's full device-level memory/compute test ([AWS EC2 status checks](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-system-instance-status-check.html)).
- **[observed]** ParallelCluster GPU health checks run at job start.
  ParallelCluster marks failed nodes unavailable for new work.
  It de-provisions them after other jobs finish.
  It can requeue failed jobs ([AWS ParallelCluster 3.6](https://aws.amazon.com/blogs/hpc/introducing-gpu-health-checks-in-aws-parallelcluster-3-6)).
- **[observed]** Capacity Blocks reserve GPU capacity for a defined period.
  They place instances close together in EC2 UltraClusters.
  That is capacity/placement assurance.
  It is not proof that each device passes ECC, memory correctness, or XID checks ([AWS EKS compute best practices](https://docs.aws.amazon.com/eks/latest/best-practices/aiml-compute.html)).
- **[inference]** Do not use placement proximity, reservation acceptance, or EC2 status checks as a measured GPU PASS.

### 5.1.1 EC2 automatic recovery: scope and limits

- **[observed]** AWS enables simplified automatic recovery by default only on supported instance types.
  CloudWatch action-based recovery needs a configured alarm/action.
  Recovery responds to system status check failures that underlying host hardware/software causes.
  Recovery attempts migration to another host.
  It appears as an unplanned reboot.
  It does not operate when only the instance status check fails ([AWS automatic instance recovery](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html)).

- **[observed]** An operator must configure recovery before failure.
  If recovery fails, manual intervention is necessary.
  AWS recommends stop/start if the instance is unreachable or system checks continue to fail.
  Recovery loses volatile RAM and resets OS uptime.
  CloudWatch-based recovery also loses instance-store data ([AWS automatic recovery](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html)).

- **[observed]** Simplified recovery has eligibility restrictions and daily recovery-attempt limits.
  It excludes metal instances and instances with instance-store volumes at launch.
  AWS may retire instances after repeated recovery failure and identified hardware degradation ([AWS simplified recovery requirements](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-configuration-recovery.html), [AWS recovery comparison](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-recover.html)).

- **[inference]** This infrastructure mechanism is not evidence that each GPU passes a CUDA/HBM test.
  AWS does not promise that a GPU XID alone triggers system-status-check recovery.

### 5.2 Azure N-series and NVIDIA extension

- **[observed]** The Linux extension is `Microsoft.HpcCompute` / `NvidiaGpuDriverLinux`.
  CLI example: `az vm extension set --resource-group <rg> --vm-name <vm> --name NvidiaGpuDriverLinux --publisher Microsoft.HpcCompute --version 1.6`.
  The extension installs drivers/CUDA as applicable.
  It may reboot and requires internet connectivity.
  It does not auto-update after installation ([Azure extension](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/hpccompute-gpu-linux)).

- **[observed]** Extension exit codes include 11 GPU not found on VM size, 13 unsupported VM size, and 14 unsuccessful operation.
  The logs are `/var/log/azure/nvidia-vmext-status`.
  Secure Boot with the extension is unsupported.
  Driver/kernel compatibility is SKU-specific ([Azure extension](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/hpccompute-gpu-linux)).

- **[inference]** Extension success means that provisioning succeeded.
  It does not show measured GPU quality.
  Pin driver/tool versions, and use only supported VM/image combinations.
  Do not install or update a driver during a certification window.
  The exception is when reboot and the resulting changes are in scope.

- **[observed]** The Azure page reports v18.x until the v20.x rollout completes in Q3 CY2026.
  This research date is Oct 11, 2026.
  So the page's rollout statement is stale/ambiguous.
  It does not show that Azure actually deploys v20 ([Azure extension](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/hpccompute-gpu-linux)).

### 5.3 Google A3, A4X/GB300, and reservations

- **[observed]** Google's troubleshooting guide covers A3 H100/H200 and offers DCGM and `nvidia-smi`.
  The guide reports A3 performance degradation when temperatures remain above 87°C under load.
  Do not apply this threshold to GB300 without its platform-specific thermal limit ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[observed]** Google lists A4X Max as GB300 and bare metal, A4X as GB200, and A4 as B200.
  A4X Max differs from an A3 VM and from the NVL72-class rack under certification ([Google machine families](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines), [GPU machines](https://docs.cloud.google.com/compute/docs/gpus)).
- **[observed]** Google passive health checks can trigger emergency maintenance for likely hardware failures.
  Google names XID 74, 79 and 140 as examples.
  Google may pattern-match other XIDs.
  So single occurrences do not always trigger host repair ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[observed]** Google documents GPU-reset command support for A3/A4/A4X/A4X Max.
  Reset remains a workload-disruptive maintenance action ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).
- **[inference]** A4X Max hardware documentation establishes GB300 support context.
  It does not publicly endorse validation of every DCGM level/plugin/calibration for third-party GB300 NVL72-class assemblies.

## 6. Per-GPU NVLink health (in-scope, fabric benchmark out-of-scope)

- **[observed]** NVIDIA lists DCGM health checks for NVLink and XID 74.
  NVIDIA recommends `nvidia-smi nvlink` for link status/error details.
  NVIDIA says repeated XID 74 that persists after GPU reset/reboot merits vendor support ([NVIDIA XID catalog](https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html)).
- **[inference]** Include read-only per-GPU NVLink link state, CRC/replay/error counters, and counter deltas.
  Attribute them by GPU UUID and link index.
  Do not turn this check into NCCL/fabric throughput coverage.
  An unknown/unsupported counter is `skip` with reason, never zero-error PASS.
- **[observed]** Google A3's fault-finding discussion includes multi-node NCCL benchmarks and logs.
  These are cluster/fabric isolation steps.
  They are outside the bench-gpu scope of this GPU-device brief ([Google GPU troubleshooting](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-gpus)).

## 7. Recommended two-hour evidence runbook for rack-bench

### 7.1 Proposed schedule (engineering inference, validate on rack)

1. **0–10 min — baseline snapshot. [inference]** Capture UTC, driver/CUDA/DCGM versions, `nvidia-smi -L`, and `nvidia-smi -q -x`.
   Also capture kernel XIDs and per-GPU NVLink counters.

   Compare 18 trays × 4 GPUs = 72 expected UUIDs.
   **[calculated]** 18 × 4 = 72.
   NVIDIA identifies four GPUs per GB300 NVL compute tray and 72 GPUs across the rack ([NVIDIA GB300 NVL72 components](https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html)).

2. **10–25 min — fast diagnostic. [inference]** Run `dcgmi diag -r 1 -j` across the rack.
   Cap concurrency, and keep per-GPU reports.
   Run it only if DCGM supports the GPU/driver.
   Then use selected level-2 checks if the measured wall-time permits.

3. **25–85 min — device correctness and performance [inference].** Run bounded DCGM memory/correctness and compute/power checks.
   Optionally serialize them by tray or by controlled concurrency.
   Record the actual memory tested, utilization, temperature, achieved clocks/power, throttles, and errors.
   Require an observed result on each GPU rather than aggregate success.

4. **85–105 min — thermal/power and NVLink snapshot [inference].** Repeat telemetry under load, then at idle.
   Compare counter deltas.
   A single instantaneous sample cannot establish sustained throttling behavior.

5. **105–120 min — postflight [inference].** Recheck XID, ECC, remap, MIG, inventory, and link state.
   Emit JSON with per-field status and explicit skip reasons.

### 7.2 PASS / FAIL / WARN / SKIP boundaries

- **[inference] PASS** requires all of these:
  The exact expected GPU UUID count is present.
  Supported diagnostics complete, and data correctness passes.
  No newly observed uncorrectable ECC appears.
  No failed/pending remap requires action.
  No fatal XID, unexplained throttle, or per-GPU NVLink fault occurs.

- **[inference] FAIL** covers these cases:
  A GPU is missing.
  A memory miscompare, uncorrectable DBE, or remap failure occurs.
  An unsupported topology mismatch appears in the expected hardware map.
  XID 79 appears, or a DCGM hardware diagnostic fails.
  A repeatable per-GPU error grows.

- **[inference] WARN** covers these cases:
  A recoverable/application XID 94 follows an isolated app failure.
  Existing corrected ECC/remap counts show no fresh errors.
  Thermal/power constraints require interpretation.
  Performance sits below a locally measured/rated threshold.
  DCGM runs in generic mode without calibrated limits.

- **[inference] SKIP** with exact reason covers these cases:
  An unsupported telemetry field appears, or DCGM/privilege is absent.
  A workload occupies the GPU, or a reset is unavailable.
  GB300 calibration is unknown, or a test exceeds budget.
  A skip is not a pass.

- **[observed]** DCGM returns per-test statuses, findings, and error severity/category.
  NVIDIA says ISOLATE and RESET severities are high-confidence immediate-action errors.
  Other severities can need local policy/retest/log review ([NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)).

## 8. Exact local evidence and current implementation boundary

### 8.1 Existing implementation

- **[observed]** [`rack_bench/audit/gpu.py:8,17-21`](../../../rack_bench/audit/gpu.py#L8) runs `nvidia-smi -q -x`.
  It treats no devices as unavailable.
  [`rack_bench/audit/gpu.py:40-50`](../../../rack_bench/audit/gpu.py#L40) inventories model, UUID, serial, architecture, PCI bus ID, and total framebuffer memory.
- **[observed]** [`rack_bench/audit/gpu.py:53-59`](../../../rack_bench/audit/gpu.py#L53) captures ECC current/pending and volatile uncorrected total.
  It also captures MIG current/pending.
  [`rack_bench/audit/gpu.py:62-81`](../../../rack_bench/audit/gpu.py#L62) captures firmware, clocks, and power limits/draw.
  [`rack_bench/audit/gpu.py:84-90`](../../../rack_bench/audit/gpu.py#L84) captures GPU/memory temperature, slowdown threshold, and utilization.
  It explicitly labels this data an instantaneous sample.
- **[observed]** [`rack_bench/audit/gpu.py:93-110`](../../../rack_bench/audit/gpu.py#L93) captures passive topology/P2P capability.
  It handles command unavailability.
  It is not a live performance test.
- **[inference]** Audit currently misses XID log collection, retired-page/remapped-row details, and DCGM diagnostic execution/JSON.
  It also misses NVLink per-GPU counters/deltas, load-vs-idle telemetry, and CUDA correctness.
  It also misses bit-exact comparison and expected UUID/serial map enforcement.
  Audit must remain passive.
  Add these items as bench checks with measured outputs.

### 8.2 Confidence and scope limits

- **[observed]** Highest confidence goes to primary NVIDIA diagnostics/XID docs and Google's current GPU troubleshooting runbook.
  These sources directly define commands, levels, findings, and recovery.
  Official AWS EC2 automatic-recovery docs and the ParallelCluster blog directly define customer steps/service automation.
  Azure extension docs directly establish driver deployment constraints.

- **[inference]** Confidence is medium when you apply their recommendations to physical GB300 NVL72 racks.
  AWS EC2, Azure N-series, and Google A3 are different managed platforms.
  The A4X Max GB300 listing is closer architecturally.
  It does not publish all diagnostics/calibration expectations for arbitrary racks.

- **[observed]** Public docs do not establish a universal hyperscaler-mandated certification checklist or a universal XID threshold.
  They do not establish an exact DCGM diagnostic runtime for 72 GB300 GPUs.
  They do not establish universal thermal/power limits.
  They do not establish a requirement for bit-exact numerical validation.
  Those items remain local certification policy, not sourced provider mandates.

## Gaps

- **AWS exact customer-side command list is thin.**
  The AWS indexed re:Post snippet gives `sudo nvidia-smi -q` and an expected-count comparison.
  Direct verification of its XID recovery details failed.
  AWS documents the ParallelCluster feature at service level.
  No AWS primary-source material fetched here establishes that AWS requires DCGM levels or tests HBM remap counters.
  None establishes a specific `nvidia-bug-report.sh` command requirement in every GPU support case.

- **Azure's cited extension is not a diagnosis service.**
  It documents installer parameters and the health of extension execution.
  No primary Azure source retrieved defines a GB300 N-series equivalent or per-GPU diagnostic acceptance requirements.
  The current v18/v20 rollout wording is time-stale.

- **GB300 calibration and duration remain open.**
  DCGM release notes show B300 support elements and generic-mode fallback.
  Published runtime examples are Hopper.
  Google thermal thresholds are A3-only.
  Measure the exact DCGM version, plugin eligibility, duration, and calibrated-vs-generic status on the target rack.

- **NVLink-only device checks need exact GB300 semantics.**
  Public XID/DCGM sources establish health and counters broadly.
  They do not supply a complete GB300 NVL72 per-link counter acceptance matrix or local thresholds.
  Obtain platform/NVIDIA support guidance before you set hard limits.

- **No universal vendor thresholds.**
  Temperature, clock, power, and ECC historic counters depend on board profile/firmware and operating envelope.
  Derive rated baselines from a verified GB300 SKU configuration.
  Do not reuse A3's 87°C threshold as a GB300 limit.

- **One support article URL risk:** Search indexing directly covered the AWS re:Post URL and yielded exact guidance in snippets.
  But the AWS knowledge-center mirror redirected to a dead page during the fetch.
  Verify the live AWS page and version before you embed its recovery text in production runbooks.
