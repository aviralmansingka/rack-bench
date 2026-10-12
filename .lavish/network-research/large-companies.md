# N04 — Large-company fabric mechanisms and rack diagnostics

Research date: 2026-10-11. All claims below use a source URL.

Claims use these marks: **[observed]** (explicit in a source), **[calculated]** (arithmetic from stated inputs), or **[inference]** (recommendation or interpretation). This brief uses east-west fabric quality as its only scope. It puts north-south internet and storage out of scope.

## 1. Answer in brief

A two-hour rack test cannot make a hyperscale-fabric architecture certification. It can show the same *failure signatures* from large operators. Use these: low path/rail entropy and imbalance; congestion and pause propagation; topology or link faults; and collective stragglers.

Run repeatable NCCL collectives on the GB300 target. Keep RCCL results as comparator evidence only. Run them alongside per-rail RDMA measurements. Keep counter readings before and after. Check rail/link symmetry and latency tails.

**[inference]** These tests check the rack and its currently reachable fabric. They cannot show global scale, routing control-plane quality, or provider-wide topology without operator telemetry ([Meta production observability](https://dl.acm.org/doi/10.1145/3651890.3672233); [Google Jupiter](https://research.google/pubs/jupiter-evolving-transforming-googles-datacenter-network-via-optical-circuit-switches-and-software-defined-networking)).

The evidence makes these groups. Group §2 shows production mechanisms and observed failures. Group §3 shows research/announced transport designs. Groups §4–5 show tenant-visible measurements and provider-side evidence.

Keep Swift as Google-authored, not Meta-authored ([Google Research, Swift](https://research.google/pubs/swift-delay-is-simple-and-effective-for-congestion-control-in-the-datacenter)). Keep Microsoft Sirius as a prototype/simulation result, not evidence of production deployment ([Microsoft Research, Sirius](https://www.microsoft.com/en-us/research/video/sirius-a-flat-datacenter-network-with-nanosecond-optical-switching-sigcomm-2020-short-talk)). **[observed]**

## 2. Production mechanisms and failure explanations

### 2.1 Meta: RoCE performance is an end-to-end property, not a NIC line-rate property **[observed]**

Meta shows dedicated frontend and backend fabrics. The backend runs RDMA NICs and distributed training. Its production AI zone uses a two-stage Clos. Larger domains use an aggregator layer. Meta keeps cross-zone traffic intentionally oversubscribed and ECMP-balanced.

A topology-aware scheduler keeps cross-zone traffic low. It puts ranks across zones with a minimum-cut heuristic ([Meta Engineering, 2024](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)).

The operationally useful failure mechanisms make a concrete list:

1. **Low entropy + ECMP hash collisions.** AI collectives can use few, repetitive flows. The flows run bursty at millisecond scale, with elephant flows at NIC rate. Five-tuple ECMP then shows uneven load spreading. **[observed]** Aggregate link capacity can show a healthy picture. One path/rail can run congested at the same time. A collective can run slow then ([Meta Engineering, 2024](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)).
2. **Placement-induced uplink imbalance.** Meta shows uneven uplink use from partial rack allocation. Training performance shows a >30% degradation. **[observed]** Check directional/rank-to-rank performance and per-rail symmetry. Do not use just total bandwidth ([Meta Engineering, 2024](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)).
3. **Failure remapping can make secondary congestion.** A failed uplink or switch starts ECMP reassignment. The reassignment shows collisions with existing flows. The whole job runs slow. **[observed]** Baseline and one-link-degraded tests can show lack of path headroom, if safely supported. Use provider switch/link event telemetry to attribute remapping ([Meta Engineering, 2024](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)).
4. **More QPs/entropy can show gains, not a universal fix.** Meta shows enhanced ECMP hashing on destination QP. QP scaling makes AllReduce gains up to 40%. Meta also shows probabilistic hashing and workload-specific tuning as limitations. **[observed]** For certification, keep NCCL channel/QP configuration records. Check single-/multi-rail results. Do not make Meta’s private routing design a mandate ([Meta Engineering, 2024](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)).
5. **Congestion control and PFC behavior show workload and implementation dependence.** Meta shows degraded DCQCN tuning at 400G. Firmware behavior/visibility makes part of the cause. Its production setup has run over a year with PFC, without transport-level congestion control, and with stable AI collectives. Meta also shows the dependence on coordination with collective software and relative GPU/network throughput. **[observed]** Simplistic rules make every RoCE fabric show a particular DCQCN/PFC profile; this account shows a conflict with them. Check outcomes and counters; do not make a provider architecture prescription ([Meta Engineering, 2024](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)).

The paper's transferable lesson: use instrumentation across **fabric, routing, transport, and collectives**. Any layer can show a slow-job cause ([SIGCOMM 2024 paper](https://dl.acm.org/doi/10.1145/3651890.3672233)). **[inference]** Tenant-visible NCCL timing alone shows the symptom. Use counters and operator data for root cause.

### 2.2 Google: Swift is Google's congestion control, not Meta's **[observed]**

Swift runs as a Google datacenter transport. It uses hardware timestamps, accurate RTT, AIMD and pacing under extreme congestion. Its authors show production deployment and testbed results. The testbed results show 100 Gb/s/server near full load and low short-RPC tail latency ([Google Research, Swift](https://research.google/pubs/swift-delay-is-simple-and-effective-for-congestion-control-in-the-datacenter)).

The primary source shows Google authors. It explicitly shows deployment in Google datacenters. **[observed]** Do not put Swift under Meta’s name.

Diagnostic implication: latency inflation under load can show queues/congestion even when no packets drop. **[inference]** Keep unloaded baseline latency and loaded latency during concurrent collective/RDMA traffic. Check median and tail, not just peak throughput. Do not use Swift itself as a tenant-side test. Its results do not show GB300 Swift use.

### 2.3 Google Jupiter: production topology engineering, not rack-level optical tuning **[observed]**

Google shows a decade of Jupiter production experience serving live traffic. The evolution uses MEMS optical circuit switches for dynamic topology reconfiguration, centralized SDN traffic engineering, and automated operations. Reported outcomes show 5× speed/capacity, 30% lower capex, 41% lower power, and Clos-comparable throughput for production traffic patterns ([Google Research, Jupiter Evolving, SIGCOMM 2022](https://research.google/pubs/jupiter-evolving-transforming-googles-datacenter-network-via-optical-circuit-switches-and-software-defined-networking)).

This shows that topology can change under software control and that routing/traffic engineering is part of fabric performance. **[inference]** Use a two-hour tenant test to check unexpected asymmetry, path-dependent throughput, or transient collective regressions. It cannot check OCS schedules or SDN policy without provider telemetry. Do not make an optical-circuit-switching claim for the Chennai rack.

## 3. Research and emerging mechanisms — not blanket production claims

### 3.1 MetaRoCE: emerging transport specification and validation results **[observed]**

Meta's August 2026 post shows MetaRoCE as a new RDMA transport designed for AI-scale Ethernet. It also shows a specification, reference implementation, and compliance suite release through OCP. Its design uses per-path RTT/ECN/utilization, packet spraying, explicit loss recovery, and per-path congestion state. It shows no PFC requirement or switch-side spraying ([Meta Engineering, MetaRoCE](https://engineering.fb.com/2026/08/24/networking-traffic/metaroce-rdma-transport-ai-ethernet)).

The post shows a 64-node AMD GPU cluster RCCL comparison and simulations/validations including loss and plane-failure experiments. It shows graceful recovery and throughput at packet loss. Keep these as Meta-reported results, not independent GB300 certification evidence. **[observed]** The post shows an OCP release plan for October 2026. Put the research date, October 11, before the planned release. Do not make a release-completion assumption ([same source](https://engineering.fb.com/2026/08/24/networking-traffic/metaroce-rdma-transport-ai-ethernet)).

Use these transferable diagnostic ideas: per-path telemetry; congestion-versus-path-failure separation; behavior checks with one degraded path/plane. **[inference]** For rack-bench, use these as counter/request fields from a compatible NIC/provider. Do not use them as a reason to install MetaRoCE or alter rack configuration.

### 3.2 Microsoft Sirius: optical switching prototype plus simulation **[observed]**

Microsoft Research shows Sirius as a proposed optically switched flat datacenter network. It uses nanosecond-scale reconfiguration, routing/scheduling co-design, congestion control, and time synchronization. It shows a small custom-laser prototype at 3.84 ns end-to-end reconfiguration over 50 Gb/s channels. Large-scale simulations show 74–77% lower power than an ideal electrical nonblocking network ([Microsoft Research, Sirius](https://www.microsoft.com/en-us/research/video/sirius-a-flat-datacenter-network-with-nanosecond-optical-switching-sigcomm-2020-short-talk)).

Keep this as research evidence. It makes no claim of Microsoft production deployment or commercial GB300 rack use. **[inference]** Keep only this transferable point: topology, scheduling, and congestion control can interact. Make rack-bench check measured path behavior. Do not make speculative optical hardware changes.

## 4. Tenant-visible checks feasible inside two hours

| Check | Failure signal it can expose | Practical method and boundary |
|---|---|---|
| **Per-rail RDMA bandwidth and latency** | Dead/slow rail, asymmetric paths, link-rate mismatch | Run `ib_write_bw` and `ib_write_lat` per HCA/rail and direction. Keep throughput, latency, link state/rate, and RDMA error-counter delta records. NVIDIA shows a recommendation: host- and GPU-memory comparisons for GPUDirect RDMA. **[inference]** Use supported local build options ([NVIDIA NCCL networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html). |
| **NCCL size sweep, 8 B–16 GB** | Small-message latency floor, bandwidth plateau, protocol transition, rank straggler | Run repeated all-reduce (and all-to-all if available) over the prescribed sizes. Keep algorithm/protocol/channels and per-rank result records (use RCCL only as comparator evidence, not as the GB300 target test). Check results against a declared hardware/link envelope, not an unsupported universal threshold. **[inference]** Use [NVIDIA NCCL performance and tuning](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/performance_and_tuning.html) and [NVIDIA nccl-tests](https://github.com/NVIDIA/nccl-tests) for primary tooling guidance. |
| **Symmetry and repeatability** | ECMP/QP entropy problems, one slow path, instability | Check each rail and both directions. Run repeats. Show min/median/p95 or max-rank completion time plus normalized goodput. An aggregate GB/s number can keep a slow rank hidden. **[inference]** Use Meta's reported low-entropy collision and >30% placement penalty as motivation for this check ([Meta Engineering](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)). |
| **Concurrent load / latency under load** | Queue buildup, incast, PFC pause, transport instability | Run collective traffic with per-rail probes where supported. Keep latency inflation, throughput loss, retries, ECN/CNP and pause counter records. **[inference]** Do not use PFC absence as a universal pass condition. Meta's production experience shows operating models differ ([Meta Engineering](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)). |
| **Controlled link/rail degradation** | Poor failover, asymmetric rerouting, collective collapse | Use provider approval first. Then put one rail out of use, or use documented maintenance/fault injection. Then check collective goodput and recovery. Do not make administrative changes to shared fabric unilaterally. **[inference]** Meta shows link/switch failures and path reassignment as a collective slowdown source. Without approved injection, check observed events against provider counters ([Meta Engineering](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)). |
| **SHARP / in-network collective path** | Missing/offline SHARP, fallback behavior, unexpected performance | Check SHARP support and actual selection. Run the same collective with and without it, only when supported and safe. **[inference]** Feature availability alone makes no measured performance. NVIDIA shows SHARP offload integration with NCCL and configuration requirements ([NVIDIA SHARP documentation](https://docs.nvidia.com/networking/display/sharpumv352/nvidia+scalable+hierarchical+aggregation+and+reduction+protocol)). |

**Two-hour allocation [inference]:** keep ~10 min for inventory/counters and environment capture. Keep ~25 min for per-rail RDMA baseline. Keep ~50 min for NCCL size sweeps and repeats. Keep ~20 min for concurrent-load/latency checks. Keep ~10 min for optional SHARP comparison or approved degradation. Keep ~5 min for final counter capture and report.

Keep buffer for setup and one rerun. This window makes no reliable room for long burn-in, fleet-scale all-to-all, or disruptive fault injection.

The excerpted local project context uses `/home/avirus/.herdr/worktrees/rack-bench/research-network/.lavish/network-research/README.md` (research boundaries and acceptance). It also uses `research.md` (N04 scope and expected evidence). Keep these as context documents, not benchmark implementations or local-test-behavior evidence. **[observed]**

## 5. Counters, root-cause limits, and evidence confidence

### 5.1 Collect before/after deltas, not just snapshots **[inference]**

Keep per-port byte, error/discard, link-state, symbol/CRC fault, and retransmit/timeout counters where exposed. Keep ECN mark/CNP counters for RoCE, PFC pause-frame/duration counters per priority, and NIC queue/congestion counters. Put timestamps alongside NCCL run IDs, ranks, rail mapping, and test phases. NIC/switch generations show different counter names and semantics.

Keep device/driver/firmware and unit records. A static counter value without a delta or run correlation makes weak evidence. NVIDIA shows RDMA retry/error, InfiniBand port-error, and RoCE drop/pause/ECN/CNP counters as diagnostics ([NVIDIA NCCL networking troubleshooting](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)).

### 5.2 Provider telemetry required for root cause **[inference]**

Tenant data can show *where* performance is uneven but usually not *why*. Send requests for time-correlated switch port counters and queue occupancy. Send requests for ECN/PFC and pause propagation data and ECMP route/hash or adaptive-routing decisions. Also send requests for link flaps/optic alarms, switch health, oversubscription/topology mapping, and maintenance/fault events.

Meta's account explicitly shows fabric, routing, transport and collectives. Google's Jupiter uses centralized SDN and automated topology operations ([Meta paper](https://dl.acm.org/doi/10.1145/3651890.3672233); [Google Jupiter](https://research.google/pubs/jupiter-evolving-transforming-googles-datacenter-network-via-optical-circuit-switches-and-software-defined-networking)). **[inference]** Without such evidence, show “measured symptom; cause unconfirmed,” not “bad ECMP” or “bad PFC.”

### 5.3 Conflicts and confidence

- **PFC/DCQCN expectations:** Meta's production account shows stable AI traffic without transport congestion control after DCQCN issues. Keep that account as workload/topology specific. **[observed]** Keep confidence high for the account. Keep confidence low for generalizing it to another vendor/rack ([Meta Engineering](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)). Check measured loss, latency, pauses and goodput. Do not use a configuration dogma as the score.
- **Adaptive routing/QP scaling:** Meta shows its own evolution and gains. Traffic, placement, and switch/NIC capabilities make the results differ. **[observed]** Keep confidence high for the failure-mode explanation. Do not make it a universal expected feature ([Meta Engineering](https://engineering.fb.com/2024/08/05/data-center-engineering/roce-network-distributed-ai-training-at-scale/)).
- **Swift:** Google Research directly shows Google production deployment. Do not use it as adoption evidence for Meta or this rack. **[observed]** Keep high confidence in authorship and reported deployment ([Google Research, Swift](https://research.google/pubs/swift-delay-is-simple-and-effective-for-congestion-control-in-the-datacenter)).
- **Jupiter:** Google primary publication explicitly shows production experience on live traffic. **[observed]** Keep high confidence in production status. Keep its rack configuration prescription relevance low ([Google Research, Jupiter](https://research.google/pubs/jupiter-evolving-transforming-googles-datacenter-network-via-optical-circuit-switches-and-software-defined-networking)).
- **Sirius:** Microsoft Research source explicitly shows the prototype and simulation distinction. **[observed]** Keep high confidence in reported experimental status. It shows no production deployment ([Microsoft Research, Sirius](https://www.microsoft.com/en-us/research/video/sirius-a-flat-datacenter-network-with-nanosecond-optical-switching-sigcomm-2020-short-talk)).
- **MetaRoCE:** Meta source shows open specification plans and a vendor implementation/testing. It shows no broad production availability or GB300 compatibility. **[observed]** Keep high confidence in the Meta claims. Keep lower confidence in independent/generalizable performance ([Meta Engineering, MetaRoCE](https://engineering.fb.com/2026/08/24/networking-traffic/metaroce-rdma-transport-ai-ethernet)).

## 6. Gaps

- No public primary source shows the target Chennai rack's transport, adaptive-routing mechanism, SHARP configuration, or congestion-control policy. Send for operator inventory and configuration evidence.
- Public large-company accounts make no independent evaluations. Operators make these performance-number and causal-interpretation claims. Use independent replication on the target 18-tray rack.
- These sources alone make no defensible universal goodput/latency pass thresholds. Make thresholds from GB300/NVL72 topology, NIC speed, rail count, software versions, and vendor acceptance envelope.
- Keep per-rail fault injection and simultaneous congestion testing as possibly unsafe or unavailable for tenants. If unavailable, use provider-side counters and event timelines. Otherwise, make the certification from observed performance only.
- MetaRoCE's announced October 2026 release may run past the research date label or keep a pending status. Do not make a claim of already-available specification/release.
- The seed phrase “self-serving fabric” shows no identifiable primary-source title in a bounded exact-phrase search. Keep this as a search gap, not evidence that no such post exists.
- Keep the local files cited above as scope/context only. The N04 task inspection shows no repository source files or exact line-level implementation evidence.
