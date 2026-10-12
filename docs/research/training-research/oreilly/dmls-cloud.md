# Supplement pass N05 — *Designing Machine Learning Systems in the Cloud*

Research date: 2026-10-11. All claims below use a source URL.

Bench safety: process interruption must not start without operator approval.
Default checks do not use power removal, PCIe reset, or hardware-error injection.
Show expected checkpoint rollback and replay separately from silent duplicate or skipped progress.

## 1. Verified identity, edition, chapters, and access

[Observed] O’Reilly’s official title page shows *Designing Machine Learning Systems in the Cloud* as a video course with Kyle Gallatin. The page shows its lesson sequence. The catalog shows this framing: an introduction to the design and implementation of production ML systems. [Official O’Reilly catalog](https://www.oreilly.com/videos/designing-machine-learning/0636920953234)

[Observed] The catalog shows the listed contents. The sequence starts with Course Introduction.

The catalog shows Lesson 1.1: Introduction to Systems Design. The catalog shows Lesson 1.2: ML-Specific Systems Design. The catalog shows Lesson 1.3: ML-Software Versus “Classic” Software. The catalog shows Lesson 1.4: Data Engineering Concepts for ML.

The catalog shows Lesson 2.1: Working with Training Data. The catalog shows Lesson 2.2: Feature Engineering for ML. The catalog shows Lesson 2.3: Working with Feature Stores. The catalog shows Lesson 3.1: Defining Offline and Online ML Metrics. The catalog shows Lesson 3.2: Model Performance Testing and A/B Testing. The catalog shows Lesson 3.3: Experiment Tracking and Management.

The catalog shows Lesson 4.1: Strategies for ML Model Deployment. The catalog shows Lesson 4.2: Managing ML Model Serving Applications. The catalog shows Lesson 4.3: Automating Model Training and Deployment. The catalog shows Lesson 5.1: Observability in the ML Domain. The catalog shows Lesson 5.2: ML Model Observability for ML Systems. [Official lesson page](https://www.oreilly.com/videos/designing-machine-learning/0636920953234/0636920953234-video367064)

[Observed] The supplied O’Reilly Learning URL fetch shows HTTP 403. A search index shows the public O’Reilly catalog and lesson pages, with title/author/lesson listings. The review therefore keeps catalog access verified. This pass cannot check member video playback or the underlying lesson contents. [Supplied Learning URL](https://learning.oreilly.com/videos/-/0636920953234/?orm_source=mcp) [Official catalog](https://www.oreilly.com/videos/designing-machine-learning/0636920953234)

[Unverified] The accessible official catalog/lesson results do not show the requested 2024 publication year and 75-minute runtime. The review keeps them unverified. Search results and the catalog do not show a separate edition/version statement.

Concise official wording: “practical tactics for engineering training data, features and data pipelines to deploying and monitoring ML models for real-time inference in production.” [O’Reilly catalog](https://www.oreilly.com/videos/designing-machine-learning/0636920953234)

## 2. Training reliability coverage

[Observed] The catalog explicitly shows training-data work, experiment tracking, automated training and deployment, and ML observability. The catalog puts its stated emphasis on end-to-end production ML and real-time inference. [Official catalog and contents](https://www.oreilly.com/videos/designing-machine-learning/0636920953234)

[Observed] The publicly visible course structure does not show MFU or distributed-training performance accounting. It does not show checkpoint/resume semantics, interruption recovery, node/accelerator fault detection, or flaky-node isolation. It does not show loss/gradient anomaly triage or data-loader stall diagnosis. This claim uses the verified catalog only. The inaccessible video content can still show these subjects.

[Inference] Use this course for system-level questions about training data, experiment tracking, automation, and observability. The available evidence does not show operational guidance for a long-running, multi-node LLM pretraining job. Do not make cloud-oriented production-ML design equal to NVL72 fault engineering.

## 3. Portable techniques for a two-hour rack workload [inference/proposal]

These proposals use the catalog topics as their basis; they do not show course instructions. The named measured workload on the actual rack makes the evidence source. Vendor specifications alone do not make a PASS.

1. **Make the measurement traceable.** Keep exact model/configuration and software/data versions, warm-up exclusion, timed interval, tokens/s, step-time distribution, and rank-level variation in the record. For an MFU calculation, show the FLOP convention and workload inputs. The course’s listed experiment tracking and performance-testing topics make the source basis; keep the measurement design as a proposal. [Course contents](https://www.oreilly.com/videos/designing-machine-learning/0636920953234) **Evidence:** per-step/per-rank measurements in the record, plus observed throughput and dispersion calculations for the two-hour run. Do not make a universal GB300 pass threshold claim.

2. **Make input-pipeline waits visible separately.** Use instrumentation for data-wait time and step time, and keep the actual data path in the record. The record then keeps a slow step and loader starvation separate. Source basis: training-data and data-engineering lessons. [Course contents](https://www.oreilly.com/videos/designing-machine-learning/0636920953234) **Evidence:** waiting/step-time fractions during the measured workload. A short run cannot show behavior under later storage contention.

3. **Run resume as an explicit interruption drill.** Make a checkpoint, put the process/job through a controlled stop, then start it again. Check the expected step and consumed-data position, and keep save, restore, and lost-work times in the record. Keep this as a proposed rack test, not a video-verified technique. The catalog shows automated training and experiment tracking only. **Evidence:** checkpoint identity, before/after step and sampler position, restore outcome, and timings; the catalog does not show checkpoint semantics. [Course contents](https://www.oreilly.com/videos/designing-machine-learning/0636920953234)

4. **Check loss with context, not loss alone.** Keep loss in the log beside step time, rank identity, data position, and available device/job telemetry. Put a flag on excursions for investigation; do not make a fault declaration from loss alone. The course listing shows observability/metrics as broad topics, not this specific diagnostic method. [Course contents](https://www.oreilly.com/videos/designing-machine-learning/0636920953234) **Evidence:** the aligned trace and the disposition of any anomaly in the window. A clean two-hour trace cannot show the absence of rare or silent faults.

5. **Put interruptions and stragglers in the report as observed events.** Keep per-rank progress and job interruptions during the exact workload in the record. Keep measured outliers separate from inferred hardware causes. The catalog shows observability and experiment management at a general level only. [Course contents](https://www.oreilly.com/videos/designing-machine-learning/0636920953234) **Evidence:** counts, durations, affected ranks, and recovery success in the report. Do not put a defective label on a node without diagnostic corroboration.

[Observed] Context for incident-count interpretation: the Llama 3 paper shows Meta’s 466 total interruptions as **47 planned and 419 unexpected**. Hardware-related attribution uses the 419 unexpected events, not all 466. The review keeps these separate from course findings. [Llama 3, §3.3.4](https://arxiv.org/html/2407.21783v3)

[Inference] A two-hour workload can show measured behavior and recovery for the named test. It cannot show a 30–90-day lease guarantee or a 54-day Llama training warranty. Keep two hours as a sample, not a long-run reliability demonstration. Do not make this course’s cloud-systems framing into universal GB300 acceptance gates or destructive default tests.

## 4. Canon relation / candidate

[Observed] The canon already puts Chip Huyen’s *Designing Machine Learning Systems* (DMLS book) as a systems-framing source. The canon shows verified chapters on distributed training, debugging, monitoring, and infrastructure. [Canon, N07](../books.md)

[Inference] Keep this video as an adjacent, lower-evidence companion, not a new reliability authority. Its public outline makes these topics explicit: production-system, training-data, experiment-management, and observability. The accessible sources do not show material depth on distributed pretraining reliability beyond the book’s canon entry. Candidate canon note:

> “O’Reilly video by Kyle Gallatin; catalog topics include training data, experiment management, automation and observability; playback inaccessible; runtime/year unverified; not a checkpoint/fault-engineering reference.”

## Gaps

- This pass shows HTTP 403 on O’Reilly Learning playback. The review keeps transcripts and lesson-level content unverified.

- The accessible official catalog evidence does not show the stated 2024 date or 75-minute runtime.

- No reviewed public evidence shows course coverage of MFU accounting, interruptions/recovery, or checkpoint state semantics. It does not show loss triage, flaky-node detection, or loader-stall diagnosis.

- No two-hour test can show a 54-day run guarantee. Use the exact tenant workload. Put measurements, interruptions, and recovery outcomes in the report. Do not make a long-term uptime extrapolation from them.
