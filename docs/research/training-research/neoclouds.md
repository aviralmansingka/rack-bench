# Neoclouds: promises and evidence for multi-week training

Research date: 2026-10-11. All claims below use a source URL.

Claims use three labels: **[observed]**, **[calculated]**, and **[inference]**. An **[observed]** label shows a claim directly in cited material. A **[calculated]** label shows arithmetic from stated values. An **[inference]** label shows a bounded interpretation by this report.

Use “Availability” for provider/service uptime per its contractual definition. Use the term “run reliability” for the no-interruption completion probability for a customer job. Use the term “goodput” for useful completed training progress per paid GPU-hour. Do not use these terms interchangeably.

## 1. Executive answer: an SLA is not a 54-day run result

Source basis: [Crusoe screening](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you),
[CoreWeave terms](https://docs.coreweave.com/policies/terms-of-service),
[Nebius SLA](https://docs.nebius.com/legal/sla), and
[ClusterMAX observations](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard).
The conclusions below use these sources and the product evidence in §8.

- **[observed]** Public neocloud material makes three kinds of promise. The material shows monthly availability/credits, node qualification/monitoring, and failed-node orchestration. This report uses the term failed-node orchestration for detection, node replacement, and work resumption. These sources do not show fleet-level distributions of training-job interruptions, recovery duration, lost work, or successful 30–90-day completion. A 2-hour rack test can make a measured baseline and show immediate instability. It cannot show a 54-day survival probability or the provider's job recovery path over weeks.

- **[inference]** A tenant must check four points before a 30–90 day lease. First, check (a) rack health now and (b) job checkpoint/restart correctness. Then check (c) provider control-plane and replacement behavior and (d) historical interruption/recovery distributions for the exact SKU/site/topology. Public uptime targets chiefly make claims about a narrow definition of service availability. They do not show model progress or economic goodput.

- **[observed]** Public sources show few and heterogeneous quantitative-looking figures. Crusoe shows a 99.5% GPU-VM uptime SLA and a node-burn-in description. Nebius shows service-specific SLAs and a managed-Kubernetes node-autohealing description. CoreWeave’s retrieved terms show monthly uptime, exclusions, and remedy. The fetched current page extract does not show its numerical table. None of those sources shows a multi-week run-interruption dataset.

## 2. The three metrics buyers must keep separate

### 2.1 Advertised availability

- **[observed]** Crusoe’s burn-in article shows a **99.5% uptime SLA** for GPU-enabled VMs ([Crusoe burn-in article](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you)). The customer terms show the details. The SLA shows contractual monthly availability, not observed completion reliability for a distributed job.

- **[observed]** CoreWeave terms show monthly uptime as total month minutes minus downtime minutes, divided by month minutes. The terms show credits as the sole/exclusive remedy. The customer must send notice and logs. The terms remove certain upstream-carrier events and announced maintenance from downtime ([CoreWeave TOS](https://docs.coreweave.com/policies/terms-of-service)). The page shows last modified June 30, 2022; do not use it for a current numeric target. Check the current order form and the applicable regional terms.

- **[observed]** Nebius uses its SLA only for specific linked services and paid services ([Nebius SLA](https://docs.nebius.com/legal/sla)). Nebius makes the customer send unavailability reports; the process also uses customer cooperation. Specific service-level pages can show different terms. The disks page shows 99.50%, two-minute measurement intervals, service-specific exclusions, and credits ([Nebius disk SLA](https://docs.nebius.com/legal/sla-levels/disks)). Do not use a disk commitment as a GPU compute commitment.

- **[calculated]** For a service with constant availability p, the calculation 54×24×(1−p) shows expected unavailable time over 54 days. The calculation shows 6.48 hours at 99.5%, 12.96 hours at 99%, and 1.296 hours at 99.9%. These values show arithmetic illustrations only—not forecasts, confidence bounds, or job downtime. Events can show correlation, exclusion, or a different scope.

- **[inference]** Monthly aggregation does not show event count and duration. One outage and many short interruptions can make equal downtime but very different checkpoint loss and recovery overhead. Credits do not make the tenant whole for replay GPU-hours, failed optimizer steps, or missed completion dates. Only an express contract term makes a wider remedy.

### 2.2 Observed interruption statistics

- **[observed]** Crusoe uses Pinckney et al. (2024) for cluster-scale event rates ([Crusoe article](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you); [paper](https://arxiv.org/html/2410.21680v1)). The paper shows mean time between failures of roughly 47 days at 8 GPUs. It also shows 8 hours at 1,024 GPUs and 1.8 hours at 16,384 GPUs. These figures show research-cluster scale; they do not show Crusoe customer-run interruption statistics. Do not use them directly for an 18-tray GB300 rack. Check the paper scope and definitions first; do not use them directly as a prediction.

- **[observed]** Crusoe shows a distributed-job interruption sequence: failure detection, replacement provisioning, and rollback to the last checkpoint ([Crusoe article](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you)). Without checkpointing, interruptions can make substantial delays. The article shows no public denominator, per-run interruption histogram, checkpoint interval distribution, MTTR percentiles, or multi-week completion rate.

- **[observed]** The Nebius Q1 2025 update shows node autohealing in its managed Kubernetes service ([Nebius Q1 2025 updates](https://nebius.com/blog/posts/q1-2025-cloud-updates)). The update shows faulty-node replacement and training-interruption reduction as the feature’s purpose. The update also shows inline health checks for compromised-node identification and isolation. The announcement shows feature availability only; it does not show observed interruption reduction or a service guarantee.

- **[inference]** The sources show selected mechanisms and a few independently tested events. They do not show comparable provider-specific interruption rates or p50/p95 recovery distributions with job/GPU-hour denominators ([ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). The provider docs in §8 do not show them either.

## 3. Mechanisms that can protect training progress

### 3.1 Pre-admission screening and live health

- **[observed]** Crusoe shows per-node qualification across node, GPU, and fabric domains ([Crusoe burn-in article](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you)). The node/GPU checks use DCGM diagnostics, ECC, PCIe, sustained power, and pulsed power. Crusoe also runs storage performance/latency, NIC, and RDMA bandwidth checks, and multi-node NCCL/RCCL tests. Crusoe runs the tests in customer-like VMs. Crusoe puts failed nodes through repair/replacement and a retest. Crusoe runs targeted validation after upgrades.

  The article shows unusually specific public evidence of a mechanism. Crusoe makes this statement itself; no independent audit checks it.

- **[observed]** Crusoe shows AutoClusters for managed Kubernetes workloads ([Crusoe burn-in article](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you); [AutoClusters article](https://www.crusoe.ai/resources/blog/autoclusters-minimizing-hardware-failures-in-large-gpu-clusters)). AutoClusters checks node health. It makes replacements from a burn-in-validated spare pool, typically within minutes of detection. “Typically” does not show a measured percentile or guarantee. The article shows managed Kubernetes as the scope, not necessarily every bare-metal/Slurm offer.

- **[observed]** Nebius shows managed-Kubernetes health checks and node autohealing ([Nebius update](https://nebius.com/blog/posts/q1-2025-cloud-updates)). The public page does not show detection delay, replacement availability, or job-state preservation numbers.

- **[inference]** Preflight certification can check component health, sustained load, fabric collectives, and checkpoint-path write/read behavior. It cannot show fleet-wide spare exhaustion, control-plane outages, rare correlated power/network failures, or provider-side repair operations.

### 3.2 Checkpoint and restart are application/platform responsibilities

- **[observed]** Crusoe explicitly shows rollback to the last checkpoint as the recovery path for a distributed training job ([Crusoe article](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you)). The public article does not show checkpoint atomicity, optimizer/RNG/data-loader state, storage durability, or a mandatory checkpoint cadence.

- **[inference]** Providers put different meanings under “Auto-recovery”: node replacement, scheduler requeue, container restart, or complete training-state restoration. Only complete training-state restoration, with correct distributed coordination and durable checkpoint storage, starts useful learning again. Check each step’s owner and restored state with the provider and the tenant.

- **[inference]** Before a lease, a controlled kill/restart exercise shows stronger evidence than a promise. Make a real multi-rank checkpoint. Send a termination signal to one worker or the job. Start the documented requeue or restart path. Check the step number, optimizer state, scheduler state, RNG state, and data position, as applicable. Check checkpoint integrity and resumed loss/progress against the pre-kill record.

  Run the drill again from the actual shared checkpoint filesystem. A two-hour test can run this drill once or a few times. It cannot show a rare-event recovery distribution.

### 3.3 Spot/preemption and elastic restart

- **[observed]** Nebius can put preemptible VMs in a stopped state at any time ([Nebius preemptible docs](https://docs.nebius.com/compute/virtual-machines/preemptible)). Preemption sends SIGTERM 60 seconds before SIGKILL. The policy keeps attached volumes but removes local SSD data. The docs show no automatic `RECOVER` and no guaranteed availability. The reviewed records do not show comparable policies for CoreWeave, Lambda, and Together.

- **[inference]** For fixed-size synchronous LLM pretraining, elastic restart does not start automatically. One failed rank commonly makes an interruption in the collective job. A world-size change can make the optimizer and training semantics different. A tenant must check “Elastic” behavior for the exact framework, launcher, checkpoint format, and model configuration. This finding uses [PyTorch DCP recipe](https://docs.pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html) and [CoreWeave Slurm signal guide](https://docs.coreweave.com/products/sunk/run_workloads/handle-slurm-signals).

## 4. Provider evidence snapshot (public evidence, not provider ranking)

| Provider | What public evidence shows | What it does not show |
|---|---|---|
| **Crusoe** | **[observed]** Crusoe shows a 99.5% GPU VM uptime SLA claim. It shows detailed published pre-customer burn-in. AutoClusters node detection/replacement typically runs within minutes for managed Kubernetes ([burn-in article](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you)). | **[observed]** The cited material shows no public customer-run interruption denominator, run completion probability, MTTR percentile, or checkpoint recovery success rate. The burn-in description shows first-party evidence. |
| **Nebius** | **[observed]** Nebius shows a service-specific SLA framework; the disk SLA shows 99.50%. The Q1 2025 update shows managed K8s autohealing and inline health checks ([SLA](https://docs.nebius.com/legal/sla), [disk SLA](https://docs.nebius.com/legal/sla-levels/disks), [Q1 2025 update](https://nebius.com/blog/posts/q1-2025-cloud-updates)). | **[observed]** A disk SLA does not show a GPU/job SLA. The feature announcement shows no observed training interruption/recovery statistics. |
| **CoreWeave** | **[observed]** The terms show monthly uptime accounting, downtime and exclusions, support evidence, and credits/remedy ([TOS](https://docs.coreweave.com/policies/terms-of-service)). | **[observed]** The retrieved TOS shows an old (2022) version. The extracted page does not show a reliable current GPU SLA percentage. Check current SKU/region/order-specific terms; the cited material shows no run-interruption distribution. |
| **Lambda** | **[observed]** The [1CC docs](https://docs.lambda.ai/public-cloud/1-click-clusters) show multi-week reservations and attached Lambda filesystems, with ephemeral local NVMe. [ClusterMAX](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) shows bounded health-check and XID events (§8.3). | **[observed]** These sources show no job recovery contract and no shared-filesystem durability SLA. |
| **Together** | **[observed]** The [Storage docs](https://docs.together.ai/docs/gpu-clusters-overview) and [health docs](https://docs.together.ai/docs/health-checks) show persistent shared volumes and active/passive checks. [ClusterMAX](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) shows an active-job drain and replacement events (§8.4). | **[observed]** The sources show no comparable fleet statistics and no complete filesystem durability/backup contract. |
| **Others** | **[observed]** Provider marketing increasingly shows managed orchestration, health visibility, node replacement, and job resumption ([Crusoe training](https://www.crusoe.ai/cloud/solutions/model-training)). These claims show mechanisms for testing, not measured outcomes. | **[inference]** Do not put unlike managed-service and raw-instance claims into one reliability score. |

## 5. Economic GPU-hour goodput: availability is only one factor

Source basis: [Meta productive-time accounting](https://arxiv.org/html/2410.21680v1)
and [Crusoe checkpoint rollback](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you).
The calculations below show their assumptions.

- **[inference]** Use useful completed training progress / paid GPU-hours as a practical measure. A conceptual decomposition shows: productive fraction ≈ uptime × (1 − recovery/replay overhead) × useful-work efficiency. The decomposition does not show queueing, throttling, data stalls, or failed/invalid steps. Show those factors separately; do not make one universal formula from them.

- **[calculated]** The model uses checkpoint interval C and uniform failure timing between checkpoints. The model shows expected lost computation per failure of about C/2, before restart time. Shorter intervals make less replay but use more checkpoint I/O. This checkpoint I/O can make training stalls. The approximation uses periodic checkpoints and uniform failure timing.

- **[inference]** For a 54-day run, check offers on expected usable progress and downside tails, not the SLA credit alone. The comparison must show GPU rental cost during restart and replayed GPU-hours. It must show checkpoint storage, write stalls, replacement wait/queue, and the deadline-miss chance. The tenant must send a request for actual paid-versus-useful GPU-hour data from comparable runs. Do not use claimed uptime or peak benchmark throughput for this number.

## 6. Candidate two-hour checks for rack-bench (no multi-week claim)

Proposal basis: [CoreWeave checkpoint signals](https://docs.coreweave.com/products/sunk/run_workloads/handle-slurm-signals),
[Crusoe screening](https://www.crusoe.ai/resources/blog/how-crusoe-burn-in-tests-every-node-before-it-reaches-you),
and [ClusterMAX observations](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard).
The statistical limit uses the [Poisson model](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366j.htm).
The proposals do not show provider results.

1. **[inference] Make a continuous baseline:** Run representative distributed training/collectives for the full available window. Put timestamps on rank health and GPU XID, ECC, thermal, and power clocks. Put timestamps on NCCL errors/retries and link counters. Put timestamps on filesystem latency and checkpoint duration. Put timestamps on step time, loss, and completed tokens/steps. Show measured uptime only for this two-hour interval.

2. **[inference] Check the checkpoint path under load:** Make a representative checkpoint on the actual shared durable filesystem during ongoing training. Keep records of bytes, duration, throughput, latency, integrity/checksum, and all-rank agreement on the completed step. Run a read-back of the checkpoint and check it.

3. **[inference] Make a controlled restart/requeue:** With operator approval, send a termination signal to a test worker or job. Do not use hardware or power fault injection. Start the documented scheduler path. Check the timing from detection→reschedule→checkpoint-read→first-valid-step. Check exact state continuity and the absence of silent loss/corruption. Run the drill again only with available time.

4. **[inference] Keep host survival separate from job survival:** Check process, node, and fabric event timelines against each other. A clean smoke test does not show an SLA observation. A recovery demonstration does not show a measured provider-wide MTTR.

5. **[inference] Keep provenance.** Put the exact rack/SKU, software stack, scheduler, job shape/world size, checkpoint backend, and test start/end in the record. Keep all event logs and PASS criteria in the record. PASS shows the observed result only. Absence of failure in 2h does not show low multi-week failure probability.

### What two hours cannot certify

- **[inference]** One short test cannot make a meaningful direct estimate of rare multi-week failure probability. Even a zero-failure interval shows only weak evidence. Under a simplistic Poisson model, zero events over two hours make a 95% upper rate bound. The bound shows roughly 3/2 = 1.5 events/hour. The bound shows a range far too loose for multi-week inference. Real failures do not necessarily show Poisson or independent behavior.

- **[inference]** The test does not check spare capacity under simultaneous regional incidents, control-plane availability, or upstream power/cooling/transit resilience. It does not check long-run thermal drift, firmware/maintenance changes, or provider staffing/repair quality. It does not check a 54-day storage-retention guarantee.

- **[inference]** Make no inference from a successful small-scale or short synthetic workload to 405B-class convergence, full-run MFU, or model quality. A single restart shows only one successful run of the tested recovery path under tested conditions.

## 7. Evidence quality and unresolved issues

- **High confidence, narrow scope:** The evidence shows the Nebius legal SLA framework and service-specific disk page. It shows CoreWeave legal definitions, with old page/version caution. It shows direct provider description of Crusoe’s test mechanisms. This evidence shows the text of promises/mechanisms, not actual operational outcomes.

- **Medium confidence:** The Crusoe-cited cluster-scale MTBF figures show a secondary presentation. Crusoe puts a peer-reviewed paper’s figures in its article. The figures do not use the same workload, provider, or rack scale. Check the paper definitions before quantitative reuse.

- **Low/absent public evidence:** The record shows no comparative provider run reliability. It shows no observed interruption statistics, checkpoint/restart success, or economic GPU-hour goodput. Marketing case studies without exposure duration, job count, interruption denominator, and censored-run handling cannot make these quantities.


## 8. Targeted product and policy evidence (verified follow-up)

This section shows direct product documentation and ClusterMAX 3.0 counterevidence. Use a documented mechanism as a vendor statement. SemiAnalysis makes its observations independently of those vendors. These observations still show a limited external test sample, not a fleet-wide dataset.

### 8.1 CoreWeave: SUNK, stragglers, checkpoints, Tensorizer

- **[observed — vendor mechanism]** CoreWeave SUNK GPU Straggler Detection uses NCCL telemetry. It shows lagging rank/node identification and rank-level dashboards ([CoreWeave straggler docs](https://docs.coreweave.com/products/sunk/discover_sunk/straggler-detection); [enable guide](https://docs.coreweave.com/products/sunk/optimize_workloads/enable-gpu-straggler-detection)). The docs show the plugin on by default in SUNK v8+. The docs also show configuration prerequisites and opt-out. The docs show detection/diagnosis and recommendations. They do not show guaranteed automatic replacement or restoration of a training job.

- **[observed — vendor mechanism]** The CoreWeave Slurm signal-handling guide shows a SIGTERM catch recipe ([CoreWeave Slurm signals](https://docs.coreweave.com/products/sunk/run_workloads/handle-slurm-signals)). The code sends model and optimizer state to a writable shared filesystem or an AI Object Storage checkpoint path. The handler then makes an exit and puts the job in a ready state for requeue or resumption. The recipe uses checkpoint-capable user code. It does not show provider-side transparent checkpointing. It does not show tests of complete optimizer/RNG/dataloader continuity.

- **[observed — vendor product scope]** CoreWeave shows Tensorizer as a PyTorch module/tensor serializer/deserializer. It uses HTTP/HTTPS and S3 sources, primarily for model-load acceleration ([project](https://github.com/coreweave/tensorizer); [article](https://www.coreweave.com/blog/coreweaves-tensorizer-decrease-pytorch-model-load-times)). It does not by itself run distributed training checkpoint/restart orchestration. For training checkpoint path evidence, use two more directly relevant sources. Use the CoreWeave SUNK signal recipe and the ClusterMAX Torch DCP checkpoint benchmark.

- **[observed — independent ClusterMAX observation]** SemiAnalysis shows a CoreWeave GPU straggler detection addition ([ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). It uses NCCL telemetry for lagging-rank attribution; it shows remediation advice. Testers show its use in customer calls, with active idle-node burn-in and rigorous node bring-up. The observation shows a real operational mechanism. The report shows no false-positive/negative rates, detection latency distribution, or resulting multi-week goodput uplift.

### 8.2 Nebius: Soperator, preemption, shared root filesystem, GB300 recovery

- **[observed — vendor mechanism]** Nebius Soperator runs Slurm components as Kubernetes resources. Soperator uses a SlurmCluster custom resource as the reconciliation source. The docs show a shared root filesystem as a Kubernetes PersistentVolume ([Soperator architecture](https://docs.nebius.com/slurm-soperator/overview/architecture)). The docs show data preservation across node restarts. The docs show node-local SSD as ephemeral; they make it a scratch/cache recommendation, not durable shared data.

  The docs show a persistence statement only. They do not show a published durability/availability percentage, backup/restore guarantee, corruption rate, or multi-week endurance result.

- **[observed — vendor policy]** Nebius can put preemptible VMs in a stopped state at any time. Capacity or price reasons make each stop. Nebius sends SIGTERM 60 seconds before SIGKILL. The policy keeps attached-volume data. It removes dynamic public IPs and local SSD data on stop. The policy shows no guaranteed availability for preemptible VMs.

  The docs show only the `FAIL` recovery policy (not VM auto-`RECOVER`) and the `STOP` preemption action ([docs](https://docs.nebius.com/compute/virtual-machines/preemptible)). The docs show an explicit, verified policy. Tenant software must make checkpoints on signal. The tenant must run the VM/job recovery itself. The provider does not make a transparent VM recovery promise.

- **[observed — independent ClusterMAX observation]** ClusterMAX 3.0 shows an automatic Nebius node return-to-service. The test uses synthetic error injection on the tested GB300 rack. The test shows immediate detection, but **8h40m end-to-end** recovery ([ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). SemiAnalysis shows other tested GB300 racks without automatic reboot/return of injected failed nodes. The report shows an observed test event on a particular allocation. The event does not show a general Nebius MTTR or a commitment.

  It puts a direct qualification on broad “autohealing” language.

- **[inference]** The Soperator design’s shared-root persistence and a node-recovery controller run at separate failure layers. A node return after 8h40m does not show correct resumption of the distributed training job. It also does not show checkpoint-filesystem availability throughout the incident.

### 8.3 Lambda: 1-Click Clusters and filesystem boundary

- **[observed — vendor mechanism/product]** Lambda shows 1-Click Clusters as reserved multi-node H100/B200 clusters ([Lambda 1CC docs](https://docs.lambda.ai/public-cloud/1-click-clusters)). Current docs show 16–512 GPUs and 3 CPU management nodes. The docs show Slurm-style admin/job-scheduling use and automatic Lambda-filesystem attachment to nodes. The docs show reservation duration in weeks. The docs show a long-reservation product and shared filesystem integration. They do not show an uptime SLA or job-level recovery guarantee.

- **[observed — vendor caveat]** The docs show local NVMe as ephemeral. The reservation end removes the data; the docs show no possible recovery. The user must keep backups of the data, e.g. on a Lambda filesystem. The docs show Filesystem S3 Adapter availability only in some regions ([Lambda 1CC docs](https://docs.lambda.ai/public-cloud/1-click-clusters)). The cited documentation does not show a shared-filesystem durability SLA, snapshot cadence, replication factor, or recovery-time objective.

- **[observed — independent ClusterMAX observation]** ClusterMAX 3.0 Lambda testing shows active health checks. The checks make autoremediation of two synthetic XIDs in under 15 minutes. A genuine XID 79 path shows no visible K8s GPU-XID/cordon/monitoring signals. The node starts service again after two hours. The review also shows Slurm CPU allocation defaults in that tested environment. It shows absent compute-node SSH outside allocations and stale CUDA/driver versions there ([ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

  These observations show bounded outcomes from one test engagement, not present-day policy or fleet rates.

### 8.4 Together: documented storage/health checks versus observed drain behavior

- **[observed — vendor mechanism]** The Together GPU-cluster overview shows persistent shared volumes ([GPU-cluster overview](https://docs.together.ai/docs/gpu-clusters-overview)). The docs show persistence across pod restarts, node reboots, and cluster deletion. On Slurm, the docs show `/home` as NFS-backed/persistent. The docs show Kubernetes `/home` and local NVMe as ephemeral. The overview shows no backup, replication, filesystem failure-domain, durability percentage, or tested checkpoint recovery.

- **[observed — vendor mechanism]** The Together docs show active checks that fully use the GPU ([Together health checks](https://docs.together.ai/docs/health-checks)). The active checks can make interruptions for running jobs. The docs make a maintenance/idle-window recommendation. Passive health checks run on production workloads without impact. The documentation shows checks and repair recommendations, not a no-disruption guarantee.

- **[observed — independent ClusterMAX observation]** ClusterMAX 3.0 shows Together’s Slurm `HealthCheckProgram` with `dcgmi diag -r 1` on already-scheduled nodes. The program uses a 45-second timeout. The timeout makes a false failure classification; the classification makes a mid-run drain of active nodes. Together removes the issue after feedback. A separate PCIe reset test shows a 67-second Slurm node drain. Automatic replacement runs to completion in 35m7s.

  The report also shows two node failures during compute testing. It shows one node sent for RMA without notice. It shows a storage-NIC provisioning race with manual reprovisioning ([ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). These events show valuable, direct counterevidence to the uniform safety of “health checks”. Health-check scheduling and timeout policy can themselves make work interruptions. The report shows one tested environment/time, not fleet statistics.

- **[inference]** The verified Together docs and ClusterMAX observations do not show a contradiction. Passive monitoring can run non-invasively; active checks use GPUs. Scheduler-integrated checks can still make interruptions against allocated nodes or with unsuitable timeouts. Send a request for policy by check type and state, not a generic health-check feature list.

## 9. Stronger conclusions after source review

Source basis: the product URLs in §8 and
[ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard).
This section checks those bounded disclosures against each other.

- **[observed]** Products show materially different specific interruption handling. The Nebius preemptible policy shows explicit stop, not automatic recovery. CoreWeave SUNK shows a user-code checkpoint-on-SIGTERM recipe. Crusoe makes an AutoClusters promise. Lambda 1CC docs show a reserved cluster/filesystem workflow but no job recovery contract. Together docs show health-check and storage behavior.

  ClusterMAX shows a Together health-check timeout with a drain of active work.

- **[observed]** The best public quantitative counterevidence uses test-event data, not multi-week run populations. ClusterMAX shows 8h40m Nebius GB300 synthetic-error recovery. Together shows an injected PCIe reset with replacement in 35m7s. Together also shows a separate misconfigured health check with active-job drains. Lambda shows two synthetic errors under 15 minutes but genuine XID 79 return in two hours. Do not make provider MTTR rankings from these events.

  These events use different event types, cluster state, and measured endpoints.

- **[inference]** Bench must check health-policy semantics safely. Check active versus passive check types. Check whether checks can run on allocated jobs. Use only a controlled software-level test event, with operator approval. Put timestamps on detection/drain/requeue/replacement. Run the checkpoint resume and check it.

  For NVL72, check the rack-specific degradation/recovery contract. Do not make a hot-swap assumption for a four-GPU tray.


## Gaps

- No verified public source here shows comparable multi-week job counts, interruption rates per GPU-hour, or completion denominators. None shows p50/p95 recovery, checkpoint replay loss, or paid-versus-useful GPU-hour goodput. This gap uses these providers: CoreWeave, Nebius, Crusoe, Lambda, and Together ([ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

- CoreWeave docs show SUNK straggler telemetry and a user-code SIGTERM checkpoint example. They do not show production recovery guarantees, false-positive rates, or complete optimizer/RNG/dataloader restoration. Tensorizer sources show serialization/model loading, not distributed training restart orchestration ([SUNK](https://docs.coreweave.com/products/sunk/discover_sunk/straggler-detection); [signal guide](https://docs.coreweave.com/products/sunk/run_workloads/handle-slurm-signals); [Tensorizer](https://github.com/coreweave/tensorizer)).

- Nebius Soperator documents show shared-root PV persistence across node restarts. They do not show a backing-storage durability SLA or checkpoint restore performance. Nebius shows an explicit preemptible policy. The research does not check SKU-specific reclaim frequency and price history ([Soperator architecture](https://docs.nebius.com/slurm-soperator/overview/architecture); [preemptible policy](https://docs.nebius.com/compute/virtual-machines/preemptible)).

- Lambda 1CC docs show attached filesystems and an ephemeral-local-data deletion warning ([Lambda 1CC docs](https://docs.lambda.ai/public-cloud/1-click-clusters)). They do not show shared-filesystem durability/backup guarantees or recovery distributions. Together docs show persistence and check types. They do not show complete filesystem failure domains, backup terms, or current health-check scheduling/timeout policy. Check ClusterMAX’s reported correction on the offered site/SKU ([Together overview](https://docs.together.ai/docs/gpu-clusters-overview); [health checks](https://docs.together.ai/docs/health-checks); [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

- The research does not show comparable current spot/preemption policies for CoreWeave, Lambda, and Together. Do not use the Nebius policy as their general policy.

- No source here shows Chennai-specific upstream power/connectivity event correlation. No source shows long-run failure rates for this exact GB300 NVL72 18-tray rack. Before the lease, send requests for a binding site/SKU SLA, maintenance and preemption terms, and a filesystem service schedule. Also send requests for a checkpoint/recovery runbook and historical events with denominators ([CoreWeave SLA terms](https://docs.coreweave.com/policies/terms-of-service); [Nebius SLA](https://docs.nebius.com/legal/sla)).
