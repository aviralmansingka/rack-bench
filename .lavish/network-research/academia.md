# Academic methods for diagnosing east-west fabric quality

Research date: 2026-10-11. All claims below use a source URL.

Use three claim tags. **[observed]**: direct support from a cited source. **[calculated]**: arithmetic from cited definitions. **[inference]**: recommended interpretation/design.

Scope: N06 / academia only. The scope puts academic methods and primary technical sources in use. It checks congestion and collective limits in an 18-tray GB300-class rack. The certification window runs two hours. This text makes no claim that rack-bench already contains all suggested tests.

## 1. What the measurement must answer

A collective benchmark alone shows the operation time. It does not show the limiting resource. Candidates: GPU/NVLink, PCIe/C2C, NIC, one rail, a switch path, congestion, CPU progress, or the collective algorithm. NVIDIA makes an explicit statement: NCCL `busbw` estimates the bottleneck hardware bandwidth. Candidate bottlenecks: NVLink, PCI, QPI, or network. The result does not always show the external fabric [observed] [NCCL performance definitions](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md).

**[inference]** Use four parts for a defensible certificate. Use (1) collective scaling measurements with (2) one-rail and concurrent-rail RDMA measurements. (3) Rail/topology isolation. (4) Before/after counter deltas. Correlation among those independent views makes the diagnosis. A single peak number does not show fabric health.

The local design context puts an 18-tray NVL72-class rack in scope. It shows these requirements: an 8 B–16 GB NCCL sweep, `algbw`/`busbw`, perftest, and a multi-node collective. It also shows a monotonicity heuristic [observed] [README.md](../../README.md#L320-L348). It also shows active bench checks. Items: per-rail QP sanity, a two-rank all-reduce canary, expected rail naming, and NCCL configuration [observed] [README.md](../../README.md#L220-L240). Keep these local excerpts as context, not independent evidence for performance claims.

## 2. NCCL bandwidth definitions: use the right numerator

Put **S** as the operation's total logical payload in bytes. Put **t** as the measured operation time in seconds. Put **n** as the participating rank count. NCCL-tests shows algorithm bandwidth as `algbw = S/t` (GB/s in output). It makes a useful application-level throughput. Its peak shows dependence on collective and rank count [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md).

Point-to-point Send/Recv and root-centric Broadcast/Reduce use a documented correction factor of 1: `busbw = algbw`. AllReduce uses `busbw = algbw × 2(n−1)/n`. ReduceScatter and AllGather use `busbw = algbw × (n−1)/n`. AlltoAll also uses `(n−1)/n` [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md).

**Why AllReduce's factor:** each element makes `n−1` additions plus distribution to all ranks. The document's point-to-point model puts `2(n−1)` transfers over `n` ranks/links. Ideal time: `t = (S/B) × 2(n−1)/n`. Hence `B = (S/t) × 2(n−1)/n`. ReduceScatter sends only reduction traffic; AllGather only distribution traffic. Each factor therefore makes `(n−1)/n` [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md).

**[calculated] Example, 8 ranks:** AllReduce factor = 14/8 = 1.75. If `algbw=100 GB/s`, `busbw=175 GB/s`. ReduceScatter or AllGather factor = 7/8 = 0.875, with result 87.5 GB/s. Keep those values as normalization, not physical wire counters. Do not compare `busbw` to one NIC's line rate when faster intra-tray links or concurrent rails contribute. Use only a stated topology-aware bottleneck budget for the comparison [inference] [NCCL-tests definition](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md); [Nebius NCCL test interpretation](https://docs.nebius.com/slurm-soperator/jobs/examples/nccl-all-reduce).

NCCL's document shows **S as total array bytes** for ReduceScatter and AllGather [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md). Per-rank values: `recvcount × datatype_size × n` for ReduceScatter and `sendcount × datatype_size × n` for AllGather. **[inference]** Keep these items with every result: command, rank count, datatype, per-rank count, and total S.

Also keep time, algorithm/protocol selection, and both bandwidth columns. Otherwise an independent `algbw` recomputation can silently use the wrong S.

## 3. Collective limits: separate algorithm, topology, and congestion

Ring AllReduce makes a bandwidth-efficient choice for large messages. Its decomposition: reduce-scatter plus all-gather. Across both phases, each rank sends `2S(n−1)/n` bytes in total. It receives the same volume for an S-byte tensor. Not `2S(n−1)/n` in each phase [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md); [Patarasuk & Yuan, bandwidth-optimal AllReduce](https://www.cs.fsu.edu/~xyuan/paper/07hips.pdf).

Tree methods make a smaller dependency depth for small-message latency. But they put different pressure on paths and can make root/branch bottlenecks visible. NCCL's primary test documentation shows an explicit statement. One bus-bandwidth accounting runs for all point-to-point algorithm choices under its transfer model. On real hardware, the selected algorithm/protocol and topology can still make different measured times [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md); [NCCL technical report, Jeaugey, OLCF PDF](https://www.olcf.ornl.gov/wp-content/uploads/2019/12/Summit-NCCL.pdf).

The NCCL technical report shows Tree and Ring AllReduce as distinct algorithms. Tree runs log-latency; Ring runs linear-latency with high bandwidth [observed] [NCCL technical report](https://www.olcf.ornl.gov/wp-content/uploads/2019/12/Summit-NCCL.pdf). **[inference]** Check both latency-sensitive small payloads and throughput-sensitive large payloads through normal auto-selection. If the library supports a controlled diagnostic override, check algorithm/protocol variants as a *triage experiment*. Do not use it as the acceptance default. A forced algorithm can make a non-production path.

AlltoAll makes a useful complement to AllReduce. Every rank sends distinct data. A ring AllReduce does not show its traffic pattern or hotspot behavior. NVIDIA shows all-to-all as prone to congestion/hotspots at scale. It also shows routing/message aggregation optimizations [observed] [NVIDIA NCCL all-to-all technical article](https://developer.nvidia.com/blog/doubling-all2all-performance-with-nvidia-collective-communication-library-2-12).

**[inference]** Use an AlltoAll point at representative small/medium sizes in a short rack test, or a short sweep. Use it to make path entropy and incast/contention problems visible. Do not interpret it as a universal training workload.

### Halving-doubling / Rabenseifner tradeoff

Rabenseifner-style AllReduce uses reduce-scatter plus allgather. It commonly uses recursive halving, then recursive doubling, for power-of-two rank counts. The method makes the bandwidth communication-volume lower bound with logarithmic communication rounds, unlike a simple ring's linear round count. Large payloads can show benefit from the lower round count and volume. Per-round latency and startup make the dominant costs for small payloads. Non-power-of-two rank counts use variants and can make imbalance or extra communication [observed] [Rabenseifner, “Optimization of Collective Reduction Operations”](https://www.hlrs.de/people/rabenseifner/papers); [Patarasuk & Yuan, bandwidth-optimal AllReduce](https://www.cs.fsu.edu/~xyuan/paper/07hips.pdf).

The tradeoff shows topology sensitivity. Recursive partner exchanges may put load on specific cuts. They may also show a poor fit to multi-rail and hierarchical GPU fabrics. A ring can run an even pipeline when its logical ring matches physical links. Neither option shows universal superiority [inference] [NCCL technical report](https://www.olcf.ornl.gov/wp-content/uploads/2019/12/Summit-NCCL.pdf); [Patarasuk & Yuan](https://www.cs.fsu.edu/~xyuan/paper/07hips.pdf).

**[inference]** Check the normal library-selected algorithm. Use forced variants only as controlled diagnostics, not acceptance defaults.

### Message-size sweeps and protocol switching

For each collective, use logarithmic/geometric sizes from 8 B to 16 GB. Repeat selected points. Keep raw time plus `algbw` and `busbw`. Small messages primarily show fixed launch/communication latency. Large messages increasingly show throughput [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md).

**Strict monotonicity makes an unsafe rule.** NCCL's algorithm and protocol choices may show changes across payload sizes. Tiny-message latency, chunking, pipeline depth, channel count, registration, and hardware tiers also make curve changes. A regime switch may make a legitimate step or local dip. A bad link can still make a smooth but low curve. **[inference]** Keep curve discontinuities as investigation signals, not automatic failures.

Check them against repeated-run noise and matched algorithm/protocol metadata. Do not require every successive `busbw` point to increase. The NCCL performance source shows the latency-to-bandwidth regime transition. It makes no monotonicity promise [observed] [NCCL-tests performance document](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md).

### Concurrent rail aggregation

Run each rail alone. Then run all expected rails concurrently, with traffic bound to their intended devices. **[inference]** Check aggregate goodput against the sum of isolated-rail goodputs. Also check it against the topology's realizable egress/ingress budget. Keep per-rail results as well.

Each rail can run healthy alone. The aggregate can still show poor scaling. Then check shared switch uplinks, bad rail placement/routing, NIC/PCIe/GPU feed limits, CPU launch/affinity, or congestion. Do not stop at a simple slow port. A weak lone rail with a similarly degraded pinned collective shows stronger fault localization.

A collective may send intra-node data on NVLink and cross-node data on RDMA. A high normalized `busbw` therefore does not show the NIC at that sustained rate. Nebius puts an explicit caution in place: two-node mixed NVLink/InfiniBand AllReduce can make `busbw` overestimate InfiniBand load [observed] [Nebius NCCL test interpretation](https://docs.nebius.com/slurm-soperator/jobs/examples/nccl-all-reduce). **[inference]** Keep ranks and NIC rails pinned. Keep NCCL topology/debug logs. Use concurrent per-rail RDMA as the external-fabric cross-check.

## 4. Controlled checks within two hours

Use the following as an evidence-oriented time budget, not a vendor-independent pass threshold. **[inference]** Run independent per-rail tasks in parallel under one condition only. Check first: the harness binds them and captures counters without competing with the collective phase.

| Approx. window | Check | Diagnostic value |
|---|---|---|
| 0–10 min | Put NIC/switch counters in a snapshot. Check active rate, link layer, expected rail map, and errors. Check per-rail QP/connectivity sanity. | This check removes obvious downshift, missing rail, and bad route/configuration from suspicion before bandwidth interpretation. [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html) |
| 10–35 min | Per-rail RDMA write and read bandwidth over several sizes. Small-message latency. Host-memory and GPU-memory path where supported. | Direct link/path evidence. Direction and host/GPU-path comparison. [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html) |
| 35–80 min | NCCL AllReduce/AllGather/AlltoAll geometric 8 B–16 GB sweep. Multiple ranks and MPI plus torch.distributed launch path. Repeat boundary/representative points. | This check shows collective scaling, wrong transport, threshold/protocol changes, and rank/launch issues. [NCCL-tests](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md) |
| 80–105 min | Concurrent all-rail bandwidth. Then short concurrent collective + rail traffic if safe. Put counters in a snapshot. | This check shows aggregate oversubscription and contention sensitivity, not just isolated peak. [DCQCN paper](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p523.pdf) |
| 105–120 min | Run anomalous points again. Check NCCL logs, per-rail performance, and switch/NIC counter deltas together. Put uncertainty and unresolved causes in the report. | This check keeps a single transient or host stall away from a false pass/fail. [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html) |

An 18-tray rack shows many links and rank placements. **[inference]** A two-hour bench cannot exhaustively check every ordered endpoint pair. It also cannot check all rail combinations, every message size repeatedly, or sustained thermal/failure behavior. Use topology-stratified pairs: same tray, neighboring trays, and distinct switch/plane where known. Also use all-rail aggregate and explicit representative rankfiles. Keep exhaustive mesh and long-duration stability for smoke.

## 5. Congestion causality: ECN, DCQCN, PFC, counters

The paper shows DCQCN as an end-to-end, rate-based congestion-control design for RoCEv2. It also shows the path. The switch uses ECN marks for queue-buildup signals. The receiver sends a CNP notification. The sender makes a rate reduction.

PFC keeps its role as a loss-prevention backstop. It does not show absent congestion. The authors show improved throughput/fairness in a three-tier testbed. They also show that PFC can spread congestion [observed] [Zhu et al., “Congestion Control for Large-Scale RDMA Deployments,” SIGCOMM 2015](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p523.pdf).

ECN marks show that configured queue-marking conditions are met. Do not read them as packet drops. A mark/CNP increase under load with stable throughput may show functioning congestion control. A mark increase plus queue/latency growth and throughput collapse shows overload or ineffective control.

An absence of visible marks does **not** show a congestion-free state. Possible reasons: high thresholds, unexposed counters, or a bottleneck elsewhere. **[inference]** Show mark and CNP deltas with device, priority/traffic class, time interval, and counter source.

PFC pause counters show link-level pause activity, not flow-level attribution. PFC pauses run per port/priority. Unrelated flows sharing that class/path may run into stalls. The DCQCN paper shows unfairness and “victim flow” effects. Causes: cascading pause propagation and head-of-line blocking [observed] [DCQCN paper](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p523.pdf).

**[inference]** A pause delta with latency spikes or uneven pair throughput makes a congestion warning. Do not automatically read it as a defective cable. Sustained pause storms or pause increases on unrelated links make a case for escalation to switch queue/route analysis.

Counters keep implementation-specific definitions. The stack often puts them in separate places: NIC, switch, firmware, and driver. NVIDIA's troubleshooting guide shows a recommendation: check RoCE port errors, drops, pause/PFC counters, and available ECN/CNP/queue-drop counters. It also shows RDMA retry/sequence/timeout indicators plus InfiniBand symbol, link-recovery, and link-down counters [observed] [NVIDIA NCCL network troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html).

**[inference]** Put counters in before/after snapshots. Run delta calculations. Cumulative nonzero counters can start before the run. Do not label “ECN zero” or “PFC zero” as established without actual exposure and validation of the relevant counter. Keep counter units and reset/wrap semantics in the record.

### InfiniBand congestion/performance evidence

Gran et al. ran experimental checks on InfiniBand hardware congestion control. Their paper shows congestion resolution and fairness improvement, including the parking-lot problem, under appropriate configuration. This source makes an actual IB performance study, not a modern GB300 comparison. It shows why contention and fairness tests make visible problems that unloaded peak bandwidth misses [observed] [Gran et al., “First Experiences with Congestion Control in InfiniBand Hardware,” IPDPS 2010](https://ieeexplore.ieee.org/document/5470419).

**[inference]** Put brief controlled contention in the test plan. Use multiple senders on a shared receiver/path. Use an unrelated victim flow if safely constructible. Check per-flow goodput and latency against isolated baselines. Keep fairness as diagnostic evidence, not a universal threshold. Do not transplant the paper’s testbed results numerically to GB300.

### Failure and route diagnosis

NVIDIA shows these recommendations. Use `ibstat`/`ibstatus` for active state, link layer, and rate. Use `ib_write_bw`/`ib_write_lat` for direct bandwidth/latency. Use `rdma statistic` for retry/loss symptoms. Use `perfquery` for InfiniBand physical/link errors. Use `ibdiagnet` for topology/routing diagnostics when switch-management access exists.

The guide also puts GPU-memory variants forward. Use them to check the GPUDirect path against host-memory results [observed] [NVIDIA NCCL network troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html).

**[inference]** Do not inject a physical failure during acceptance without explicit authorization. Instead, check for naturally missing/downshifted links. Check each rail isolated and in aggregate. Check the bad rail against selected collective rankfiles and topology. An observed impairment under one rail plus corresponding link/recovery counters makes a causality case. A collective slowdown alone does not.

Tenant-side tooling may show no switch/Subnet Manager access for fabric-wide route/port diagnostics. Put that in the record as an evidence limitation, not a pass.

### Link failure and mitigation evidence

NetPilot’s primary SIGCOMM paper runs a study of production datacenter failures and link-down mitigation. It shows how a failed member link can leave a logical LAG overloaded after traffic redistribution. It puts mitigation candidates through impact estimates on maximum link utilization and packet loss before deactivation. Its scope puts Ethernet scale-out datacenters in focus, not GPU collectives or InfiniBand.

The diagnostic lesson: check link state, utilization imbalance, and traffic impact together. Do not attribute a collective slowdown to one root cause by itself [observed] [Wu et al., “NetPilot: Automating Datacenter Network Failure Mitigation,” SIGCOMM 2012](https://users.cs.duke.edu/~xwy/publications/2012_sigcomm_netpilot.pdf); [Microsoft Research](https://www.microsoft.com/en-us/research/publication/netpilot-automating-datacenter-network-failure-mitigation).

**[inference]** Use passive evidence in rack certification: expected versus active link count/rate, per-rail throughput, utilization, and error/recovery counter deltas. Keep rank placement in the correlation. Do not inject or deactivate links routinely. Keep fault injection behind authorization and redundancy headroom.

## 6. Read/write asymmetry and host confounds

RDMA write and read do not make interchangeable probes. The DCQCN paper's early RoCE evaluation uses an RDMA **READ** workload. It shows different operation semantics and sender/receiver roles. It also shows READ's loss-detection limitations in the implementation discussed [observed] [DCQCN paper](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p523.pdf).

A read/write gap can start from NIC protocol/firmware behavior, receiver-side processing, direction-specific path/congestion, PCIe/GPU data path, or benchmark setup. Do not assume asymmetric physical link capacity as the cause [inference].

**[inference]** Run both directions with matched parameters. Use the same message sizes, QP count, MTU, duration, CPU affinity, memory registration, and endpoint pair. Run a repeat with endpoints swapped. Check host-memory RDMA first, then the GPU-memory/GDR path. Host-memory symmetry with GPU-memory asymmetry puts suspicion on GPU/NIC locality, DMA-BUF/GDR support, PCIe/C2C, or GPU feed. Asymmetry in both, with a deficit on one rail/route, makes a fabric or NIC port more likely.

NVIDIA shows a recommendation: host-vs-GPU-memory comparison for GPUDirect troubleshooting [observed] [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html).

Host confounds make a long list. Items: CPU scheduling/affinity, NUMA placement, PCIe congestion, and GPU clocks/power/thermal state. More items: insufficient pinned memory, QP creation/registration overhead, MPI progress/rendezvous, competing workloads, and kernel/driver differences. NCCL documentation shows pinned-memory registration failures as a communication-setup-error cause. NVIDIA's troubleshooting flow puts NIC, RDMA, and GPU-memory tests in separate steps [observed] [NVIDIA troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html).

**[inference]** Keep these records: GPU/NIC/NUMA affinity, clocks, CPU utilization, driver/NCCL versions, test command, rank mapping, and competing load. Otherwise, host bottlenecks can make false fabric-failure reports.

## 7. Statistical limits and pass/fail discipline

A two-hour sweep runs on finite samples. The finite samples may keep rare congestion, intermittent link faults, burst-loss episodes, or thermal drift uncovered. NCCL output commonly puts iterations in aggregates. Means can keep tails out of view. A single maximum-throughput result does not make a stable estimate [inference].

**[inference]** Repeat selected latency and throughput points at minimum. Make enough repeats for a median-and-spread report. Use interquartile range or p95 where iteration samples exist. Keep between-run variability separate from within-run tails. Do not present a p99 from a handful of samples as meaningful.

Use warm-up and timed iterations. Keep raw logs. Show sample count and duration. Where only aggregate NCCL timing is available, put that label on it. Do not claim a latency distribution.

These academic sources show no universal “percent of line rate” threshold. NCCL `busbw` makes a model-based normalization. A topology may put multiple link tiers together. DCQCN results keep workload/testbed specificity [observed] [NCCL-tests](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md); [DCQCN paper](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p523.pdf).

**[inference]** Make thresholds from the certified rack topology and a known-good measured baseline. Use stratification by message regime and rail count. Put uncertainty in the report. Do not turn a marketing/vendor figure or a single academic testbed's result into a universal pass bar.

## 8. Actionable suite findings

1. **[inference] Normalize correctly.** Keep the total logical payload. Use collective-specific NCCL `busbw` factors. Do not equate `busbw` with one external rail.
2. **[inference] Cross-check collective against point-to-point.** Per-rail RDMA plus all-rail aggregate shows the location of link/rail limits. NCCL shows the actual collective mapping and scale behavior.
3. **[inference] Use regime-aware anomaly detection.** Do not use strict monotonicity. Protocol/algorithm transitions, small-message latency, and tier changes can make legitimate curve breaks. Use repeatability and metadata.
4. **[inference] Check congestion causally.** Put throughput/latency anomalies with ECN/CNP, PFC, drops/retries, queue, and physical-link counter deltas. Do not read ECN marks as drops. PFC can make head-of-line blocking even without packet loss.
5. **[inference] Keep device path and fabric separate.** Matched read/write and endpoint swap keep asymmetry distinct from host/GPU feed limits. Use host-vs-GPU memory and locality controls as well.
6. **[inference] Use conservative failure-evidence handling.** A failing collective makes symptom evidence only. Rail isolation plus link/route/counter correlation makes stronger causal evidence. Do not actively pull links in an ordinary acceptance window.
7. **[inference] Show what the window cannot prove.** Two hours can show gross, repeatable bottlenecks and concurrent-load contention. It cannot show rare-event reliability, long-term congestion behavior, or exhaustive pairwise correctness.

## Gaps

- **GB300-specific academic baseline:** this research puts no primary peer-reviewed source in view. None shows expected NCCL or per-rail values for a specific GB300 NVL72 18-tray rack. Use topology-aware local measurements and the accepted configuration for thresholds.
- **Rail topology details:** README context shows multiple rails. This research makes no independent check of the exact switch/rail wiring or oversubscription. No aggregate-capacity computation without that map.
- **Counter availability:** the sources show no data on actual switch ASIC/firmware and tenant permissions. The stack may keep some of ECN marks, CNPs, PFC pause duration, queue occupancy, drops, and route counters unexposed. Show missing visibility as a diagnostic gap.
- **NCCL algorithm/protocol metadata:** the primary performance document shows the normalization only. It shows no universal expected curve or complete version-specific algorithm/protocol switching points. NCCL build, topology, and hardware put these points in different places.
- **Academic RoCE-versus-IB comparability:** this research shows no matched contemporary GB300 study. Such a study keeps identical GPU, NIC count, topology, congestion tuning, and workload under control. Do not infer fabric-technology rankings from unpaired vendor figures.
- **Failure injection:** the two-hour acceptance recommendation makes an observational, safe-by-default approach. Controlled link/switch failure testing uses explicit operational approval and a separate fault-injection plan as prerequisites.
- **Search limitation:** additional search results show rate limits. The brief consequently uses the fetched primary NCCL, SIGCOMM DCQCN, and NVIDIA troubleshooting sources in place of weaker comparisons. This brief shows no unsupported universal threshold.
