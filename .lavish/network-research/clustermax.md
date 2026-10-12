# ClusterMAX 3.0 — East-West Fabric Coverage Research

Research date: 2026-10-11. All claims below use a source URL.

## 1. Current release and evidence model

### 1.1 Current release [observed]

The live homepage shows ClusterMAX 3.0 (September 2026) as the current release. It shows “3.0 (current)” and earlier releases ([release page](https://www.clustermax.ai), [3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). The article shows a request for 32 GPUs (4×8 HGX or 8×4 NVL72). It also shows an 800G RoCE or XDR InfiniBand fabric where available. It shows five days each for Slurm and Kubernetes testing ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

### 1.2 Methodology is not the public CLI [observed]

SemiAnalysis makes Audit public. Audit runs about 15 minutes. The Performance phase uses pass/fail thresholds with microbenchmarks and real workloads. SemiAnalysis keeps the rest of the test suite internal ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

The current `cmax` README shows the released tool as an audit CLI. The README shows its initial release as a small subset. The core audit does not run planned performance or reliability tests ([public cmax README](https://github.com/SemiAnalysisAI/clustermax)). It shows no performance, reliability, provider-side and scale-out-network evidence ([public cmax README](https://github.com/SemiAnalysisAI/clustermax)).

Keep the NCCL and endurance methods below as publicly described proprietary testing. Buyers cannot use them through public `cmax` today.

## 2. What the published east-west suite measures

### 2.1 Collectives and message-size sweep [observed]

The article shows this sweep: ClusterMAX runs MPI collectives through NCCL or RCCL across 8-byte to 16-GB message sizes. The article shows these named operations: all-to-all, all-reduce, and all-gather. It also runs the same workloads through PyTorch `torch.distributed` ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). This checks more than a NIC's nominal rate. It runs collective algorithms and software launch paths. The sweep uses latency-sensitive small messages and bandwidth-dominated large messages.

The article shows MPI and `torch.distributed` as separate launch paths. It shows no names for two specific MPI implementations. The article shows no evidence of an identical full sweep for every NCCL/RCCL configuration. **[inference]** Use a certification harness that keeps framework, launcher, rank placement, algorithm/protocol, and fabric mode with each result. Unlike-for-like curves make no fair comparison.

### 2.2 Normalization, curve shape, and monotonicity [observed / inference]

ClusterMAX checks collective bandwidth and latency across message sizes and world sizes. The article shows no single normalized “goodput-%” headline metric for every collective ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). The Google example shows 16-node, 16-GiB all-to-all at 99.5 GB/s with gIB versus 95.3 GB/s with other providers’ setup. The article shows NVLink disabled to isolate scale-out RoCE ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

**[calculated]** 99.5 GB/s makes approximately 796 Gb/s of reported collective bus bandwidth. Do not use it as a universal line-rate percentage. Make the usable denominator from per-GPU rails, topology, algorithm, and the traffic fraction across the scale-out boundary.

The article shows a roughly logistic, monotonically increasing curve with message size. Its GCP jagged curve shows a wrong GID initially. It then shows a missing gIB plugin ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

**[inference]** Keep monotonicity as a diagnostic heuristic, not a health proof. Collectives can start a different algorithm/protocol at size thresholds. Topology puts effective bandwidth at different values.

Make tolerance bands. Keep raw points. Check abrupt regressions. Do not fail every local dip unconditionally.

### 2.3 Per-rail RDMA and scale [observed]

They use `ib_write_bw` and `ib_read_bw` per network rail. They also run host-memory fallback over PCIe to check for path-specific problems ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). ClusterMAX keeps doubling world size until it uses the whole allocation. It also makes NVLink-disabled GB200/GB300 NVL72 runs to isolate the scale-out fabric ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). Use careful accounting for results: world size, algorithm, placement relative to the scale-out boundary, and NVLink state ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

The article shows Prime Intellect tests up to 13 nodes on ConnectX-8 after NCCL bootstrap standardization. Separately, its Google Cloud example shows 16-node, 16-GiB all-to-all results ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). **[inference]** Prime Intellect’s example shows thirteen nodes. GCP shows 16 nodes. The article shows no ClusterMAX overall maximum tested scale. Neither point shows a universal target or performance at larger scales.

### 2.4 Endurance and concurrent GPU load [observed]

Reliability testing starts with an eight-hour simultaneous GPU-GEMM and network all-to-all burn-in. Monitoring keeps temperature, power, clock, FLOPs, connectivity, latency, bandwidth, and kernel-ring-buffer error records ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

The methodology then shows a further sustained scale-out/scale-up fabric test. It runs large-message all-to-all, all-gather, and reduce-scatter loops. It shows average/minimum/maximum bandwidth and collective errors ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). The public description shows no duration for this second fabric loop.

Keep the eight hours as an endurance/reliability phase. Do not use them as a two-hour quick performance pass.

**[inference]** Make the defensible parity target a bounded representative collective/rail sweep, telemetry, and short repetition. Use it within a two-hour rack certification window. Do not make an equivalent eight-hour endurance claim. Link retrains, packet errors, retries, and collective errors make useful measured signals. They do not by themselves show a switch, cable, NIC, or congestion-control root cause.

## 3. What fault injection and teardown actually show

The documented injection methods make a GPU-centric set. The set uses DCGM error injection, synthetic NVIDIA XID/SXID messages written to the kernel log, and PCIe upstream-bridge reset. The PCIe reset makes a genuine XID 79. AMD systems show a UMC RAS error. The team checks detection, drain duration, and return-to-service time ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

Separately, the team runs reboots on all cluster nodes. The team checks recovery time ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

An Oracle MI355X case shows per-rail `ib_write`/`ib_read` testing across all eight NICs. The tests show 391 Gb/s on every rail. The case shows the node wedged during RDMA connection-manager teardown. The ports still show ACTIVE at 400 Gb/s. The node still shows Ready. RCCL failures and `dmesg` inspection show the issue ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

**[inference]** This makes direct evidence. Peak bandwidth plus link-state/Ready checks show no guaranteed detection of a broken post-test control path. A teardown-completion check and post-test canary (e.g. fresh RDMA operation or collective) make valuable complementary gates.

**Correction to README assumption:** the public methodology does not show deliberate network link-flap injection. It does not show switch-port shutdown or a node kill while collectives run. The public methodology shows real node reboots and GPU error injection. They show no evidence of link-flap/node-kill job-level fabric failover testing. Do not put such network-fault injection claims on ClusterMAX without further evidence.

(The local README makes the stronger claim at lines 504–506. The published description shows no support for its own coverage statement: [local README, lines 497–516](file:///home/avirus/.herdr/worktrees/rack-bench/research-network/README.md#L497).)

## 4. Public criteria and public tool boundary

The official Networking criteria page shows the dimension as performance, latency, connectivity, RDMA and high-speed interconnects. Its rendered public page shows no detailed criterion list in the fetched text ([criteria page](https://www.clustermax.ai/criteria/networking)). The 3.0 article nonetheless shows active NCCL/RCCL, RDMA-perftest, scaling, and endurance methods as above ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). Keep criteria/checklist items and audit inventory separate from those proprietary measurements.

The public CLI's networking profile checks configuration and inventory. The README explicitly shows performance/reliability testing as not included. Standalone audits show no scale-out checks ([public cmax README](https://github.com/SemiAnalysisAI/clustermax)). Public sources show no internal benchmark code or raw provider result corpus. They show no exact pass thresholds, sweep timing, or reproducible command lines. A provider rating therefore makes no independently reproducible performance certificate from the open CLI.

## 5. Coverage gaps material to rack certification

1. **PFC/ECN:** ClusterMAX shows observed fabric throughput, latency, collective errors, and monitoring telemetry. Its public methodology does not show deliberate PFC-storm testing, pause-frame validation, ECN marking/threshold validation, or congestion-control misconfiguration injection ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)). Use the phrase “not described publicly,” not proven absence from internal methods.
2. **Asymmetry and drift:** Per-rail RDMA tests can show a weak rail. The article shows all-pair directed management-network testing only for the frontend network. The public text shows no systematic east-west per-rank/per-rail asymmetry report, cross-node drift baseline, or repeated time-series drift threshold ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).
3. **Failure path coverage:** Public sources show no description of link flap, switch failure, or routing convergence. They show no description of collective recovery/job checkpoint behavior during network failure. Do not use GPU/XID injection and whole-node reboot as substitutes ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).
4. **Scale limit:** Prime Intellect’s example shows 13 nodes. GCP’s example shows 16. The article shows no overall maximum tested world size across providers ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).
5. **Diagnostic granularity:** The public article shows selected output and case narratives. It shows no raw per-rank/per-rail traces, stable thresholds, or full private results dataset ([3.0 article](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)).

## 6. Two-hour parity takeaways for GB300 NVL72

A two-hour `bench network` can reasonably use the most diagnostic quick checks. Use link/rail state and error counters. Run per-rail `ib_write_bw`/`ib_read_bw`. Check small-message latency. Run representative NCCL all-reduce/all-gather/all-to-all from 8 B through large payloads.

Use both MPI and PyTorch launch paths. Use bus bandwidth normalized to the expected fabric and topology. Make a curve-shape/regression check. Keep NVLink-enabled and scale-out-isolated modes distinct.

**[inference]** This selection puts configuration mistakes, missing rails, poor small-message latency, scale-out bottlenecks, and conspicuous asymmetry first. It keeps longer endurance and fault recovery in `smoke`.

Do not make ClusterMAX-equivalence claims for a two-hour result. Its described 8-hour concurrent GPU/network burn-in and additional sustained fabric loop run past the bench window. Do not show static inventory as measured throughput. Local `README.md` shows this bench target at [lines 327–337](file:///home/avirus/.herdr/worktrees/rack-bench/research-network/README.md#L327) and smoke at [lines 478–493](file:///home/avirus/.herdr/worktrees/rack-bench/research-network/README.md#L478). Keep those as project design targets, not implemented functionality, per [lines 17–22](file:///home/avirus/.herdr/worktrees/rack-bench/research-network/README.md#L17).

The public audit can check configuration and topology. The proprietary ClusterMAX Performance and Reliability phases show evidence that the audit CLI does not. Do not make either equivalent to this project's acceptance rule. This project's acceptance rule keeps PASS measured and never vendor-claimed ([cmax README](https://github.com/SemiAnalysisAI/clustermax), [local README, lines 117–130](file:///home/avirus/.herdr/worktrees/rack-bench/research-network/README.md#L117)).

Put adjacent slices in the [internet sibling brief](/home/avirus/.herdr/worktrees/rack-bench/research-internet/.lavish/internet-research/clustermax.md) and [storage sibling brief](/home/avirus/rack-bench/.lavish/storage-research/clustermax.md). This brief does not check those topics again.

## Gaps

- Public sources show no disclosure of the private suite's exact commands or thresholds. They show no full provider run artifacts, elapsed time per test, or full scale-out result matrix.
- The public text shows no PFC storms or ECN misconfiguration. It shows no fabric route manipulation, link flap, or node kill during a live collective. Keep these topics **not described publicly**. The text cannot show whether private or provider-specific extensions ever tested them.
- Public sources show both Prime Intellect’s 13-node example and GCP’s 16-node example. They show no overall maximum.
- The criteria page's rendered public text shows no full itemized networking list. This brief uses the official article for test-method claims, not an inferred scorecard.
