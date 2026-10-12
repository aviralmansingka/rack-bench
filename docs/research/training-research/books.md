# N07 — Books and canonical guides for rack training validation

Research date: 2026-10-11. All claims below use a source URL.

This report uses three claim marks: [observed] (explicitly present in source), [calculated] (arithmetic), [inference] (application to rack certification). This research node runs independently. Scope: a GB300-class NVL72-class rack (18 trays) in Chennai. Category checks use measured data, about two hours per category, plus smoke burn-in. PASS shows a measured result, not a vendor claim.

The tenant must check one risk before a 30–90 day commitment. Can a 54-day Llama-3-class training job run for its full term?

## 1. Executive answer

[Inference] Books make useful systems framing. Current operational guides and reliability papers show stronger evidence for distributed pretraining failure engineering. NVIDIA shows restart, checkpointing, and straggler features ([Megatron Bridge resiliency](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)). PyTorch shows distributed checkpoint and torchrun restart semantics ([DCP](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html), [torchrun tutorial](https://docs.pytorch.org/tutorials/beginner/ddp_series_fault_tolerance.html)). Recent SDC papers show failure modes ([AEGIS](https://www.usenix.org/conference/osdi26/presentation/lei), [controlled SDC study](https://arxiv.org/html/2604.00726v1)).

[Inference] Among books, this report puts DMLS and *Reliable Machine Learning* in one equal-priority tier. DMLS makes a broad foundation ([author TOC](https://github.com/chiphuyen/dmls-book)). *Reliable Machine Learning* shows reliability and monitoring coverage ([O’Reilly TOC](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218)). This report keeps *AI Engineering* at lower priority for pretraining. The official TOC shows finetuning, dataset engineering, and inference ([O’Reilly catalog](https://www.oreilly.com/library/view/ai-engineering/9781098166298)).

[Inference] Two hours can check present-state throughput and MFU for a specified workload. Two hours can check rank-to-rank variation and observed data stalls. Two hours can check checkpoint write/read/resume correctness and latency. Two hours can check short-run loss behavior and immediate flaky-node indicators under the exact test load. Two hours cannot show 54-day uptime or rare intermittent fault rates. Two hours cannot show long-term thermal/aging behavior, dataset correctness at full scale, or final model convergence.

[Inference] Smoke burn-in makes the exercised exposure larger. It does not make an hours-long sample a 54-day reliability guarantee ([AEGIS deployment scale](https://www.usenix.org/conference/osdi26/presentation/lei); [SDC study](https://arxiv.org/html/2604.00726v1)).

## 2. Ranked canon

### 2.1 Rank 1 — NVIDIA Megatron Bridge: resiliency, checkpointing, performance guide

[Observed] NVIDIA’s current Bridge resiliency guide shows fault tolerance (hang detection/restart). It shows NVRx straggler detection, preemption, async checkpoint saves, and local checkpointing. It shows experimental rerun attribution for NaN/spiky loss and in-process restart. The guide makes an explicit warning: one feature does not make coverage for all failure modes.

[Observed] A recipe does not always use each feature by default. Users must use several features together. Straggler detection shows slow-performing nodes. It does not make training stop by default. [NVIDIA Megatron Bridge Resiliency](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[Observed] The page shows operational caveats. Fault tolerance must use Slurm and `ft_launcher` with an accessible checkpoint directory. Fault tolerance cannot run together with Nsight Systems profiling. Async save must use `torch_dist`. The rerun state machine keeps an alpha/experimental status. Do not use in-process restart for hardware-level switch failures or network partitions. [same guide](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

[Inference] Use this guide as the best single practical entry point. Use it for recovery/checkpoint correctness, flaky-node screening, and loss-spike investigation on NVIDIA distributed training. Use its linked checkpointing and performance guides alongside it. A rack certificate must not show an API feature as enabled merely because the software package makes it available.

Mapping: MFU/throughput — performance guide; the specific recipe/config makes the difference.
Recovery/checkpoint correctness — resiliency plus checkpointing.
Loss spikes — rerun state machine, but experimental.
Flaky-node screening — straggler detector.
Data stalls — partial; step timing/profiling must run.
Tenant acceptance — high value as a checklist, not certification evidence.

### 2.2 Rank 2 — PyTorch distributed checkpointing and torchrun docs

[Observed] PyTorch Distributed Checkpoint (DCP) documentation shows multi-rank parallel save/load. It shows load-time resharding across cluster topologies. DCP makes multiple files and runs in place. It does not currently make backwards-compatibility guarantees for saved state dictionaries. The current stable page shows PyTorch 2.14.0 and last update July 8, 2026. [PyTorch DCP](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html)

[Observed] The PyTorch fault-tolerant DDP tutorial shows torchrun restart semantics. The tutorial shows a torchrun restart of all processes from the last saved snapshot. A snapshot must keep continuity-relevant state, not only model weights. A failure removes progress since the last checkpoint. The tutorial shows last verification November 5, 2024. Keep the examples as conceptual; check them against installed versions. [PyTorch fault-tolerant training tutorial](https://docs.pytorch.org/tutorials/beginner/ddp_series_fault_tolerance.html)

[Inference] Use these sources for a real restore drill. Put model, optimizer, step/consumed-data position, and relevant RNG/sampler state into the checkpoint. Remove the job processes; then start the job again. Check the restart at the expected step with equivalent training state. Check checkpoint completeness and integrity. Check the save time, the load time, and the lost-work window.

[Inference] DCP makes the mechanics available. But a two-hour test cannot show a production tenant’s custom trainer’s exact state contract. The test must run that trainer, or a faithful harness, for that result.

Mapping: MFU/throughput — low.
Recovery/checkpoint correctness — very high.
Loss spikes — none.
Flaky-node screening — none directly.
Data stalls — checkpoint I/O stalls and loader throughput, only with instrumentation.
Tenant acceptance — very high for an explicit restart test and measured RPO/RTO.

### 2.3 Rank 3 — current reliability papers, not books

[Observed] The OSDI ’26 AEGIS paper shows deployment over 35 million GPU-hours. It shows 18 real-world SDC incidents and 13 faulty GPUs with 0.86% performance overhead. It shows an online sensor/verifier approach to SDC. The paper shows large-scale production evidence, not a rack-sized test recipe. [USENIX OSDI 2026 paper](https://www.usenix.org/conference/osdi26/presentation/lei)

[Observed] The paper *Exploring Silent Data Corruption as a Reliability Challenge in LLM Training* shows injected GPU matrix-multiply faults. These faults can make NaNs, transient loss/gradient/attention-logit spikes, and persistent parameter divergence. The paper also shows that normal dynamics can make loss spikes. Do not use loss alone for diagnosis. [arXiv paper](https://arxiv.org/html/2604.00726v1)

[Inference] For silent failure modes and detection evidence, papers make stronger sources than books. They do not remove the need for executable vendor/framework docs in a rack acceptance workflow. Do not make this claim: the rack’s two-hour loss trace removes SDC risk. Rare corruption does not always show detectable symptoms. A normal loss curve does not make a correctness proof.

Mapping: MFU/throughput — paper-dependent secondary evidence.
Recovery/checkpoint correctness — not the primary focus.
Loss spikes — very high.
Flaky-node screening — very high at scale.
Data stalls — low.
Tenant acceptance — strong rationale for monitoring and honest limits; weak as a simple short test.

### 2.4 Rank 4 (tie) — Chip Huyen, *Designing Machine Learning Systems* (O’Reilly, 2022)

[Observed] The author’s book resource repository shows DMLS as an O’Reilly 2022 work. It shows the table of contents and chapter materials. Chapter 6 shows “Model Development and Offline Evaluation”. Chapter 6 shows “Distributed Training” and “Debugging ML Models”. Chapter 8 shows “Data Distribution Shifts and Monitoring,”. Chapter 10 shows “Infrastructure and Tooling for MLOps”.

Chapter 10 shows storage/compute, resource management, and ML platform sub-topics. [Author’s book repository](https://github.com/chiphuyen/dmls-book); [O’Reilly official catalog and contents](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956)


[Inference] Use DMLS to make an acceptance test into whole-system requirements, instrumentation, data/compute dependencies, and monitoring. Do not use its “Distributed Training” section as a substitute for current Megatron/NeMo failure engineering. Keep current sources for checkpoint semantics, GPU screening, and long-horizon reliability evidence.

Mapping: MFU/throughput — useful framing, not a current benchmark protocol.
Recovery/checkpoint correctness — weak.
Loss spikes — debugging concepts, not robust SDC methods.
Flaky-node screening — weak.
Data stalls — useful system-level framing.
Tenant acceptance — strong requirements/observability framing.

### 2.5 Rank 4 (tie) — Cathy Chen et al., *Reliable Machine Learning* (O’Reilly, 2022)

[Observed] O’Reilly’s official catalog shows the book, its authors, and its focus. The focus: running ML reliably, production troubleshooting, monitoring, and organizational practice. The contents list: “Evaluating Model Validity and Quality,” “Fairness, Privacy, and Ethical ML Systems,” “Monitoring and Observability for Models,” “Integrating ML into Your Organization,” and “Case Studies: MLOps in Practice.” Chapter pages show Chapter 4 “Feature and Training Data” and Chapter 9 “Monitoring and Observability for Models”. Chapter 9 also shows “What Is Production Monitoring and Why Do It?”. [O’Reilly title page](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218) [Official Chapter 4](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch04.html) [Official Chapter 9](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch09.html)

[Observed] The publisher’s full catalog page sends access denied during research. Search indexing of O’Reilly’s official domain shows the contents and chapter headings. Claims use visible headings only; claims do not use inaccessible full text. [Official catalog URL](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218)

[Observed] The catalog supplement shows a Google Research abstract for the book's data-management chapter. The abstract shows SLOs, SLIs, monitoring, and data handling. The author Q&A shows one fact: the book uses no code examples.
Sources: [Google Research abstract](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production),
[author Q&A](https://datatalks.club/books/20221121-reliable-machine-learning.html).

[Inference] These records show general reliability context; they do not show operational distributed-training validation. Keep the book beside DMLS. Do not put it above current recovery guides. The [source note](oreilly/reliable-ml.md) keeps metadata conflicts and full-text limits.

[Inference] Keep it tied with DMLS overall. It shows stronger relevance for monitoring and ML reliability framing. Keep both books below operational distributed-training docs/papers. The verified contents do not show Megatron-scale checkpoint restart, GPU stragglers, MFU, or pretraining SDC defenses.

Mapping: MFU/throughput — not established by the visible TOC.
Recovery/checkpoint correctness — not established.
Loss spikes — not established.
Flaky-node screening — not established.
Data stalls — Chapter 4 shows conceptual relevance, not device-level stalls.
Tenant acceptance — useful monitoring/validity framing; no rack test procedure.

### 2.6 Rank 5 — *Machine Learning Platform Engineering* (Manning, 2026)

[Observed] Manning shows these authors: Benjamin Tan Wei Hao, Varun Mallya, and Shanoop Padmanabhan.
The catalog shows February 2026 and 504 pages.
Public samples show Chapters 8–9 training and validation, plus Chapter 11 monitoring.
Chapter 9 shows PersistentVolumes, TensorBoard, MLflow, and lineage.
Sources: [publisher](https://www.manning.com/books/machine-learning-platform-engineering),
[catalog](https://learning.oreilly.com/library/view/-/9781633437333/?orm_source=mcp),
[Chapter 8](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-8),
[Chapter 9](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9),
[Chapter 11](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-11).

[Inference] Use these selected chapters before older cloud-specific pipeline material.
They show direct platform context for training metrics, data management, and artifact records.
They do not show MFU accounting, complete resume state, or GPU screening methods.
This reading change does not put the full book *MLOps Engineering at Scale* out of use.
Check the [source note](oreilly/ml-platform.md) for samples, pagination limits, and proposed checks.

Mapping: metrics and lineage — verified topics.
Recovery and screening — unverified.
Tenant acceptance — platform context only.

### 2.7 Rank 6 — Carl Osipov, *MLOps Engineering at Scale* (Manning)

[Observed] Manning’s official catalog shows an AWS/serverless-oriented PyTorch pipeline and dataset ETL/SQL. It shows deployment of training pipelines as service endpoints. It shows pipeline lifecycle monitoring/management and performance improvement measurement. It also shows PyTorch Lightning, Optuna, and MLflow. The catalog shows less infrastructure management through cloud vendors’ prebuilt services, not validation of physical GPU racks. [Manning official title page](https://www.manning.com/books/mlops-engineering-at-scale)

[Observed] The public Manning page shows these topics. The retrieved catalog does not show a complete chapter-by-chapter contents list. Do not make inferences about chapter numbers or recovery coverage. [Manning official title page](https://www.manning.com/books/mlops-engineering-at-scale)

[Inference] Use it for pipeline operations and lifecycle monitoring, not 54-day distributed pretraining resilience. For pipeline operations, it makes a better match than *AI Engineering*. Its serverless/cloud abstraction does not show evidence about NVL72 fabrics, checkpoint reliability, or flaky-node detection.

Mapping: MFU/throughput — general performance measurement, no MFU.
Recovery/checkpoint correctness — not established.
Loss spikes — not established.
Flaky-node screening — not established.
Data stalls — ETL/pipeline concepts, not device-level stalls.
Tenant acceptance — lifecycle monitoring at a general process level.

### 2.8 Rank 7 — Chip Huyen, *AI Engineering* (O’Reilly, 2025)

[Observed] Two sources show the chapter list: [O’Reilly official catalog](https://www.oreilly.com/library/view/ai-engineering/9781098166298); [author companion repository](https://github.com/chiphuyen/aie-book). The chapters: 7 Finetuning, 8 Dataset Engineering, 9 Inference Optimization, and 10 AI Engineering Architecture and User Feedback.

[Inference] Use Chapter 8 for dataset construction and provenance reasoning. Chapter 9 shows inference optimization, not pretraining infrastructure. Chapters 7–10 do not show long-run pretraining failure handling. Do not use this as the main rack-training validation book. The inference-focused content does not show fault tolerance for a 54-day pretraining run.

Mapping: MFU/throughput — low for pretraining.
Recovery/checkpoint correctness — very low.
Loss spikes — low.
Flaky-node screening — none.
Data stalls — dataset engineering concepts, not loader diagnostics.
Tenant acceptance — low, indirect only.

### 2.9 Optional catalog candidates

[Inference] These candidates show selected topics, not operational rack-validation authority.
The [catalog supplement](oreilly.md) shows ten source entries and their access limits.

| Candidate | Verified public scope | Reading decision |
| --- | --- | --- |
| [Machine Learning System Design](https://livebook.manning.com/book/machine-learning-system-design/chapter-10) | Pipeline testing; Chapter 14 monitoring and reliability. | Optional pipeline-testing and reporting context. |
| [Designing Deep Learning Systems](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4) | Training service, parallelism, and hyperparameter optimization. | Optional training-service context. |
| [Parallelism Deep Dive](https://learning.oreilly.com/videos/-/9781806110896/?orm_source=mcp) | Catalog shows parallelism and Chapter 14 checkpoint strategies. | Optional introduction; no inspected videos or recovery results. |
| [DMLS in the Cloud](https://www.oreilly.com/videos/designing-machine-learning/0636920953234) | Catalog shows training data, experiment tracking, automation, and observability. | Lower priority; no verified year, runtime, or playback. |
| [Deep Learning for Vision Systems](https://www.manning.com/books/deep-learning-for-vision-systems) | Vision systems; contents show project structure and hyperparameter tuning. | Low priority for distributed pretraining validation. |

The [System Design sample](https://livebook.manning.com/book/machine-learning-system-design/chapter-14)
puts software health, data quality, and model quality in separate sections.
This separation does not show checkpoint-resume correctness.
The [Deep Learning Systems publisher](https://www.manning.com/books/designing-deep-learning-systems)
shows Chi Wang and Donald Szeto; the supplied catalog shows Kit Pang Szeto.
Keep this naming difference explicit. Do not make an alias inference.

### 2.10 Alternate formats

[Observed] The author shows the 2025 DMLS audiobook announcement under her 2022 book.
The [audio catalog](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp) shows 774 minutes.
The [System Design Video Edition](https://learning.oreilly.com/videos/-/9781633438750VE/?orm_source=mcp)
shows a narrator reading the book with its figures and text.
Sources: [author book page](https://huyenchip.com/books), [audio note](oreilly/dmls-audio.md),
and [video note](oreilly/system-design-video.md).

[Inference] Keep these formats as reading options, not independent technical evidence.
No reviewed source shows a new DMLS technical edition or exact audio passage equivalence.
The supplied video URL does not show *Machine Learning Platform Engineering Video Edition*.

## 3. Explicit six-topic comparison

[Inference] Book ratings below show likely usefulness for rack acceptance, not promises the books make. Each topic claim keeps within the linked official TOC/catalog evidence.

| Source | MFU / throughput accounting | Recovery / checkpoint correctness | Loss spikes | Flaky-node screening | Data stalls | Tenant acceptance |
| --- | --- | --- | --- | --- | --- | --- |
| [Megatron Bridge docs](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html) | Performance guide and workload-specific measurement [observed]; use for the rack recipe [inference] | Strong, specific features and constraints [observed] | Rerun attribution present but experimental [observed] | NVRx straggler detection [observed] | Profiling needed; not a universal stall detector [inference] | Strong checklists; check the exact config [inference] |
| [PyTorch DCP + torchrun](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html) | Not a performance canon [observed] | Strong APIs and restart model; state coverage: workload-specific [observed/inference] | No diagnosis [observed] | No dedicated fleet test [observed] | Checkpoint I/O measurable, input pipeline not covered [inference] | Excellent basis for restore drill [inference] |
| [AEGIS / SDC papers](https://www.usenix.org/conference/osdi26/presentation/lei) | Production overhead quantified, not rack MFU baseline [observed] | Not a general checkpoint guide [inference] | Strong failure mechanisms; loss alone ambiguous [observed] | Faulty GPU detection at scale [observed] | Not central [inference] | Use for explicit caveats and telemetry, not pass thresholds [inference] |
| [DMLS](https://github.com/chiphuyen/dmls-book) | Conceptual [inference] | Checkpoint/restart depth not established by verified contents [inference] | ML debugging frame [inference] | Not a rack screening recipe [inference] | System and data pipeline framing [inference] | Strong systems framing [inference] |
| [Reliable Machine Learning](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218) | No MFU topic established by visible contents [observed] | Restart/checkpoint correctness not established [observed] | No training loss-spike guidance established [observed] | No GPU-node screening established [observed] | Data pipeline framing; not device stall measurement [observed/inference] | Monitoring/validity chapters useful for acceptance framing, no rack procedure [inference] |
| [Machine Learning Platform Engineering](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9) | Training metrics; no verified MFU method [observed] | Complete resume state unverified [observed] | Specialized triage unverified [observed] | GPU screening unverified [observed] | Dataset management; no verified loader-stall procedure [observed] | Metrics/artifacts and lineage context [inference] |
| [Machine Learning System Design](https://livebook.manning.com/book/machine-learning-system-design/chapter-10) | Measurement/reporting; MFU unverified [observed] | Pipeline testing, not verified resume equivalence [observed] | Specialized triage unverified [observed] | GPU screening unverified [observed] | Data-pipeline health; device diagnosis unverified [observed] | Requirements/testing context [inference] |
| [MLOps Engineering at Scale](https://www.manning.com/books/mlops-engineering-at-scale) | Performance measurement mentioned, no MFU [observed] | Recovery coverage not visible in catalog [observed] | Not established [observed] | Not established [observed] | ETL and pipeline lifecycle; not GPU data-loader stalls [observed/inference] | Pipeline monitoring relevant, cloud/serverless orientation [inference] |
| [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298) | Little pretraining focus [inference] | Not established by TOC [observed/inference] | Not established by TOC [observed/inference] | None established [inference] | Dataset engineering, not stall measurement [observed/inference] | Application engineering context, not rack certification [inference] |

[Inference] Do not make an MFU threshold a universal PASS. Megatron’s reported performance shows configuration-specific results ([NVIDIA Megatron-LM performance summary](https://github.com/NVIDIA/Megatron-LM)). Put model, precision, sequence length, global batch, parallelism, and optimizer in the report. Also put software versions, warm-up exclusion, measurement interval, and formula in the report. Workloads make throughput and MFU conditional. A measured baseline makes sense only against a tenant-approved reference configuration or a stated expected envelope.

## 4. What two hours can and cannot establish

### 4.1 Useful measured evidence in a two-hour category window

[Inference] Use a representative multi-node training harness. Use workload-specific profiling and the stated framework instrumentation ([PyTorch profiler recipe](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html); [Megatron Bridge resiliency](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)). Keep collection at per-step and per-rank granularity.

Check steady-state tokens/s and step-time distribution after warm-up. Check MFU with a declared FLOP convention. Check per-rank throughput and straggler spread. Check GPU clocks, power, temperature, and error telemetry. Check NCCL collective behavior under that workload. Check dataloader wait time, CPU utilization, and storage-read stalls.

Check checkpoint write and restore wall time. Check a forced process/job restart from a validated checkpoint, without silent duplicate or skipped steps. Show expected rollback and replay separately. Keep a record of any test interruptions and all measured intervals.

[Observed] NVIDIA makes DCGM diagnostics for GPU deployment/readiness, active hardware/integration/stress tests, and health telemetry. The diagnostics run in an invasive way. They can use GPU, memory, PCIe, NVLink, CPU, power, and cooling resources. Check with the scheduler. Keep the tested resources isolated. [NVIDIA DCGM diagnostics overview](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/dcgm-diagnostics.html)

[Inference] Existing rack smoke burn-in plus a reproducible training-loop test makes complementary evidence. Stress can show immediate faults. A training workload shows application-path performance. Neither makes a statistical demonstration of low multi-week failure probability.

### 4.2 Remains unknown after two hours

[Inference] The two-hour test cannot show these unknowns. Rare-failure probability and clustering over 54 days. Intermittent SDC below available detection. Failures from long-term thermal/power/environment drift. Complete checkpoint recovery under every failure mode.

[Inference] The two-hour test also cannot show these items. Production data quality/coverage and full-run convergence. Multi-day storage/network contention. Scheduler/preemption and human-response behavior. Interactions with tenant-specific framework, data loader, model, optimizer, and checkpoint format.

[Calculated] The calculation: 54 days makes 1,296 hours, 648 times a two-hour observation. [Inference] This exposure ratio does not make a reliability estimate. Large-scale fleet evidence in [AEGIS](https://www.usenix.org/conference/osdi26/presentation/lei) shows the distinction.

[Inference] Start from a simplified stationary Poisson failure process. This process makes an assumption; no source shows it for hardware faults. Zero events in a two-hour sample make a very weak upper bound on rare-event rate. It cannot show zero failures in the future run. Do not make numerical reliability claims without an explicit statistical model, confidence level, and representative exposure.

[Inference] Make the acceptance wording “measured healthy under named workload for stated interval,” plus restore-test results and untested risks. Do not use the wording “will survive 54 days.”

## 5. Practical reading and rack validation sequence

1. [Inference] Use the Megatron Bridge resiliency overview first. Check which capabilities the exact training recipe uses. Check Slurm, format, and experimental restrictions. [Guide](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

2. [Inference] Use PyTorch DCP and torchrun semantics next. Then make the tenant’s restart contract. The contract: state saved, maximum acceptable lost work (RPO), restore time (RTO), data sampler position, and version compatibility. [DCP](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html) [torchrun tutorial](https://docs.pytorch.org/tutorials/beginner/ddp_series_fault_tolerance.html)

3. [Inference] Use *Reliable Machine Learning* Chapters 4 and 9 for data and monitoring context. Public evidence shows indexed headings, a chapter abstract, and author Q&A, not inspected full chapters. [Chapter 4](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch04.html),
   [Chapter 9](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch09.html),
   [Google Research abstract](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production),
   [source note](oreilly/reliable-ml.md).

4. [Inference] Use DMLS Ch. 6 “Distributed Training” and “Debugging ML Models,” then use Ch. 8 monitoring/data-shift and Ch. 10 infrastructure/resource management. [Author TOC repository](https://github.com/chiphuyen/dmls-book) [O’Reilly catalog](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956)

5. [Inference] Use *Machine Learning Platform Engineering* Chapters 8, 9, and 11 for platform metrics and artifacts. Keep *MLOps Engineering at Scale* for its cloud-specific pipeline context. Neither source shows distributed pretraining recovery correctness. [New Chapter 9](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9),
   [older Manning catalog](https://www.manning.com/books/mlops-engineering-at-scale), [catalog supplement](oreilly.md).

6. [Inference] Use AEGIS (OSDI 2026) and the SDC pretraining study for failure-model calibration. Make loss anomaly monitoring one signal among telemetry, recomputation/verification, and health checks. [AEGIS](https://www.usenix.org/conference/osdi26/presentation/lei) [SDC study](https://arxiv.org/html/2604.00726v1)

7. [Inference] Run the specific tenant’s or agreed representative Llama-3-class configuration across all trays. Put rank-level steps/s, tokens/s, step latency, GPU telemetry, loader wait, collective timing, and loss/grad norm in the log. Then run checkpoint save, terminate/restart, and a restored step/state comparison. Show observed numbers and deviations; make no extrapolated uptime promise. [Megatron Bridge](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html) [PyTorch DCP](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html)

8. [Inference] Keep acceptance thresholds tenant-defined and versioned. Put exact artifact/config hashes, software versions, measured interval, excluded warm-up, and repetitions in the record. Put checkpoint integrity evidence, restart outcome, and exceptions in it too. [Workload-specific performance basis](https://github.com/NVIDIA/Megatron-LM) [Checkpoint basis](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html)

## 6. Reject / low-priority list

Source basis: [AI Engineering contents](https://www.oreilly.com/library/view/ai-engineering/9781098166298),
[MLOps Engineering at Scale](https://www.manning.com/books/mlops-engineering-at-scale),
[SDC study](https://arxiv.org/html/2604.00726v1), and
[AEGIS fleet evidence](https://www.usenix.org/conference/osdi26/presentation/lei).
The recommendations below use these source limits.

- [Inference] *AI Engineering* as primary training-reliability reading. Its TOC shows application adaptation, finetuning, data engineering, and inference optimization. It makes no distributed pretraining reliability handbook claim. Keep it only for dataset engineering, if relevant.

- [Inference] *MLOps Engineering at Scale* as authority for NVL72 collective behavior, MFU, GPU SDC screening, or checkpoint compatibility. Its Manning catalog shows pipeline/lifecycle learning, not rack-level claims.

- [Inference] Vendor product pages or peak-throughput marketing as PASS evidence. Use an explicit measured workload. Show all conditions in the report.

- [Inference] Any loss-only “no spikes means healthy” claim. SDC literature shows ambiguity. It can show persistent parameter divergence without a decisive simple loss signature.

- [Inference] A two-hour “54-day reliability test” label. The observation window does not make it valid.

## 7. Source confidence and currency

- [Observed] **High confidence, primary docs:** the NVIDIA Megatron Bridge guide and the PyTorch DCP reference make first-party operational documentation. Caveat: NVIDIA makes “latest” docs mutable and product-specific. Keep software and doc versions in the acceptance artifact. PyTorch DCP stable docs currently show v2.14.0 and a July 2026 update.

- [Observed] **High confidence, primary evidence:** OSDI ’26 paper page and linked paper; primary arXiv paper for controlled SDC work. A very large production fleet or controlled injected-fault setup makes the evidence base. Do not put those findings directly into rack-specific thresholds.

- [Observed] **Medium-high confidence, book contents:** the author repository plus O’Reilly official catalog/contents show DMLS and *Reliable Machine Learning* coverage. O’Reilly catalog and author repository sources show *AI Engineering* topics. Manning’s official catalog shows *MLOps Engineering at Scale* topics, but not chapter numbering. The O’Reilly *Reliable Machine Learning* full catalog page sends access denied. So this node uses only official indexed headings and chapter pages. Specific instructional-depth claims use the inference mark, not asserted chapter text.

- [Observed] **High confidence for DCGM intent, lower for exact URL stability:** NVIDIA DCGM documentation shows health diagnostics and operational cautions. Some `latest` paths do not keep one address; NVIDIA can remove them. Put the DCGM version and the exact diagnostic suite in use in the record.

## Gaps

- The [catalog supplement](oreilly.md) keeps source-specific access limits and metadata conflicts.

- Public Manning samples show selected introductions and headings, not necessarily full chapter text.

- The 2026 platform title makes a reading-priority change only; the operational recovery canon keeps its position.

- Course chapter titles do not show measured recovery results or complete checkpoint-state coverage.

- Alternate audio/video formats make no independent technical evidence.

- No single public source shows a validated two-hour pass threshold for GB300/NVL72 18-tray, Chennai, Llama-3-class pretraining. Such a threshold must use tenant workload targets and local measured baselines.

- The searched sources do not show compatibility for every Megatron Bridge resiliency capability. The untested items: the exact GB300 deployment, the installed framework release, and the tenant’s checkpoint backend. Check compatibility in the pinned release, then run the drill.

- Public summaries do not show a universal MFU calculation convention or an expected Llama-3-class throughput. Model size, sequence length, precision, batch, parallelism, and FLOP accounting make variations in these numbers.

- No two-hour trial shows a robust estimate of rare 30–90 day failure rates. Use a longer soak, fleet history, operating procedures, and an explicit reliability model for that question.

- Book chapter lists show topical coverage, not executable rack-scale pretraining fault-injection or acceptance procedures. The verified DMLS contents do not show detailed checkpoint/restart coverage. [Author contents](https://github.com/chiphuyen/dmls-book)
