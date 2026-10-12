# N04 — *Reliable Machine Learning*

Research date: 2026-10-11. All claims below use a source URL.

Bench safety: process interruption must not start without operator approval.
Default checks do not use power removal, PCIe reset, or hardware-error injection.
Show expected checkpoint rollback and replay separately from silent duplicate or skipped progress.

Rack context: a GB300-class, NVL72-class, 18-tray Chennai rack. The bench runs the measured testing window for roughly two hours. It runs before a 30–90-day lease / 54-day Llama-class training run. A PASS must show measured evidence for a named workload, not vendor-only claims. Labels: [observed], [calculated], [inference].

## 1. Verified edition, authors, contents, and access

[Observed] The supplied O’Reilly Learning URL fetch shows HTTP 403. O’Reilly’s public catalog page and chapter pages also show HTTP 403 in a direct fetch. Search-indexed O’Reilly catalog material shows the title and contents headings. The record shows the material as publisher-origin content. This session cannot check the full book text. [Supplied Learning URL](https://learning.oreilly.com/library/view/-/9781098106218/?orm_source=mcp) · [O’Reilly catalog](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218)

[Observed] The record shows the title *Reliable Machine Learning: Applying SRE Principles to ML in Production*. The record shows the authors: Cathy Chen, Niall Richard Murphy, Kranti Parisa, D. Sculley, and Todd Underwood.

The supplied catalog shows ISBN 9781098106218 and 408 pages. Search-indexed O’Reilly catalog metadata, not a directly accessible page, shows 466 pages. Google Books metadata shows publication in 2021 and 410 pages. Keep these as conflicting records, not a verified distinction between formats or editions.

The review keeps high confidence that the records show a discrepancy. The review keeps low confidence on the authoritative pagination/date for the supplied catalog record. [Inference] Keep a different format or edition as a possible explanation, not an established finding. [Supplied Learning URL](https://learning.oreilly.com/library/view/-/9781098106218/?orm_source=mcp) · [O’Reilly catalog](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218) · [Google Books record](https://books.google.com/books/about/Reliable_Machine_Learning.html?id=c4iKEAAAQBAJ)

[Observed] Official O’Reilly indexed headings show these chapters: “Feature and Training Data” (Chapter 4), “Fairness, Privacy, and Ethical ML Systems” (Chapter 6), “Monitoring and Observability for Models” (Chapter 9). They also show organizational/case-study material through Chapter 15. The index shows Chapter 9 subtopics, including “What Is Production Monitoring and Why Do It?” [O’Reilly Chapter 4](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch04.html) · [O’Reilly Chapter 9](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch09.html) · [O’Reilly index](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ix01.html)

[Observed] A Google Research publication page for the book’s Chapter 1B, “Data Management Principles,” shows an abstract. The abstract makes this framing: data management, SRE practices, SLOs/SLIs, monitoring, and reliable production ML. Keep it as a chapter abstract, not evidence of details in the full chapter. [Google Research](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production)

[Observed] An author Q&A shows this focus for the book: the “whole system,” organizational/ethical/technical aspects, productionization and monitoring, not model creation. The Q&A shows no code examples in the book and a framework-agnostic aim. Keep this as useful corroboration. Put publisher contents first. [DataTalks.Club author Q&A](https://datatalks.club/books/20221121-reliable-machine-learning.html)

## 2. Training-run validation and reliability evidence

[Observed] The verified material shows broad reliability framing, data management, production monitoring/observability, and organizational practice. Chapter 4’s surfaced description shows infrastructure for data acceptance and preparation for the training system. Chapter 9 explicitly shows production-model monitoring and observability. [Chapter 4](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch04.html) · [Chapter 9](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/ch09.html)

[Observed] The accessible catalog headings and abstract do not show book guidance for MFU accounting or distributed GPU training telemetry. They do not show guidance for checkpoint save/load/resume, optimizer/RNG/sampler/data-position recovery, restart correctness, or loss-spike triage during pretraining. They do not show flaky GPU screening or GPU-side dataloader stalls. Do not use the book’s verified “training data” topic as proof of device-level data-stall diagnosis. The record shows no specific procedure, threshold, or executable rack test.

[Inference] Use the book for the acceptance case’s system-level monitoring and data-management concepts. Its available evidence does not make it an operational guide for the certification of a multi-node LLM training rack. The reviewed sources do not show a checkpoint drill, an MFU method, or a GB300/NVL72 reliability gate. Keep it as useful context, not a measured pass standard.

## 3. Portable bench techniques (inferences/proposals, not book procedures)

These proposals make measurable evidence from the verified high-level themes. The proposals do not use the book as their source. They make no universal pass thresholds.

1. **Put the workload name and its measured performance in the report.** [Inference] For an agreed training configuration, keep these in the record: model/workload identity, software and config versions, and measurement interval. Keep warm-up treatment, tokens or steps per second, and step-time distribution there. Put the declared MFU convention there when the report shows MFU. **Check:** actual measurements and per-rank spread against a tenant-approved reference/envelope. Do not make vendor peak a PASS.

2. **Make input-path wait measurements separately.** [Inference] Use instrumentation for separate training compute/collective time and input wait or data-loading time. **Check:** the observed wait-time distribution and throughput during the named workload, with instrumentation and interval in the record. A short sample does not show long-run storage behavior.

3. **Check the actual recovery contract when the tenant can use the harness.** [Inference] Make the contract explicit: the state and data position that the restart must keep. Run a controlled save/restore/restart on the representative job. Check the resumed step, optimizer/training state, RNG, and consumed-data position against the contract. **Check:** checkpoint integrity, save/load/resume duration, lost work, and any duplicate/skipped data in the record. Do not use a weights-only load as a training-resume test.

4. **Check anomalies together; do not use loss as the sole health verdict.** [Inference] For a loss spike, keep aligned loss/step, gradient or training telemetry, rank/node health, and input/collective timings for triage. **Check:** the anomaly occurrence and the examined evidence in the report. A normal short loss trace does not show the absence of silent corruption or future faults.

5. **Check for immediate weak nodes under exercised load.** [Inference] Keep node/rank-level throughput and available health/error telemetry during the named run. Put a flag on persistent outliers for investigation. **Check:** the observed interval, signals, and follow-up disposition in the record. Do not make a two-hour clean sample into a multi-week failure-rate estimate. Do not run destructive fault injection by default.

[Calculated] A two-hour sample makes 1/648 of 54 days (54×24÷2). Keep the exposure ratio as arithmetic, not a reliability forecast. It makes no defensible 30–90-day failure probability without representative longer exposure and an explicit statistical model.

## 4. Canon relation and headline decision

[Observed] The existing canon notes show *Reliable Machine Learning* tied with *Designing Machine Learning Systems* as a broad systems/monitoring book. The canon keeps claims to visible contents because the catalog shows an access barrier. This pass independently checks the access barrier. It makes the evidence stronger for the data-management, monitoring/observability, and whole-system framing of the book. It uses these sources: official chapter/index search results, a Google Research chapter abstract, and author Q&A. It does not show full text or rack-scale pretraining reliability methods. [Canon](../books.md) · [Google Research chapter abstract](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production) · [Author Q&A](https://datatalks.club/books/20221121-reliable-machine-learning.html)

[Inference] Keep the book tied with DMLS as a broad conceptual canon. This book makes the stronger source for SRE/monitoring and organization-level reliability framing. Do not put it as the headline operational source for this bench. Verified evidence does not show the decisive training-run checks: MFU accounting, checkpoint/resume correctness, loss triage, flaky-node screening, or datastalls. Keep it as useful context, not a measured pass standard.

## Gaps

- Direct fetches of the supplied Learning URL, catalog, and chapter pages show HTTP 403. The researcher cannot check full text and detailed passages.

- Contents headings and an abstract do not show the depth, examples, or actual prescriptions in the relevant chapters.

- No verified passage shows training-scale MFU, optimizer/RNG/data-position recovery correctness, pretraining loss-spike diagnosis, GPU flaky-node screening, or device-level datastall measurement.

- Pagination/date records show discrepancies. The supplied catalog shows 408 pages; search-indexed O’Reilly metadata shows 466 pages. Google Books shows 410 pages and 2021, while O’Reilly indexed metadata shows 2022. Direct publisher fetches show a barrier, so the review keeps 466 pages and the edition/date reconciliation unverified. Keep a differing-format/edition explanation as [inference], not an established fact.

- No source here shows a universal two-hour pass threshold or a 30–90-day reliability forecast for this rack and workload.
