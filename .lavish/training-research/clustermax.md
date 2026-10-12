# ClusterMAX and training-run health: what a short acceptance test can establish

Research date: 2026-10-11. All claims below use a source URL.

## 1. Executive answer

ClusterMAX 3.0 does not make only a configuration audit. The current published methodology shows two short, real training workloads: Llama 3.1 8B pretraining and GPT-OSS MoE. It also shows detailed compute/network/storage benchmarks, an eight-hour combined GPU/network burn-in, and explicit health-check fault injection. These procedures put gross performance/configuration defects, collective-path problems, thermal degradation, detectable GPU errors, and some scheduler/remediation failures on display. This research makes no reproduction of the runs. [observed methodology] [ClusterMAX 3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The public evidence does not show a 54-day run or model convergence from a two-hour test. It does not even show restart correctness end to end. The article shows no procedure or acceptance criterion for Llama loss-trend triage. It shows no criterion for checkpoint-resume numerical equivalence, interruption accounting/goodput during actual training, or multi-day stability. SemiAnalysis explicitly shows this limit: its hands-on process cannot directly check reliability over time or performance at scale. [observed] [ClusterMAX 3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

For this rack-bench project—GB300-class NVL72, 18 trays, Chennai—keep separate evidence types. Use these types: audit/configuration, component and workload benchmarks, burn-in, injected-fault response, and actual training convergence. A measured PASS in any one does not show the others. None of them makes a 30–90 day availability guarantee.

[inference] [basis: ClusterMAX keeps audit, performance, reliability, and fault-tolerance phases separate, and shows reliability over time as not directly testable in its hands-on evaluation](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 2. Current ClusterMAX coverage

### 2.1 Product, scope, and current release

The current ClusterMAX site shows 3.0 (September 2026) as current. It shows the historical 2.1, 2.0, and 1.0 versions. 3.0 shows 77 rated providers. It shows managed GPU cluster evaluation through audit, performance, reliability, and fault-tolerance testing. [observed] [ClusterMAX site](https://www.clustermax.ai) [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

For its sample, SemiAnalysis makes one request. The request: 32 GPUs (four 8-GPU HGX nodes or eight 4-GPU NVL72 nodes). The request also puts high-bandwidth networking, file and object storage, and dashboards on the list. The request runs up to five days each for Slurm and Kubernetes testing.

The list of acceptable accelerators shows GB300. This makes a multi-day access window. It does not show that one training job runs for five days. Published 3.0 training procedures show workload types but not job durations. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The target rack here makes a material difference in topology and context. Its context: 18 GB300-class trays in one NVL72-class rack, Chennai. ClusterMAX shows tests across heterogeneous allocations/providers. ClusterMAX shows no complete same-rack test recipe or results for this exact Chennai configuration. Therefore, keep the direct application of its findings to this target limited.

[inference] [basis: the requested test allocation makes 32 GPUs; the article shows heterogeneous providers; it shows no Chennai 18-tray test specification](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

[3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

### 2.2 Audit/configuration (not a workload benchmark)

The public `cmax` CLI explicitly makes an audit tool. It makes only an initial subset of the full internal suite. It checks installed versions, hardware/software inventory, scheduler and container setup, networking configuration, health telemetry, and selected binary checks. The README shows one omission. The omitted criteria make performance, reliability, provider-side, commercial/contractual, or scale-out evidence necessary. Core audit does not run planned performance or reliability tests. [observed] [public `cmax` README](https://github.com/SemiAnalysisAI/clustermax)

Accordingly, `cmax` can make a useful preflight on prerequisites (for example GPU/device visibility, topology/NCCL configuration, utilities, and health instrumentation). But `cmax` alone does not make certifications for achieved Llama throughput, MFU, convergence, recovery correctness, or long-run reliability. The repo also shows an exclusion list: benchmark implementations, provider results, internal notes, private dashboard, and database code.

[observed] [public `cmax` README](https://github.com/SemiAnalysisAI/clustermax)

### 2.3 Performance benchmarks and real training

The 3.0 methodology shows per-GPU GEMM and grouped-GEMM measurements across supported precisions and model-like shapes. It also shows memory bandwidth/copy tests and HPL-MxP. HPL-MxP uses compute, memory, MPI, NVLink, and numerical correctness together. But it makes a linear-system benchmark, not evidence of optimizer convergence or correct model training. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

It runs scale-up/scale-out collectives over message sizes and world sizes. The benchmark set shows NCCL/RCCL, MPI, `torch.distributed`, RDMA perftest, and NVLink-disabled runs. ClusterMAX uses these runs to check scale-out behavior alone. The published methodology shows these benchmark runs. This brief makes no reproduction of them.

Their results can show configuration and fabric bottlenecks relevant to training. But benchmark output does not itself make a full training goodput or 54-day reliability measurement. [observed methodology; inference on implication] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

For actual training, the article explicitly shows two torchtitan jobs. The first torchtitan job: Llama 3.1 8B pretraining on C4 with FSDP, described as FLOPs-bound. The second torchtitan job: GPT-OSS MoE training with expert parallelism, described as collective-bound except on NVL72. The published methodology shows application-level training coverage. The MoE workload makes network problems visible, per the methodology. This research makes no reproduction of the jobs or results. [observed methodology] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The article shows no fixed run duration, token/step count, or seed for these two training jobs. It shows no target loss curve, convergence threshold, repeatability tolerance, or per-provider MFU results. It makes no statement that training passes use converged loss. It also shows no standardized loss-triage rubric. Therefore, the article shows coverage of a runnable short training workload. It does not show a public reproducible convergence acceptance protocol. [observed, bounded to published methodology] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

### 2.4 Burn-in, fault injection, and reliability response

The published burn-in runs eight hours: large tensor-core GEMMs and all-to-all communications run simultaneously. Monitoring keeps records of temperature, power, clock, FLOPs, connectivity, latency, bandwidth, and kernel-ring-buffer errors. This can show concurrent-load, thermal, clock-throttling, and hard-error symptoms during that interval. It makes a materially stronger test than a two-hour-only stress test. But it does not show multi-day reliability. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

Other reliability procedures show sustained collectives. They also show frontend management-network packet loss, RTT, and TCP bandwidth between directed node pairs. They show filesystem endurance: 7.5 minutes sequential mixed I/O plus 7.5 minutes random mixed I/O per client count. They show 15-minute object-storage mixed operations.

The article shows these bounded test procedures. This research makes no reproduction of their results. They do not make continuous operational exposure. [observed methodology] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The fault handling tests run separately. The tests use node reboots. They put in DCGM errors or synthetic XID/SXID kernel messages. The final method uses a PCIe bridge reset to make a genuine XID 79. Then the tests check the timing of detection, drain, and return-to-command availability. This checks provider health-check and scheduler/remediation behavior.

It does not make a training-job fault/restart experiment. The methodology makes no claim of an injected event during Llama training. It also makes no claim that the run starts again from checkpoint and checks numerical continuity. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

For NVL72, ClusterMAX makes this statement: hot-swapping a node does not make practical sense. Its expectation: a health check makes an unhealthy node visible within two minutes. The check also keeps scheduling off it. The proposed “NVL64+” SLA puts a rack in the down state. The trigger: three or more of its 18 nodes in simultaneous failure.

This makes useful rack-specific reliability context. But detection/containment and contractual downtime definitions make separate concepts from model progress preservation. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The online Reliability criteria show stated evaluation requirements. The requirements: network stability, SLA evaluation, link-flap monitoring, GPU fall-off-bus and PCIe errors, thermal/power/ECC monitoring. More requirements: XID/SXID detection, IB health/counters/PKey consistency, NCCL/topology health, and NVLink error tracking (called critical for NVL72). They do not make proof of uniform measurement through a public, reproducible procedure. [observed] [Reliability criteria](https://www.clustermax.ai/criteria/reliability)

### 2.5 Training-specific indicators and what is easy to misread

The same article shows a future PostTrainingX/RL benchmark. The benchmark shows trainer/rollout metrics. These metrics: training throughput, optimizer-step time, MFU, train/rollout KL, and policy staleness. More: clipping fractions, gradient norms, and rejected rollouts. It also shows archived trajectories/logs and reproducibility for that benchmark.

Crucially, this framing makes upcoming evaluation of RL/post-training infrastructure. It does not make evidence that ClusterMAX 3.0's Llama 3.1 pretraining suite already uses those measures. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

Thus the public methodology shows support for “MFU is named for the planned PostTrainingX trainer metrics,” not “ClusterMAX publishes standardized MFU validation for its Llama 3.1 pretraining runs.”

Likewise, this research shows no public procedure for loss-anomaly classification: data, numerical, or hardware-induced. It shows no procedure that makes the pass decision for a loss curve. [observed absence in inspected corpus] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

### 2.6 Related storage work: do not conflate it with long-run validation

ClusterMAX shows a custom Torch/Torch DCP checkpoint save/load benchmark. It also shows a custom datagen workload shared by Skild AI. The article shows these benchmarks. This makes a description of published coverage, not independently reproduced results. They make relevant storage throughput/functionality evidence. They do not make a published training interruption/recovery trial or a 54-day checkpoint lifecycle validation. [observed methodology; inference on scope] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The sibling storage brief shows the DCP checkpoint save/load and Skild AI datagen methodology at `/home/avirus/rack-bench/.lavish/storage-research/clustermax.md`, lines 21–22 (§1.2). This makes inherited secondary research, not independently verified benchmark execution or locally reproduced results. The primary methodology article itself shows both tests. [inherited from sibling brief; primary-methodology report](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) [local source: `/home/avirus/rack-bench/.lavish/storage-research/clustermax.md#L21-L22`]

## 3. Public coverage gaps (carefully bounded)

### 3.1 What this absence claim means

Inspected corpus: the live ClusterMAX site and Reliability criteria page. Also in the corpus: the full readable ClusterMAX 3.0 methodology article, and the public GitHub `SemiAnalysisAI/ClusterMAX` README. The 3.0 article makes an explicit statement: the public audit makes only the released portion. The article also shows “the rest we keep internally for now”. The public repository shows an exclusion of benchmark implementations and provider results. These findings show public discoverability, not the contents of private procedures. [observed] [methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) [repo](https://github.com/SemiAnalysisAI/clustermax)

The following make “no public standardized procedure found in this inspected corpus,” not claims that SemiAnalysis never runs them privately or that no provider does them.

[inference] [basis: the methodology keeps the rest of its test suite internal, and the repo keeps benchmark implementations/results out](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) [public repo](https://github.com/SemiAnalysisAI/clustermax)

### 3.2 Missing public training-run procedures

1. **MFU for the named Llama pretraining acceptance run:** The methodology shows no measured MFU values for that run. It shows no formula/denominator, sample window, or acceptance threshold. The methodology explicitly shows MFU for upcoming PostTrainingX trainer performance. Therefore, “MFU is absent everywhere” makes a false statement. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

2. **Numerical resume equivalence:** No published procedure makes these steps. One step puts an interruption during training. One step runs a load of a saved checkpoint. One step checks resumed optimizer/model/data-loader state or subsequent outputs against uninterrupted control. Checkpoint storage benchmarking alone does not show this. [observed absence, bounded] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

3. **Loss triage/convergence criteria:** No public source makes these specifications. The absent items: fixed loss bounds, expected curve, divergence alarms, and finite-value checks. Also absent: gradient/optimizer diagnostics or adjudication protocol for a Llama training PASS. Upcoming RL metrics such as KL and gradient norms do not remove this pretraining-method gap. [observed absence, bounded] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

4. **Training interruption and recovery accounting:** Fault injection makes timing measurements: detect, drain, and return. But the public method shows no interrupted training steps, checkpoint age, or lost work. It shows no restart latency, recovery success, or training goodput for a deliberately interrupted and resumed job. [observed absence, bounded] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

5. **Long-run stability:** The explicitly described workload windows do not show a 30–90-day run. Those windows: eight-hour burn-in, 15-minute object-store test, and short stated storage endurance intervals. SemiAnalysis itself puts reliability over time among the not-directly-measurable items in its hands-on test allocation. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

6. **Long-horizon failure rate and goodput:** The article shows goodput and customer-reported reliability as important. But it makes no publication of a standardized multi-day numerator/denominator or uptime series. It shows no interruption distribution or confidence bound with projection to 54 days. [observed, bounded] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 4. What a two-hour rack-bench can honestly say

A two-hour category check cannot run ClusterMAX's eight-hour burn-in. It cannot run the longer provider evaluation. It can still make useful, measured evidence. But make its short-window-screen role explicit.

[inference] [basis: ClusterMAX shows an eight-hour combined burn-in and up to five days of test access per scheduler](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) [PROPOSAL]

For this rack, run a representative Llama-3-class training workload with the intended software/configuration. Keep a record of the exact recipe, parallelism, batch/sequence lengths, precision, data source, seed, and checkpoint policy.

[PROPOSAL; motivated by ClusterMAX’s named Llama 3.1 training run and listed telemetry/metrics, but not a ClusterMAX procedure](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

Make these training-health observations within two hours. Check (a): successful distributed initialization and stable steps. Check (b): step-time distribution and throughput after warm-up. Show (c): measured MFU with formula and hardware peak assumptions disclosed.

Check (d): loss/gradient/parameter finite values and trend review against the run's expected short-horizon behavior. Check (e): GPU clocks/temperature/power/ECC/XID and NCCL errors correlated to steps. Run (f): one checkpoint save and restore, then a deterministic or tolerance-bounded state/output comparison under an explicitly controlled recipe. These items make proposed rack-bench checks, not procedures from ClusterMAX.

[PROPOSAL; ClusterMAX publicly shows separate node reboot/XID fault tests and DCP save/load benchmarking, but not training interruption/resume](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

Put one operator-approved, non-destructive interruption after checkpoint creation, time permitting. For example, use preemption or worker process restart. Do not use physical PCIe fault injection. Then show detection, pause, restart, lost steps, checkpoint age, resumed throughput, and state-equivalence result. Do not make this event evidence that provider hardware fault remediation keeps training state. Make that claim only when the fault actually runs in the training path.

[PROPOSAL; the CLI uses discrete pass/warning/fail/skipped states and ClusterMAX keeps audit, performance, and reliability phases separate](https://github.com/SemiAnalysisAI/clustermax)

Show PASS only for the measured interval and defined assertions. Show these results separately: config/audit PASS; component benchmark PASS; short burn-in PASS; actual training smoke PASS; checkpoint round-trip PASS; injected-fault response PASS

Do not make a single umbrella “54-day safe” verdict.

## 5. Decision for the tenant considering 30–90 days

ClusterMAX evidence makes a useful screen for the infrastructure and management stack. Its short Llama/MoE runs show more than synthetic GEMM alone. The public evidence makes no answer to “will my 54-day run survive?”

A two-hour rack-bench can make uncertainty smaller: immediate performance, numerical sanity, basic checkpoint handling, and observed faults. It cannot show the probability of multi-week outages. It cannot make a convergence guarantee.

[inference] [basis: published reliability testing keeps a time-bounded character, and SemiAnalysis puts reliability over time outside direct hands-on measurement](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

[3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

[PROPOSAL; ClusterMAX shows SLA definitions, downtime, monthly review, and acceptance testing as contract topics](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

Make an operational plan a requirement before commitment. Put these in the plan: checkpoint cadence and externally durable copies, tested resume procedure and ownership, and telemetry/log retention. Also put these in the plan: maintenance and interruption notice, escalation SLA, and rack/NVL72 downtime definition. Put one more item in the plan: a customer-visible interruption/goodput report over time. These items make buyer safeguards proposed here. The brief makes no claim of public ClusterMAX validation. [Reliability criteria](https://www.clustermax.ai/criteria/reliability) [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 6. Source confidence and limits

- **High confidence:** ClusterMAX 3.0 publicly shows Llama 3.1 8B and GPT-OSS MoE training. It also shows the simultaneous eight-hour GEMM/all-to-all burn-in. It shows specified node health-check/fault injection. These items make direct statements in the primary methodology article. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

- **High confidence about public CLI limits:** The README explicitly shows the CLI as an audit. The README shows an omission of performance/reliability tests and provider results/benchmark implementations. [observed] [public repo](https://github.com/SemiAnalysisAI/clustermax)

- **High confidence:** The listed Reliability criteria make expectations/checklist entries. Do not put them in the verified-test-execution category for every provider. [observed] [Reliability criteria](https://www.clustermax.ai/criteria/reliability)

- **Moderate confidence:** The absence claims make a boundary at the named public corpus. This research cannot check internal proprietary methodology, dashboards, paid material, or unpublished run artifacts. [observed] [methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) [repo](https://github.com/SemiAnalysisAI/clustermax)

- This brief makes no independent audit of provider results and full benchmark scripts. It shows the published methodology's account of the work. It does not make a reproduction of ClusterMAX runs. [observed] [methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## Gaps

- SemiAnalysis’ internal training scripts, run lengths, exact pass thresholds, loss records, and per-provider results make no public appearance. The inspected corpus shows none of them. Send a direct request for these when they make a difference to the decision.

- No public evidence shows numerical checkpoint-resume equivalence during a real training interruption. No public evidence shows interruption-to-goodput accounting for the named Llama run.

- The inspected corpus shows no published multi-day or 54-day stability dataset. A two-hour measurement does not make that guarantee.

- The task makes reference to sibling checkpoint/datagen work. This worktree shows none of its implementation artifacts. This brief keeps a link to the sibling storage brief. This brief makes no re-derivation of its storage claims.

- The public methodology shows no per-provider MFU/convergence data for the named Llama pretraining job. Its MFU references make part of the future PostTrainingX description.
