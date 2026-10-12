# Large-company training reliability: what a two-hour rack test can and cannot establish

Research date: 2026-10-11. All claims below use a source URL.

Claims use three marks. The **[observed]** mark shows a direct source report. The **[calculated]** mark shows arithmetic from reported values. The **[inference]** mark shows transfer to rack-bench.

The review keeps one scope: a GB300-class NVL72-class rack (18 trays) in Chennai. A measured two-hour category check and smoke burn-in can show short-window health and behavior. The same check cannot show survivability of a 30–90-day or 54-day Llama-3-class run. Large-company practices make useful causal design patterns, not GB300 guarantees.

## 1. Executive answer: reliability is a chain, not a pass/fail component test

### 1.1 What hyperscalers actually do

[observed] The common operating chain runs in stages. Preflight/screen checks run on the hardware first. Continuous collection keeps correlated device, network, runtime, and training signals. Monitoring checks for anomaly, timeout, and performance regression. Diagnosis then uses differential evidence and targeted tests; quarantine or replacement removes suspect nodes/components. A validated-checkpoint restore plus progress/loss checks make the final stage.

Meta shows categorization, triage, node selection, cluster validation, and restore. ByteDance runs heartbeat-triggered diagnostics, eviction/replacement, and checkpoint resume. Google TPUv4 puts preflight, health telemetry, scheduler exclusion, and rescheduling together. [Meta, “How Meta keeps its AI hardware reliable,” opening and “Infrastructure strategies”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable); [MegaScale, §§4.1–4.4](https://arxiv.org/html/2402.15627v1); [Google TPUv4, §§3.1, 3.6](https://www.usenix.org/system/files/nsdi24-zu.pdf)

[inference] A rack certification can check chain pieces and keep evidence. It cannot show a future model’s application-level correctness. It cannot show long-horizon fault rate, checkpoint cadence/recovery time under real state size, or provider operational response. Explicit checks and measurements must run on those items first. [Meta FAIR §II-D](https://arxiv.org/html/2410.21680v1); [NVIDIA resiliency guide](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

### 1.2 Direct answer for two hours

[inference] Two hours can show current inventory/health. Load can show gross hardware and fabric defects. Repeatable tests can show GPU/NVLink/NIC/storage performance. Short windows can show rank skew and stalls. The tested workload can show temperature/power behavior. [Meta SDC strategies](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable); [NVIDIA rerun state machine](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[inference] Two hours can check checkpoint write/read/restore correctness for a representative checkpoint. Two hours can check a forced restart/recovery path. Immediate numerical sanity checks can run against deterministic/reference results.

[inference] Two hours cannot show rare/intermittent faults with day-scale manifestation or aging/environment/data dependence. It cannot show fleet-scale recurrence/MTTF, 54-day ETTR/goodput, or all possible silent data corruption (SDC). It cannot show actual end-to-end model convergence, or workload-specific loader behavior at full dataset scale. [MegaScale §§6.2–6.3](https://arxiv.org/html/2402.15627v1); [Llama 3 Herd §3.3.4](https://arxiv.org/html/2407.21783)

[inference] Two hours cannot show long-run thermal/clock behavior or shared-fabric contention. It cannot show checkpoint integrity after many cycles, outage, or storage corruption. It cannot show real-world restart frequency and MTTR across operator escalation.

[calculated] A 54-day run runs 648 times longer than a two-hour observation. [Llama 3 Herd §3.3.4](https://arxiv.org/html/2407.21783)

[calculated] The calculation even uses an unrealistically stationary independent failure process assumption. A zero-failure short sample still cannot show a useful low failure rate. That result must use many more node-hours and confidence bounds. Correlated rack/system failures make simple extrapolation worse still.

## 2. Detecting failures before a run: screen, then keep the evidence

### 2.1 Health checks are repeated, layered, and exclusion-capable

[observed] Meta’s two research clusters run node health checks every five minutes. The codes show pass, fail, or warning status for GPU XIDs, filesystem mounts, and services. One overlap case: a PCIe failure can show an inaccessible GPU even without its own XID. Severe findings start immediate removal/rescheduling: GPU inaccessible, NVLink, uncorrectable ECC, row-remap, PCI/IB link, block device, missing mount. Lower-severity findings can start remediation after job completion. The scheduler keeps a failed node unschedulable until the end of repair and a passing check. [Meta FAIR, “Revisiting Reliability…,” §II-C, exact text “every five minutes” and “transitioned to a remediation state”](https://arxiv.org/html/2410.21680v1)

[observed] The same study shows health-check false positives on fewer than 1% of successfully completed jobs. The authors make an explicit caution: the observed correlation does not make causation. Its operating principle keeps the same bad node away from a second job. [Meta FAIR, §II-C](https://arxiv.org/html/2410.21680v1)

[observed] Google’s TPUv4 runs preflight before each job. An end-to-end mini workload checks hardware/software interactions. A separate intent-driven checker checks physical metrics against golden thresholds. A preflight failure sends the job to different cubes. Continuous healthd telemetry checks TPU ASICs, PCIe, and ICI links. The checks use modeled expected values and thresholds. [Google TPUv4, §§3.1, 3.6.1–3.6.2, pp. 764, 767–768](https://www.usenix.org/system/files/nsdi24-zu.pdf)

[observed] Azure’s published operational guidance puts Node Health Checks before training. It puts NCCL tests beside them for distributed all-reduce. The guidance makes checkpoint intervals, data volume, and storage capacity/performance open decisions. It does not make a checkpoint-existence assumption. The page shows provider guidance, not evidence of an Azure customer SLO. [Microsoft Learn, “Well-architected considerations…,” “Megatron-LM test use,” “Implement checkpoint storage”](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai/infrastructure/well-architected)

[inference] rack-bench check: Keep per-device records *before and after* load. The records: device identity/firmware, ECC/XID/row-remap counters, PCIe/NVLink link state/errors, NIC/fabric counters, and link flaps. Also keep disk/media errors, mount status, and filesystem status. Run a reproducible mini training and in-rack collectives. Then run the same checks again. Keep counters and timestamps, not only PASS.

[inference] Put exclusion marks in the record. Run reruns only after repair. An audit snapshot does not make a health screen. [Google TPUv4 §3.6](https://www.usenix.org/system/files/nsdi24-zu.pdf); [Meta FAIR §II-C](https://arxiv.org/html/2410.21680v1)

### 2.2 Flaky nodes can pass simple static checks

[observed] Meta puts hardware faults in three classes: static, transient/load-dependent, and silent. Static failures show no power-up and no enumeration. Transient/load-dependent failures: thermal runaway, intermittent uncorrectable errors, condition-dependent faults. Meta shows that artificial workloads can make transient faults reproducible. “sticky” status telemetry can keep evidence after a transient event. [Meta engineering, “Types of hardware faults encountered at Meta”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

[observed] Meta’s Fleetscanner uses directed microbenchmarks and telemetry signatures. Its scheduled fleet coverage runs every 45–60 days. Ripple runs short co-located tests, milliseconds to seconds, for faster fleet coverage. Meta makes an explicit note: the periodic dedicated test can run too slow for some SDCs. These make fleet systems, not a claim of equivalent two-hour coverage. [Meta engineering, “Novel SDC detection mechanisms”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

[observed] Meta FAIR shows “lemon” nodes; health checks and normal repair workflows keep these nodes in service. The detector uses seven candidate signals. The signals: distinct-job node exclusions, XID count, repair tickets, scheduler removals, and single-/multi-node failure counts/rates.

Historical 28-day signals show 40 faulty nodes. Subsequent tests show failures on >85% of them. The study shows detection accuracy above 85%. Large-job failures (512+ GPUs) show a change from 14% to 4%. The method uses history; it does not make a two-hour diagnostic yield. [Meta FAIR, §IV-A](https://arxiv.org/html/2410.21680v1)

[inference] rack-bench check: Run repeated warm/cold and sustained-load cycles. Put thermal soak and transition conditions in the cycle set. Check each GPU/tray/rank against peers, not only aggregate averages. Keep per-component error deltas. A repeatable outlier makes a quarantine/investigation signal even above a vendor threshold. Two hours can show gross/intermittent faults, not 28-day history. [Meta FAIR §IV-A](https://arxiv.org/html/2410.21680v1)

## 3. Telemetry to diagnosis: attribute causes rather than blame the loudest symptom

### 3.1 Measure step-level behavior and rank tails

[observed] Executors send periodic heartbeats to the MegaScale driver. The heartbeats show process/hardware status, stdout/stderr, and RDMA traffic metrics. The driver checks them for warning/error keywords. Steps must show recurring traffic patterns. A decline or fluctuation in RDMA traffic makes an anomaly. Zero traffic starts automatic recovery.

[observed] The system runs second-level monitoring for host/network health. It runs millisecond-level monitoring for congestion. It also checks whether data-/pipeline-parallel transfers run at physical limits. [MegaScale, §4.2](https://arxiv.org/html/2402.15627v1)

[observed] MegaScale keeps CUDA-event durations per rank and critical segment. Its interface shows heatmaps and cross-rank timelines. About 0.5% of machines run substantially slower in training. After outlier removal, peak MFU shows consistency.

Some hosts use ~10% more time on forward computation. Their removal makes MFU better by ~0.7%. These tools show stragglers that single-GPU GEMM microbenchmarks do not show. [MegaScale, §§5.1, 6.3](https://arxiv.org/html/2402.15627v1)

[observed] ByteDance shows a long-run performance decline. The record shows stable compute and optimizer times with a rising step time. A differential analysis makes the diagnosis: delayed reduce-scatter initiation (rank skew). The trace runs upstream to forward-stage variation, including irregular garbage collection and PyTorch operations. Code removal/modification then makes MFU stable. This case shows a network-looking symptom from software timing, not link bandwidth. [MegaScale, §6.3, “MFU decreasing”](https://arxiv.org/html/2402.15627v1)

[inference] rack-bench check: Keep step-time distributions. Keep per-rank and per-tray spans: compute, communication, input-wait, checkpoint, synchronization. The report shows p50/p95/p99, max/min spread, rank identity, missed/late heartbeats, and NIC traffic. It also shows retransmit/error counters and clocks/temperature against time. An average throughput number does not show stragglers and stalls. [MegaScale §§5.1–5.2](https://arxiv.org/html/2402.15627v1)

### 3.2 NCCL timeout is a symptom, not a diagnosis

[observed] Meta FAIR makes a warning: a collective timeout does not make a diagnosis by itself. The timeout may show network trouble. It may instead show a rank that never starts the collective. Causes: a stall on next-batch loading, a deadlock in application code, or a failure elsewhere. [Meta FAIR, §§II-E, V “Debugging Tools”](https://arxiv.org/html/2410.21680v1)

[observed] Root-cause work uses a comparison of rank logs and the collective sequence. Check for the first collective that some ranks start and others do not. If all ranks start but the collective shows no completion, check traffic and expected messages.

[observed] MegaScale keeps a log of each worker’s in-progress event at communication timeout. It shows rank dependencies across tensor/pipeline/data parallel groups. Waiting ranks put their operation in the log. A defective GPU can make a stall and send no log entry. This makes origin localization easier. The system does not make all timeout cascades faults. [MegaScale, §5.2](https://arxiv.org/html/2402.15627v1)

[inference] rack-bench check: Put one deliberately induced/controlled rank or link interruption in the test, if safe. Check that the system shows the root node/rank and timestamps, not only a generic NCCL error. Run fabric tests under loader-paused and loader-active conditions. Do not make a faulty-fabric inference from a timeout alone. [Meta FAIR §II-E](https://arxiv.org/html/2410.21680v1)

### 3.3 Data-loader and storage stalls are first-class failure hypotheses

[observed] MegaScale shows GPU idle time from data preprocessing/loading. Per-GPU loaders can make disk-bandwidth contention. MegaScale puts preprocessing in overlap with communication. It uses a shared-memory tree loader to remove redundant reads. [MegaScale, §3.4](https://arxiv.org/html/2402.15627v1)

[observed] Meta FAIR makes the cause specific: “stuck trying to load data for the next iteration”. A rank in that state does not start the collective. Misled peers then run into timeouts. [Meta FAIR, §II-E](https://arxiv.org/html/2410.21680v1)

[inference] rack-bench check: Run the training/inference smoke with a representative data source, shard count, preprocessing, and cache state. Check loader wait, storage latency/throughput, queue depth, read errors, and GPU idle intervals. Run cold-cache and warm-cache behavior in the test. A synthetic fio pass or a preloaded batch does not make a production-loader proof. [MegaScale §3.4](https://arxiv.org/html/2402.15627v1); [Meta FAIR §II-E](https://arxiv.org/html/2410.21680v1)

## 4. Containment and recovery: quarantine, reconfigure, restore, verify

### 4.1 Exclude and replenish rather than retry on the same suspect hardware

[observed] MegaScale recovery runs one chain. A missing heartbeat or abnormal process starts the chain. The chain: executor suspension → lightweight self-check diagnostics → Kubernetes eviction of faulty node identities. Then: replenishment with diagnostics-passing healthy nodes → resume from the latest checkpoint.

The reported production run shows automatic identification/fixes for >90% of software/hardware faults. Detection and diagnostic tests together run <10 minutes on average. [MegaScale, §§4.1, 6.2–6.3](https://arxiv.org/html/2402.15627v1)

[observed] Google TPUv4’s health monitor removes faulty cubes. Borg puts the job on other resources after preflight. OCS reconfiguration and fault-tolerant routing make detours possible around some link/switch faults. The routing shows workload-dependent performance penalties. The paper shows 99.98% system availability and hardware outages on ~1% of training jobs. These figures show TPUv4 pod/system results, not a per-job promise for a single GPU rack. [Google TPUv4, abstract, §§3.1, 4, 5.2–5.3](https://www.usenix.org/system/files/nsdi24-zu.pdf)

[observed] Meta FAIR’s periodic checks keep known bad nodes out of new allocations. Historical lemon detection removes recurrent nodes without a periodic-check fault flag. Unfiltered retries can make restart loops. One example shows a 1024-GPU job with 35 requeues and 548 preemptions. The preemptions show effects on >7,000 GPUs. [Meta FAIR, §§II-C, III “Preemptions and Failure Cascades,” IV-A](https://arxiv.org/html/2410.21680v1)

[inference] rack-bench check: Check failed-node containment at rack scope. The alert must show tray/GPU/NIC identity. A scheduler/admin action must keep the unit unavailable. The record must put the replacement or reduced allocation in explicit terms. A subsequent run must not silently put the same suspect unit back in use.

[inference] A single rack keeps limited spare/reconfiguration capacity, unlike hyperscale clusters. The record must show the failure path: job halt or degraded continuation. [Google TPUv4 §§3–4](https://www.usenix.org/system/files/nsdi24-zu.pdf); [MegaScale §4.1](https://arxiv.org/html/2402.15627v1)

### 4.2 Restart statistics and MTTR matter as much as raw fault count

[observed] MegaScale’s report shows a several-week production run on >10,000 GPUs. The run shows >100 restarts, and loss shows continued convergence. The report shows >90% effective training time. Detection/diagnosis shows a <10-minute average. Catch-up to pre-crash training progress runs within 15 minutes from the latest checkpoint. These figures show their proprietary stack, HDFS, model, and cluster, not hardware-only metrics. [MegaScale, §§6.2–6.3](https://arxiv.org/html/2402.15627v1)

[observed] Meta’s Llama 3 public summary shows training on 16K GPUs. It shows automated error detection/handling/maintenance, improved SDC detection, and scalable checkpoint/rollback storage. The combined improvements make >95% effective training time. That summary does not show a per-rack failure rate, checkpoint interval, or per-event MTTR. [Meta, “Introducing Meta Llama 3,” “Scaling up pretraining”](https://ai.meta.com/blog/meta-llama-3)

[observed] Meta FAIR shows the ETTR definition: productive runtime / available wall-clock time. The definition puts re-training lost since checkpoint and restart initialization overhead in unproductive time. It keeps ETTR and MFU separate. ETTR shows interruptions/restarts/queueing; MFU shows compute efficiency. The source makes an explicit note about workload dependence in the exact productive-runtime definition. [Meta FAIR, §II-D](https://arxiv.org/html/2410.21680v1)

[calculated] The Llama 3.1 405B paper shows 466 interruptions in a 54-day snapshot. Division by 54×24 = 1,296 elapsed hours shows 0.360 interruptions/hour. The rate shows one interruption per 2.78 hours on average (466/54 = 8.63 interruptions/day).

[calculated] The number shows the observed *job interruption frequency* for that specific 16K-H100 production run. It does not show a downtime fraction, component failure rate, or GB300 estimate. It does not show the duration of each interruption. The paper separately shows >90% effective training time, useful training time / elapsed time by definition. [Llama 3 Herd, §3.3.4](https://arxiv.org/html/2407.21783)

[inference] Keep measured throughput and run health in separate reports. The throughput report shows steady-state tokens/s or steps/s. The health report shows rank-tail and trend, loader wait, checkpoint overhead, restarts, and recovery. It also shows effective useful progress / elapsed time. A 2-hour performance PASS shows only measured performance under defined load and contention. It does not show 54-day goodput. [Meta FAIR §II-D](https://arxiv.org/html/2410.21680v1)

### 4.3 Checkpoint correctness is more than “file exists”

[observed] MegaScale puts checkpointing in two stages. Stage one makes a short GPU→host-memory copy. Stage two sends the state to HDFS asynchronously. The restore path uses one shared-state read per data-parallel group and a broadcast. This makes the storage load smaller and keeps pause and restore time small. A completed write does not make a checkpoint valid by itself. [MegaScale §4.4](https://arxiv.org/html/2402.15627v1)

[observed] Meta says scalable storage makes checkpointing/rollback overhead smaller for Llama 3. The product post does not show checkpoint intervals, sizes, or a restore-time distribution. [Meta Llama 3, “Scaling up pretraining”](https://ai.meta.com/blog/meta-llama-3)

[observed] Google’s MaxText recovery demonstration shows a concrete configuration failure. A proxy configured for 100 GB keeps a 135-GiB checkpoint out. After correction, the run restarts from committed step 3300 after reaching 3388. The restart makes a loss of 88 steps. The demonstration shows a specific TPU/GKE example, not a GB300 claim. [Google Developers Blog, recovery walkthrough](https://developers.googleblog.com/we-terminated-a-tpu-mid-training-and-it-recovered-in-seconds-introduction-to-elastic-training-with-maxtext)

[inference] Check the checkpoint manifest and the expected shard count. Check checksums or equivalent integrity. Put optimizer, scheduler, RNG, and data-position state in the checkpoint. Run the restore in a fresh process. Check the resumed step, loss, and deterministic reference outputs.

[inference] Run an interrupted-write simulation. Check that recovery selects the last committed checkpoint, not a partial newer one. A storage throughput pass does not make a correctness test. [MegaScale §4.4](https://arxiv.org/html/2402.15627v1); [NVIDIA checkpointing guidance](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

## 5. Silent numerical corruption and loss-spike attribution

### 5.1 Device errors are not equivalent to numerical correctness

[observed] Meta shows the silent data corruption (SDC) definition: hardware miscomputation without detectable traces. SDC dependencies: input, voltage, frequency, temperature, or lifecycle. The input space makes exhaustive checks impractical. Checks can first show some faults only after months. Fleetscanner, Ripple, and application-exception analysis make coverage better, with limits. [Meta Engineering, “Silent errors” and “Key challenges presented by SDCs”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

[observed] Meta puts NaN propagation and in-range corrupted gradient variance in separate classes. NaN propagation can start from a few accelerator computations and can put training at a halt. In-range corrupted gradient variance can show apparent progress while training runs toward divergence or a poor local minimum. Detection can run for weeks or months. [Meta Engineering, “SDCs in training workloads”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

[observed] Meta’s mitigation examples: deterministic known-model iterations, mini-training binary-search triage for NaNs, and more frequent checkpoints. More frequent checkpoints make the corruption window narrower. Meta makes an explicit caution. Reproducibility keeps data, electrical, and temperature dependencies. Gradient clipping shows benefit for some NaNs, but it can put partial errors in place. [Meta Engineering, “Detection of SDCs in AI hardware”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

[observed] NVIDIA’s Megatron Bridge rerun state machine keeps an alpha/experimental status. It runs same-GPU and different-GPU rerun comparisons for NaN/spiky-loss attribution. It shows validation and determinism-statistics modes. NVIDIA explicitly keeps it outside exhaustive SDC coverage. [NVIDIA guide, “Re-run State Machine”](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[inference] rack-bench check: Run known-answer GPU compute tests and repeated seeded small training steps. Check for finite loss/gradients. Check rank outputs against references. Keep per-step loss/gradient norm and available RAS telemetry in the record. These checks can show gross/deterministic errors. They cannot remove the risk of rare, data-dependent, or long-latency SDCs. [Meta SDC strategies](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable); [NVIDIA rerun guide](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

### 5.2 Loss spikes need temporal and rank-correlated evidence

[inference] A loss spike alone does not show the cause. Put loss and gradient-norm changes on one timeline. Alignment items: data sample/step, checkpoint boundaries, rank-specific errors, thermal/power/clock events, fabric retries/flaps, loader stalls, and software changes. A shared spike can show data/algorithm/shared-event causes. A first divergence on one rank starts a check of that device/path. Use this as a diagnostic procedure, not as a validated universal classifier. [Meta Engineering, “Corrupted gradient variance”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable); [MegaScale §§4.2, 5.1–5.2](https://arxiv.org/html/2402.15627v1)

[inference] Two hours can check the telemetry and the response to an injected, known anomaly. Two hours cannot show the effects of corruption with latency of weeks. Put this wording in the report: “none observed in these tests,” not “SDC-free.” [Meta Engineering, SDC discussion](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

## 6. Thermal, fabric contention and goodput

### 6.1 Thermal and hardware telemetry

[observed] Meta shows temperature range and workload sensitivity as contributors to transient hardware faults. It shows artificial workloads for reproduction of such failures. [Meta Engineering, “Transient errors”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

[inference] rack-bench check: Run the load long enough for near thermal equilibrium in the test window. Keep GPU clocks, power, temperature, throttling reasons, and available inlet/environment sensors in the log, against throughput. Run the test again under representative site conditions. Two hours cannot show seasonal HVAC, dust, facility-power, or long-term aging resilience. [Meta Engineering, “Transient errors”](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable); [Llama 3 Herd §3.3.4](https://arxiv.org/html/2407.21783)

### 6.2 Fabric faults and contention

[observed] MegaScale shows network-interface flapping with stalls or speed drops. Packets show loss during a link-down period. The trace runs to link quality: NIC, cable, and switch. MegaScale puts timeout/retransmission settings in place for short flaps. Its monitoring uses second-level host/network health and millisecond-level congestion/transfer measurements. [MegaScale §§4.2, 6.3](https://arxiv.org/html/2402.15627v1)

[observed] Meta FAIR shows 50–75% bandwidth loss in one fabric bring-up episode with link errors. Adaptive-routing experiments make 512-GPU all-reduce bandwidth better under injected bit errors. They make variance smaller under concurrent traffic. The benefits keep workload and topology dependencies. [Meta FAIR §IV-B](https://arxiv.org/html/2410.21680v1)

[observed] Google TPUv4 shows single-OCS-fault all-to-all throughput at 92.2% of healthy for one 4×4×4 slice. Other topologies show differences. The result keeps TPU’s OCS/ICI design as its basis. It does not show NVLink/NVSwitch or Ethernet/InfiniBand behavior. [Google TPUv4 §4.3, Table 2](https://www.usenix.org/system/files/nsdi24-zu.pdf)

[inference] rack-bench check: Run in-rack collectives and bandwidth/latency tests across representative message sizes, intended rails, and GPU pairs. Keep per-link errors/retries/flaps and congestion signals in the record, if exposed. Put safe concurrent traffic in the test when relevant. An isolated peak all-reduce result does not show shared-fabric goodput. A single rack cannot make a scale-out spine or multi-rack contention proof. [MegaScale §§4.2, 6.3](https://arxiv.org/html/2402.15627v1); [Meta FAIR §IV-B](https://arxiv.org/html/2410.21680v1)

### 6.3 Short-run speed is not long-run useful work

[observed] MegaScale shows MFU decline with stable forward/backward/optimizer time and apparent bandwidth. Rank arrival skew makes the reduce-scatter late. Its CUDA-event tools also show a ~0.5% slow-machine tail. That tail puts limits on synchronous progress. [MegaScale §§5.1, 6.3](https://arxiv.org/html/2402.15627v1)

[observed] Meta FAIR puts MFU, ETTR, and cluster goodput in separate boxes. MFU shows model compute efficiency. ETTR shows productive time after interruption, restart, and queue effects. These metrics show answers to different questions. [Meta FAIR §II-D](https://arxiv.org/html/2410.21680v1)

[inference] Put throughput and run health in separate publications. Items: steady tokens/s or steps/s, rank-tail and time trend, loader wait, checkpoint cost. Also interruptions/recovery and useful progress per elapsed time. A short performance PASS keeps its scope: its workload and test window. It does not make evidence of 54-day goodput. [Meta FAIR §II-D](https://arxiv.org/html/2410.21680v1); [MegaScale §§5–6](https://arxiv.org/html/2402.15627v1)

## 7. Practical two-hour training-health protocol for rack-bench

All items below make **[inference]** recommendations for measurable checks. These checks use evidence from [Meta FAIR §§II-C–D](https://arxiv.org/html/2410.21680v1), [MegaScale §§4–6](https://arxiv.org/html/2402.15627v1), [Google TPUv4 §3.6](https://www.usenix.org/system/files/nsdi24-zu.pdf), and [NVIDIA resiliency guidance](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html). Acceptance thresholds must use local specification. The sources make no such claims.

### 7.1 Suggested evidence sequence (fit to the category’s two-hour allocation)

1. **Baseline snapshot (10 min):** Make an inventory of all 18 trays and accelerators. Keep firmware/software, GPU RAS/XID/ECC, PCIe/NVLink, NIC/fabric, and storage health counters in the record. Keep temperature/power/clock in the record. Check mounts and data access. Put timestamps on the raw outputs and keep them.

2. **Correctness/preflight (15–20 min):** Run deterministic GPU compute validation again. Run representative multi-GPU and inter-tray collectives. Check every expected rank and data path. Run a small known-model training with seeded data, finite loss/gradients, and a reference comparison. Keep per-device results, not only the overall exit status.

3. **Sustained smoke (45–60 min):** Run a representative distributed training loop on the real loader/storage path. Keep continuous capture of step-time percentiles, per-rank CUDA event spans, and loader wait. Keep collective times, data rate, GPU idle, thermal/power/clocks, fabric counters, and errors in continuous capture. Keep loss/gradient norms in continuous capture. Put concurrent traffic in the test, if safely representative.

4. **Checkpoint/recovery (15–20 min):** Make a real representative checkpoint. Check the manifest/checksums. Remove a worker or the job, then run the restore path. Check the expected resumed step and a valid loss. Check detection, diagnosis, exclusion, restore, restart, and lost work as separate measurements. If the scope removes destructive fault injection, put this in the record: the test makes no recovery measurement.

5. **Final delta check (5–10 min):** Check counters and device status against the baseline. Make errors, outliers, retries, throttling, stale counters, skipped checks, and test limits explicit in the report. The PASS mark shows only the observed checks.

### 7.2 Metrics and causal evidence to publish

- **[inference]** Detection: event-to-alert latency; missed heartbeat; per-rank loss/gradient anomaly; error-counter delta; device/link identity.

- **[inference]** Diagnosis: time to one cause domain — software, loader/storage, GPU/device, PCIe/NVLink, fabric, or facility. Put evidence with each finding. Put an explicit mark on ambiguous attribution.

- **[inference]** Containment: suspect-resource exclusion status; blast radius; continued-vs-aborted training; successful replacement/reroute, if supported.

- **[inference]** Recovery: checkpoint age and integrity; lost steps/tokens; restore/reinitialization duration; time back to productive progress; loss-trajectory agreement with expectation.

- **[inference]** Efficiency: step/token throughput distribution and trend; p95/max rank skew; loader stall share; checkpoint duty-cycle cost. Also: thermal throttling and useful work per wall time for the test window.

- **[inference]** Do not use “MTBF” or “54-day reliable” from two hours. Put the exposure denominator (GPU-hours/tray-hours), observed event count, test workload, and confidence limitation in the report. A zero-failure rate estimate must show its statistical model and its assumptions.

## 8. Transfer limits to GB300-class NVL72-class, Chennai

### 8.1 What transfers robustly

[inference] Put these operational principles in the transfer set. The set: preflight and health telemetry, repeated checks, rank-level timeline, counter deltas, differential diagnosis. Also: node/tray quarantine, checkpoint/restore validation, loss/gradient monitoring, and performance separate from goodput. These requirements make an architecture-independent set. Meta, ByteDance, Google, and Microsoft practice shows them.

[inference] Check the specific rack’s physical and software topology; do not use imported published thresholds. Topology items: 18 trays, GPU/NVLink/NVSwitch fabric, host CPU/PCIe, NIC/fabric, storage, cooling, and power. A vendor’s link-rate or health claim does not make a measured PASS. [Microsoft Azure guidance](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai/infrastructure/well-architected)

### 8.2 What does not transfer numerically or structurally

[observed] The sources use different hardware and deployment regimes. Meta Llama 3 uses H100-class 16K-GPU-scale clusters. MegaScale’s production cluster uses >10,000 NVIDIA Ampere GPUs, a custom 200G multi-rail RoCE-era network, and HDFS. Google’s paper uses TPUv4 with 4096 chips, 3D torus ICI, optical circuit switches, and Borg. The Meta FAIR study uses A100 clusters. Their failure rates, diagnostic thresholds, recovery times, availability, and routing behavior do not make GB300 specifications. [Meta Llama 3](https://ai.meta.com/blog/meta-llama-3); [MegaScale, §§3.6, 6](https://arxiv.org/html/2402.15627v1); [Google TPUv4, §§2–5](https://www.usenix.org/system/files/nsdi24-zu.pdf); [Meta FAIR, §§II–IV](https://arxiv.org/html/2410.21680v1)

[inference] NVL72’s rack scale can make changes to the failure unit and blast radius. The cited results do not show GB300 NVL72 reliability data. Do not put 18 trays in the same class as 72-GPU servers, TPU cubes, or a 10K-GPU cluster. Check NVIDIA-specific RAS, NVLink/NVSwitch counters, rack firmware, NIC/fabric, and orchestration on this exact system. [MegaScale](https://arxiv.org/html/2402.15627v1); [Google TPUv4](https://www.usenix.org/system/files/nsdi24-zu.pdf)

[inference] Chennai puts local facility/context variables in play: ambient and inlet temperature, power quality, cooling redundancy, maintenance, and WAN/operator path. The cited training studies do not put numbers on these for this deployment. Run rack telemetry tests in the actual site conditions. Keep site-level long-term resilience as an explicit gap. [Llama 3 Herd §3.3.4](https://arxiv.org/html/2407.21783)

## 9. Source confidence, conflicts and evidence limits

### 9.1 Confidence assessment

**High confidence for mechanisms and measured claims.** The ByteDance MegaScale paper keeps peer-reviewed USENIX NSDI’24 systems-paper status. It shows detailed implementation and multi-week production-run evidence. The Google TPUv4 paper keeps peer-reviewed NSDI’24 status with architecture, preflight, health telemetry, and fleet statistics. The Meta FAIR study makes a quantitative 11-month analysis of 150M+ A100 GPU-hours and 4M jobs. These sources make primary engineering/system evidence, but the same companies show their own deployments. [MegaScale](https://www.usenix.org/conference/nsdi24/presentation/jiang-ziheng); [Google paper](https://www.usenix.org/system/files/nsdi24-zu.pdf); [Meta FAIR](https://arxiv.org/html/2410.21680v1)

**High confidence for Meta’s disclosed SDC taxonomy and methods; moderate for external generalization.** Meta’s engineering post shows first-party operational disclosure. It puts static/transient/silent errors in clear separate classes. It does not make enough public denominators available for reproduction of all SDC rates. It does not show coverage for a two-hour test. [Meta engineering](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable)

**Moderate confidence for Meta’s distinct Llama metrics.** Meta’s April 2024 product blog shows >95% effective training time as an aggregate outcome, with limited methodological detail. The July 2024 Llama 3 Herd paper shows a separate >90% result for its 405B production pretraining. It shows a 54-day snapshot with 466 total interruptions (47 planned, 419 unexpected). It also shows >90% automated handling and only three significant-manual-intervention cases. Do not put these values together: the sources and contexts make different cases without public reconciliation. [Meta Llama 3 blog](https://ai.meta.com/blog/meta-llama-3); [Llama 3 Herd §3.3.4](https://arxiv.org/html/2407.21783)

**Moderate for Microsoft practices.** Azure Learn shows authoritative provider guidance on checkpoints, monitoring, and Node Health Checks. It does not make an empirical large-run reliability study or a contractual performance result. [Microsoft Learn](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai/infrastructure/well-architected)

### 9.2 Apparent conflicts are metric/scope differences

[observed] Meta Llama 3 shows >95% effective training time. The FAIR paper shows Llama 3 MFU of 38–43% as an example. These do not make a conflict. The ETTR/effective-training-time metric uses useful wall-clock time after interruption overhead. MFU shows achieved model FLOPs relative to peak. [Meta Llama 3](https://ai.meta.com/blog/meta-llama-3); [Meta FAIR §II-D](https://arxiv.org/html/2410.21680v1)

[observed] MegaScale shows >90% effective training time in its >10K-GPU run, with >100 restarts. Meta Llama 3 shows >95%. Neither result shows rare failures. Both show that automation/checkpointing can keep useful progress despite interruptions. The workloads, clusters, metric definitions, and reporting make different cases. [MegaScale §§6.2–6.3](https://arxiv.org/html/2402.15627v1); [Meta Llama 3](https://ai.meta.com/blog/meta-llama-3)

[observed] Google’s 99.98% system availability shows an infrastructure availability result. About 1% of training jobs run into outages. Reconfiguration/recovery keeps them in training. Do not use system availability as uninterrupted job success or 99.98% goodput. [Google TPUv4 abstract and §5](https://www.usenix.org/system/files/nsdi24-zu.pdf)

[inference] Failure rates show material differences even within Meta’s two clusters, and over time. The FAIR paper shows changing rates, driver bugs, mount issues, and an IB-failure burst on a few nodes. This evidence removes support for a universal imported rate. It also removes support for a particular-rack prediction from a short observation. [Meta FAIR §§III, IV-A](https://arxiv.org/html/2410.21680v1)

### 9.3 Exact local source evidence map

NVIDIA Megatron Bridge evidence uses these anchors first: ‘Fault Tolerance,’ ‘Straggler Detection,’ ‘Re-run State Machine,’ ‘Preemption,’ then more. The section/page references below show the specific evidence reviewed. The fetched text makes a reproduction from the linked source. The numbering uses source-local rules, not this brief’s line numbering. The remaining anchors: ‘Async Checkpoint Save,’ ‘Local Checkpointing,’ ‘In-Process Restart,’ and ‘Practical Caveats’ at https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html.

| Source | Exact evidence location | Key evidence |
|---|---|---|
| Meta Engineering, 2025 | “Types of hardware faults”; “Novel SDC detection mechanisms”; “SDCs in training workloads”; “Infrastructure strategies” | Static/transient/SDC split; Fleetscanner 45–60 days; Ripple ms–s; NaN vs in-range gradient variance; binary-search triage, deterministic training, hyper-checkpointing. [URL](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable) |
| Meta Llama 3 | “Scaling up pretraining” | 16K GPUs, 24K-GPU clusters; automated error handling, SDC detection, checkpoint/rollback; >95% effective training time. [URL](https://ai.meta.com/blog/meta-llama-3) |
| ByteDance MegaScale, NSDI’24 | §§4.1–4.4, 5.1–5.2, 6.2–6.3 | heartbeat→diagnostics→evict/replenish→checkpoint; monitoring granularity; straggler tools; 100+ restarts; <10-min detection/diagnosis; <15-min catch-up; link flapping and falling MFU. [HTML](https://arxiv.org/html/2402.15627v1), [USENIX](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf) |
| Google TPUv4, NSDI’24 | Abstract; §§3.1, 3.6.1–3.6.3, 4.3 Table 2, 5 | 4096-node TPUv4; healthd/preflight; reschedule; online link repair/routing; 99.98% system availability; fault-rate and performance details. [PDF](https://www.usenix.org/system/files/nsdi24-zu.pdf) |
| Meta FAIR reliability study | §§II-C–E, III, IV-A–B, V | five-minute checks; health severity/remediation; ETTR/MFU/goodput definitions; MTTF and restart loops; lemon-node features; adaptive routing and timeout diagnosis. [HTML](https://arxiv.org/html/2410.21680v1) |
| NVIDIA Megatron Bridge | ‘Fault Tolerance’; ‘Straggler Detection’; ‘Re-run State Machine’ | Slurm/launcher/checkpoint constraints; no default detector stop; experimental rerun modes. [URL](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html) |
| Llama 3 Herd paper | §3.3.4 ‘Reliability and Operational Challenges’ | 405B-specific >90% effective time; 54-day window, 466 interruptions and planned/unexpected split. [URL](https://arxiv.org/html/2407.21783) |
| Microsoft Azure Learn | Reliability; Operational excellence; “Implement checkpoint storage”; “Megatron-LM test use” | monitoring, backups, checkpoint state recovery and Node Health Checks/NCCL tests. Guidance rather than measured guarantee. [URL](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai/infrastructure/well-architected) |
| Google MaxText recovery demonstration | Walkthrough/checkpoint-size example | 135-GiB checkpoint vs 100-GB proxy failure; recovery with an 88-step rewind to the committed checkpoint. Specific TPU/GKE demo only. [URL](https://developers.googleblog.com/we-terminated-a-tpu-mid-training-and-it-recovered-in-seconds-introduction-to-elastic-training-with-maxtext) |

## 10. NVIDIA Megatron Bridge / NVRx: workload-side recovery controls

### 10.1 Features and constraints

[observed] Megatron Bridge puts resiliency features from NVIDIA Resiliency Extension (NVRx) in layers. Fault tolerance checks setup, training-step, and checkpoint sections with distinct timeouts, then runs a restart. It runs in-job restarts inside a Slurm allocation and new job launches, with configurable limits. Its prerequisites: Slurm plus `ft_launcher` (not `torchrun`), accessible checkpoint storage, and RankMonitorClient. It cannot run together with Nsight Systems profiling. [NVIDIA guide, “Fault Tolerance”](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[observed] NVRx straggler detection makes relative and individual rank performance scores. It does **not** put training at a halt by default. Automatic termination runs only with `stop_if_detected=True`. Its prerequisite: NVRx. Check the `profiling_interval` setting. Do not start NVRx and legacy MCore detectors together. [NVIDIA guide, “Straggler Detection” and “Practical Caveats”](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[observed] The re-run state machine keeps experimental/alpha status with limited integration. It runs computations again on same and different GPUs. The purpose: NaN/spiky-loss attribution to transient error, persistent hardware fault, or correct-but-unexpected output. Modes: `disabled`, `validate_results`, and `report_determinism_stats`. Job behavior uses exit codes 16/17. [NVIDIA guide, “Re-run State Machine”](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[inference] Use this hypothesis set for rerun results. A same-input/state anomaly on one GPU only: device-specific persistent fault. Intermittent same-GPU results: transient behavior. Reproducibility across devices: data/model/software or expected numerical behavior. Keep these as hypotheses, not definitive attribution; nondeterminism, topology, and execution-path changes can make them unclear. Keep exact input, checkpoint, seed, and comparison outputs. [NVIDIA guide, “Re-run State Machine”](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[observed] In-process restart keeps experimental status. Its prerequisites: PyTorch ≥2.5.1 and NCCL ≥2.26.2. Do not use it for switch failures or network partitions. Use it together with job-level fault tolerance. Preemption handling checks for termination at the end of each training step. Async checkpoint save prerequisite: `torch_dist`; local checkpointing prerequisites: sufficient local storage and a configured replication degree. [NVIDIA guide, “Preemption,” “Async Checkpoint Save,” “Local Checkpointing,” “In-Process Restart”](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

### 10.2 rack-bench implications

[inference] For the tenant’s actual recipe, keep a record of the launcher and checkpoint path. Also keep timeout configuration, restart limits, NVRx detector status, and the `stop_if_detected` status. Run a chosen same/different-GPU rerun test and check the exit codes. Check that the system does not silently put a suspect device back in use. Put an alpha mark on alpha functionality. The review keeps an unverified status for anything untested. [NVIDIA guide](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

## Gaps

- No reviewed public source shows GB300/NVL72 rack failure rates, SDC coverage, validated health thresholds, or 30–90-day rack goodput results. [inference]

- Meta’s Llama-3 >95% effective-training-time headline does not show its calculation details, checkpoint intervals, restart distribution, or MTTR. The later Meta SDC article shows mechanisms, not that run’s raw telemetry. [observed]

- ByteDance’s >90% effective time and recovery timings show results from its proprietary >10K-Ampere cluster, software, storage, and workload. The public disclosure does not show identical automation in a tenant’s rack. [observed]

- A two-hour category check cannot show meaningful long-horizon MTTF or silent-error absence. It cannot show full-cycle thermal/facility behavior or recurrent lemon-node history. It cannot show seasonal Chennai conditions or storage integrity across dozens of checkpoint generations. [inference]

- The customer must make exact acceptance thresholds for the proposed two-hour checks. Inputs: the chosen model, precision, parallelism, dataset, checkpoint size, and intended scale. The cited companies do not show a universally portable threshold set. [inference]
