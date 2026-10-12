# AI-lab methods for diagnosing east-west fabric quality

Research date: 2026-10-11. All claims below use a source URL.

## 1. Executive finding

AI labs put three evidence kinds in correlation for fabric faults. (1) Topology-aware collective performance across representative sizes/patterns. (2) Rank-level timing. It separates compute-ready time from communication/wait time. (3) Physical network/NIC/switch telemetry. A slow all-reduce alone does not show a bad link.

Several factors can make a rank arrive late. Examples: late data-loader batches, CPU proxy starvation, GPU throttling, workload imbalance, and communication itself. Use rank-matrix collectives with per-rail isolation and counter snapshots for the strongest short certification. Keep sustained mixed-load fault discovery in smoke/burn-in. **[inference]** [Meta SIGCOMM paper](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf) [PyTorch DDP straggler analysis](https://pytorch.org/blog/straggler-mitigation) [Google Cloud straggler detection](https://cloud.google.com/blog/products/compute/stragglers-in-ai-a-guide-to-automated-straggler-detection)

## 2. Production topology evidence: do not conflate designs

### 2.1 Meta: dedicated backend RoCE; topology and routing evolved by deployment

Meta shows separate frontend (data ingestion/checkpoint/logging) and backend (training RDMA) networks. Its AI-zone backend uses a two-stage Clos. Larger DC-scale networks use an aggregator tier and keep oversubscription across zones. The paper shows Grand Teton/H100-era infrastructure, production workloads, and clusters scaling to thousands of GPUs. It makes no claim of one universal rail arrangement for every Meta cluster. **[observed]** [Meta, *RDMA over Ethernet for Distributed AI Training at Meta Scale*, §§2–3](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf)

Meta’s operational account shows special diagnostic value. The account shows poor default-ECMP performance with low-entropy, bursty collective flows. Path pinning could show imbalance under partial rack allocation or failures. The account shows 5–10% traffic-engineering improvement over E-ECMP on controlled 128-node benchmarks. But it shows extra complexity and possibly less resilience under multiple link failures.

Meta shows E-ECMP at DC scale as a tradeoff choice. Keep these as deployment-specific measured results, not a universal routing prescription. **[observed]** [Meta paper, §§4.1–4.4](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf)

Meta’s observable symptoms make a list: NIC out-of-sequence (OOS) packets, link-flap counts, and local-ACK-timeout (LAT) counts. Their paper shows OOS identification of packet drops not visible in other metrics. It also shows monitoring of long PFC pauses, buffer utilization, and congestion drops. The root cause of one turn-up performance regression: switch-image scheduling latency. No monitored congestion metric showed a baseline crossing. This makes a case for measuring latency and collective outcomes, not counters alone **[observed]** [Meta paper, §§6.3–6.4](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf).

### 2.2 DeepSeek: identify the multi-plane topology as V3/R1-era, not an older report

The primary source: the 2025 ISCA paper *Insights into DeepSeek-V3: Scaling Challenges and Reflections on Hardware for AI Architectures*. It explicitly shows DeepSeek-V3 trained on 2,048 H800 GPUs with an eight-plane, two-layer Multi-Plane Fat-Tree (MPFT) infrastructure. Node details: eight GPU/NIC pairs per node, each put on a distinct IB plane. Also a separate 400-Gb/s RoCE storage-network plane. The paper shows policy/regulatory constraints behind the missing deployment of the theoretical 16,384-GPU capacity. Actual scale: just over 2,000 GPUs **[observed]** [DeepSeek ISCA’25 paper, §§1, 5.1](https://arxiv.org/html/2505.09343v1).

Put that MPFT attribution with V3’s documented H800-era training infrastructure (the paper also shows V3/R1 architecture). Do not back-project it onto DeepSeek’s earlier V2/LLM runs or their different reported hardware. V2: the 236B MoE model (21B active). V3: 671B (37B active). That model’s report makes the explicit MPFT pairing **[observed]** [DeepSeek ISCA’25 paper, §§1–2](https://arxiv.org/html/2505.09343v1).

The topology’s diagnostic implications make a concrete list. Check physical paths independently where exposed. Then check aggregate multi-plane behavior and cross-plane forwarding. Do not equate plane with rail. Multiple physical planes may run fused beneath one logical HCA/rail. Make a list of device, port, plane, and rail mappings.

DeepSeek shows near-equivalent MPFT/MRFT all-to-all results from 32–128 GPUs. It shows >40 GB/s per GPU in its DeepEP EP pattern. It shows similar V3 training metrics at 2,048 GPUs within normal variation. But the current CX7 implementation did not make the ideal single logical NIC across planes. Cross-plane traffic ran through forwarding inside the node and could make extra latency.

The paper shows no deliberately broken-plane experiment. Keep that diagnostic implication as an inference, not an observed failure result **[inference]** [DeepSeek paper, §§5.1–5.1.2](https://arxiv.org/html/2505.09343v1).

DeepSeek also shows a distinct V3 design response to scale-up/scale-out disparity. Its node-limited expert routing makes fewer target nodes per token. This makes less IB traffic. Do not use that optimized model pattern as the sole fabric test. It can keep network demand out of view. A general all-to-all or all-rank collective makes the same demand visible **[observed + inference]** [DeepSeek paper, §4.3](https://arxiv.org/html/2505.09343v1).

## 3. Collective bring-up: diagnose connectivity, topology, and performance separately

NCCL’s own environment documentation makes rail intent explicit. It also shows rail/plane identifiers separately. A physical plane and a logical rail/HCA do not always make a one-to-one pair. Keep a physical cabling-to-device mapping on record. Do not infer it from NCCL terminology.

`NCCL_CROSS_NIC=0` keeps corresponding ring/tree traffic on the same NIC. Use it for per-NIC switch rails. Use `1` for fabrics where all NICs land on a common switch; it makes cross-NIC traffic possible. Default `2` starts on the same NIC. It can make a cross-NIC move when beneficial. Use `NCCL_IB_HCA` for explicit HCA selection and rail/plane identity assignment.

A bring-up test therefore keeps detected topology and effective NCCL selection on record. Do not infer correct rail mapping from a successful job **[observed]** [NVIDIA NCCL environment variables: CROSS_NIC, IB_HCA](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html).

A practical certification matrix, **[inference]** from production patterns and the rack-bench contract:

1. **Bootstrap/connectivity:** run a small two-rank GPU collective per representative pair, with initialization, selected transport/HCA, timeouts, and completion on record. Intra-rack NVL72 ranks may use NVLink (or multi-node NVLink/MNNVL) paths. Successful intra-rack NCCL alone does not show scale-out RDMA. For an RDMA-only result, keep the NCCL NVLink/MNNVL policy on record and check transport/HCA plus NIC counter deltas. Otherwise use a cross-rack peer. Use the intended path, not socket fallback, for PASS; coverage: wrong GID/route, dead path, bad rankfile, plugin/fallback, hangs [NCCL env docs](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html).
2. **Per-link/per-rail:** run RDMA read/write perftest and a GPU-buffer test on each mapped rail/port. Check measured throughput and latency against the same-rack peer distribution and link rate. Run one rail at a time, then all rails. This makes dead links and striping-hidden asymmetry visible. [Meta paper](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf)
3. **Collective-pattern × size sweep:** run all-reduce (DDP), reduce-scatter + all-gather (FSDP), and all-to-all (MoE/EP). Use small, medium, and large message sizes. Check latency-size and bandwidth-size behavior. Use both MPI-launch and framework path where feasible. Meta documentation shows distinct traffic patterns: all-to-all full-mesh/incast; all-reduce tree/ring; FSDP ring gather/scatter. [Meta paper, §2.2](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf) [NVIDIA NCCL collectives](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html)
4. **Rank placement and scale:** check same-tray, cross-tray, rail-aligned, and topology-spanning rank assignments. Run a progression from a small subset to the whole 18-tray NVL72 acceptance unit. Keep per-rank completion and tail in view, not only global average. Meta shows topology-aware rank assignment and scheduler placement as performance-relevant. [Meta paper, §§3.3, 6.1](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf)
5. **Before/after evidence:** put NIC counters, link state/speed, switch counters when available, NCCL logs, and GPU/CPU telemetry in snapshots. Check counter diffs around each test. OOS/LAT/link flap make especially actionable Meta signals. Keep versions/configuration with the results. [Meta paper, §6.3](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf)

A matrix shows its value because a single all-reduce score stays underdetermined. The chosen collective algorithm, message size, rank placement, and rail use put traffic and the bottleneck in different places. NCCL itself makes algorithm/protocol choices from topology and size. Its documentation shows debugging overrides as temporary diagnostic tools, not production settings. Do not start “fixing” certification with a forced algorithm/protocol. Make an exception for an explicit controlled comparison **[inference]** [NVIDIA NCCL env docs](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html) [Meta paper, §2.2](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf).

## 4. Straggler attribution: communication wait is a clue, not a verdict

Synchronous training puts waits at synchronization points. PyTorch’s DDP straggler guidance shows two effects. One rank can make an unusually long all-reduce report: it arrives early and waits for slower ranks. Another rank shows short synchronization time precisely because it enters late as the straggler. Their documentation shows the causes: outlier data examples, variable data I/O/transforms, and imbalanced pre-sync computation. Gradient-sync duration alone therefore does not show a network fault **[observed]** [PyTorch, *Straggler Mitigation on PyTorch DDP*](https://pytorch.org/blog/straggler-mitigation).

Use synchronized rank timelines for attribution. Check these together: forward/backward or “ready-to-communicate” timestamps, collective entry/exit, and exposed wait. Also check GPU clocks/utilization/throttle/ECC, CPU/proxy thread scheduling and utilization, and data-loader batch-ready times.

A fabric suspect shows more strength under conditions: the rank makes ready time, but its collective progress/completion runs late. The pattern shows repetition by HCA/rail or path. Network error/counter deltas show up at the same time. A late collective entry after slow compute/data loading points away from the fabric. Host proxy starvation with clean link signals does the same. Keep these as diagnostic rules from the sources’ causal distinctions, not a guaranteed root-cause classifier **[inference]** [PyTorch](https://pytorch.org/blog/straggler-mitigation) [Google Cloud](https://cloud.google.com/blog/products/compute/stragglers-in-ai-a-guide-to-automated-straggler-detection) [Meta paper, §6.3](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf).

Google’s production straggler service shows a two-step method. Step one: passive traffic observation for a directed communication graph. Step two: causal traversal, for separation of a waiting node from the original delay source. Its post shows deployment on an 8,000-GPU Magic workload and localization reduction from days to minutes. But the post makes a vendor-authored source without full algorithm disclosure or controlled evaluation.

It shows the scale-practice direction: dependency correlation across ranks, not isolated utilization or RTT rankings **[observed; vendor-reported impact]** [Google Cloud straggler detection](https://cloud.google.com/blog/products/compute/stragglers-in-ai-a-guide-to-automated-straggler-detection).

### 4.1 Communication/compute overlap limits interpretation

DeepSeek V3/R1 uses DualPipe to overlap attention/MoE computation with MoE communication. The paper also shows dual-microbatch overlap in inference. It shows that communication work can consume GPU SMs (up to 20 SMs in its described training case). Purposes: message handling, forwarding, copies, reductions, and casts. It also shows that inference can use NIC RDMA all-to-all to avoid some SM contention.

Observed step time therefore does not make pure network time. Compute can keep hidden communication masked until communication exceeds the overlap window. Conversely, network/proxy work can remove GPU/CPU resources from compute **[observed]** [DeepSeek paper, §§2.3.1, 4.4](https://arxiv.org/html/2505.09343v1).

For a short certification, use explicit standalone collectives to isolate fabric capacity. Then run a short representative compute+collective overlap probe. Use it to detect gross interference.

Check exposed communication time and end-to-end step time against each other. Do not label a hidden/overlapped communication phase “zero network cost.” Use longer real jobs/telemetry for full workload traces and rare stragglers. It also checks long-tail causal attribution **[inference]** [DeepSeek paper](https://arxiv.org/html/2505.09343v1) [PyTorch DDP](https://pytorch.org/blog/straggler-mitigation).

## 5. Candidate two-hour bench versus longer smoke

Use this plausible two-hour allocation for one certification unit (18 trays) **[inference]**. Prerequisites: compiled test tools, controlled scheduling, and parallel execution:

- 0–10 min: topology/rank/HCA/rail manifest and counter baselines. Check that all 18 trays participate.
- 10–25 min: NCCL initialization/connectivity canary and per-rail RDMA probes in parallel. Use a small sampled pair set plus every tray’s mapped links.
- 25–75 min: collective matrix (all-reduce, all-gather/reduce-scatter, all-to-all; latency and bandwidth sizes). Run it first on rail-aware placements, then rack-spanning ranks. Keep per-rank distributions and repeat outliers.
- 75–100 min: full-rack aggregate saturation and deliberate concurrent collectives. Use them to make contention/imbalance visible. Run counter sampling during load.
- 100–115 min: brief compute+communication overlap run with data resident in memory and fixed workload. Keep GPU/CPU/loader timings for attribution.
- 115–120 min: counter deltas, artifact completeness, deterministic rerun of failures.

Put these fail conditions on bench: non-completing collectives, missing expected ranks/rails, and measured per-link/collective results below profile thresholds. More fail conditions: severe rank/rail asymmetry, error-counter increments attributable to fabric, or a result with a silent unintended fallback. Use model/rank-count/topology calibration for thresholds. No public primary source shows universal GB300 acceptance numbers **[inference]** [NVIDIA NCCL docs](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html) [rack-bench README, `bench network`, lines 327–337](../../../README.md#L327-L337).

Use longer smoke for intermittent link retrains, rare packet drops/timeouts, cumulative counter growth, thermal/power effects, and PFC deadlock/watchdog events. It also checks failures that emerge only under sustained concurrent GPU+network load.

Meta shows rare drops, link flaps, LAT, and interactions among firmware, bursty jobs, and buffer bugs. The rack-bench README puts sustained RDMA/TCP mesh and GPU+interconnect concurrent stress in smoke. Use two hours to screen and localize obvious defects. Do not claim reliability over days from two hours. Do not claim every production model’s traffic mix either **[observed + inference]** [Meta paper, §§5–6](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf) [rack-bench README, Stage 3 smoke, lines 478–493](../../../README.md#L478-L493).

## 6. Evidence limits and interpretation

The rack-bench README makes a design specification. It does not show that network bench is implemented. It does not show that listed tests have run. It shows these proposals: 8B–16GB collectives, matrix samples, line-rate comparison, and a multi-node rankfile path. This research puts AI-lab diagnostic rationale on top, not empirical GB300 thresholds **[observed]** [rack-bench README, lines 327–337](../../../README.md#L327-L337).

Meta’s publication makes unusually rich primary operational evidence. But it shows Meta’s RoCE clusters and platforms, not an NVL72 GB300 rack. DeepSeek’s MPFT evidence shows H800/V3 context. It does not show GB300 performance. README lines 335–337 show N-node collectives for scale-out. An intra-rack NVL72-only collective may keep to NVLink/MNNVL.

It does not make RDMA-path evidence without transport/HCA/counter proof or a cross-rack peer. PyTorch’s example shows attribution pitfalls, not a universal detection algorithm. Google’s causal system makes a vendor description with limited public implementation detail. Keep these limits on claims and thresholds **[inference]** [Meta](https://cs.stanford.edu/~keithw/sigcomm2024/sigcomm24-final246-acmpaginated.pdf) [DeepSeek](https://arxiv.org/html/2505.09343v1) [PyTorch](https://pytorch.org/blog/straggler-mitigation) [Google](https://cloud.google.com/blog/products/compute/stragglers-in-ai-a-guide-to-automated-straggler-detection).

## Gaps

- No public source here shows validated per-rail, per-collective GB300/NVL72 pass thresholds or a tested two-hour schedule. Use verified platform/vendor specifications and measured healthy-rack baselines for rack-bench’s thresholds.
- DeepSeek’s report shows V3/H800 MPFT and V3/R1-era context. It does not show that all later DeepSeek deployments use this same fabric. Keep topology claims version- and run-specific.
- Meta’s counters and routing lessons do not show which equivalents a GB300/NVIDIA fabric management stack exposes. Possible absence: switch-side access/telemetry permissions.
- Public straggler writeups do not show enough implementation detail for reproduction of Google’s causal graph system. A rack bench can keep causal-friendly timestamps and counters. But robust fleet-wide diagnosis uses job telemetry and historical baselines as prerequisites.
- The proposed matrix makes a candidate design, not a schedule benchmarked against actual 18-tray GB300 setup/teardown overhead. Concurrent runs may run into contention with one another. This can make isolation invalid. Run hardware validation on exact orchestration and run ordering.
