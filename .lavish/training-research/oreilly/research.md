# Training canon: O'Reilly catalog supplement

Question: Which catalog sources put useful methods into measured training-run validation?
Research date: 2026-10-11; audience: rack-bench maintainers and training tenants.
Scope: a supplement to the completed seven-category training research.
The rack keeps GB300-class NVL72-class hardware and 18 trays in Chennai, India.
The tenant uses a two-hour `bench training` window before a 30–90-day commitment.
The operator checks measured assertions for a named workload, not catalog content or vendor specifications.

[Observed] The [Llama 3 paper](https://arxiv.org/html/2407.21783v3) shows 466 interruptions: 47 planned and 419 unexpected.
Use 419 only for unexpected-event attribution.
Do not use this external inventory as a local failure-rate estimate.
Two hours cannot show multi-week reliability, rare-fault rates, or full convergence.
Check for operator approval before a process interruption.
The default suite does not use power removal, PCIe reset, or hardware-error injection.

Labels show evidence type: [observed] shows source evidence, [calculated] shows arithmetic, [inference] shows a proposed application or reading decision.
Publisher samples show selected introductions and headings, not complete chapter text.
The source notes keep catalog, sample, playback, and metadata limits separately.

## Node map

Each researcher uses an independent search for one source node.
Each lesson uses its own node result.
Readers must not use alternate formats as independent technical corroboration.

```mermaid
flowchart TD
N01["Designing Machine Learning Systems"]
N02["DMLS audiobook"]
N03["Machine Learning System Design"]
N04["Reliable Machine Learning"]
N05["DMLS in the Cloud video"]
N06["LLM Parallelism Deep Dive video"]
N07["Machine Learning Platform Engineering"]
N08["Designing Deep Learning Systems"]
N09["Deep Learning for Vision Systems"]
N10["System Design Video Edition"]
```

## Node table

| Node | Question | Dependencies | Acceptance condition | Child | State |
| --- | --- | --- | --- | --- | --- |
| N01 | Does DMLS show verified training checks? | None | Check edition, contents, methods, and canon relation. | oreilly-dmls | done |
| N02 | Does the audiobook show distinct content? | None | Check identity, duration, edition relation, and text limits. | oreilly-dmls-audio | done |
| N03 | Does ML System Design show training methods? | None | Check chapters and keep design separate from runtime validation. | oreilly-ml-system-design | done |
| N04 | What reliability methods does RML show? | None | Check training, monitoring, recovery, and chapter evidence. | oreilly-reliable-ml | done |
| N05 | Does the cloud video show relevant procedures? | None | Check syllabus, cloud scope, and transfer limits. | oreilly-dmls-cloud | done |
| N06 | Does the parallelism video show support for training checks? | None | Check syllabus, accounting, recovery coverage, and limits. | oreilly-llm-parallelism | done |
| N07 | Does ML Platform Engineering make changes to the canon? | None | Check 2026 edition, platform chapters, and newer coverage. | oreilly-ml-platform | done |
| N08 | Does Deep Learning Systems show validation methods? | None | Check chapters, training optimization, and correctness coverage. | oreilly-dl-systems | done |
| N09 | Does Vision Systems show portable checks? | None | Keep numeric debugging separate from GPU-rack reliability. | oreilly-vision-systems | done |
| N10 | Does the Video Edition show distinct evidence? | None | Check the linked product and put a flag on the missing second-product URL. | oreilly-system-design-video | done |

A “Done” mark shows one of two outcomes.
The brief shows an answer to its bounded question, or it shows the evidence limit.
It does not show a rack PASS for an assertion.
The catalog keeps its second platform-video title as an explicit source gap.

## Artifacts and decisions

- [Sourced supplement](../oreilly.md): ten source entries and reading decisions.
- [Updated book canon](../books.md): selected platform chapters before older cloud-specific pipeline material.
- [Distilled reading list](../docs/training-bench-research.md#reading-list): operational guides keep the first position.
- [Handoff report](../ORCHESTRATOR-REPORT.md): verdicts, source checks, limits, and project placement.

## N01: A topic heading is not a test procedure

This lesson checks whether DMLS shows verified training-validation methods.
A chapter heading shows topic coverage, not an executable acceptance procedure.
[Observed] Chapter 6 shows distributed training, experiment tracking, and debugging.
Chapters 8 and 10 show monitoring and infrastructure.
The author's repository shows the book as systems design, not a tutorial.

[Inference] Operators use these topics to make definitions for the workload and its observed signals.
For example, operators put model configuration and input waits in the record before a throughput comparison.
A distributed-training heading does not show complete checkpoint state.
A checkpoint test uses the actual trainer's state contract.
The public contents do not show DMLS's detailed MFU or recovery procedures.
Keep DMLS at its existing general reading priority.

Sources: [catalog](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp),
[author repository](https://github.com/chiphuyen/dmls-book).
Check the [source note](dmls.md) and [review record](nodes/N01.md).

## N02: A newer format does not prove newer methods

This lesson checks whether the DMLS audiobook shows additional technical evidence.
An alternate format makes a change in the delivery to the reader.
It does not show independent support for the underlying technical claims.
[Observed] The author shows the 2025 audiobook under her 2022 book.
The catalog shows 12h 54m and numbered tracks.
[Calculated] This duration shows 774 minutes.

[Inference] Keep the audiobook as a reading option.
For example, use it for systems context, then check current checkpoint documentation before a restore drill.
No inspected source shows a revised technical edition or exact passage equivalence.
The reviewed records do not show Kathleen Li's precise role.
Reviewers do not check playback or named track contents.
The audiobook does not make a change to the operational reading order.

Sources: [author page](https://huyenchip.com/books),
[audio catalog](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp).
Check the [source note](dmls-audio.md) and [review record](nodes/N02.md).

## N03: Test pipeline properties separately from hardware health

This lesson checks the Manning book's training-validation contribution.
A pipeline property shows behavior that the pipeline must keep.
[Observed] Chapter 10 shows training-pipeline testing and property-based testing.
Chapter 14 shows software health, data quality, and model quality separately.
The public samples show these topics, not complete distributed recovery.
Manning shows the names Valerii Babushkin and Arseny Kravchenko.

[Inference] Keep optional pipeline-testing and reporting reading.
For example, check the next batch after restore against the declared checkpoint cursor.
This property shows a bench proposal, not a verified book checkpoint recipe.
Operators show expected rollback and replay separately from silent skipped or duplicate progress.
A successful pipeline test does not show GPU health or multi-week reliability.
The reviewed samples do not show MFU or full resume-state guidance.

Sources: [Chapter 10](https://livebook.manning.com/book/machine-learning-system-design/chapter-10),
[Chapter 14](https://livebook.manning.com/book/machine-learning-system-design/chapter-14).
Check the [source note](ml-system-design.md) and [review record](nodes/N03.md).

## N04: Reliability objectives need observed signals

The question checks whether Reliable Machine Learning makes the operational headline.
An SLI shows service behavior.
An SLO shows its target.
[Observed] A Google Research abstract shows SLIs, SLOs, monitoring, and data handling.
Indexed contents show training-data and model-monitoring chapters.
An author puts this on record: the book shows no code examples.

[Inference] Use this context to make definitions for observable training-service objectives and response ownership.
For example, put the allowed recovery time in place before an approved process-restart drill.
Run that drill with the actual trainer and its complete state contract.
The reviewed book evidence does not show this executable recovery procedure.
Keep the book beside DMLS for general reliability reading.
Do not put it above current framework guides for this bench.

Full chapter text and authoritative pagination keep an unresolved status.
Keep these limits in place.

Sources: [Google Research abstract](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production),
[author Q&A](https://datatalks.club/books/20221121-reliable-machine-learning.html).
Check the [source note](reliable-ml.md) and [review record](nodes/N04.md).

## N05: Cloud observability does not establish training recovery

The question checks Kyle Gallatin's cloud-design video's relevance.
Experiment tracking puts configuration, metrics, and artifacts together for one run.
[Observed] Indexed contents show training data, experiment tracking, automation, and observability.
The catalog shows production ML and real-time inference.
The review keeps the supplied date and runtime unverified.

[Inference] Use the tracking theme to keep an auditable workload record.
For example, make a step-time trace comparison only when the declared configurations show a match.
Make measurements of input waits separately from compute and collective time.
These measurements make an adaptation of the general course topics.
They do not show inspected lesson procedures.

No reviewed passage shows distributed checkpoint recovery or GPU screening.
Keep the course optional and below sources with inspected training samples.
Playback and transcripts keep an inaccessible status.

Source: [official catalog](https://www.oreilly.com/videos/designing-machine-learning/0636920953234).
Check the [source note](dmls-cloud.md) and [review record](nodes/N05.md).

## N06: Parallelism concepts do not constitute measured recovery

The question checks the parallelism course's accounting and recovery coverage.
Parallel layout makes a difference to communication, pipeline waiting, and useful training throughput.
[Observed] The researcher's catalog fetch shows data, pipeline, tensor, and hybrid parallelism.
Chapter 14 shows fault tolerance and checkpoint strategies.
The catalog shows small demonstrations, not measured rack-scale recovery.
The orchestrator's repeat fetch shows an access denial.

[Inference] Put an optional parallelism and checkpoint-design introduction in place.
For example, make a step-time comparison across two declared layouts with the same workload settings.
Show the FLOP convention separately for MFU calculations.
Use current framework documentation for checkpoint state and approved interruption drills.
The syllabus does not show successful optimizer, RNG, or data-cursor restoration.

Playback, framework versions, and recovery results keep an unverified status.
Do not use course metadata to make a universal MFU threshold.

Source: [course catalog](https://learning.oreilly.com/videos/-/9781806110896/?orm_source=mcp).
Check the [source note](llm-parallelism.md) and [review record](nodes/N06.md).

## N07: Join training metrics with data lineage

The question checks whether the 2026 platform book makes a change to selected reading priority.
Lineage makes a link between a training artifact and its data and run history.
[Observed] Chapter 9 shows PersistentVolumes, TensorBoard, MLflow, and lineage.
Chapter 11 keeps service monitoring separate from model drift monitoring.
Public samples show selected introductions and contents, not complete chapter text.

[Inference] Start with Chapters 8, 9, and 11 before older cloud-specific pipeline material.
For example, put the dataset version, configuration, step metrics, and checkpoint identity in one record.
Operators use this record to make result comparisons without context loss.
The record does not show all resume state in the checkpoint.
The samples do not show MFU, flaky-node screening, or distributed recovery.
Do not make a full-book supersession claim for MLOps Engineering at Scale.

Current framework guides keep first place for the actual recovery contract.
The samples do not make a change to this order.

Sources: [Chapter 9](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9),
[Chapter 11](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-11).
Check the [source note](ml-platform.md) and [review record](nodes/N07.md).

## N08: A training service must expose useful progress

The question checks Designing Deep Learning Systems for validation methods.
A training service keeps job execution and resources under its control.
Job status alone does not show useful training progress.
[Observed] Chapter 3 shows training-service design.
Chapter 4 shows distributed training; Chapter 5 shows hyperparameter optimization.
Manning shows the names Chi Wang and Donald Szeto.

[Inference] Put optional training-service reading in place.
For example, keep job status, rank progress, and input waits in separate records.
A running job can still show slow ranks or input starvation.
Hyperparameter optimization makes changes to training choices, not the hardware's reliability evidence.
The reviewed samples do not show complete resume state or fault-screening procedures.

Keep the supplied Kit Pang Szeto naming difference explicit.
Do not make an alias inference.

Sources: [publisher](https://www.manning.com/books/designing-deep-learning-systems),
[Chapter 4](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4).
Check the [source note](dl-systems.md) and [review record](nodes/N08.md).

## N09: Controlled experiments do not isolate hardware faults alone

The question checks the vision book's portable training-validation value.
A controlled comparison keeps the baseline fixed and makes a change to one declared variable.
[Observed] The publisher shows the title and Mohamed Elgendy as author.
A contents record shows Chapter 4 project structure and hyperparameter tuning.
The verified scope shows vision systems, not distributed pretraining reliability.

[Inference] Use this theme only for experiment records and controlled comparisons.
For example, keep one configuration while you make repeated step-time interval measurements.
Check data, model, and system evidence before fault attribution on a changed loss trace.
The reviewed contents do not show GPU screening or checkpoint-resume procedures.
Keep this title outside the main training-reliability reading sequence.
Full chapter text, the supplied year, and the page count keep an unverified status.

Sources: [publisher](https://www.manning.com/books/deep-learning-for-vision-systems),
[contents record](https://books.google.com/books/about/Deep_Learning_for_Vision_Systems.html?id=sDszEAAAQBAJ).
Check the [source note](vision-systems.md) and [review record](nodes/N09.md).

## N10: Check the product before counting evidence

The question checks the combined catalog entry's linked Video Edition.
A catalog URL shows one product.
A second title must show its own evidence.
[Observed] The supplied URL shows Machine Learning System Design, Video Edition.
The catalog shows narrated book content with figures and text.
It does not show Machine Learning Platform Engineering Video Edition.

[Inference] Keep this video as an alternate format of the Babushkin/Kravchenko book.
For example, use the public book samples to check the pipeline-testing scope.
Do not use the book and its Video Edition as independent technical corroboration.
Playback and exact content equivalence keep an unverified status.

The platform-video title check must use a separate URL.
Keep this explicit gap in the source note and final handoff.
No catalog entry shows a measured rack PASS.

Source: [video catalog](https://learning.oreilly.com/videos/-/9781633438750VE/?orm_source=mcp).
Check the [source note](system-design-video.md) and [review record](nodes/N10.md).
