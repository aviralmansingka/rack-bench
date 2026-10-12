# Public AI-lab training runs: health, accounting, interruptions, and recovery correctness

Research date: 2026-10-11. All claims below use a source URL.

Each claim uses one of three labels. A source shows an **[observed]** claim directly. Arithmetic from reported data makes a **[calculated]** claim. Interpretation or a proposed rack-bench implication makes an **[inference]** claim.

## 1. Executive answer: two hours certify a snapshot, not a 54-day run

### 1.1 Scope of this node

This research checks public AI-lab training records for operational health and scientifically valid recovery. Rack-bench does not use vendor specifications as PASS evidence. Rack-bench runs measured category checks (~2h/category) on an 18-tray GB300-class NVL72 rack. A training microbenchmark can show a specified workload that runs reproducibly. It can show measured throughput, MFU, loss behavior, and checkpoint/resume correctness in the tested software/configuration. It cannot show multi-week failure rate, day/night stability, the tail of recovery times, or correctness across all interruption causes. **[inference]**

The scale and duration of the Llama 3, OPT, and BLOOM records make that separation directly. The records show many weeks and real interruptions, not a short acceptance run.

Sources: [Llama 3 paper §3.3.4](https://arxiv.org/html/2407.21783); [OPT logbook](https://github.com/facebookresearch/metaseq/tree/main/projects/OPT/chronicles); [BLOOM chronicles](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md).

### 1.2 Top findings

1. **Llama makes the useful interruption anchor, but its denominator must keep 419 unexpected events.** The 54-day snapshot shows 466 total interruptions: 47 planned and 419 unexpected. The report shows ~78% of the 419 unexpected interruptions as confirmed or suspected hardware issues. GPU issues make 58.7% of unexpected issues, not 58.7% of all 466 interruptions. Check the table’s GPU subtypes and rounded percentages with care (§2). [observed] [Meta primary report](https://arxiv.org/html/2407.21783).

2. **A failure count does not make a failure rate or rack lifetime.** The Llama run uses up to 16,384 H100s on a production cluster. A rack-scale two-hour test cannot show that population or 54 days of aging/exposure. It can show existing defects, this sample’s throughput, and this sample’s recovery. It cannot show a low future event rate. [inference] [Meta report](https://arxiv.org/html/2407.21783).

3. **MFU makes an accounting convention, not a self-validating scalar.** The numerator uses model FLOPs/token and useful token throughput. The denominator uses accelerator count, precision-specific theoretical peak, and time window. Dense-vs-MoE, recomputation, padded/dropped tokens, warmup, and evaluation/checkpoint pauses can make a material difference to the interpretation. Also check the “peak” label: a precision-appropriate Tensor Core peak, or another definition. [inference] [Meta report](https://arxiv.org/html/2407.21783); [DeepSeek-V3 report](https://arxiv.org/html/2412.19437v1); [MFU metric study](https://arxiv.org/html/2608.03880v1).

4. **Weight loading alone does not make recovery correctness.** BLOOM public evidence shows a concrete optimizer/TP synchronization defect that can make ranks inconsistent. The logbook also shows an RNG state synchronization need. Check model, optimizer, scheduler, scaler, RNG, data position, gradient accumulation, and step counters. A process restart alone does not show correctness. [observed] [BLOOM chronicle](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md).

5. **Two hours can run the mechanism test; they cannot show an MTTR distribution.** Run controlled failure injections: process, GPU, network, and storage. Keep detection-to-useful-step latency, lost useful tokens, rollback point, and exact replay equivalence. A published “automatic recovery” claim does not show zero downtime or full state equivalence. [inference] [Meta report](https://arxiv.org/html/2407.21783); [Gemini SOSP’23](https://zhuangwang93.github.io/docs/Gemini_SOSP23.pdf).

## 2. Llama 3.1 405B: verified interruption denominator and reliability claims

### 2.1 Exact scope and counts **[observed]**

Meta’s paper shows a **54-day snapshot period of Llama 3 405B pre-training**. The run uses a production cluster with up to **16K H100 GPUs**. The paper shows **466 job interruptions total**: **47 planned** (automated firmware upgrades or operator-initiated configuration/dataset updates) and **419 unexpected**.

The paper shows **higher than 90% effective training time**. The paper shows the definition: time spent doing useful training divided by elapsed time. These values make snapshot/run-report data. They do not make a device-level MTTF or a guaranteed utilization SLA ([Meta, “The Llama 3 Herd of Models,” §3.3.4](https://arxiv.org/html/2407.21783)).

### 2.2 What 78% and 58.7% actually mean **[observed]**

- The paper shows approximately **78% of the 419 unexpected interruptions** as confirmed hardware issues or suspected hardware-related issues. The paper puts silent data corruption and unplanned individual-host maintenance as examples. The denominator uses unexpected interruptions, not 466 total interruptions ([Meta §3.3.4](https://arxiv.org/html/2407.21783)).

- The paper then shows GPU issues as the largest category. The intended denominator again uses the 419 unexpected events, not the hardware-only subset, not 466 total interruptions. The paper shows the words: “accounting for **58.7% of all unexpected issues**.”

  The paper’s table puts “% of Interruptions” on its percentage column. The listed subtype percentages do not all show agreement with the stated unexpected-event denominator.

  For faulty GPU, the table puts 148 events; 148 / 466 = 31.8%, but the table shows 30.1%. Also, 148 / 419 = 35.3%. The reported 30.1% does not show agreement with either denominator.

  For HBM3, the table puts 72 events; 72 / 466 = 15.5%, and 72 / 419 = 17.2%. The table’s HBM3 percentage shows agreement with the latter. **Do not use the subtype table percentages as a set with one consistently auditable denominator.** Use the paper’s prose-level 58.7% as the anchor for citations. Use subtype counts in place of copied percentages; the counts make safer evidence. [calculated] ([Meta Table 5 and §3.3.4](https://arxiv.org/html/2407.21783))

- The paper shows these GPU-related subtype counts. The counts show 148 faulty-GPU events, 72 GPU HBM3 memory events, and 19 GPU SRAM memory events. The counts also show 17 GPU system-processor events, 6 silent-data-corruption events, and 6 thermal-interface/sensor events. The paper also shows 35 switch/cable network events and 54 software-bug events.

  The paper shows other host/dependency categories too. The source does not show the full taxonomy details. Do not make blind sums of the counts into mutually exclusive root causes. [observed] ([Meta Table 5](https://arxiv.org/html/2407.21783))

- The paper shows “Only three” events with significant manual intervention. The remaining events use automation. This statement shows intervention burden, not automatic repair correctness. The table does not show a full per-event MTTR distribution. [observed] ([Meta §3.3.4](https://arxiv.org/html/2407.21783))

### 2.3 What Meta actually did for health, diagnosis, and resilience **[observed]**

In synchronous training, one GPU failure can start a whole distributed job restart. Meta shows these measures: production-grade automated maintenance, reduced startup/checkpoint time, and rapid diagnosis tooling. Meta also shows PyTorch NCCL flight-recorder metadata and stack traces. Watchdog/heartbeat timeout starts automatic trace dumps. Meta starts extra tracing online without a job restart. NVLink failures can show stalled GPU load/store operations without clean error codes.

This failure mode makes monitoring and timeout detection essential. A slow, still-functioning straggler can keep thousands of GPUs waiting. Meta puts suspicious process-group communications first. This check shows the stragglers ([Meta §3.3.4](https://arxiv.org/html/2407.21783)).

The report also shows 1–2% diurnal throughput variation. The report shows the cause: mid-day temperature and GPU DVFS. This record makes direct evidence of a risk. A short test at one time of day does not always show a small but real drift. The record does not make evidence for the same magnitude or cause on GB300. [observed] ([Meta §3.3.4](https://arxiv.org/html/2407.21783))

### 2.4 Calculated event-rate illustrations—not lifetime predictions

- The full reported cluster shows 419 unexpected interruptions / 54 days = **7.76 unexpected job interruptions/day**. Also, 54 days × 24 hours / 419 = **3.09 hours per event on average**. This arithmetic uses the entire cluster-job record. It does **not** show a 3.09-hour failure interval for each GPU. It does **not** show independent events or a uniform distribution. [calculated] ([Meta §3.3.4](https://arxiv.org/html/2407.21783))

- 47 planned + 419 unexpected = 466 total. Planned interruptions make 10.1% of that total; unexpected interruptions make 89.9%. Use these percentages for the 54-day snapshot only. [calculated] ([Meta §3.3.4](https://arxiv.org/html/2407.21783))

## 3. Cross-run evidence: failures, loss behavior, and incompatible claims

### 3.1 OPT-175B logbook: operational granularity, imperfect comparability **[observed]**

OPT’s first-party 10%-through update shows exact incidents. Experiment 11.xx shows ECC-related restarts. It also shows repeated gradient-norm/loss explosions and NaNs after restarts. The team uses instability mitigations (clipping/LR/optimizer changes). Experiment 12.xx later shows hardware-related restarts. The 12.xx incidents show missing GPUs, hangs after node additions, ECC/CUDA/NCCL errors, and partial checkpoint upload after hardware error.

The update also shows a dataset formatting problem. The problem makes implausibly low perplexity (JSON escaping/whitespace/corpus formatting). The update also shows a warning. Operators must check loss metrics with data-pipeline sanity checks. These records make dated author reports, not a normalized event-rate dataset.

Separately, Gemini shows an OPT summary: 992 A100 GPUs and ~110 failures over two months. Gemini also shows ~178,000 GPU-hours wasted. Do not use that secondary summary as a direct comparison to Llama’s 419 job interruptions. Use harmonized exposure and event definitions first ([OPT 10%-through update, Nov. 17, 2021](https://github.com/facebookresearch/metaseq/blob/main/projects/OPT/chronicles/10_percent_update.md); [Gemini SOSP’23](https://zhuangwang93.github.io/docs/Gemini_SOSP23.pdf)).

The logbook shows a lasting certification lesson about operations. Failures can run at a frequency that makes manual restart untenable. Operators must check training behavior, check suspect nodes, remove them, and put in replacements. Susan Zhang’s public talk shows recurring 2–3 restarts/day at one point and cluster health checks. But that record makes recollection/talk, not an independently normalized failure-rate dataset ([Susan Zhang, OPT lifecycle talk](https://www.youtube.com/watch?v=R8cHHKp1Fvg)).

### 3.2 BLOOM: checkpoint intervals and recovery correctness **[observed]**

BLOOM chronicles show unusually detailed dated logs. At the 176B run start, the logbook shows 105-second iterations. A checkpoint uses ~40 seconds. Evaluations run every 1,000 iterations. They use about seven iterations (~0.7% of training). A GPU crash makes a 7.3-hour loss, two iterations before a checkpoint.

The team then makes the checkpoint interval 200 iterations, then 100 iterations. This puts a rough three-hour bound on rollback. The record shows a **run-specific** checkpoint trade-off, not a universal ideal frequency ([BLOOM chronicle, Mar 18–22, 2022](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md)).

A checkpoint interval also uses save time. It can also make a correctness boundary. BLOOM shows a BF16 optimizer bug. The bug removes gradient clipping on tensor-parallel ranks >1. This puts layer-norm weights/biases out of sync. The run can show apparent training.

TP-rank merging at completion can show damaged correctness. The team makes a reproducer. The team makes an optimizer/checkpoint-load synchronization fix. The team later puts RNG state in synchronization too. This makes concrete evidence. The quote “resumed and loss keeps decreasing” does not make a sufficient correctness criterion ([BLOOM chronicle, Mar 24–Apr 6](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md)).

The BLOOM logbook also shows an LM-loss spike. The spike makes a sharp rise for a few steps. It runs back near baseline in ~30 iterations. The logbook shows a concurrent gradient-norm spike. The logbook does not automatically put a fatal-divergence label on it. Elsewhere the logbook shows evaluation deadlocks.

It shows a 5% throughput drop from a slow GPU/node. It also shows lost hours from hangs. Therefore run joint triage on loss, gradient norm, throughput, collectives, data-loader state, and evaluation behavior ([BLOOM chronicle](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md)).

### 3.3 DeepSeek-V3: stable loss is an outcome, not a general guarantee **[observed]**

DeepSeek-V3 shows 14.8T pretraining tokens on 2,048 H800 GPUs. The report shows no irrecoverable loss spikes. The report shows no rollback during the full training process. The report shows the cause of its training efficiency: extensive system/model co-design. The co-design uses FP8 mixed precision and high-precision accumulation in selected paths. It also uses dynamic expert-load bias adjustment and no token dropping.

It uses communication/computation overlap. The report shows author-reported results only. The report does not show an interruption-event table. It does not show an independent audit log comparable to Meta’s ([DeepSeek-V3 report §§1, 3, 4](https://arxiv.org/html/2412.19437v1)).

DeepSeek’s FP8-vs-BF16 ablations show relative loss error below 0.25% on two smaller baseline MoE models. This does not make a general full-scale rack reliability bound. The appendix also shows a divergence at ~300B tokens in a ~16B-parameter MoE experiment. An activation-gradient quantization granularity change makes the cause. This makes an important distinction ([DeepSeek-V3 report §3.3 and Appendix B](https://arxiv.org/html/2412.19437v1)). The stable headline run and the ablation evidence use their recipes/configurations as scope.

### 3.4 Reconciling stability claims

Meta shows few loss spikes and no divergence interventions under its dense Llama 3 recipe. The same report shows hundreds of *infrastructure/job* interruptions. DeepSeek shows no irrecoverable loss spikes or rollbacks under a distinct MoE/FP8 recipe. BLOOM shows both recoverable training loss spikes and substantial infrastructure/software interruptions. These statements make a compatible set ([Meta](https://arxiv.org/html/2407.21783); [DeepSeek](https://arxiv.org/html/2412.19437v1); [BLOOM](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md)). Numerical stability, hardware uptime, job recovery, and end-to-end useful progress make separate dimensions. [inference]

## 4. Throughput, MFU, useful-token accounting, and eval cadence

### 4.1 MFU requires declared numerator and denominator **[observed + inference]**

Use this standard form:

`MFU = (useful model FLOPs per token × useful tokens processed per second) / (GPU count × peak FLOP/s per GPU for the chosen precision)`

This formula makes an analytical ratio. `nvidia-smi` utilization, Tensor Core active time, or executed hardware FLOPs — the ratio makes none of these. A dense-transformer approximation commonly starts near 6×parameter-count FLOPs/token for forward+backward. Attention terms put sequence-length-dependent work on top. Architecture, context, objective, and convention make exact accounting dependent. [observed] Sources: [PaLM, Chowdhery et al., §4.1 and Appendix B](https://arxiv.org/html/2204.02311); [Meta Llama report](https://arxiv.org/html/2407.21783); [MFU metric study](https://arxiv.org/html/2608.03880v1).

Meta shows an unusually interpretable example. The example shows BF16 MFU 43% on 8,192 GPUs. It shows 41% on 16,384 GPUs at 8K context, and 38% on 16,384 GPUs at 128K context. The paper shows a cause for the 43→41% drop: smaller batch per data-parallel group. The run keeps global tokens/batch constant. The 128K configuration uses a different context-parallel setup.

So MFU must use configuration labels. Run the measurement across the actual job shape. Do not show MFU as a rack-invariant property ([Meta Table 4](https://arxiv.org/html/2407.21783)).

**Run these accounting checks:** [inference; grounded in PaLM §4.1 and Appendix B](https://arxiv.org/html/2204.02311)

- Put the precision and peak table in the report (e.g., BF16 vs FP8 peak). Also check the peak type: Tensor Core peak or IEEE FP32 scalar peak. [inference]

- Put the model FLOPs/token formula in the report. Check the coverage: attention, embeddings/output head, auxiliary losses/MTP, and any sparsity/routing. For MoE, keep total parameters and activated parameters distinct. DeepSeek V3 shows 671B total parameters and 37B activated/token. So dense 6×total-parameter arithmetic plainly makes the wrong denominator/numerator proxy for routed layers. [observed/inference] ([DeepSeek report](https://arxiv.org/html/2412.19437v1))

- Show the MFU basis: only analytically necessary model FLOPs, or all executed work. Activation recomputation makes the executed operation count larger. The model-FLOPs MFU convention keeps recomputation overhead separate from hardware FLOPs utilization (HFU). Both can make useful measures. But the measures put different questions. [inference] ([PaLM §4.1 and Appendix B](https://arxiv.org/html/2204.02311); [MFU metric discussion](https://arxiv.org/html/2608.03880v1))

- Put a clear definition on “tokens”: input tokens actually consumed. Do not use padded slots, generated/evaluation tokens, or samples×nominal sequence length in its place. Put raw useful tokens/s next to MFU. Show the coverage: data-loader starvation, skipped steps, gradient accumulation, warmup, and eval/checkpoint windows. [inference]

One benchmark setup keeps warmup out of steady-state MFU. It keeps warmup wall time inside end-to-end goodput. That benchmark can show MFU efficiency. It can still make fewer useful tokens per wall-clock hour.

Put both numbers in the report: steady-state throughput/MFU and wall-clock goodput. Wall-clock goodput uses useful training tokens / elapsed benchmark time. Keep setup, warmup, eval, checkpoint, and recovery overhead inside it. [inference]

### 4.2 Evaluations and scientific health monitoring

BLOOM runs a multi-dataset evaluation once every 1,000 iterations. The observed cost runs at ~7 training iterations (~0.7%). Llama 3 checks adaptation after context-length changes with short-context eval recovery and needle-in-a-haystack tests. DeepSeek’s public report shows no irrecoverable spikes/rollbacks. It does not show a universal evaluation cadence ([BLOOM chronicle](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md); [Meta §3.4](https://arxiv.org/html/2407.21783); [DeepSeek](https://arxiv.org/html/2412.19437v1)). These records show one lesson: eval makes both a measurable throughput cost and an essential model-quality signal. [observed]

### 4.3 Loss-spike triage: operationally useful policy **[inference]**

A short rack-bench run cannot show zero future divergence for a customer’s full data/model recipe. It can check the diagnostic loop and immediate numerical pathologies. Keep a record of per-step/short-window loss, gradient norm, and skipped/NaN/Inf updates. Check gradient norm globally, and per-layer where possible. Also keep learning rate, token count, throughput, GPU error counters, and collective timeout/trace evidence. Keep temperatures/power and per-rank agreement too.

A single spike must start synchronized evidence capture. Repeated spikes, non-finite state, persistent loss offset, or a rank mismatch must make a FAIL or start explicit investigation. Do not automatically run a loss-history reset. Do not silently run an update skip. [inference] ([BLOOM incident evidence](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md); [Meta diagnostic methods](https://arxiv.org/html/2407.21783); [DeepSeek numeric-stability ablations](https://arxiv.org/html/2412.19437v1))

For any spike, check before/after checkpoints on the *same fixed validation token set* and recipe. Run a replay of the affected batch sequence. Check loss/gradients/update tensors and optimizer state. Check data corruption/duplicate or cursor changes, precision/scaler state, collective/rank consistency, and hardware logs.

This check shows the difference: a transient outlier, or persistent numerical divergence or a recovery-state mismatch. This text makes a proposed triage protocol. It does not show that a single public lab uses exactly this rubric.

PaLM shows roughly 20 irregular loss spikes. The paper makes the mitigation: resume about 100 steps before a spike, then skip 200–500 batches. The BLOOM logbook also shows transient loss/gradient spikes and instability. These source examples make a case for evidence capture and triage. They do not make a universal pass/fail rule. [inference] ([PaLM §5.1](https://arxiv.org/html/2204.02311))

## 5. Checkpoint and restart correctness: what state must survive

### 5.1 Full-resume state inventory **[inference]**

For ordinary synchronous optimizer training, a valid restart must put this state back, as applicable:

1. Model parameters (including all shards/ranks and master weights).

2. Optimizer state (e.g. Adam first/second moments, step counters, FP32 master weights, gradient-scaler state).

3. Learning-rate scheduler state and global optimizer/update step.

4. RNG states for Python, NumPy, framework CPU, and each GPU/rank; check RNG synchronization where the setup uses topology/parallel ranks.

5. Data sampler/shuffle state, dataset shard/epoch, and exact cursor/consumed-sample/token position; keep worker/prefetch state where it makes order changes.

6. Gradient accumulation/microbatch position and any in-flight gradient state. Or make a checkpoint only at a well-defined optimizer-step boundary, and run a replay from there.

7. Training configuration/code/data identity, parallelism mapping, tokenizer, precision mode, and checkpoint manifest/version.

This inventory makes a correctness requirement. The inference uses optimizer dynamics. The public logs directly make the motivation: optimizer-state, TP-rank, and RNG synchronization problems. This text does not make a blanket claim. The cited labs do not all publicly show every field ([BLOOM chronicle](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md); [PyTorch distributed checkpoint docs](https://pytorch.org/docs/stable/distributed.checkpoint.html)).

### 5.2 A convincing resume-equivalence test **[inference]**

Run a deterministic baseline from state S for K updates. Keep the final model/optimizer/scheduler/RNG/data-cursor state. Separately, start a restart from a checkpoint at step k. Run the same remaining data with the same world-size/parallel layout.

Check step and consumed-token counters, next-batch/sample IDs, LR, and loss and gradient norms. Check model/optimizer tensor checksums or bounded numerical differences, the final checkpoint manifest, and a fixed validation loss.

Hardware failures can make a topology change necessary. The change can put exact bitwise equality out of reach. So put numerical tolerances on record before the test. Check against a clean run under that same changed topology.

Check for silent data repetition or skipping after restart. Do not put a partially written checkpoint in use as complete. A process at “step K” does not show equivalence by itself.

This proposed test uses two anchors. PaLM shows a bitwise-reproducibility claim from checkpoints. BLOOM shows optimizer/TP synchronization and RNG-state defects. The PyTorch distributed-checkpoint documentation shows save/load support. It does not show application-level replay validation ([PaLM §5](https://arxiv.org/html/2204.02311); [BLOOM chronicle](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md); [PyTorch distributed checkpoint docs](https://pytorch.org/docs/stable/distributed.checkpoint.html)). [inference]

### 5.3 Checkpoint interval, save cost, and MTTR are separate quantities

Checkpoint frequency puts a bound on potential lost work. Save time makes the pause/overlap cost. Retrieval/reload/warmup and machine replacement make the recovery time. Gemini’s SOSP paper shows an explicit model of average wasted time.

The model uses checkpoint time, half the checkpoint interval (assuming uniformly distributed failures), and retrieval time. The paper shows >13× faster recovery than baselines in its tested setup. It also shows high-frequency in-memory checkpointing. Those make its evaluated configurations, not a guaranteed NVL72 outcome ([Gemini SOSP’23](https://zhuangwang93.github.io/docs/Gemini_SOSP23.pdf)).

Meta shows >90% effective training time; it puts startup/checkpoint time reduction as a contributor. The cited section does not show an event-level MTTR distribution. The Llama report’s three significant manual-intervention events do not show 416 zero-duration recoveries. Keep median and tail recovery latency separate in the report. Also keep useful progress lost, automatic/manual classifications, and the denominator ([Meta §3.3.4](https://arxiv.org/html/2407.21783)).

## 6. What two hours can measure on rack-bench—and what it misses

### 6.1 Practical measured checks (PASS means observed evidence) **[inference]**

Keep the model recipe, software, precision, GPU topology, data sample, and clock/thermal conditions fixed inside a two-hour training-category slot. Then start this collection:

- **Repeatable training throughput:** keep useful tokens/s, step-time median/p95, rank skew, and wall-clock goodput, including warmup/eval/checkpoint. Run enough steady-state steps to make outliers visible. Check repeated windows.

- **Declared MFU:** make the calculation from measured useful tokens/s × declared model FLOPs/token. Put installed GPU count × precision-appropriate published peak in the denominator. Put the full formula and configuration in the report. Keep MFU and useful tokens/s side by side. Neither one alone makes training-quality certification.

- **Loss/numerical health:** keep baseline and interval loss, gradient norm, NaN/Inf/skipped steps, rank equality, and a fixed validation sample. Use an actual training step with backward/optimizer work, not just GPU burn.

- **Checkpoint mechanism:** run save/restore at a clean optimizer boundary. Check the full state manifest and the next data batch/cursor. Run a process-kill injection. Also run a single-GPU/node/network interruption, but only under safe conditions. Keep detection-to-first-useful-step and lost useful tokens on record.

- **Repeated interruption drill:** check checkpoint interruption during/around save (atomicity). Check a restart from the newest complete checkpoint. Check recovery after stale/corrupt/incomplete checkpoint rejection. A single successful retry shows one path, not a reliability probability.

- **Telemetry correlation:** check XID/ECC/HBM/PCIe/NVLink/network/storage errors, thermal/power/throttle indicators, and training pauses against a step-level timeline. Run a per-GPU performance comparison. This check shows a straggler.

This list makes proposed actionable two-hour checks. Public mechanisms and incidents make the basis ([Meta report](https://arxiv.org/html/2407.21783); [BLOOM chronicles](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md); [Gemini](https://zhuangwang93.github.io/docs/Gemini_SOSP23.pdf)). No claim here shows these exact tests as published universal industry protocol.

### 6.2 Honest misses

Two hours of measurement cannot show:

- a 30–90-day hazard rate, failure-free probability, or aging/thermal-cycle behavior; one run’s event rate cannot make a projection basis without assumptions and a much longer observation window;
- day/night, seasonal, utility-power, facility cooling, sustained storage pressure, network drift, or fleet-wide correlated failure behavior;
- a statistically meaningful MTTR tail or rare multi-node correlated interruption rate;
- production recipe’s convergence and model quality over trillions of tokens, rare data pathologies, delayed numerical instability, or long-horizon checkpoint corruption;
- a match between benchmarked throughput and 54-day useful-token throughput after all eval, checkpoint, maintenance, data, and recovery overhead;
- equivalence to a customer’s exact model, data, precision, training framework, or distributed parallelism, in cases with differences from the rack-bench workload;

Put a measured 2h PASS in these words: “this rack/configuration completed the specified workload and recovery drills with these observed values,” not “will survive a 54-day Llama-class run.” ([Meta](https://arxiv.org/html/2407.21783); [DeepSeek](https://arxiv.org/html/2412.19437v1); [Gemini](https://zhuangwang93.github.io/docs/Gemini_SOSP23.pdf)). [inference] The 54-day commitment still must use operational monitoring, periodic fault drills, checkpoint/restore rehearsal, and an agreed service/recovery objective.

## 7. Source confidence and limits

- **High confidence:** the primary Meta paper shows interruption totals, scope, definitions, tooling, and the MFU table. DeepSeek’s own technical report shows its reported stability/recipe. First-party BLOOM operational chronicles show timestamps, checkpoint policy, and concrete state bugs. Each source keeps a team attribution. But the reports keep self-reported status. The BLOOM logbook makes a dated public operational diary, not a controlled reliability study.

- **High confidence, narrower scope:** Gemini makes a peer-reviewed SOSP’23 systems paper. The paper shows an explicit failure/checkpoint model, test setup, and results. The paper uses AWS A100/V100-era hardware/workloads. Do not use them as measured NVL72 or GB300 performance.

- **Medium confidence:** arithmetic from those records keeps a transparent basis. But it also keeps source taxonomy and denominator limitations. Llama Table 5 shows percentage denominator inconsistencies. So prose claims and raw counts make safer evidence than subtype percentages.

- **Not established:** independent reproduction of Llama/DeepSeek production telemetry, all event-level root-cause records, event-by-event MTTR. Also not established: a public 30–90-day trial of the target rack class.

## 8. Sources

- Kept: [The Llama 3 Herd of Models, Meta (arXiv HTML)](https://arxiv.org/html/2407.21783). Primary source for 54-day snapshot, 466/47/419 denominator, 78%/58.7% prose, effective training time, diagnostic tooling, MFU, and temperature variation.

- Kept: [DeepSeek-V3 Technical Report (arXiv HTML)](https://arxiv.org/html/2412.19437v1). Primary author report for stable-loss claim, architecture/precision context, compute accounting and ablation boundaries.

- Kept: [BLOOM 176B training chronicles](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md). First-party dated logbook with checkpoint cadence, eval costs, spikes, interruptions, synchronization defects and restart changes.

- Kept: [OPT chronicles source tree](https://github.com/facebookresearch/metaseq/tree/main/projects/OPT/chronicles). Primary dated author update, fetched for specific numerical-instability, data-formatting and restart incidents; not a full logbook/event census. Gemini shows a separately labeled secondary summary of failure counts and wasted GPU-hours.

- Kept: [Gemini: Fast Failure Recovery in Distributed Training with In-Memory Checkpoints, SOSP 2023](https://zhuangwang93.github.io/docs/Gemini_SOSP23.pdf). Primary peer-reviewed systems work for checkpoint frequency/recovery mechanisms and experimental qualifications.

- Kept: [Evaluating MFU as a Proxy for GPU Power, arXiv 2608.03880](https://arxiv.org/html/2608.03880v1). Recent technical treatment of MFU’s analytical definition and limits; not the original definition paper.

- Kept: [PyTorch Distributed Checkpoint documentation](https://pytorch.org/docs/stable/distributed.checkpoint.html). Implementation reference for distributed state checkpointing; not evidence of a particular rack’s recovery correctness.

- Dropped: [Tom’s Hardware Llama failure article](https://www.tomshardware.com/tech-industry/artificial-intelligence/faulty-nvidia-h100-gpus-and-hbm3-memory-caused-half-of-the-failures-during-llama-3-training-one-failure-every-three-hours-for-metas-16384-gpu-training-cluster). Secondary summary; this research uses the primary Meta report instead, particularly because its paraphrasing can make denominator mix-ups.

- Dropped: general commercial training/recovery blogs and non-primary MFU explainers. This research removes them where primary reports or the systems paper show the claim.

## Gaps

- Llama Table 5’s printed subtype percentages do not consistently show agreement with raw counts under one denominator. The prose denominator for 78% and 58.7% keeps clarity: 419 unexpected events. This research does not make a reconciliation for every table percentage.

- The section does not show per-event interruption timestamps, MTTR distribution, lost-token totals, or machine-level exposure. This research cannot make a defensible failure rate per GPU-hour from this section.

- This research uses one dated 10%-through update only, as OPT primary evidence. It shows support for the specific dataset-formatting, numerical-instability, and restart examples in §3.1. It does not make a comprehensive extraction of the full OPT chronicles. It does not make a source for a normalized failure rate.

- No cited public run uses a GB300/NVL72 Chennai rack. No cited public run makes a 30–90-day controlled reliability trial. No source puts a number on short-test-to-long-run prediction.

- Resume correctness tolerances use deterministic kernels, software version, topology changes, and precision as inputs. The customer training stack must put a definition on acceptable equivalence for an actual acceptance plan.
