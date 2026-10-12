# Designing Machine Learning Systems — independent supplement (N01)

Research date: 2026-10-11. All claims below use a source URL.

Bench safety: process interruption must not start without operator approval.
Default checks do not use power removal, PCIe reset, or hardware-error injection.
Show expected checkpoint rollback and replay separately from silent duplicate or skipped progress.

## 1. Verified identity, edition, chapters, and access coverage

[observed] The supplied O’Reilly Learning catalog page shows *Designing Machine Learning Systems* by Chip Huyen. The record shows these data: O’Reilly Media, May 2022, 386 pages, ISBN 9781098107956. The catalog shows the level as intermediate to advanced. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

[observed] The catalog shows the full chapter contents. The catalog shows Chapter 2: “Introduction to Machine Learning Systems Design”. It shows “Requirements for ML Systems” and reliability/scalability/maintainability/adaptability. The catalog shows Chapter 3: “Data Engineering Fundamentals”. The catalog shows Chapter 4: “Training Data”.

Chapter 6 “Model Development and Offline Evaluation” shows “Model Development and Training,” “Distributed Training,” “Experiment Tracking and Versioning,” and “Debugging ML Models.” Chapter 8, “Data Distribution Shifts and Monitoring,” shows failure causes, monitoring and observability. Chapter 9 shows continual learning.

Chapter 10, “Infrastructure and Tooling for MLOps,” shows storage/compute, resource management, schedulers/orchestrators and workflow management. The review keeps these as verified headings, not assertions about unviewed detailed chapter text. [O’Reilly contents](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

[observed] The supplied catalog URL fetch runs successfully. It shows the metadata, contents, overview, and an access prompt (“Read now Unlock full access”). The canonical O’Reilly publisher page and Chapter 6 fetches show HTTP 403 in this research session. Researchers can check the public catalog/TOC; they cannot independently check full chapter prose and detailed procedures.

The publisher shows the book as a “holistic approach” to ML systems. The overview shows these topics: creating training data, continual development/evaluation/deployment, monitoring, and ML platforms. The review keeps these as publisher overview claims, not evidence of rack-acceptance recipes. [Catalog](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp) [Canonical publisher page, access denied](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956) [Chapter 6 fetch, access denied](https://learning.oreilly.com/library/view/designing-machine-learning/9781098107956/ch06.html)

## 2. Training-run and reliability coverage: what sources establish

[observed] Chapter 6 explicitly shows “Distributed Training,” “Debugging ML Models,” and “Experiment Tracking and Versioning.” This shows topical coverage for training and diagnosis. The accessible headings do not show methods for MFU measurement, interruption accounting, or flaky GPU screening. They do not show full distributed checkpoint recovery validation. [O’Reilly Chapter 6 contents](https://learning.oreilly.com/library/view/-/9781098107956/ch06.html)

[observed] Chapter 2 explicitly shows “Requirements for ML Systems” and “Reliability”. Chapter 8 shows “Causes of ML System Failures,” “Monitoring and Observability,” “ML-Specific Metrics,” and “Monitoring Toolbox.” The publisher overview shows monitoring with this aim: “quickly detect and address issues” in production. Keep this as requirements/monitoring framing. It does not show a specific training-run fault model or hardware qualification protocol. [O’Reilly contents](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

[observed] Chapter 3 and Chapter 4 show data engineering and training data. Chapter 10 shows “Storage and Compute,” “Resource Management,” schedulers/orchestrators and workflow management. Their headings show system components in scope. They do not show dataloader-stall diagnosis, input wait instrumentation, checkpoint serialization semantics, optimizer/RNG/sampler restoration, or resume correctness. [O’Reilly contents](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

[calculated] A supplied rack reliability anchor shows 466 total interruptions: 47 planned and 419 unexpected. For hardware-failure attribution, use the denominator of 419 unexpected interruptions, not all 466. [Llama 3, §3.3.4](https://arxiv.org/html/2407.21783v3)

[inference] The visible headings and accessible overview do not show these in DMLS: the interruption accounting and specific checkpoint-state requirements. They also show no loss-spike triage, flaky-node tests, or data-loader instrumentation. Keep such claims out of DMLS citations. A two-hour acceptance window can make a record of observed behavior under a named Llama-class workload. It cannot show long-run reliability over a 30–90-day lease or a 54-day run. [Rack-bench canon](../books.md) [O’Reilly contents](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

## 3. Portable bench-training techniques

These proposals use the book’s verified headings. They do not use quotations or procedures from the inaccessible full text. A PASS must show measured evidence for a named workload. The bench uses the one GB300-class NVL72-class rack (18 trays) in Chennai. No vendor specification makes a pass.

1. **[inference/proposal] Make the measurement contract before the run.** Chapter 2’s “Requirements” and Chapter 6’s “Distributed Training” show the source theme. Use them to show the exact model/workload, software/configuration, precision, sequence length, batch, and parallelism. Also put the warm-up exclusion, measurement interval, and throughput/MFU accounting convention in the contract. Check results only against a declared tenant target/reference; the book does not show a universal GB300 threshold. **Evidence:** saved config/version identifiers, timed per-step samples, the explicit accounting formula, and measured tokens/s and step-time distribution. [Source basis: Ch. 2 and Ch. 6 headings](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

2. **[inference/proposal] Use explicit interruption classes and denominators.** Use Chapter 2’s reliability framing to keep planned and unexpected events separate in the report. Show the denominator for each rate or attribution. For hardware attribution, use unexpected interruptions only; the canon anchor uses 419, not the total 466. **Evidence:** an event ledger with timestamps, classification rationale, affected components, lost steps, and recovery outcome. Put counts and exposure in the report; do not make a lease-long rate estimate from two hours. [Source basis: Ch. 2 headings](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp) [Llama 3 interruption anchor](https://arxiv.org/html/2407.21783v3)

3. **[inference/proposal] Make recovery correctness a state-equivalence drill, not a “checkpoint written” assertion.** Chapter 6’s training/versioning headings and Chapter 10’s infrastructure/workflow headings make the source basis. Run the drill on the actual training harness with a controlled test job. Keep model, optimizer, step/data position, and relevant RNG/sampler state in the save and restore scope. Check the resumed step and next-batch/progression against the defined contract. **Evidence:** checkpoint integrity, completed save/load timings, resumed step, data position, and a documented state comparison.

   Keep this detailed state checklist as a proposal, not verified DMLS text. [Source basis: Ch. 6 and Ch. 10 headings](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

4. **[inference/proposal] Check loss anomalies with corroborating signals.** Chapter 6 “Debugging ML Models” and Chapter 8 monitoring/observability show the source theme. Keep loss in the record beside gradients and system events. Check the combination before a health verdict. Do not make loss the sole proof of health. **Evidence:** timestamped loss/gradient/step metrics correlated with rank timing, hardware/error telemetry, and data position; keep investigated and unresolved spikes annotated. [Source basis: Ch. 6 and Ch. 8 headings](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

5. **[inference/proposal] Make input-path waiting and rank variance measurable.** Chapter 3 data engineering and Chapter 10 storage/compute/resource-management headings show the source theme. Use them for loader-wait and per-rank step-time measurements under the real workload. **Evidence:** per-rank step-time distributions, input-wait duration, delivered samples/tokens, and recorded stalls/errors during the stated interval. Do not make absent stalls into long-run reliability proof. Do not use destructive default fault injection. [Source basis: Ch. 3 and Ch. 10 headings](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

## 4. Relation to existing books.md canon

[observed] The existing canon already shows DMLS in its list. It puts DMLS beside *Reliable Machine Learning*, below current Megatron/PyTorch documentation and reliability papers. It shows DMLS Chapters 6, 8 and 10 as relevant framing. [Existing canon](../books.md)

[observed] This supplement checks identity and pagination directly on the supplied O’Reilly page (May 2022, 386 pages). It checks exact chapter headings, including Chapter 6 “Distributed Training” and “Debugging ML Models,” Chapter 8 monitoring, and Chapter 10 infrastructure/resource management. These facts do not make a ranking change necessary. Visible contents show broad systems framing, not rack-level reliability operations. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

[changed] Make canon descriptions precise where needed: The catalog shows Chapter 8: “Data Distribution Shifts and Monitoring”, not simply “monitoring/data-shift”. The catalog shows Chapter 10’s visible relevant headings: “Storage and Compute” and “Resource Management”. The exact listed headings do not show checkpoint/restart. [O’Reilly contents](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp)

[observed] The Llama 3 paper shows 466 total = 47 planned + 419 unexpected interruptions. Hardware attribution uses the unexpected denominator (419). Keep these counts as contextual input, not findings from DMLS. [Llama 3, §3.3.4](https://arxiv.org/html/2407.21783v3)

## Gaps

- This session cannot check full Chapter 6 and other chapter prose. The canonical publisher and chapter fetches show HTTP 403. Depth findings therefore use official visible contents and overview only. No verified DMLS passage shows MFU accounting, interruptions, checkpoint/resume, optimizer/RNG/data restoration, loss-spike triage, flaky-node screening, or loader stalls. [Publisher chapter page](https://learning.oreilly.com/library/view/designing-machine-learning/9781098107956/ch06.html)

- The public contents cannot show the full book. The full book can use a detailed technique under a different heading. Only an authenticated full-text check can show that.

- The book’s verified scope shows no measured PASS threshold for this rack. It shows no basis for a two-hour-test extrapolation to 30–90-day / 54-day reliability. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9781098107956/?orm_source=mcp) [Rack-bench canon](../books.md)
