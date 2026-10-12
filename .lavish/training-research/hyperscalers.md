# Hyperscaler guidance for long training runs: preflight, recovery, and the two-hour limit

Research date: 2026-10-11. All claims below use a source URL.

Labels: **[observed]** — a cited source makes the claim; **[calculated]** — arithmetic from cited values; **[inference]** — bounded interpretation. This brief puts a GB300-class NVL72-class rack with 18 trays in Chennai in scope. Cloud recipes show operational mechanisms. They do not make a certification for this rack. They do not show matching hardware, topology, drivers, software, or failure behavior.

## 1. Executive answer: what two hours can and cannot establish

### 1.1 The useful claim

[Inference] A two-hour bench can show a specified stack at a specified scale and rank layout. The workload must run reproducibly. The workload must show correct loss and state behavior. It must show useful throughput and observable telemetry during the test window. The bench can check checkpoint creation and read-back/restore. It can run a controlled process restart and show recovery time.

It cannot show 54-day survival. It cannot show future power, network, or storage stability. It cannot show provider replacement capacity or usable termination notice. It cannot show coverage of the run by a 30–90 day lease. [Source basis for measurable checkpoint/restart scope: AWS auto-resume](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events).

[Observed] AWS guidance shows node health/replacement as separate from job restart at the last saved checkpoint. Google TPU guidance shows checkpoint recovery as essential. It also shows edge cases in automatic recovery. Google GPU maintenance documentation shows GPU-family-specific notice windows. It shows that attached-GPU VMs make a stop, not a live migration. Sources: [AWS HyperPod recovery](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html), [Google TPU maintenance](https://docs.cloud.google.com/tpu/docs/maintenance-events), [Google GPU maintenance](https://docs.cloud.google.com/compute/docs/instances/live-migration-process).

### 1.2 Relevant arithmetic, not reliability extrapolation

[Calculated] The tenant scenario uses a 54-day run and a 30–90 day lease. Two hours makes 120 minutes: 1/648 of 54 days, 1/360 of 30 days, and 1/1080 of 90 days. These fractions show exposure only, not reliability estimates. Even zero observed faults in two hours cannot make a meaningful claim about rare faults across weeks. Such a claim must use a justified statistical model and representative independent exposure. [Scenario basis: task context; AWS capacity-period caveat](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html).

[Inference] Keep this in the certifiable output: “measured X for Y minutes on workload/configuration Z,” not “will complete a 54-day run.”

The tenant must still keep a recovery design and capacity/lease terms. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

## 2. What hyperscaler guidance tells tenants to check

### 2.1 AWS: health checks are not the same as resumable training

[Observed] SageMaker HyperPod Slurm recovery guidance shows two distinct mechanisms. Automatic node recovery makes a reboot/replace action on faulty infrastructure. Auto-resume makes a training restart from the last saved checkpoint after failures. Recovery triggers can make use of health-monitoring agent findings, basic checks, and deep health checks. [AWS HyperPod resiliency](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm.html); [automatic node recovery and auto-resume](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html).

[Observed] The AWS documentation shows NVIDIA SMI checks for GPU health and EFA connectivity tests with all available EFA cards. The specific recovery path keeps a conditional status. Slurm GRES allocations can make in-place allocation changes impossible. HyperPod can then put the faulty job back in the queue and start the job again from the beginning. A job with a supported auto-resume arrangement does not run this path.

The AWS guide puts four user instructions in place. Use an exclusive allocation and a single `srun` entrypoint. Make the environment again on replaced nodes. Do not use a potentially stale `SLURM_JOB_NODELIST` after resumption. [AWS auto-resume guide](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html).

[Inference] The tenant checks the intended deployment: exact scheduler, GRES, launcher, retry mode, node replacement action, checkpoint restore path. The label “Automatic recovery enabled” does not show proof of resume at the latest valid checkpoint for this tenant job. A bench can check the job’s restart behavior with a controlled worker/process interruption. It cannot show AWS-specific service automation on an independently operated rack. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### 2.2 Azure: health agents, scheduler state, and topology are operational configuration

[Observed] The Azure public CycleCloud Slurm project shows a Healthagent daemon and Slurm `HealthCheckProgram`. These components can put nodes in drain state on health errors. The project configuration runs checks on a 60-second interval, across node states by default in that project documentation. Monitoring can show Node Exporter, NVIDIA DCGM exporter, and AzSlurm scheduler metrics. The AzSlurm exporter shows job terminal states/reasons, node states, provisioning/quota availability, and scheduler-cycle metrics. [Azure CycleCloud Slurm project](https://github.com/Azure/cyclecloud-slurm).

[Observed] The Azure Slurm project shows topology generation with VMSS, Fabric Manager/SHARP, and NVLink-domain options. Its warning shows this: autoscaling does not make topology part of its calculations. Autoscaling also does not put new topology in place.

The GB200/GB300-specific `scale_m1` procedure makes three requirements in a strict order. The order runs: rack-aligned scaling, block topology generation and installation, then Slurm block topology plugin start. This procedure shows a concrete software/topology example with direct relevance. It does not show a topology-semantics match for a Chennai NVL72 rack. [Azure project: topology and GB200/GB300 scale_m1](https://github.com/Azure/cyclecloud-slurm#scaling-with-scale_m1-gb200gb300).

[Observed] Microsoft’s CycleCloud Slurm reference shows `slurm.resume_timeout` with a default of 1800 seconds. It shows `slurm.hpc` placement behavior for tightly coupled MPI nodes. These examples show node startup and placement as configured operational parameters, not instantaneous guarantees. [CycleCloud Slurm integration](https://learn.microsoft.com/en-us/azure/cyclecloud/slurm?view=cyclecloud-8).

[Inference] The tenant keeps the exact Azure Slurm/CycleCloud project version and configuration on record, and sends the provider these questions. Which checks put nodes in drain state? Do the checks use intrusive methods? How often do the checks run? Can the tenant check health events? Which topology does the project keep static, and which topology does autoscaling make?

The current GitHub project README shows a moving project, not a contractual SLA. The Microsoft Learn page shows legacy examples and defaults. Current project versions can use different values. Check version/date before the tenant uses the settings. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### 2.3 Google: checkpoint frequently, but know the restart boundary

[Observed] Google’s Cloud TPU maintenance guide shows checkpoints approximately hourly as a rule of thumb. Save time can run from seconds to minutes. TPU jobs can make an automatic recovery from most maintenance events. Edge cases can make deletion/recreation of TPU resources and a restart from a saved checkpoint necessary. The guide shows two recommendations: training-script retries only together with checkpoints, and records of maintenance events. [Google Cloud TPU maintenance events](https://docs.cloud.google.com/tpu/docs/maintenance-events) (page updated 2026-10-09).

[Observed] Google Cloud’s Multi-slice description shows this: training jobs can make a restart from a previous checkpoint after slice failures. GKE can make job retries after errors. The description shows coordination across intra-slice ICI and inter-slice data-center networking. That description shows a product/example, not a measured guarantee for arbitrary GPU racks. [Google TPU Multislice overview](https://cloud.google.com/blog/products/compute/using-cloud-tpu-multislice-to-scale-ai-workloads).

[Observed] Google shows this for Compute Engine VMs with GPUs: no live migration during maintenance. The VMs must make a stop; a restart after the stop keeps an optional status. Google puts notice at 60 minutes for most GPUs but 10 minutes for A4X, A4, and A3 Ultra. Do not put these exact figures on unrelated SKUs. Do not make a notice into a hardware failure warning. [Google live migration and GPU limits](https://docs.cloud.google.com/compute/docs/instances/live-migration-process) (updated 2026-10-09).

[Inference] The tenant checks checkpoint completeness and restore on the actual intended storage path. A mere save-call return does not show completeness. The tenant checks signal handling and termination-notice consumption. The tenant checks the graceful-stop deadline, retry behavior, and provisioning/restart duration.

The hourly checkpoint interval shows a vendor rule of thumb, not a universal optimum. Use checkpoint duration, expected interruption exposure, storage cost, and acceptable lost work for the interval choice. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

## 3. Lease duration, interruption notice, and capacity are separate questions

### 3.1 Capacity reservation can end the job on schedule

[Observed] AWS shows this: Capacity Blocks put GPU capacity in reserve for a defined future period. AWS shows P5/P5e and other listed instance families on the blocks in only selected regions. Region/SKU and reservation conditions put limits on availability. A Capacity Block runs until 11:30 UTC; instance termination starts at 11:00 UTC on its final day. AWS shows this as predictable capacity assurance for the reserved period, not perpetual capacity. [AWS EC2 Capacity Blocks](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html).

[Observed] AWS PCS documentation shows instance termination at Capacity Block expiry. Depending on Slurm settings, active jobs cannot always keep running. The compute node group keeps its place, but it cannot start new instances from the expired block. [AWS PCS Capacity Block expiration](https://docs.aws.amazon.com/pcs/latest/userguide/capacity-blocks.html).

[Inference] The tenant checks the complete run plan against the exact lease end and termination policy. The complete run plan shows these parts: setup, validation, checkpointing, pauses, and recovery reserve.

A 30-day lease alone does not make sufficient cover for a 54-day continuous run. The cover must use documented extension/replacement capacity and tested restart semantics. Even a 90-day lease puts the slack before overhead at less than 36 days for a nominal 54-day run. That arithmetic shows nothing about capacity or performance. [Scenario basis: task context; AWS documents reservation end/termination semantics](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html).

### 3.2 Replacement capacity and topology may change

[Observed] Google’s AI Hypercomputer capacity documentation shows reservation-bound options, future-reservation limits for supported types, and managed recovery modes. The managed recovery modes make automatic replacements of faulty machines. The documentation shows a warning: replacement can put a different topology in place. [Google AI Hypercomputer consumption models](https://docs.cloud.google.com/ai-hypercomputer/docs/consumption-models); [reserve capacity](https://docs.cloud.google.com/ai-hypercomputer/docs/reserve-capacity).

[Inference] The provider must send written answers to four questions. Does the provider keep a replacement-hardware guarantee for the entire tenant term? Does replacement keep rack/switch/NVLink/fabric topology intact? Does replacement capacity keep the same SKU and software baseline? Does repair/replacement use up paid lease time?

Two-hour rack tests can show current rank mapping and gross topology/configuration issues. They cannot show future replacement availability or stable placement. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### 3.3 Notice is useful only if the workload handles it

[Observed] Google’s GPU maintenance notice examples show 60-minute and 10-minute windows by family. GPU instances make a stop, not a live migration. Google TPU guidance separately shows the monitoring of maintenance notifications and the use of autocheckpointing/checkpoint restore. [Google GPU maintenance](https://docs.cloud.google.com/compute/docs/instances/live-migration-process); [Google TPU maintenance](https://docs.cloud.google.com/tpu/docs/maintenance-events).

[Inference] The tenant sends questions about event semantics: planned maintenance versus emergency fault. The tenant sends questions about the notice channel, the minimum notice, and the allowed actions. Does the notice make it to the job? Can the tenant make a complete checkpoint within that window?

A short test can send a software-level termination signal. It can show the checkpoint-and-exit time. It cannot check the provider’s real notice delivery or minimum notice without that mechanism in the tested environment. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

## 4. Failure mechanisms and concrete tenant checks

### 4.1 Health screening: detect bad parts before allocating ranks

[Observed] AWS shows GPU and EFA checkers. Azure’s project shows health agents that can put labels or drain states on nodes. The operational pattern shows error detection and unhealthy-node exclusion before or during scheduling. The pattern makes no promise of zero new faults. [AWS recovery](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Azure CycleCloud Slurm project](https://github.com/Azure/cyclecloud-slurm).

[Inference] Bench candidate: after the existing burn-in, the bench keeps records of per-GPU error/health telemetry and ECC/XID counters. The bench also keeps records of link state, fabric errors, PCIe/NVLink status, temperatures/power/throttling, kernel logs, and scheduler-visible health state. The bench checks the exclusion of a suspect node from allocation.

Use safe, non-destructive signals and agreed operational procedures. A 2-hour PASS shows a snapshot plus a short trend, not latent-defect screening over weeks. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### 4.2 Distributed correctness: a running step counter is not correctness

[Inference] Run a representative distributed training script at full rack scale. Keep records of rank/world-size, global batch, data-parallel/tensor/pipeline layout, and collective completion. Keep records of loss, tokens/second, and per-rank progress. Check loss for finite values, and check that loss runs within the expected tolerance. Where feasible, check the results against a known-good reference/configuration.

Run an all-reduce/checksum or a deterministic small validation batch before/after checkpoint restore. Success shows valid progress by the workload and participation from all ranks. Success does not show convergence of a 54-day optimization to a target model quality. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

[Observed] Google shows different communication paths for Multislice: intra-slice ICI and inter-slice DCN, with collectives and hierarchical communication. AWS shows EFA connectivity checks. These sources show the importance of network path/topology and the workload’s communication pattern. Neither source makes a small-scale pass proof of different scale/topology performance. [Google Multislice](https://cloud.google.com/blog/products/compute/using-cloud-tpu-multislice-to-scale-ai-workloads); [AWS auto-resume](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html).

### 4.3 Checkpoint integrity, durability, and restart time

[Inference] Bench candidate: make a realistic checkpoint with model, optimizer, scheduler, RNG, and dataloader/sampler position. Put global step and any framework-specific state in the checkpoint too. Check the manifest, size, checksum, and atomic commit semantics. Run a read-back of the checkpoint in a fresh process. Make a resume, and check the expected step/loss/data position.

If supported, run an interrupted or partial-write scenario safely. Remove incomplete checkpoints from the selection. Check checkpoint wall time and restore wall time. Check the data-loss window: steps since the last committed checkpoint. Check the end-to-end time to useful training throughput after the restart. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

[Observed] Google shows checkpoint times from seconds to minutes. Google shows recovery from the saved checkpoint. AWS auto-resume likewise makes a restart from the last saved checkpoint. Its GRES caveat can make a restart from the beginning necessary. [Google TPU maintenance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [AWS auto-resume](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html).

[Inference] Durability and a successful local write keep separate statuses. Check the actual persistent/shared/object storage target, its permissions, its capacity, and its concurrent access. Check the retention/replication contract. A two-hour test can run a read-back of a just-written checkpoint. It cannot show months-long retention, protection against correlated site/storage loss, or contractual durability. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### 4.4 Rank mapping, data pipeline, and monitoring

[Inference] Bench candidate: keep a record of the rank-to-tray/GPU/NIC mapping. Check the expected rank count, unique ranks, GPU visibility, affinity, local/remote link paths, and collective traffic.

Keep records of step-time distributions, per-rank skew, and GPU utilization. Keep records of network utilization/retries, storage throughput/latency, and CPU utilization. Keep records of dataloader wait time, queue depth, and input-cache behavior.

Use representative dataset reads and enough warm/cold data to make obvious stalls visible. Keep metric records at a cadence that shows stall/step-time-spike correlation. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

[Observed] Azure’s project shows node/GPU/scheduler metrics and topology tooling. It also shows an explicit limitation: autoscaling can run without a topology update. [Azure CycleCloud Slurm project](https://github.com/Azure/cyclecloud-slurm). Google’s Multislice system uses the known ICI/DCN hierarchy for communication. [Google Multislice](https://cloud.google.com/blog/products/compute/using-cloud-tpu-multislice-to-scale-ai-workloads).

[Inference] The bench can show a current mapping error or an obvious slow rank. It can show repeated input stalls, low GPU busy time, and missing/uncorrelated monitoring. It cannot show behavior for a different dataset, cache state, or checkpoint frequency. It cannot show behavior for different model parallelism, training framework version, or tenant-side preprocessing code. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

## 5. Recommended two-hour training category protocol

### 5.1 A bounded test plan

[Inference] Keep the training category’s ~120 minutes for a defined, versioned tenant-like workload. Do not make a generic vendor “training ready” claim. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

1. Keep a record of image/container digest, driver/runtime/framework versions, firmware/config, model/test configuration, exact tray/GPU/rank layout, scheduler settings, and dataset/storage path.

2. Run a brief distributed preflight.
Check every expected rank for visibility.
Check collective correctness and connectivity.
Check a representative data batch and finite loss.
Check for no unexplained health/error counters.

3. Run a sustained workload for step-time and utilization distributions across warm-up and steady state.
Show medians and tails, not a single peak.
Check outlier steps against GPU, network, storage, CPU, and dataloader signals.

4. Make a realistic checkpoint, and check it for completeness and readability.
Run a controlled worker/process stop/relaunch, then a restore.
Keep the training in progress after the restore.
Check checkpoint duration, restore time, lost steps, and time back to steady useful progress.

5. Send a report of every intervention, anomaly, retry, and excluded component.
Do not put a repaired/retried run behind a PASS.
Send per-run outcomes and the final state in the report.

[Inference] Workload/checkpoint size makes the exact time split. A realistic checkpoint can use a substantial part of the two hours. In that case, remove other test scope. Do not put a tiny checkpoint in its place with an equivalence claim. Show the test result as a screened configuration, not a lease-level reliability verdict. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### 5.2 Suggested PASS language

[Inference] “Measured on [date] for [duration] using [configuration/workload]. All N ranks completed [steps/tokens]; loss was finite and within [declared bounds]; observed throughput/step-time distribution was [metrics]; [checkpoint] was written, verified, restored, and training resumed in [time], with [steps] of progress lost; observed health/error counters were [results]. This does not establish multi-week availability, replacement capacity, checkpoint durability beyond the tested target/period, or 54-day completion.” [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

## 6. Policy, empirical evidence, and extrapolation are different

### 6.1 Policy and feature documentation

[Observed] Service documentation shows capacity reservation windows, configured health agents, termination notice rules, and auto-resume functionality as policies/features. These policies/features show the mechanisms under specified conditions. They do not show the rack’s measured reliability. Examples: [AWS Capacity Blocks](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html), [AWS HyperPod recovery](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html), [Google GPU notice behavior](https://docs.cloud.google.com/compute/docs/instances/live-migration-process).

### 6.2 Empirical evidence

[Inference] Make rack-bench evidence its own measured record. The record shows observed errors, rank/step progress, throughput distribution, and monitored stalls. It also shows checkpoint/restore behavior, restart time, the test workload, and the exact tested configuration. A vendor recipe or health-agent status does not make that measurement. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### 6.3 No unsupported GB300 extrapolation

[Observed] Azure’s public CycleCloud Slurm project shows GB200/GB300-specific topology and `scale_m1` instructions. The instructions show Azure’s software/project workflow. [Azure GB200/GB300 Slurm scaling](https://github.com/Azure/cyclecloud-slurm#scaling-with-scale_m1-gb200gb300).

[Inference] This source shows rack-aware rank mapping and topology setup as operational concerns for this class of hardware. It does not show that the Chennai 18-tray rack makes a match or a pass against Azure’s implementation. AWS P5/P5e, AWS EFA, Azure ND, Google A3, and Google TPU recipes keep platform-specific scope. They do not make interchangeable specifications for GB300 NVL72. Keep a finding only where the specific tested hardware, firmware, fabric, scheduler, driver, framework, and workload show a match. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

## 7. Tenant due-diligence questions before signing 30–90 days

1. **Duration and interruption:** What guaranteed start/end time does the lease show? What does lease expiry put an end to? Can the tenant make a lease extension? What result does the boundary make for a running job? AWS Capacity Blocks show the importance of exact end-of-block semantics. [AWS Capacity Blocks](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html).

2. **Notice and action:** Which event types send a notice? Which channel does the notice use? What minimum notice does the provider send? Can tenant code make a checkpoint/exit before termination? Google shows GPU notices by family, not a universal GPU rule. [Google maintenance](https://docs.cloud.google.com/compute/docs/instances/live-migration-process).

3. **Replacement:** Does the provider keep capacity in reserve for replacement nodes for the full term? Can a replacement make changes to tray/rack/fabric topology, GPU count, software baseline, or rank mapping? Does the contract make replacement downtime billable? [Google AI Hypercomputer capacity/recovery](https://docs.cloud.google.com/ai-hypercomputer/docs/reserve-capacity).

4. **Recovery semantics:** Does recovery make a node reboot/replacement, a job restart, or only a requeue? Does the job make a resume from the latest committed checkpoint or the beginning? Which scheduler/GRES/launcher configurations can the job use? [AWS auto-resume limitations](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html).

5. **Checkpoint:** Which state does the checkpoint keep, and what storage does it use? How often does the job make a checkpoint commit? What durability/retention does the contract put in place? What restore time does the demonstration show? Google shows roughly hourly checkpoints as a starting point, not a service-level promise. [Google TPU checkpoint guide](https://docs.cloud.google.com/tpu/docs/maintenance-events).

6. **Observability and escalation:** Can the tenant check job, GPU, fabric, storage, dataloader, health-agent, and maintenance events with timestamps? Who puts nodes in drain state or makes node repairs? What response-time commitment does the provider show? Azure’s published monitoring examples show useful metrics, but they do not make an SLA for this rack. [Azure project](https://github.com/Azure/cyclecloud-slurm).

## 8. Findings in brief

1. [Inference] Two hours can make a measured workload/configuration screen, distributed correctness check, short performance/stall profile, and checkpoint/restore/restart measurement. It cannot show 54-day survival.

2. [Observed] AWS explicitly shows node recovery and job auto-resume as separate items. AWS also shows configurations that can put the restart at the beginning, not at the latest checkpoint. [AWS guide](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html).

3. [Observed] Google shows a recommendation for frequent checkpoints. Google shows GPU maintenance notice and stop behavior with variation by GPU family. TPU recovery can still make resource recreation and restart necessary. [TPU guide](https://docs.cloud.google.com/tpu/docs/maintenance-events); [GPU guide](https://docs.cloud.google.com/compute/docs/instances/live-migration-process).

4. [Observed] Lease/capacity end semantics can put an end to active jobs. The tenant must check exact reservation duration and replacement capacity independently of rack health. [AWS Capacity Blocks](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html); [AWS PCS](https://docs.aws.amazon.com/pcs/latest/userguide/capacity-blocks.html).

5. [Inference] Keep PASS scoped to the measured rack/workload/configuration. Show the specific tested checkpoint/restart result in the PASS disclosure. Never make hyperscaler documentation or a two-hour PASS into an unsupported GB300 reliability claim.

## Sources and confidence

- **High confidence, primary vendor documentation:** AWS HyperPod recovery and EC2 Capacity Blocks. Google Cloud TPU and Compute Engine maintenance docs. Microsoft Learn CycleCloud Slurm reference. These sources show mechanisms and stated limits directly.

- **Moderate confidence, primary but version-sensitive project documentation:** Azure `cyclecloud-slurm` GitHub README. It shows unusually concrete topology, health, and monitoring details, including the GB200/GB300 workflow. The repository can show new content at any time. Keep the release/commit on record before operational use.

- **Lower confidence for empirical reliability:** None of these materials show an independently measured reliability rate. The materials show no such rate for the tenant’s 54-day scenario or this Chennai rack. The task scenario, not these vendor sources, puts the 54-day duration in place. Product feature descriptions and vendor examples do not make empirical outcomes for the subject system.

## 9. Seeded primary preflight recipes: concrete checks to borrow, not hardware equivalence claims

The following sections show provider-authored procedures for the named platforms. A **[Proposal]** label shows a candidate rack-bench check made from those recipes. The label does not show a vendor requirement, a certified GB300 procedure, or an inferred performance threshold. Keep the tested image/container and software versions in every result. The sources keep live-documentation status; version-specific values below show snapshots of the pages checked on the research date.

### 9.1 AWS P5/P5e: EFA/NCCL setup, tests, and important version caveats

[Observed] EC2’s primary “Get started with EFA and NCCL” guide shows a full setup walk-through. The walk-through shows an EFA-enabled security group, supported OS/instance setup, GPU/CUDA/cuDNN, GDRCopy, and EFA software. It also shows NCCL, `nccl-tests`, and a multi-GPU MPI-launched `all_reduce_perf` test.

EFA must use self-referencing inbound/outbound security-group rules. The example shows its broad SSH rule as explicitly testing-only.

The sample checks EFA provider selection from NCCL logs (`NET/OFI Selected Provider is efa*`). It shows cluster placement groups as a suggestion for low latency in a single AZ. It shows placement groups as recommended rather than mandatory. [AWS EC2 EFA+NCCL recipe](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html).

[Observed] The AWS recipe’s page currently shows these values in its generic installation example. The values: EFA installer `1.50.0`, NCCL `2.30.4-1`, and CUDA path `/usr/local/cuda-13`. The recipe makes EFA-compatible NCCL (2.4.2+) a requirement.

Its sample `mpirun` uses the export `FI_EFA_USE_DEVICE_RDMA=1`. It starts NCCL debug logging. It runs `all_reduce_perf` across eight GPUs. Put instance-appropriate `-n`/`-N` values in the command.

Those generic current values do not make a P5/P5e-specific supported matrix. Check them against the actual AMI, instance type, PyTorch-bundled NCCL, and EFA installer release. [AWS EC2 EFA+NCCL recipe](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [AWS EFA-supported libraries](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html).

[Observed] AWS’s current GPU quickstart matrix shows distinct driver/CUDA/EFA/NCCL combinations by SKU. Its page search extract shows P5 at driver 530/CUDA 12.1/EFA 1.24.1/NCCL 2.18.3. It shows P5e at driver 550/CUDA 12.1/EFA 1.24.1/NCCL 2.18.3. It shows P5en similarly at driver 550/CUDA 12.1/EFA 1.24.1/NCCL 2.18.3.

The page separately shows a P5.4xlarge EFA/NCCL GPU-to-GPU compatibility issue. The mitigation uses EFA 1.43.1+ and `FI_HMEM_DISABLE_P2P=1`. Do not put that P5.4xlarge-specific workaround on P5.48xlarge, P5e, or another platform automatically. Check the live SKU table and release notes before freeze. [AWS GPU setup/version matrix](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/gpu-instances-started.html).

[Observed] AWS’s SageMaker EFA container guidance shows these container requirements: EFA/Libfabric/Open MPI and its own MPI/NCCL stack. With PyTorch, keep the container NCCL version at the PyTorch NCCL version (`torch.cuda.nccl.version()`). The guidance shows an EFA-recognition check with `fi_info -p efa`. It shows this split: TCP control/peer traffic can use ENI; kernel-bypass OFI traffic uses EFA. [AWS SageMaker EFA container guidance](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-efa.html).

[Proposal] On the tested rack, keep records of `nvidia-smi` output and driver/CUDA/runtime/framework/NCCL versions. Put `torch.cuda.nccl.version()` in the version records. Keep records of `fi_info -p efa` or the actual fabric’s equivalent inventory, loaded NIC/RDMA libraries, and container-visible device mappings.

Keep NCCL debug logs that show the selected transport/provider. Do not put an assumption about the intended path in their place.

Run a collective correctness test at rack scale with the actual launcher and rank count. Run a short representative distributed training step too.

Use AWS’s EFA commands as examples only. This rack does not necessarily use EFA, Libfabric, AWS’s plugin, security groups, or placement groups. Source basis: [AWS EC2 recipe](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html), [AWS container guidance](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-efa.html).

### 9.2 Azure ND: InfiniBand, NCCL and node health

[Observed] Microsoft’s current ND H100 v5 SKU page shows each VM with eight H100 GPUs. It shows NVLink 4.0 inside the VM. It shows eight dedicated topology-agnostic 400 Gbps NVIDIA Quantum-2 CX7 InfiniBand connections, with GPU Direct RDMA.

It shows cross-VM connections as automatically configured for VMs in the same VM scale set. It shows InfiniBand as supported and Live Migration as not supported. It shows ND H100 v5 product facts, not NVL72 facts. [Azure ND-H100-v5 specifications](https://learn.microsoft.com/en-us/azure/virtual-machines/nd-h100-v5-series).

[Observed] Azure’s current `cyclecloud-slurm` project README shows Healthagent on nodes and Slurm health check/drain behavior. In that project, the configured Slurm check runs Healthagent at a default 60-second cadence.

The README also shows NVIDIA DCGM, Node Exporter, and AzSlurm exporters. These show job terminal reasons, node state, available partition capacity, and scheduler metrics.

Configuration keeps version sensitivity. The README shows project version 4.x and the `slurm.enable_healthchecks` toggle. Check the exact project release and deployed Slurm config. Do not put values from old CycleCloud examples into the configuration. [Azure CycleCloud Slurm project, health and monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks); [Microsoft CycleCloud Slurm integration](https://learn.microsoft.com/en-us/azure/cyclecloud/slurm?view=cyclecloud-8).

[Observed] Azure’s public CycleCloud Slurm project shows topology generation. Its warning shows this: autoscaling does not make topology part of its calculations. Autoscaling also does not put new topology in place. It also shows a GB200/GB300 `scale_m1` workflow with rack/block topology and `TopologyParam=BlockAsNodeRank`. That workflow shows this Azure project’s deployment mechanics, not the topology of this Chennai rack. [Azure topology and scale_m1](https://github.com/Azure/cyclecloud-slurm#scaling-with-scale_m1-gb200gb300).

[Proposal] For an ND-inspired preflight, keep records of actual node/SKU, GPU count, and driver/CUDA/NCCL/MPI/PMIx versions. Keep records of `nvidia-smi topo -m`, GPU↔NIC/RDMA device association, and link state/rate. Keep records of Slurm node/GRES, rank mapping, topology file/plugin, and placement boundaries.

Run the same NCCL collective across one node and all allocated nodes. Keep a record of the selected path against the expected InfiniBand/GPU-direct path. Also keep records of correctness/error count, bus bandwidth, and per-rank skew.

Keep Healthagent/Slurm drain and DCGM/host metrics with timestamps in the record. Anchors: [ND H100 v5](https://learn.microsoft.com/en-us/azure/virtual-machines/nd-h100-v5-series), [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks), [Azure topology](https://github.com/Azure/cyclecloud-slurm#topology).

### 9.3 Google Cloud A3 Mega: Cluster Toolkit deployment and NCCL preflight

[Observed] Google’s A3 Mega Slurm deployment guide makes Cluster Toolkit `v1.62.0` or later a requirement. It also makes capacity/consumption planning and a minimum 10 TiB HIGH_SCALE_SSD Filestore quota requirements for that blueprint.

It shows NCCL-test validation of provisioned clusters as a recommendation. It also shows a Slurm deployment blueprint. The guide shows A3 Mega’s availability and machine-type limitations.

These requirements put their scope on its A3 Mega blueprint, not on a rack certification checklist. [Google A3 Mega Slurm deployment](https://docs.cloud.google.com/cluster-toolkit/docs/deploy/slurm/deploy-a3-mega-cluster).

[Observed] Google’s A3 Mega GPUDirect-TCPXO guide makes Cluster Toolkit v1.51.1+ a requirement for the documented cluster. It shows topology-aware scheduling for clusters created with v1.39.0+. It shows Slurm prolog/epilog behavior in detail. The steps: check `import-helper`, put the NCCL net plugin in place, start/stop RxDM.

RxDM startup can use 10–20 seconds. For single-node jobs, the GPUDirect-TCPXO plugin without RxDM can run into a timeout. Google shows `NCCL_NET_PLUGIN=none` as its recommendation for that case. RxDM configuration for all jobs makes the alternative.

The guide shows an `nccl-tests` build/run under Slurm, eight GPUs per node. It checks collective output including `#wrong` and out-of-bounds counts. [Google A3 Mega GPUDirect-TCPXO/NCCL guide](https://docs.cloud.google.com/cluster-toolkit/docs/machine-learning/a3-mega-enable-gpudirect-tcpxo).

[Proposal] For an A3-inspired but hardware-neutral preflight, start with a precise device and topology list. The list shows per-rank GPU, NIC, and tray mapping. It also shows effective Slurm `NodeList`, `SLURM_PROCID`/local rank, world size, and GPUs per node. It shows topology/rank order and all relevant environment variables.

Then run NCCL tests at intra-node and full-rack scope with the production launcher/container. Check collective correctness (`#wrong`/out-of-bounds zero). Check the expected network plugin/path, no timeout, and stable per-rank participation.

Run a short training step with the same image and environment. Keep the logs.

On this rack, use its actual fabric/plugin names. Do not use Google-specific `NCCL_NET_PLUGIN` values. Remove the RxDM expectation unless the rack actually uses those components. Sources: [Google deployment guide](https://docs.cloud.google.com/cluster-toolkit/docs/deploy/slurm/deploy-a3-mega-cluster), [Google NCCL/TCPXO guide](https://docs.cloud.google.com/cluster-toolkit/docs/machine-learning/a3-mega-enable-gpudirect-tcpxo).

### 9.4 Cross-provider preflight record for this rack [Proposal]

[Proposal] Put the following evidence fields in the two-hour training result. These fields show practical proposed observations from the cited AWS EFA, Azure ND/CycleCloud, and Google A3 recipes. They do not make claimed vendor requirements or thresholds. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

- **Identity and versions:** rack/tray inventory; GPU model/count; OS/kernel; BIOS/BMC/firmware; driver; CUDA; NCCL. Also: framework and PyTorch-bundled NCCL; MPI/PMIx; scheduler; container digest; fabric plugin/driver. Keep exact output and timestamp records. [AWS version compatibility guidance](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-efa.html); [AWS GPU matrix](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/gpu-instances-started.html).

- **Topology and ranks:** GPU/NIC/RDMA visibility; `nvidia-smi topo -m` or platform equivalent; rank-to-tray/GPU/NIC mapping; expected/actual world size. Also: local rank and global rank uniqueness; Slurm node list/GRES; topology file/plugin; launcher command and environment. [Azure topology tooling](https://github.com/Azure/cyclecloud-slurm#topology); [Google A3 blueprint/NCCL test](https://docs.cloud.google.com/cluster-toolkit/docs/machine-learning/a3-mega-enable-gpudirect-tcpxo).

- **Transport and collective correctness:** show the actual selected NCCL network plugin/provider in debug logs. Run representative collective sizes intra-node and across all 18 trays. Keep throughput/latency and correctness counters in the record. Put the run in a FAIL state on hangs, mismatched ranks, or reported wrong elements. Do not put advertised link rate in place of a measured result. [AWS EFA test](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [Google NCCL test](https://docs.cloud.google.com/cluster-toolkit/docs/machine-learning/a3-mega-enable-gpudirect-tcpxo).

- **Health and monitoring:** keep pre/post health signal snapshots. Keep GPU error/temperature/power/throttle counters, link/fabric errors, kernel logs, and node drain state records. Check alert/timestamp alignment with a deliberately observed (non-destructive) event. [Azure CycleCloud health/metrics](https://github.com/Azure/cyclecloud-slurm#node-health-checks); [AWS HyperPod health checks](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html).

- **Workload and data path:** keep records of model/config, global and per-rank batch, sequence length, and dataset path/cache state. Keep records of dataloader workers, step-time distribution, useful tokens/s, and loss and data-wait time. Make a checkpoint/restore cycle on the tenant’s intended storage. These fields show proposed measurements, not claims of any cited vendor prescription for this exact schema. [Checkpoint motivation and intervals](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Google A3 training deployment](https://docs.cloud.google.com/cluster-toolkit/docs/deploy/slurm/deploy-a3-mega-cluster).

[Inference] These checks make configuration mistakes and short-run path/correctness failures visible. A zero-error collective test shows evidence only for the tested topology, versions, sizes, duration, and routes. A matching hyperscaler recipe does not show a shared topology, throughput, replacement policy, or long-term reliability for the rack. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).

### Source/version caveats

[Observed] The AWS EFA/NCCL primary guide now shows very recent generic toolchain values, including EFA 1.50.0 and NCCL 2.30.4-1. AWS’s SKU matrix shows older distinct P5/P5e combinations.

This case does not necessarily make a contradiction. The recipe keeps generic scope, and the SKU matrix shows documented bundled/setup combinations. Check it against the exact tested AMI and compatibility matrix. Do not put numbers from different recipes together without validation. [AWS EFA+NCCL guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [AWS GPU matrix](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/gpu-instances-started.html).

[Observed] Google’s A3 documentation shows explicit version gates. Its current deployment guide makes Cluster Toolkit v1.62.0+ a requirement. The GPUDirect-TCPXO procedure shows v1.51.1+ for that feature.

Use the current deployment guide’s gate for a new deployment. Keep the exact toolkit/blueprint revision on record. The feature guide’s RXDM and environment behavior keeps A3 Mega-specific scope. [A3 deployment](https://docs.cloud.google.com/cluster-toolkit/docs/deploy/slurm/deploy-a3-mega-cluster); [A3 TCPXO guide](https://docs.cloud.google.com/cluster-toolkit/docs/machine-learning/a3-mega-enable-gpudirect-tcpxo).

[Inference] Keep all preceding policy caveats in view. Documented auto-recovery, notices, reservations, and retry features make policy/mechanism statements, not independent uptime measurements. Capacity can show SKU/region/time limits. A two-hour test cannot check multi-week durability or a future replacement pool.

§§3 and 7 show the exact Google GPU notice windows and AWS Capacity Block expiry behavior. These items keep their platform-specific status. Do not make them general for this rack. [Source basis: AWS checkpoint restart](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Azure health/monitoring](https://github.com/Azure/cyclecloud-slurm#node-health-checks).


## Gaps

- **No independent multi-week reliability comparison:** The reviewed primary documents show mechanisms and product policies. They do not show apples-to-apples observed failure rates for AWS P5/P5e, Azure ND, Google A3, or the Chennai rack. The 54-day duration keeps tenant-scenario status, not a vendor-validated guarantee. [AWS recovery](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html); [Google A3](https://docs.cloud.google.com/cluster-toolkit/docs/deploy/slurm/deploy-a3-mega-cluster).

- **Unresolved Azure ND recovery-notice limits.** The ND-H100-v5 SKU page shows InfiniBand support and no live migration. The reviewed sources do not show an ND-specific tenant checkpoint/restart limit or a guaranteed maintenance notice window. Do not use Google or AWS notice values. [Azure ND H100 v5](https://learn.microsoft.com/en-us/azure/virtual-machines/nd-h100-v5-series).

- **AWS version matrix makes SKU/image pinning necessary.** The current generic EFA recipe and AWS SKU setup table show different version contexts. Check the exact compatible versions for a chosen P5/P5e AMI, container, framework, and NCCL plugin against that image. Do this before use. This brief intentionally makes no single-universal-AWS-stack claim. [AWS EFA recipe](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [AWS GPU matrix](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/gpu-instances-started.html).

- **Unspecified rack-specific workload details.** Model size/configuration, optimizer state, dataset, checkpoint format/size, parallelism strategy, storage target, and target-quality criterion keep unknown status. These details can make the two-hour test sufficient or insufficient for a realistic checkpoint/restore. Meaningful correctness evidence also shows dependence on these details. The proposed record shows a template, not a calibrated acceptance threshold. [Google checkpoint guidance](https://docs.cloud.google.com/tpu/docs/maintenance-events); [Google A3 training guide](https://docs.cloud.google.com/cluster-toolkit/docs/deploy/slurm/deploy-a3-mega-cluster).

- **No unsupported hardware equivalence:** AWS EFA/P5, Azure ND-H100 InfiniBand, and Google A3 TCPXO examples keep platform-specific status. The tenant must not put these items on a GB300 NVL72-class rack automatically. The items: exact commands, environment variables, software versions, topologies, and failure behavior. [AWS EFA](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html); [Azure ND](https://learn.microsoft.com/en-us/azure/virtual-machines/nd-h100-v5-series); [Google A3](https://docs.cloud.google.com/cluster-toolkit/docs/machine-learning/a3-mega-enable-gpudirect-tcpxo).
