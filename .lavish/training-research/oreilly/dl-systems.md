# N08 — *Designing Deep Learning Systems*

Research date: 2026-10-11. All claims below use a source URL.

Bench safety: process interruption must not start without operator approval.
Default checks do not use power removal, PCIe reset, or hardware-error injection.
Show expected checkpoint rollback and replay separately from silent duplicate or skipped progress.

Scope: independent supplement for a GB300-class, NVL72-class rack (18 trays) in Chennai; measured named workload only. Use the two-hour measurement window as input to a 30–90-day lease decision and a 54-day Llama-class run. PASS shows measured evidence, not specifications. Meta inventory: 466 total interruptions = 47 planned + 419 unexpected; use 419 as the unexpected denominator. [Llama 3, §3.3.4](https://arxiv.org/html/2407.21783v3)

Labels: [observed] = the source explicitly shows it; [calculated] = arithmetic; [inference] = application to this rack. This report makes no rack test result from a book claim.

## 1. Verified edition, chapters, access

[Observed] Manning shows the authors Chi Wang and Donald Szeto. It shows *Designing Deep Learning Systems: A software engineer’s guide* as a production-platform engineering book. Its stated scope shows dataset management, model training/serving, hyperparameter tuning, and automated training in TensorFlow and PyTorch. [Manning book page](https://www.manning.com/books/designing-deep-learning-systems)

[Observed] This research uses one supplied O’Reilly catalog URL: `https://learning.oreilly.com/library/view/-/9781633439863/?orm_source=mcp`; direct fetch makes no content available. Search results show the matching title at O’Reilly’s public catalog route [O’Reilly catalog](https://www.oreilly.com/library/view/designing-deep-learning/9781633439863). Manning’s public LiveBook, not O’Reilly, makes the retrieved primary full text for chapter verification.

[Observed] Manning LiveBook chapter pages show the relevant chapter names and contents. Chapter 3, “Model training service,” shows service design, workflow, training code patterns, and job status. Chapter 4, “Distributed training,” shows data/model/pipeline parallelism and a sample data-parallel training service. Chapter 5, “Hyperparameter optimization service,” shows HPO approaches and service design. [Ch. 3](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-3) [Ch. 4](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4) [Ch. 5](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-5)

[Observed] Chapter 4 makes its stated focus the support of distributed training from a software-engineering perspective. Researchers’ code across machines also runs under that focus. Chapter 5 shows automated hyperparameter selection as its topic. These chapters do not make evidence of fault-tolerance procedures, optimizer/RNG/data-cursor checkpoint completeness, or node-failure recovery. They do not make evidence of loss-spike triage or hardware validation. [Ch. 4](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4) [Ch. 5](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-5)

## 2. Training-run validation and reliability evidence

[Observed] The verified book material puts its focus on training-service building and training/optimization automation. Chapter 3 shows the service as responsible for compute-resource management and training-code execution. Chapter 4 shows parallelism and multiworker training challenges. Manning shows model training, dataset management, and HPO as platform capabilities. [Ch. 3](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-3) [Ch. 4](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4) [Manning overview](https://www.manning.com/books/designing-deep-learning-systems)

[Inference] Engineers can use these topics for rack-workload launch, managed-job observation, and data/training-component connection. They do not show a measured MFU method or threshold, or hardware qualification. They do not show interruption/recovery statistics or a correctness guarantee for resuming a real distributed run. Do not make a claim from “multiworker training challenges” that the book shows a fault-tolerance or checkpoint-validation protocol.

[Inference] The book shows no verified evidence here about MFU accounting, interruption-frequency measurement, flaky-node classification, loader stalls, or loss-spike diagnosis. A clean two-hour trace cannot make a 54-day reliability claim. Show only observations under the exact named workload and interval. Make untested duration and failure modes explicit.

[Inference] Automated hyperparameter optimization and training optimization do not make fault tolerance or physical hardware validation. HPO makes a search over model/training choices. A training service puts jobs and resources under management.

The full state set: model weights, optimizer state, RNG streams, scheduler state, sampler/data position, and distributed metadata.

Neither one alone shows a complete or correct restore of that state set. The chapter abstracts and Manning overview show support for the first distinction only. They do not make the book a source for the second. [Ch. 3](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-3) [Ch. 5](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-5)

## 3. Portable techniques and measured checks

These [inference] proposals make applications of the book’s service-oriented framing. They do not make quoted book procedures or universal GB300 gates.

1. **Put a name on the workload and keep it fixed.** Make a record of model/code and data versions, precision, sequence length, batch, parallelism, optimizer, framework, and launch configuration. [Manning](https://www.manning.com/books/designing-deep-learning-systems) [Measured check] Run that exact job across the intended 18 trays. Show interval, warm-up exclusion, tokens/s, step-time distribution, and the declared MFU formula. Make comparisons only with a tenant-approved target or baseline, not a vendor peak.

2. **Check the whole training service path.** Chapter 3 shows training as managed compute plus execution; Chapter 4 shows distributed execution. [Measured check] Check per-rank step times, collectives, GPU telemetry, dataloader wait, and storage-read stalls during the named workload. Show observed slow ranks and stall intervals. Do not make a node faulty from one symptom. [Ch. 3](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-3) [Ch. 4](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4)

3. **Run a real interruption and restore.** The verified chapter contents do not show checkpoint semantics; this item makes an acceptance-test proposal, not book-derived functionality. [Ch. 3](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-3) [Measured check] Put the tenant’s representative job through a save, a termination, and a resume. Check expected step and data position, model/optimizer/scheduler state, and relevant RNG/sampler state against the declared contract. Show save/load time, lost work, replay/skip behavior, and the integrity result. Do not make a complete-correctness claim without an exercised production state contract.

4. **Check anomalies with multiple signals.** HPO does not make fault diagnosis. [Measured check] Keep step-level loss and gradient summaries with rank timing, device/error telemetry, input wait, and checkpoint events. Start an investigation of a spike or stall from the correlated signals. A normal short loss trace does not remove the possibility of silent corruption or later failures. [Ch. 5](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-5)

5. **Show interruption evidence as sampled exposure.** [Measured check] Show counts of observed job interruptions, restart outcomes, and affected ranks during the actual measurement interval. Keep observed events separate from injected drills. A zero-event count in two hours shows “none observed in this interval,” not a long-run failure-rate estimate or assurance for 54 days.

[Calculated] 54 days = 1,296 hours, 648 two-hour windows. Keep the ratio as exposure arithmetic, not a reliability estimate.

## 4. Canon relation and candidate

[Observed] Canon N07 already keeps books as systems-framing sources. It puts current operational documentation and reliability evidence above books for distributed training failure engineering. It shows *Designing Machine Learning Systems* (DMLS), *Reliable Machine Learning*, and *AI Engineering* as separate titles. N08 makes a separate title: *Designing Deep Learning Systems*, by Chi Wang and Donald Szeto. [Canon: N07](../books.md)

[Inference] Put N08 in the canon as a distinct, lower-priority platform-engineering supplement. Do not use it as another reliability handbook or as the previously listed DMLS by Chip Huyen. Its verified service/parallelism/HPO topics make a complement to broad systems framing. It does not remove N07’s gaps on hardware screening, checkpoint/restart correctness, flaky-node evidence, MFU accounting, or multiweek reliability.

[Observed] The Manning public page puts a “Look inside” link to the LiveBook. The supplied O’Reilly access URL does not make its content available to direct fetches. This pass shows no verified chapter-level O’Reilly text. [Manning LiveBook](https://livebook.manning.com/book/designing-deep-learning-systems) [O’Reilly supplied URL](https://learning.oreilly.com/library/view/-/9781633439863/?orm_source=mcp)

## Gaps

- The supplied O’Reilly learning URL does not make its content available to direct fetches. Public Manning and O’Reilly catalog results show corroboration for edition/author/title. Manning LiveBook shows the chapter details. The research does not independently show exact O’Reilly edition metadata or full text.

- Verified public chapter material does not show checkpoint/resume correctness, optimizer/RNG/data-state completeness, or interruption statistics. It does not show loss-spike diagnosis, flaky-node screening, or loader-stall measurement.

- No two-hour measurement can show 30–90-day or 54-day reliability. Rack/workload-specific thresholds and confidence claims must use tenant targets, measured evidence, and appropriately long exposure.

- No reviewed source shows a universal GB300/NVL72 acceptance gate. Use workload-specific measured checks, not specifications or book descriptions.
