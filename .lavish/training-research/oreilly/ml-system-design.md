# N03 — *Machine Learning System Design*

Research date: 2026-10-11. All claims below use a source URL.

Bench safety: process interruption must not start without operator approval.
Default checks do not use power removal, PCIe reset, or hardware-error injection.
Show expected checkpoint rollback and replay separately from silent duplicate or skipped progress.

Claims use the labels [observed], [calculated], or [inference]. Scope: rack-bench training on a GB300-class, NVL72-class, 18-tray rack in Chennai. A PASS must show measured evidence for the named workload, not a specification claim. The bench uses an acceptance window of about two hours. It runs before a 30–90-day lease and a possible 54-day Llama-class training run.

## 1. Verified edition and chapters

[Observed] Manning shows the authors as **Valerii Babushkin and Arseny Kravchenko**, not “Dmitry Babushkin”. The record shows these data: title *Machine Learning System Design: With end-to-end examples*, January 2025, ISBN 9781633438750, 376 pages. Manning’s public summary shows these themes: end-to-end ML project design, requirements, metrics, datasets, development, release, and maintenance. [Manning catalog](https://www.manning.com/books/machine-learning-system-design)

[Observed] The supplied O’Reilly learning URL fetch shows HTTP 403. It does not show text or contents in this research session. This research session also shows the corresponding public O’Reilly catalog record, but no full chapter contents from it. [Supplied O’Reilly URL](https://learning.oreilly.com/library/view/-/9781633438750/?orm_source=mcp) [O’Reilly book record](https://www.oreilly.com/library/view/machine-learning-system/9781633438750)

[Observed] Directly readable Manning LiveBook samples show these chapters. Chapter 6 “Gathering datasets” shows data sources, ETL, metadata, and healthy data pipelines. Chapter 10 “Training pipelines” shows tools/platforms, scalability, configurability, testing, and property-based testing. Chapter 12 “Measuring and reporting results” shows model performance, experiments, and reporting. Chapter 13 “Integration” shows release cycle, operation, and overrides/fallbacks. Chapter 14 “Monitoring and reliability” shows software health, data quality/integrity, model quality/relevance, and monitoring and response. [Ch. 6](https://livebook.manning.com/book/machine-learning-system-design/chapter-6) [Ch. 10](https://livebook.manning.com/book/machine-learning-system-design/chapter-10) [Ch. 12](https://livebook.manning.com/book/machine-learning-system-design/chapter-12) [Ch. 13](https://livebook.manning.com/book/machine-learning-system-design/chapter-13) [Ch. 14](https://livebook.manning.com/book/machine-learning-system-design/chapter-14)

[Observed] Public samples show outlines and selected introductory text, not necessarily full chapters. The review keeps these topics verified. The samples do not show coverage of MFU accounting, complete distributed checkpoint/resume state, or interruption recovery. They do not show flaky-node detection or loader-stall instrumentation. Manning shows the same author names: Valerii Babushkin and Arseny Kravchenko.

## 2. Training-run validation and reliability evidence

[Observed] Chapters 6, 10, 12, 13, and 14 make verified framing: dataset/pipeline, pipeline testing, measurement/reporting, operational, and monitoring/reliability. The public evidence does not show a distributed-pretraining procedure. [Ch. 6](https://livebook.manning.com/book/machine-learning-system-design/chapter-6) [Ch. 10](https://livebook.manning.com/book/machine-learning-system-design/chapter-10) [Ch. 12](https://livebook.manning.com/book/machine-learning-system-design/chapter-12) [Ch. 13](https://livebook.manning.com/book/machine-learning-system-design/chapter-13) [Ch. 14](https://livebook.manning.com/book/machine-learning-system-design/chapter-14)

[Inference] Use the verified chapters for requirements, data-pipeline health, testing, measurement/reporting, operational monitoring, and data/model-quality framing. Use them for acceptance criteria and observability, but not as evidence of runtime training reliability. The review keeps MFU accounting, interruption/restart drills, complete checkpoint/resume state, loss-spike diagnosis, flaky-node detection, and loader-stall instrumentation unverified. The evidence does not show their absence.

[Observed] The Llama 3 paper shows 466 total interruptions = 47 planned + 419 unexpected. Unexpected-event attribution uses 419. Keep these as context inputs, not claims from this book. [Llama 3, §3.3.4](https://arxiv.org/html/2407.21783v3)

[Inference] Do not make a two-hour measurement window into a 54-day guarantee. [Inference] Put measured named-workload throughput/MFU in the report with a declared formula and configuration. Keep per-rank timing, loader wait, and interruption counts/classification in the report. Keep checkpoint save/restore, resumed-state correctness, and observed loss behavior in the report too. A short normal loss trace or the absence of a node failure cannot show multiweek reliability.

[Inference] Use executable framework/vendor documentation and workload-specific measurement as better runtime-evidence sources. Use them before this book’s public catalog description. The existing canon shows these operational sources: [Megatron Bridge resiliency](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html), [PyTorch Distributed Checkpoint](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html), and [PyTorch torchrun fault-tolerance tutorial](https://docs.pytorch.org/tutorials/beginner/ddp_series_fault_tolerance.html). These links do not show evidence of the book’s contents. They show the gap between system-design framing and runtime recovery contracts.

## 3. Portable bench techniques

1. [Inference/proposal] **Keep a fixed workload card before timing.** Keep model/workload identity, software/config hashes, precision, sequence/batch, parallelism, data source, warm-up exclusion, interval, and MFU convention in the card. Check only results for the same declared workload against each other. Do not make a universal GB300 threshold. [Manning Chapter 12 measuring/reporting](https://livebook.manning.com/book/machine-learning-system-design/chapter-12); [Megatron-LM workload-specific performance context](https://github.com/NVIDIA/Megatron-LM). Measured evidence: tokens/s, step-time distribution, and MFU under the recorded settings.

2. [Inference/proposal] **Check input-path wait separately from compute.** Keep loader wait and per-rank step timing in the record during the named run. The report then keeps a slow input pipeline out of low-hardware-capability claims. [Manning Chapter 6 data-pipeline health](https://livebook.manning.com/book/machine-learning-system-design/chapter-6); [Chapter 10 pipeline testing](https://livebook.manning.com/book/machine-learning-system-design/chapter-10); [PyTorch profiler recipe](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html). Measured evidence: loader-wait distribution and rank-level timing for the test interval.

3. [Inference/proposal] **Make recovery an explicit, non-destructive drill.** Use a disposable test job/checkpoint, and keep the saved-state list in the record. Run a controlled stop and restart of the process or job. Then check the resumed step/data position and training-state continuity. Do not make model weights alone into complete resume state. Measured evidence: checkpoint write/read time, verified resume point, and lost-work interval. [PyTorch DCP](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html); [torchrun fault-tolerance tutorial](https://docs.pytorch.org/tutorials/beginner/ddp_series_fault_tolerance.html)

4. [Inference/proposal] **Put interruptions and node outliers in classes, not averages.** Keep planned maintenance separate from unexpected interruptions. Keep per-rank timings and recovery outcomes in the record. The supplied meta-count makes the hardware denominator 419 unexpected interruptions, not all 466. Measured evidence: counts by class, restart result, and rank timing distribution. Keep this as an observation protocol, not a rare-event-rate validation from two hours. [Llama 3 interruption anchor](https://arxiv.org/html/2407.21783v3); [Megatron Bridge resiliency](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

5. [Inference/proposal] **Make loss spikes investigation triggers, not standalone verdicts.** Check loss against step/rank timing, input position, and available health telemetry. Put the observed trace and exceptions in the report. Do not use a spike-free trace as proof of correctness. [Manning Chapter 12 measurement/reporting](https://livebook.manning.com/book/machine-learning-system-design/chapter-12); [Chapter 14 monitoring/reliability](https://livebook.manning.com/book/machine-learning-system-design/chapter-14); [SDC study cited in canon](https://arxiv.org/html/2604.00726v1). Measured evidence: loss and relevant telemetry over the stated interval; no multiweek guarantee.

## 4. Canon relation and candidate status

[Inference] Put this in the canon as a **new candidate / complementary system-design source**. Keep it below operational distributed-training references for rack acceptance. Verified Chapters 6, 10, 12, 13, and 14 make pipeline design/testing, measurement/reporting, operational, and monitoring framing. They do not show implementation-level distributed-training reliability coverage. Do not use this book as a replacement for the canon’s Megatron/PyTorch recovery material or its current reliability evidence.

[Observed] The existing canon keeps book-level system framing separate from runtime training reliability. It shows *Designing Machine Learning Systems*, *Reliable Machine Learning*, operational framework documentation, and reliability papers. [Canon](../books.md) Use this book as a complementary candidate for pipeline design, measurement, and monitoring. The public samples make chapter-level comparison possible. The review keeps runtime training reliability unverified.

## Gaps

- The supplied O’Reilly learning URL shows HTTP 403. Manning LiveBook shows readable samples for Chapters 6, 10, 12, 13, and 14, but no full-book text. The claims use visible outlines and excerpts only.

- The samples check the cited chapter titles and headings. They do not show full-book coverage of MFU, complete checkpoint/resume state, or interruption recovery. They do not show loss-spike diagnosis, flaky-node detection, or loader-stall instrumentation.

- Public catalog evidence cannot show a GB300/NVL72 threshold or a 54-day reliability guarantee. Use PASS only for a measured assertion on a named workload and stated interval.
