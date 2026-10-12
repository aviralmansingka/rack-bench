# O'Reilly catalog supplement: training-run validation

Research date: 2026-10-11. All claims below use a source URL.

Scope: `rack-bench bench training`; one GB300-class NVL72-class rack, 18 trays, Chennai, India.
The tenant uses a two-hour check before a 30–90-day commitment.
A named workload and measured assertion make a PASS.
Catalog metadata, chapter headings, and software features do not make a measured PASS.
Use the [training proposal](docs/training-bench-research.md) and [initial book canon](books.md) for context.

Labels: [observed] shows source evidence; [calculated] shows arithmetic; [inference] shows a bench proposal or research decision.
These notes keep catalog contents separate from inspected chapter text.
Each source note shows three to five proposed checks and explicit access limits.
The [supplement report](oreilly/research.md) shows the independent node map and ten lessons.

[Inference] Keep current framework guides and reliability papers first.
Keep DMLS and *Reliable Machine Learning* at the same general reading priority.
Put *Machine Learning Platform Engineering* in the reading list for selected platform chapters.
Do not use its 2026 date as proof of broader reliability coverage.
Source bases: [DMLS author resources](https://github.com/chiphuyen/dmls-book),
[Google Research book abstract](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production),
and [Manning Chapter 9](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9).

## 1. Designing Machine Learning Systems — Chip Huyen

[Observed] The catalog shows the May 2022 O'Reilly book, ISBN 9781098107956, with 386 pages.
Its contents show Chapter 6 topics: training, distributed training, experiment tracking, and debugging.
Chapter 8 shows monitoring; Chapter 10 shows infrastructure and tooling.
The author's repository shows the book as systems design, not a tutorial.
Sources: [catalog](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp),
[author repository](https://github.com/chiphuyen/dmls-book).

[Inference] Keep the existing canon position.
Use the contents for workload requirements, input-path measurements, and anomaly records.
Do not use unseen chapter text as evidence for detailed checkpoint state or MFU procedures.
[Source note and five proposed checks](oreilly/dmls.md).

## 2. Designing Machine Learning Systems — audiobook

[Observed] The audiobook catalog shows Ascent Audio, July 2025, and 12h 54m.
The author shows the audiobook with her 2022 book.
The catalog shows numbered tracks, not inspected chapter prose.
Sources: [audio catalog](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp),
[author book page](https://huyenchip.com/books).

[Calculated] 12h 54m makes 774 minutes.
[Inference] Keep the audiobook as an alternate format, not independent technical evidence.
No inspected source shows a revised technical edition or exact passage equivalence.
The reviewed records do not show Kathleen Li's precise role.
Use the book's workload card and measurement contract.
[Source note and five proposed checks](oreilly/dmls-audio.md).

## 3. Machine Learning System Design — Babushkin and Kravchenko

[Observed] Manning shows Valerii Babushkin and Arseny Kravchenko as authors.
Its catalog shows January 2025 and 376 pages.
The supplied O'Reilly catalog shows February 2025.
Keep publisher and platform dates separate.
[Publisher](https://www.manning.com/books/machine-learning-system-design),
[supplied platform record](https://learning.oreilly.com/library/view/-/9781633438750/?orm_source=mcp).

[Observed] Public samples show Chapter 10 training pipelines and property-based testing.
Chapter 14 shows software health, data quality, and model quality as separate topics.
Sources: [Chapter 10](https://livebook.manning.com/book/machine-learning-system-design/chapter-10),
[Chapter 14](https://livebook.manning.com/book/machine-learning-system-design/chapter-14).

[Inference] Put this title in optional pipeline-testing and monitoring reading.
For example, check that a declared data cursor makes progress without silent skips.
Use this property as a bench proposal, not a verified checkpoint recipe from the book.
[Source note and five proposed checks](oreilly/ml-system-design.md).

## 4. Reliable Machine Learning — Chen, Murphy, Parisa, Sculley, Underwood

[Observed] Google Research shows the 2022 O'Reilly book and its data-management chapter abstract.
The abstract shows SLOs, SLIs, monitoring, and data handling.
Indexed publisher contents show Chapter 4 training data and Chapter 9 monitoring.
An author puts this on record: the book shows no code examples.
Sources: [Google Research abstract](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production),
[publisher Chapter 9](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch09.html),
[author Q&A](https://datatalks.club/books/20221121-reliable-machine-learning.html).

[Inference] Keep this book beside DMLS for general reliability reading.
Use it for observable training-service objectives and response ownership.
The reviewed evidence does not make an operational headline for distributed pretraining validation.
The reviewed evidence does not show MFU, complete resume state, or GPU screening procedures.
[Source note and five proposed checks](oreilly/reliable-ml.md).

## 5. Designing Machine Learning Systems in the Cloud — Kyle Gallatin

[Observed] Official indexed contents show training data, experiment tracking, automation, and observability.
The catalog shows production ML and real-time inference.
The review keeps the supplied 2024 date and 75-minute runtime unverified.
Source: [official catalog](https://www.oreilly.com/videos/designing-machine-learning/0636920953234).

[Inference] Keep this video optional, below sources with inspected training chapter samples.
Use its experiment-tracking theme; keep configuration and measurement artifacts.
Keep cloud design separate from distributed training recovery.
[Source note and five proposed checks](oreilly/dmls-cloud.md).

## 6. Train Large Language Models Faster — Parallelism Deep Dive

[Observed] The researcher's catalog fetch shows Paulo Dichone, Packt, June 2025, and 8h 50m.
Its contents show data, pipeline, tensor, and hybrid parallelism.
Chapter 14 shows fault tolerance and checkpoint strategies.
The catalog shows small demonstrations, not measured rack-scale recovery.
Source: [course catalog](https://learning.oreilly.com/videos/-/9781806110896/?orm_source=mcp).

[Calculated] 8h 50m makes 530 minutes.
[Observed] The orchestrator's repeat fetch shows an access denial; the denial keeps the video and transcripts uninspected.
[Inference] Put this course in place as an optional parallelism and checkpoint-design introduction.
Make a measured step-time comparison across declared parallel layouts; keep workload settings fixed.
Use current framework documentation for the checkpoint contract and recovery drill.
[Source note and five proposed checks](oreilly/llm-parallelism.md).

## 7. Machine Learning Platform Engineering — Tan, Mallya, Padmanabhan

[Observed] The catalog shows Benjamin Tan Wei Hao, Varun Mallya, and Shanoop Padmanabhan.
The platform record shows February 2026 and 504 pages.
Public samples show Chapters 8–9 training and validation, and Chapter 11 monitoring.
Chapter 9 shows PersistentVolumes, TensorBoard, MLflow, and lineage.
Sources: [publisher](https://www.manning.com/books/machine-learning-platform-engineering),
[catalog](https://learning.oreilly.com/library/view/-/9781633437333/?orm_source=mcp),
[Chapter 9](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9),
[Chapter 11](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-11).

[Inference] Put these selected chapters before older cloud-specific pipeline reading.
For example, put a dataset version, training configuration, step metrics, and checkpoint identity in one run record.
This change makes a difference to platform reading, not to the operational recovery sources.
The samples do not show full checkpoint recovery or flaky-node screening.
Do not make a full-book supersession claim for *MLOps Engineering at Scale*.
[Source note and four proposed checks](oreilly/ml-platform.md).

## 8. Designing Deep Learning Systems — Wang and Szeto

[Observed] Manning shows Chi Wang and Donald Szeto.
The supplied catalog shows Kit Pang Szeto. The reviewed records do not show a reason for the difference.
Do not make an inference about an alias relationship.
Chapter 3 shows a training service; Chapter 4 shows distributed training; Chapter 5 shows hyperparameter optimization.
Sources: [publisher](https://www.manning.com/books/designing-deep-learning-systems),
[supplied record](https://learning.oreilly.com/library/view/-/9781633439863/?orm_source=mcp),
[Chapter 4](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4).

[Inference] Put this book in optional training-service and parallelism reading.
Check launch status, rank progress, and input waits as separate service signals.
Do not use training optimization as failure recovery or hardware validation.
[Source note and five proposed checks](oreilly/dl-systems.md).

## 9. Deep Learning for Vision Systems — Mohamed Elgendy

[Observed] Manning shows the title and author.
A Google Books contents record shows Chapter 4 project structure and hyperparameter tuning.
The supplied 2020 date and 480-page count keep an unverified status in the source note.
Sources: [publisher](https://www.manning.com/books/deep-learning-for-vision-systems),
[contents record](https://books.google.com/books/about/Deep_Learning_for_Vision_Systems.html?id=sDszEAAAQBAJ).

[Inference] Keep this title at low priority for distributed pretraining validation.
Use its project-structure theme only for controlled experiment records.
Make a change to one test variable at a time; keep the same workload baseline.
The contents do not show distributed recovery or GPU-rack reliability methods.
[Source note and five proposed checks](oreilly/vision-systems.md).

## 10. Machine Learning System Design — Video Edition

[Observed] The supplied URL shows the Manning *Machine Learning System Design, Video Edition*.
The catalog shows February 2025 and 13h 29m.
Its description shows narrated book content with its figures, text, and code.
The supplied URL does not show *Machine Learning Platform Engineering Video Edition*.
Source: [video catalog](https://learning.oreilly.com/videos/-/9781633438750VE/?orm_source=mcp).

[Inference] Keep this video as an alternate format of the Babushkin/Kravchenko book.
Do not use it as independent technical corroboration.
Use the book's verified public chapter samples for technical scope.
A check of the second supplied title must use a separate platform-video URL.
[Source note and five proposed checks](oreilly/system-design-video.md).

## 11. Canon changes

[Inference] Keep Megatron Bridge, PyTorch checkpoint/restart guides, and reliability papers before books.
Keep DMLS and *Reliable Machine Learning* at the same general reading priority.
Put *Machine Learning Platform Engineering* Chapters 8, 9, and 11 in platform reading.
Keep *MLOps Engineering at Scale* for its cloud-specific pipeline context.
Put *Machine Learning System Design* Chapters 6, 10, 12, 13, and 14 in optional reading.

Keep the parallelism course and *Designing Deep Learning Systems* optional.
Do not put the vision book in the main training-reliability reading list.
Keep alternate formats separate from independent technical evidence.
The [updated canon](books.md) shows these changes and source bases.
The [distilled reading list](docs/training-bench-research.md#reading-list) shows the selected reading sequence.

## 12. Portable checks and safety boundary

[Inference] The following checks make an adaptation of the source themes. The books do not make rack acceptance gates.
Source bases: [pipeline testing](https://livebook.manning.com/book/machine-learning-system-design/chapter-10),
[metrics and lineage](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9),
and [reliability objectives](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production).

1. Put the named workload, versions, precision, parallel layout, data identity, warm-up, and measurement interval in the record.
2. Keep step metrics and input waits separate; put them together with rank and device events.
3. Check pipeline properties, including declared data progress and complete artifact publication.
4. Put dataset lineage, training configuration, metrics, and checkpoint identity in one run record.
5. Make measured objectives and response ownership definitions before the test; keep unknown causes explicit.

Use [current checkpoint documentation](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html) for actual restore-state requirements.
Start process interruption only with operator approval.
The default checks do not use power removal, PCIe reset, or hardware-error injection.
Show expected checkpoint rollback and replay separately from silent duplicate or skipped progress.

For interruption attribution, keep 466 total = 47 planned + 419 unexpected.
The [Llama 3 paper](https://arxiv.org/html/2407.21783v3) shows this anchor, not any catalog book.
Use 419 only for unexpected-event attribution.
Do not make this external event inventory a local failure-rate estimate.

## Gaps

- Full book text and video playback keep an inaccessible status for most catalog sources.
- Public sample chapters show selected introductions and headings, not necessarily complete chapter text.
- The reviewed evidence does not show a book-based MFU convention or full distributed resume-validation procedure.
- The course catalog shows checkpoint topics but no verified recovery results.
- *Reliable Machine Learning* page counts and dates show differences across supplied and indexed records.
- The metadata does not show whether format, indexing, or edition makes these differences.

- The audiobook narrator role and exact text equivalence keep an unverified status.
- The supplied records show no URL for *Machine Learning Platform Engineering Video Edition*.
- Some dates, page counts, and runtimes keep an unverified status; source notes keep each limit.
- No source shows a universal GB300 two-hour PASS threshold.
- Two hours cannot show 30–90-day survival, rare-fault rates, or full convergence.
- The supplement shows no rack measurements and no measured PASS.
