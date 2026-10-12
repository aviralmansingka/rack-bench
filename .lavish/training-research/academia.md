# N06 — What a two-hour training health test establishes

Research date: 2026-10-11. All claims below use a source URL.

Claims show these marks: **[observed]**, **[calculated]**, or **[inference]**.

## 1. Decision answer: useful screening, not a 54-day warranty

A two-hour, fault-free, workload-faithful distributed training run can check present-step performance and variability. It can check rank stragglers and collective/pipeline behavior. It can check short-term numerical/loss behavior. It can also check checkpoint creation/publication and restart correctness. The test must run those checkpoint paths explicitly.

It cannot show rare-fault rates. It cannot show persistent-media durability across real failures. It cannot show long-horizon thermal/aging behavior. It cannot show training convergence over billions of tokens. It cannot show the probability of 54-day completion for this particular rack. [inference]

MegaScale shows operationally useful anomalies at scale. Its production validation runs for weeks. It uses >10,000 GPUs. A rack-local two-hour exposure does not show that scale. [observed] [MegaScale, NSDI’24](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

### 1.1 What “training health” means here

Training health shows separable dimensions. Dimension (a): progress and quality trajectory. Dimension (b): throughput and its stability. Dimension (c): distributed synchronization/stragglers. Dimension (d): resilience and state correctness after interruption. Dimension (e): hardware/software events.

A single scalar “training passed” does not show these distinctions. [inference] MegaScale uses logs, heartbeats, RDMA traffic, CUDA events, distributed traces, and automated diagnostics. Faults can make performance degradation or hangs, not an explicit error. This fault behavior makes those instruments necessary. [observed] [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

## 2. Academic methods and what they actually do

### 2.1 MegaScale: observability, diagnosis, and recovery

MegaScale’s production workflow sends heartbeats with executor/process status, logs and RDMA metrics. It checks for missed heartbeats/anomalous traffic. It puts a stop to the job, runs diagnostics, and removes faulty nodes. It then starts again from a checkpoint.

Its two-stage checkpoint puts GPU state into host memory first. Training runs again from that copy. The system then sends the checkpoint to HDFS asynchronously. On restart, one worker uses the shared partitions. The worker sends them to all ranks.

This mechanism makes staged asynchronous persistence. It does not show durable status for a just-copied host-memory checkpoint. [observed] [MegaScale §4](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

MegaScale’s health analysis also shows CUDA-event timing by rank, heatmaps, and distributed timeline traces. It shows ~0.5% slower machines that make training materially slower. It shows unstable MFU from critical-path skew / late collective launch. Removing stragglers makes MFU better.

Pipeline visualization shows bubbles and dependencies across ranks. These results make a design point. Show per-rank step-time distributions and collective/pipeline wait, not only rack-average tokens/s. [observed] [MegaScale §5](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

MegaScale’s model convergence evidence does not make a two-hour stability claim. Its controlled convergence microbenchmarks use a smaller 13B model. The paper shows a production run of several weeks. It starts again over 100 times. The paper thus shows the value of these mechanisms. Two hours does not show another rack’s long-run fate. [observed] [MegaScale §§6.2–6.3](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

### 2.2 CheckFreq: iteration-granular checkpointing and data position

CheckFreq (FAST ’21) makes a training profile. It uses that profile to make the checkpoint-frequency choice. It makes dynamic frequency adjustments to keep the overhead bounded. It uses a resumable iterator to make data-loader-state checkpoints. It also uses a pipelined two-phase snapshot/persist path.

The snapshot step puts learnable state in a user-space CPU buffer. The persistence step puts the data on durable storage. The resumable iterator makes an important difference. Resuming weights but replaying or skipping data makes a different training trajectory. [observed] [CheckFreq paper](https://www.usenix.org/system/files/fast21-mohan.pdf) · [Microsoft Research summary](https://www.microsoft.com/en-us/research/publication/checkfreq-frequent-fine-grained-dnn-checkpointing/)

Keep “snapshot finished” separate from “checkpoint published durably.” A passing write call or file presence does not make sufficient evidence. Put a completed manifest/commit marker in place. Check all rank shards and checksums. Remove the writer/process at controlled points. Use only a fully published generation for the reload.

This validation makes a proposal from the papers’ staged pipeline. It does not make a claim about rack power-loss behavior in CheckFreq’s paper. [inference] [CheckFreq](https://www.usenix.org/system/files/fast21-mohan.pdf)

### 2.3 Oobleck: replica-based recovery, not async checkpointing

Oobleck makes pipeline templates with redundancy. After a failure, it starts the pipeline(s) again from those templates. It makes copies of missing model state from pipeline replicas. This removes the need for a full checkpoint restart.

The mechanism therefore makes replica/state-reconstruction recovery, not “asynchronous checkpointing.” Its paper shows a comparison with checkpoint-centered systems. Varuna and CheckFreq make two such systems. [observed] [Oobleck](https://arxiv.org/html/2309.08125v2)

### 2.4 Varuna: elastic job morphing plus checkpoint-based recovery

Varuna uses pipeline and data parallelism together. Spot resources make changes over time. Varuna makes dynamic changes to pipeline depth/data replicas in response. It makes periodic checkpoints at mini-batch boundaries.

It makes a checkpoint of each layer independently. It puts the writes in shards across data-parallel replicas. It puts writes on local SSD first. In the background, it sends copies to cloud storage.

It starts again from a checkpoint under a new configuration. It keeps GPU RNG state for recomputation correctness. Heartbeats show per-microbatch forward/backward compute time. The manager can use these data to remove slow fail-stutter workers. This mechanism makes checkpoint-based elasticity with background remote copying. It does not make Oobleck-style state reconstruction from replicas. [observed] [Varuna EuroSys’22 full paper §§4.5–4.6, 6](https://www.microsoft.com/en-us/research/wp-content/uploads/2022/03/varuna-eurosys22.pdf) · [Oobleck comparison](https://arxiv.org/html/2309.08125v2)

### 2.5 Gradient-noise scale and stability are workload properties

Gradient noise scale literature shows estimates of a scale-dependent useful batch size from gradient signal/noise. Use it for optimization and parallelization decisions, not hardware reliability. A two-hour sample of loss/gradient norms can show gross divergence or overflow. It can also show repeated skipped updates or anomalies on the exact recipe.

But stochastic batches, seed, learning-rate phase, precision, and model/data choice make extrapolation unreliable. It cannot make any claim of eventual convergence. It cannot remove the risk of late loss spikes. [observed/inference] [McCandlish et al., “An empirical model of large-batch training”](https://arxiv.org/abs/1812.06162) · [OpenAI explainer](https://openai.com/index/how-ai-training-scales/)

Loss spikes do not necessarily show hardware faults. Optimization dynamics, data outliers, numerical precision, and infrastructure can all make contributions. Triage must use loss plus gradient norm, scaler/overflow and skipped-step counters, sample/data position, per-rank consistency, GPU/NVLink/network telemetry, and logs.

Check deterministic replay where feasible. Nondeterministic kernels and distributed reductions can make bitwise equivalence impossible. A spike on all ranks, repeated for the same batch, shows one pattern. A rank-local divergence with a coincident XID/link error shows a different pattern. [inference] [“Loss Spike in Training Neural Networks” (arXiv:2305.12133), a loss-landscape/feature-condensation study, not infrastructure fault diagnosis](https://arxiv.org/html/2305.12133v2) · [MegaScale observability](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

## 3. MLPerf Training: exact scope and non-scope

For Closed division, MLPerf Training checks wall-clock time. The check uses a complete benchmark run to its defined quality target. The check runs under benchmark-specific rules.

Submitters in Open division can use arbitrary stopping criteria, including fixed time. But the final quality report must use the Closed quality measure. Closed division puts constraints on model/data/training semantics. MLPerf checks convergence against reference convergence points. Multiple runs show score variation. [observed] [MLPerf Training Rules §§1, 4, 9, 12–13](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc)

This does not make an interruption-tolerance certification. General §9.4 puts checkpoints at submitter discretion. No rule makes checkpoint production or retention mandatory.

Exception: v6.1 Qwen3.5-397B-A17B post-training §14 makes a checkpoint requirement. The workload must make a checkpoint after every step in its validation window. MLPerf checks the checkpoints offline. Scoring uses the passing checkpoint’s weight-update timestamp, excluding checkpoint-writing time. This scoring protocol does not make certifications for crash recovery, checkpoint atomicity/durability, data-position/RNG restoration, restart correctness, or interruption tolerance. [observed] [MLPerf Training Rules §§9.4, 14](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc)

The MLPerf utilization appendix shows the MFU definition. Model FLOPs utilization = model-definition tensor FLOPs divided by peak system tensor FLOPs/s × runtime. The formula removes recomputation FLOPs. The appendix explicitly removes official MLPerf-metric status from the MFU.

Rack-bench must make these MFU declarations: numerator, peak denominator (hardware and precision), counted time, and treatment of communication/evaluation/recomputation. A throughput percentage without that denominator does not make an auditable metric. [observed] [MLPerf Training Rules §23](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc)

Current rules make the workload-specific nature of benchmark success clear. Version v6.1 shows distinct small-LLM, MoE pretraining, fine-tuning and post-training workloads. Quality target, evaluation cadence, allowed formats and reference convergence constraints all make differences across workloads. One benchmark pass does not make a certification for arbitrary Llama-class pretraining recipes or 54-day uptime. [observed/inference] [MLPerf Training Rules](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc)

## 4. Two-hour candidate health test: measurements and honest interpretations

### 4.1 Run a real distributed workload with meaningful exposure

Use the intended software stack. Use a representative model/configuration, sequence length, precision, parallelism layout, optimizer, data path, and checkpoint target. Run a warm-up first. Then make steady-state measurement windows across the full rack. Keep the warm-up record separate. The run must use all 18 trays.

Two hours can show measured behavior under this configuration. It cannot show behavior under different tenant recipes or later software changes. [inference] MegaScale’s findings keep a close tie to full-stack, per-rank observability at scale. [observed] [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

### 4.2 Metrics to collect

1. **Progress/performance:** Put tokens/s and samples/s in the record. Show step-time median/p95/p99 and time series. Show warm-up vs steady-state. Show GPU clocks/power/temperature/throttle, memory/ECC, XID, and NVLink/NIC counters. Keep a record of all rank values, not only the average. [inference] [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

2. **MFU:** Show exact FLOPs/token or per-step model FLOPs. Show the peak tensor throughput at the actual precision and on the deployed GPUs. Show the counted interval. Show useful-model-FLOPs MFU separately from hardware FLOPs including recomputation. Do not use an undocumented nominal peak as denominator. [observed/inference] [MLPerf utilization rules](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc#23-utilization)

3. **Stragglers / pipeline:** Show rank-wise forward/backward/optimizer time. Show all-reduce/all-gather/reduce-scatter duration and wait. Show pipeline bubble/idle fraction. Show data-loader stalls, rank spread, and outlier persistence. A rack-average rate does not show the slowest rank. The slowest rank puts a limit on synchronous progress. [inference] [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

4. **Optimization/numerics:** Show loss and validation trend on a fixed evaluation set. Show gradient norm, overflow/underflow, skipped optimizer steps, NaN/Inf, LR, and optimizer state. Show sample/token position and seed/RNG state. Make any loss spike a triage event. Do not make it an automatic hardware failure. Do not make it harmless. [inference] [gradient-noise scale](https://arxiv.org/abs/1812.06162) · [loss-spike landscape study](https://arxiv.org/html/2305.12133v2)

5. **Checkpoint transaction:** Keep a record of snapshot start/end, durable persistence completion, generation/manifest publication, and shard checksums and bytes. Then run a load of the published checkpoint in a fresh process. Run process-kill simulations at snapshot, in-flight persistence, and after publication. Check for rejection of incomplete generations. Run a reload check on the previous committed generation. [inference] [CheckFreq](https://www.usenix.org/system/files/fast21-mohan.pdf) · [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf)

6. **Restart semantic correctness:** Make a controlled interruption after committed step k. Put back the model, optimizer, scheduler, scaler, data cursor/shard position, and RNG states. Check the next-step inputs and state continuity. Check the resumed trajectory against uninterrupted control. Use tolerances appropriate to nondeterministic distributed math. Check loss/gradients and step counters, not only the job restart. [inference] [CheckFreq](https://www.usenix.org/system/files/fast21-mohan.pdf)

7. **Fault response:** Put at least one process failure into the run. Put a node/link fault where safe. Check detection, restart/replacement time, lost work since the durable checkpoint, and the return to useful throughput. One successful injected event makes a narrow proof. It shows only that event/path, and only once. [inference] [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf) · [Oobleck](https://arxiv.org/html/2309.08125v2)

### 4.3 Distinguish checkpoint staging, publication, and persistence

A GPU-to-host-memory snapshot makes the staging step. Async file/object writes make the persistence step. Atomic publication makes a separate protocol step. A valid generation must show a consistent optimizer step across shards and metadata.

A checkpoint with no committed manifest, missing shards, or host-memory volatility does not make a recoverable durable checkpoint. Rack-bench can check its configured storage path and restart semantics. It cannot show survival of facility-wide power loss, storage-site loss, or correlated control-plane failure from a two-hour run. [inference] [MegaScale §4.4](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf) · [CheckFreq](https://www.usenix.org/system/files/fast21-mohan.pdf)

## 5. Statistically honest limits of two hours

Use a fault-free observation of T hours. Use a homogeneous Poisson failure process with independent events, constant rate λ, and complete detection. Zero observed failures makes a one-sided 95% upper rate bound of −ln(0.05)/T. At T=2 h, that makes 1.498 failures/hour for the *tested unit and event definition*.

Make the equivalent calculation for the next 54 days. The 95% upper bound on the probability of at least one such event: 1−exp(−1.498×1296). That bound effectively shows 100%.

This does not make a useful assurance of long-run survival. Under the Poisson model, P(0 events)=exp(−λT). Put this probability at 0.05. Then λ=−ln(0.05)/T. [calculated] [NIST Poisson reference](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366j.htm)

The classic “rule of three” approximation makes 3/T = 1.5 events/hour. It shows the same result. [calculated] [Hanley & Lippman-Hand, “If Nothing Goes Wrong, Is Everything All Right?”](https://pubmed.ncbi.nlm.nih.gov/6827763/)

Put every GPU/tray in the model as an independent identical component with a constant rate. Pooling exposure across components can make a tighter *component-event rate* bound. But pooling makes no estimate of rack-level common-cause events, correlated failures, changing workload/temperature, repair behavior, or job failure probability. Use a validated model for such estimates. Do not use fleet failure rates to make a prediction for this rack’s 54-day completion probability. [inference] [Meta cluster reliability study](https://arxiv.org/html/2410.21680v1)

Zero-failure exposure makes information available only with stated conditions. The report must show the monitored event definition, exposure denominator, independence/stationarity assumptions, and censoring. A two-hour smoke burn-in does not show a failure rate. It shows no detected event during those particular observed hours. [inference] [NIST Poisson reference](https://www.itl.nist.gov/div898/handbook/eda/section3/eda366j.htm)

## 6. Evidence distinctions, examples, and conflicts

- **Checkpoint approach does not make one category:** CheckFreq runs a pipeline of snapshot and durable persistence. It keeps the iterator position. MegaScale puts GPU state in host memory, then sends it to HDFS asynchronously. Oobleck puts missing state back via pipeline replicas. Varuna uses elastic morphing with periodic layer-wise checkpointing to local SSD and background cloud copy. The sources show different mechanisms and failure assumptions. [observed] Sources: [CheckFreq](https://www.usenix.org/system/files/fast21-mohan.pdf), [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf), [Oobleck](https://arxiv.org/html/2309.08125v2), [Varuna full paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2022/03/varuna-eurosys22.pdf)

- **“Loss decreasing” makes weak evidence:** Healthy execution can show short monotonic loss. But short monotonic loss does not make proof of convergence. It does not show the absence of a later numerical instability. It does not show data correctness. Gradient noise and stochasticity make small-window comparisons non-deterministic. [inference] [McCandlish et al.](https://arxiv.org/abs/1812.06162)

- **MFU can show misleading values:** Formula/peak precision, model FLOP convention, time window, and recompute accounting make different results. MLPerf itself shows the metric as non-official. Make comparisons with a fixed recipe and a published denominator. Do not use an unqualified pass threshold. [observed/inference] [MLPerf](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc#23-utilization)

- **Keep failure rates separate:** Meta’s two-cluster trace study shows job failure exposure variation by job scale and failure causes. Its fleet-scale observations make useful evidence. They show long-run exposure to diverse events. But they do not make a rate for this Chennai rack. [observed/inference] [Meta study](https://arxiv.org/html/2410.21680v1)

## 7. Independent node conclusion

Put this statement in a two-hour training health result: “This exact 18-tray rack, software image, training recipe and checkpoint path sustained the reported measured throughput and loss behavior during the observed interval; listed restart/fault injections passed or failed.” Do not show these claims in the result: “safe for 54 days,” “converges,” or “MLPerf-certified for interruption recovery.” [inference] [MLPerf Training Rules](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc) · [Meta reliability study](https://arxiv.org/html/2410.21680v1)

Candidate PASS evidence makes several requirements. Check complete rack participation. Check stable per-rank step-time and communication/pipeline metrics against declared thresholds. Check for no uncorrected hardware errors/throttling. Check numerics within declared tolerances. Check durable checkpoint publication.

A controlled restart must make coherent step/data/RNG/optimizer state. Injected recovery must start useful training again. Make the thresholds measured thresholds in the rack-bench profile. Do not use vendor claims. [inference]

Layered evidence makes the strongest bridge to a 30–90-day commitment. Use these layers: two-hour measured acceptance + explicit restart test + continued production telemetry, checkpoint-retention/restore drills, alerting and operational SLA

These layers make uncertainty smaller. But they still cannot make a guarantee against rare or correlated events. [inference] [Meta reliability study](https://arxiv.org/html/2410.21680v1)

## 8. Sources and confidence

- **High confidence, primary:** MegaScale NSDI’24 full paper; MLPerf current training rules; CheckFreq FAST’21 full paper; Oobleck paper. These directly show mechanisms and benchmark scope.

- **High confidence, primary:** Varuna EuroSys’22 full paper, inspected. It shows continuous layer-wise checkpointing, local SSD plus background cloud copy, RNG state, and fail-stutter heartbeat screening.

- **Moderate:** The gradient-noise-scale primary study shows support for the limited interpretation of the statistic. The application to arbitrary Llama-class recipes keeps a workload-dependent character.

- **Moderate:** The Meta failure-trace paper shows primary fleet evidence. Its datasets and scale make material differences from one rack. It cannot make a rack-specific forecast.

- **Low as a predictor:** two-hour zero-failure observation for a 54-day horizon. The Poisson upper bound keeps mathematical validity only under stated assumptions. It shows how little the interval can show.

## Gaps

- The briefs show no exact tenant model, token budget, optimizer, data pipeline, checkpoint destination, or acceptance thresholds. The tenant must make these choices for workload-faithful tests.

- Two hours cannot check all recovery paths. Multiple fault injections and repeated restore drills make better mechanism coverage, not rare-event probability estimation.

- No public study shows a defensible conversion. The target conversion: this particular 18-tray GB300-class, Chennai rack’s two-hour exposure to a 54-day run-success probability.
