# N17 — André Bondi, *Foundations of Software and System Performance Engineering*

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Catalog access and identification

[observed] The requested O’Reilly catalog URL returns HTTP 403 Forbidden.
This shows an access limit only.
No one attempts to bypass authentication. [O’Reilly requested record](https://learning.oreilly.com/library/view/-/9780133038149/?orm_source=mcp)

[observed] O’Reilly’s public title record names this title:
*Foundations of Software and System Performance Engineering: Process, Performance Modeling, Requirements, Testing, Scalability, and Practice*.
The record names André Bondi as author.
The catalog fetch cannot access the linked TOC route. [O’Reilly public catalog](https://www.oreilly.com/library/view/foundations-of-software/9780133038149)

[observed] Pearson’s public TOC names the same title and author context.
It lists 15 chapters.
Its product-specific TOC filename lists ISBN-13 9780133038163.
This differs from the requested O’Reilly ISBN-13 9780133038149. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf)
The supplied catalog metadata says Addison-Wesley, 448 pages, 2014.
No successfully fetched publisher product record independently verifies these details. [O’Reilly public catalog](https://www.oreilly.com/library/view/foundations-of-software/9780133038149)

## 2. Pearson TOC: all numbered chapters

[observed] The fetched Pearson TOC lists these 15 numbered chapter titles. The list uses the TOC wording:

1. Why Performance Engineering?
2. Performance Metrics
3. Basic Performance Analysis

4. Workload Identification and Characterization
5. From Workloads to Business Aspects of Performance Requirements
6. Qualitative and Quantitative Types of Performance Requirements
7. Eliciting, Writing, and Managing Performance Requirements

8. System Measurement Techniques and Instrumentation
9. Performance Testing
10. System Understanding, Model Choice, and Validation

11. Scalability and Performance
12. Performance Engineering Pitfalls
13. Agile Processes and Performance Engineering
14. Working with Stakeholders to Learn, Influence, and Tell the Performance Engineering Story
15. Where to Learn More

[Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf)

[observed] Relevant subtopics include performance laws, queues, model limitations, test planning, and measurement procedures.
They also include pilot testing, instrumentation validation, stability, data collection, and result interpretation.
The TOC covers general software/system performance engineering.
It is not a GPU diagnostic manual.
It does not identify GB300, ECC/XID, HBM, NVLink, row remapping, SDC, or GPU-specific acceptance thresholds. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf)

## 3. Portable techniques for the two-hour GPU bench

1. **[inference] Declare measurable outcomes and coverage before running.**
   Chapter 2 covers metric properties.
   Chapter 9 links test plans with requirements.
   These topics suggest that you set per-GPU measures and check outcomes in advance.
   Include correctness result, measured throughput, sampled power/clocks/thermals, and RAS/link-counter deltas.

   Mechanism: this keeps a performance number from standing in for health or correctness.
   Proposed value: clear evidence and explicit PASS/FAIL/SKIP.
   Limit: the book gives no GB300 limits.
   No universal threshold or SDC-free guarantee follows from the book. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf) [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)

2. **[inference] Characterize a repeatable workload, not just a benchmark name.**
   Chapters 4 and 9 cover workload characterization and test preparation.
   Set kernel/precision, input and working-set sizes, duration, concurrency, warm-up, and expected output.
   Keep these fixed across comparable GPUs.

   Mechanism: this makes measured throughput interpretable.
   It also shows the resource that the workload actually exercises.
   Proposed value: repeatable compute and HBM observations within the two-hour window.
   Limit: workload coverage is finite.
   A test does not cover every instruction, address, or rare fault. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf) [NVIDIA CUDA Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/)

3. **[inference] Validate instrumentation and test equipment; pilot before the timed run.**
   Chapter 8 explicitly covers measurement validation and procedures.
   Chapter 9 names pilot testing, test automation, and testing the equipment/software.

   Mechanism: check identity mapping, timing, counter availability, output/reference checks, and harness behavior.
   Do these checks on a representative GPU.
   Then apply the plan to all 72.
   Proposed value: fewer false PASS results and reasoned skips for unsupported metrics.
   Limit: a successful pilot does not show support or identical behavior on every SKU/driver/plugin combination. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf) [NVIDIA `nvidia-smi` guide](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

4. **[inference] Preserve time windows, distributions, and before/after evidence.**
   Chapters 8 and 9 discuss averaging windows, data organization, reduction, and interpretation.
   Record timestamped telemetry during load.
   Also record pre/post ECC, remap, XID, and per-GPU NVLink health snapshots.
   Keep raw values and tool versions.

   Mechanism: this links performance to thermal/power state.
   It also separates new counter deltas from historical totals.
   Proposed value: diagnosis beyond a single instantaneous reading.
   Limit: sampling can miss short transients.
   Instrumentation may be unavailable or may perturb the run. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf) [NVIDIA `nvidia-smi` guide](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

5. **[inference] Treat peer comparisons and simple models as bounded evidence.**
   Chapters 3 and 10 cover performance laws, model applicability, and validation.
   Chapter 12 covers measurement pitfalls.
   Collect and report valid measurements even when no approved SKU/profile acceptance threshold exists.
   Use homogeneous-peer comparisons as an outlier screen.
   Mark only the absolute quality grade SKIP while an approved profile is pending.

   Do not skip measurements.
   Mechanism: performance laws and model checks can show implausible values or outliers.
   They do not claim to give a product limit.
   Proposed value: useful measured evidence now, with an explicit boundary on grading.
   Limit: a rack-wide slowdown can affect every peer equally.
   Simple models cannot show GPU correctness or rule out SDC. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf) [accepted GPU research](../books.md)

## 4. Relation to accepted sources and recommendation

[observed] The local accepted research uses Gregg’s performance methodology as current methodological grounding.
It uses NVIDIA guides as operational authority.
It uses PMPP 4e as architecture context. [Accepted N07](../nodes/N07.md)

[inference] Bondi is an optional general-method supplement.
It is not a GPU diagnostic source.
It does not replace Gregg, current NVIDIA operational guides, or PMPP.
For this bench, its strongest added value is explicit performance requirements and workload characterization.
It also adds measurement validation, test planning, and interpretation limits.
These topics overlap and confirm Gregg’s controlled-measurement discipline.

Bondi’s system lifecycle and requirements framing complements that discipline.
It does not supersede a GB300 procedure. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf) [Gregg, Systems Performance 2e](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)

## Gaps

[observed] O’Reilly’s requested record denies access (403).
No one accesses authenticated content.
Search gives no successful InformIT/Pearson product record or author catalog for the requested ISBN.
Thus no source confirms that ISBN’s complete metadata.
Pearson’s public TOC gives chapter coverage.
That TOC uses ISBN 9780133038163, not the O’Reilly record’s 9780133038149. [O’Reilly requested record](https://learning.oreilly.com/library/view/-/9780133038149/?orm_source=mcp) [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf)

[observed] The TOC supports chapter-level topic claims only.
The techniques above are inferences from chapter titles/subtopics.
They do not claim that the book prescribes GPU-specific procedures.

No source verifies the exact edition, publication year, page count, or ISBN-10/format mapping.
The TOC does not confirm the supplied catalog metadata.
The TOC shows chapter titles, not GPU-specific relevance. [Pearson TOC PDF](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf)
