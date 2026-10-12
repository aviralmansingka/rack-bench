# O'Reilly supplement for GPU quality research

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Scope and evidence rules

This supplement checks ten catalog sources. It does not repeat the seven category studies.
The target has 18 trays and 72 physical GB300-class GPUs in Chennai.
The category window is two hours. PASS requires measurement. PASS also requires an applicable declared acceptance rule.

Keep failures as data. Give every skip a reason.
Keep collection status separate from quality assessment.
[Scope and map](research.md) · [Accepted books brief](books.md).

The scope includes ECC, XIDs, row remaps, SDC, HBM, thermals, power, clocks, and correctness.
Keep per-GPU NVLink health. Exclude east-west and collective performance.
Preserve configuration. Do not reset GPUs or clear counters.

Do not change ECC, MIG, clocks, power limits, firmware, or host configuration.
Active workloads require exclusive allocation and approved power/cooling policy.
Active workloads are not passive collection.
[Safety and checks](docs/gpu-bench-research.md).

`[observed]` means a source statement or an access result, not a target-rack measurement.
`[inference]` means a proposed use of that evidence.
The captain supplies the initial catalog metadata through its catalog-only search.
Each child first checks the supplied O'Reilly URL.
After access fails, the children use public publisher, author, contents, and companion sources.
The notes identify supplied metadata that lacks independent confirmation.

A table of contents does not prove a complete chapter procedure.
An ISBN difference does not prove an edition change.
ISBN-10 and ISBN-13 forms can refer to the same product.
[Source notes](oreilly/README.md) · [Evidence checks](oreilly/evidence-review.md).

## 2. Decision summary

[inference] Keep Gregg 2e for general measurement methods.
Keep matched NVIDIA guides for RAS, command semantics, and platform support.
Add Fregly's public companion as a practical GPU measurement reference for test authors.
Keep PMPP 4e for kernel architecture. This pass does not verify a later edition.
The other books give optional methods or incomplete catalog evidence.
[Gregg 2e](oreilly/gregg2.md) · [Fregly](oreilly/fregly.md) · [PMPP](oreilly/pmpp.md) · [NVIDIA roles](books.md).

| Node | Source | Relationship | Decision and limits |
| --- | --- | --- | --- |
| N08 | Cook, CUDA Programming | New optional reference; confirms CUDA role | Public TOC supports workload topics. It does not support GB300 diagnosis. |
| N09 | Gregg, Systems Performance 2e | Confirms existing reference | Keep the methodology. Keep publication and copyright dates separate. |
| N10 | Motta, C++ and CUDA | Potential new reference; no verified change | Metadata and TOC remain largely unverified. |
| N11 | Professional CUDA C Programming | New optional examples; confirms CUDA role | Public examples show topics. The complete TOC remains unverified. |
| N12 | CUDA by Example | New optional reference; confirms CUDA role | Use the correct print page count. Keep old-code limits. |
| N13 | Fregly, AI Systems Performance Engineering | New practical measurement reference | Use companion methods. Do not use configuration changes or RAS limits. |
| N14 | Python and CUDA | New optional reference; confirms CUDA role | Historical dependencies limit reuse. Incomplete TOC evidence also limits reuse. |
| N15 | PMPP editions | Confirms 4e; corrects old identifier | The sources show no verified later-edition change. Older metadata has gaps. |
| N16 | Gregg, Systems Performance 1e | Confirms methods; 2e replaces preferred reading | Do not require both editions. |
| N17 | Bondi, Performance Engineering | New optional methods; confirms measurement discipline | Public TOC supports requirements and pilot methods. Edition metadata has gaps. |

The source sections below give the evidence for these decisions.

## 3. N08 — Shane Cook, CUDA Programming

[observed] Elsevier lists twelve chapters for this title.
The supplied catalog record gives Morgan Kaufmann, 2012, 600 pages, and identifier 9780124159334.
The source note records publisher identity and conflicting date/page fields.
[Publisher TOC](https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4) · [Complete note](oreilly/cook.md).

[observed] Relevant chapters include 4, error handling; 6, memory; and 7, profiling.
Chapters 9 and 11–12 cover optimization, systems, and problems.
[Publisher TOC](https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4).

[inference] Portable techniques:
1. Check CUDA errors and completed output against an independent reference.
2. Measure compute and memory workloads separately; record bytes and operations.
3. Keep warmup separate from timing; record repeated results and thermal/power context.
4. Record workload concurrency and resource contention per physical GPU.
These proposals use TOC topics. They do not use verified chapter procedures.
[Complete note and limits](oreilly/cook.md).

[inference] Add optional CUDA implementation reading. Do not replace Gregg, PMPP, or current NVIDIA guides.
[Source assessment](oreilly/cook.md).

## 4. N09 — Brendan Gregg, Systems Performance, 2nd Edition

[observed] InformIT lists second edition, 928 pages, eBook ISBN 9780136821649, and copyright 2021.
The author identifies the edition as 2020. The note keeps publication and copyright separate.
The supplied O'Reilly identifier is 9780136821694; its exact format remains unverified.
[Publisher](https://www.informit.com/store/systems-performance-9780136821649) · [Author](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) · [Complete note](oreilly/gregg2.md).

[observed] Read chapters 2, Methodologies; 4, Observability Tools; 7, Memory; and 12, Benchmarking.
The public TOC lists sixteen chapters. The publisher sample covers chapter 3.
[Publisher TOC](https://www.informit.com/store/systems-performance-9780136821649).

[inference] Portable techniques:
1. Declare inputs, precision, workload, duration, and comparison conditions before measurement.
2. Collect before/after counters with timestamps; preserve lifetime totals separately.
3. Check utilization, saturation, and errors per GPU. Do not check utilization alone.
4. Keep per-GPU distributions; peer agreement can miss a rack-wide problem.
[Complete note](oreilly/gregg2.md) · [USE method](https://www.brendangregg.com/usemethod.html).

[inference] Confirm the existing method reference. No edition change is necessary.
[Accepted books brief](books.md) · [Source assessment](oreilly/gregg2.md).

## 5. N10 — Paulo Motta, GPU Programming with C++ and CUDA

[observed] The supplied catalog metadata gives Packt, August 2025, 270 pages, and identifier 9781805124542.
O'Reilly denies access. Packt presents security verification. Search returns rate-limit errors.
The note does not verify edition, ISBN format, complete TOC, or chapter procedures.
[Requested catalog](https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp) · [Complete note](oreilly/motta.md).

[inference] Do not assign chapter numbers without a verified TOC.
Three possible techniques require current NVIDIA evidence, not attribution to this book:
1. Check deterministic arithmetic against an independent reference.
2. Test declared memory patterns; report checked bytes and mismatches.
3. Measure bounded workloads with thermal, power, clock, and error telemetry.
These are generic proposals. This source does not establish them as its teachings.
[Complete note](oreilly/motta.md) · [CUDA guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/).

[inference] Keep this source pending for optional CUDA learning. Do not change required reading.
[Source assessment](oreilly/motta.md).

## 6. N11 — Professional CUDA C Programming

[observed] Wiley names John Cheng, Max Grossman, and Ty McKercher.
Its public description covers execution, memory, streams, events, concurrency, profiling, and performance tuning.
The supplied catalog gives 2014, 528 pages, and identifier 9781118739310.
The fetched Wiley text does not independently confirm those fields or a numbered TOC.
[Wiley](https://www.wiley.com/en-us/Professional+CUDA+C+Programming-p-9781118739327) · [Complete note](oreilly/cheng.md).

[observed] The companion has ten chapter example directories.
Chapter 7 filenames include floating-point accuracy, performance, FMA, and atomic-ordering examples.
Chapter 6 filenames include asynchronous API examples.
Directory numbers are not verified chapter titles.
[Companion](https://github.com/deeperlearning/professional-cuda-c-programming) · [Complete note](oreilly/cheng.md).

[inference] Portable techniques:
1. Record the numerical comparison contract separately from measured throughput.
2. Check a declared memory working set and report bytes, duration, and errors.
3. Make stream ordering and synchronization explicit during timing.
4. Compare workload rates with concurrent telemetry and a declared profile.
[Complete note](oreilly/cheng.md).

[inference] Add optional implementation examples. Keep current CUDA and NVIDIA RAS references above them.
[Source assessment](oreilly/cheng.md).

## 7. N12 — Sanders and Kandrot, CUDA by Example

[observed] InformIT lists first edition, 320 print pages, and print ISBN 9780131387683.
Its copyright field gives 2011; the source note records July 2010 publication.
The supplied catalog gives 312 pages and identifier 9780132180160. Its format relationship remains unverified.
[Publisher](https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683) · [Complete note](oreilly/example.md).

[observed] The twelve-chapter TOC includes 5, Thread Cooperation, and 6, Constant Memory and Events.
Chapters 9 and 10 cover Atomics and Streams.
Chapter 6 includes Measuring Performance with Events.
[Publisher TOC](https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683).

[inference] Portable techniques:
1. Measure a warmed workload with CUDA events on the measured stream.
2. Check a bounded integer atomic-update workload against known output.
3. Check cooperative kernels with an independent reference and explicit synchronization.
4. Measure a declared memory working set; do not call a cache-sized result HBM bandwidth.
[Complete note](oreilly/example.md).

[inference] Add optional introductory reading. Review old APIs against current CUDA documentation before reuse.
[Source assessment](oreilly/example.md) · [CUDA guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/).

## 8. N13 — Chris Fregly, AI Systems Performance Engineering

[observed] The author and companion identify O'Reilly, 2025, and a November 2025 publication statement.
The author gives 1,062 pages. The supplied catalog identifier is 9798341627772.
Edition number and format-specific ISBNs remain unverified.
[Author](https://fregly.com/) · [Companion](https://github.com/cfregly/ai-performance-engineering) · [Complete note](oreilly/fregly.md).

[observed] The public companion lists twenty chapters.
Chapters 6–12 cover GPU execution, memory, occupancy, arithmetic intensity, pipelines, streams, and kernel orchestration.
Chapters 13–14 cover PyTorch profiling and compiler backends.
The companion checklist names GB200/GB300. It does not prove that each example runs on GB300.
[Public TOC](https://github.com/cfregly/ai-performance-engineering#book-chapters) · [Checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md).

[observed] The checklist gives matched workloads, warmup, CUDA events, output references, and raw result artifacts.
It starts profiling with Nsight Systems, then examines selected kernels with Nsight Compute.
[Checklist](https://raw.githubusercontent.com/cfregly/ai-performance-engineering/main/docs/appendix.md).

[inference] Portable techniques:
1. Use identical shapes, precision, seeds, and staging for comparable measurements.
2. Separate setup and warmup from steady-state timing.
3. Diagnose measured outliers with bounded system and kernel traces.
4. Check output against an independent reference with an explicit numerical contract.
5. Keep commands, versions, raw results, and workload configuration with each GPU result.
[Complete note](oreilly/fregly.md).

[inference] Add a practical GPU measurement reference for test authors, beside Gregg and PMPP.
Do not copy clock, power, MIG, persistence, OS tuning, or automatic recovery changes into the bench.
Do not use generic temperature or speedup examples as GB300 acceptance rules.
The living companion can differ from the published book. Keep revision information when tests use its code.
[Source assessment](oreilly/fregly.md) · [Safety contract](docs/gpu-bench-research.md).

## 9. N14 — Brian Tuomanen, Hands-On GPU Programming with Python and CUDA

[observed] Packt's companion identifies the title, author, twelve chapter directories, and historical software requirements.
Those requirements include Python 2.7, Anaconda 5, CUDA 9.2/10.x, PyCUDA, and Scikit-CUDA.
The supplied catalog gives 2018, 310 pages, and identifier 9781788993913.
Complete chapter titles and format relationships remain incompletely verified.
[Companion](https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA) · [Complete note](oreilly/python.md).

[inference] Portable techniques:
1. Record device capabilities and environment before workload execution.
2. Time host/device transfers separately from kernels; do not equate transfer rate with HBM bandwidth.
3. Check fixed-input kernels against an independent reference.
4. Use profiles to explain outliers, not as a health PASS criterion.
The note's `allclose` example uses tolerance, not bit-exact comparison.
[Complete note](oreilly/python.md).

[inference] Add optional Python implementation reading only. Do not add historical dependencies to the bench.
[Source assessment](oreilly/python.md).

## 10. N15 — Programming Massively Parallel Processors, edition comparison

[observed] Elsevier's 4e TOC has 23 chapters and Appendix A, Numerical considerations.
The accepted publisher identifier is 9780323912310; the source note records 2022 and three authors.
The supplied O'Reilly identifier is 9780323984638. Its format and edition relationship remain unverified.
[Publisher](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0) · [Complete note](oreilly/pmpp.md).

[observed] The corrected second-edition product identifier is 9780124159921, not 9780123814722.
The second-edition publisher fetch supplies contents, not all metadata fields.
Third-edition metadata and contents remain unverified in this pass.
This pass does not establish whether a later edition exists by the research date.
[Second-edition product](https://shop.elsevier.com/books/programming-massively-parallel-processors/kirk/978-0-12-415992-1) · [Edition evidence and gaps](oreilly/pmpp.md).

[observed] Useful 4e chapters include 4–6, execution/memory/performance; 10, reduction; and Appendix A, numerical considerations.
[Publisher TOC](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0).

[inference] Portable techniques:
1. Measure compute and memory paths separately.
2. Exercise more than one access pattern and data shape.
3. Check reductions with a declared ordering and numerical contract.
4. Record tested data, precision, duration, and independent reference results.
[Complete note](oreilly/pmpp.md).

[inference] Confirm the existing 4e architecture reference. Do not infer a new edition from an ISBN difference.
[Source assessment](oreilly/pmpp.md).

## 11. N16 — Brendan Gregg, Systems Performance, 1st Edition

[observed] Gregg's author page identifies the first edition, 2013, and thirteen chapters.
It names Prentice Hall; the supplied catalog names Addison-Wesley.
The note keeps those source labels separate. It does not verify 784 pages or all ISBN format labels.
The supplied identifier is 9780133390124; the author also links 9780133390094.
[Author](https://www.brendangregg.com/sysperfbook.html) · [Complete note](oreilly/gregg1.md).

[observed] Chapters 2, 4, and 12 cover methodology, observability, and benchmarking.
Gregg's 2e description adds modern Linux, cloud, perf, Ftrace, and BPF coverage.
[First edition](https://www.brendangregg.com/sysperfbook.html) · [Second edition](https://www.brendangregg.com/systems-performance-2nd-edition-book.html).

[inference] Portable techniques:
1. Keep utilization, saturation, and errors together for each resource.
2. Declare reproducible workload conditions before measurement.
3. Use per-device distributions and telemetry to examine low throughput.
4. Keep unavailable measurements separate from healthy values.
[Complete note](oreilly/gregg1.md).

[inference] Confirm the durable methods. Prefer 2e instead of requiring both editions.
This changes no existing recommendation, because the accepted brief already selects 2e.
[Source assessment](oreilly/gregg1.md) · [Accepted books brief](books.md).

## 12. N17 — André Bondi, Foundations of Software and System Performance Engineering

[observed] Pearson's public TOC identifies the full title and fifteen chapters.
Its filename carries identifier 9780133038163; the supplied O'Reilly identifier is 9780133038149.
The supplied catalog gives Addison-Wesley, 2014, and 448 pages.
Exact edition, format, publication date, and pagination remain independently unverified.
[Pearson TOC](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf) · [Complete note](oreilly/bondi.md).

[observed] Useful chapters include 2, metrics; 4, workloads; 8, instrumentation; 9, testing; and 12, pitfalls.
Section 9.6.2 covers pilot testing. Section 9.6.3 covers testing the test equipment and software.
[Pearson TOC](https://www.pearson.de/media/muster/toc/toc_9780133038163.pdf).

[inference] Portable techniques:
1. Declare measurable requirements and the evidence each check must collect.
2. Define fixed workload inputs, precision, working set, duration, and concurrency.
3. Check the measurement tools and harness on a representative GPU before the rack run.
4. Keep raw values, averaging windows, timestamps, and comparison limits.
5. Treat peer outliers as relative evidence, not universal quality grades.
Missing acceptance rules must not stop valid measurement collection.
[Complete note](oreilly/bondi.md).

[inference] Add optional requirements and test-planning reading. Do not replace Gregg or current GPU operational guides.
[Source assessment](oreilly/bondi.md).

## 13. Bench consequences

[inference] The supplement changes the test-author reading list. It does not change the GPU safety or acceptance contract.
Use Fregly's public measurement checklist for fixed workloads and recorded results.
Do not import configuration tuning or distributed performance tests.
Keep independent references and explicit numerical contracts.
Keep all measurements from failed devices.

Missing acceptance rules prevent an absolute grade, not measurement collection.
[Distilled checks and tickets](docs/gpu-bench-research.md) · [Fregly source note](oreilly/fregly.md).

[inference] The source pass does not establish two-hour rack feasibility.
It supplies no GPU failure-rate estimate, full HBM coverage, SDC absence, or lifetime reliability claim.
A representative-tray pilot and a controlled rack pilot remain necessary.
[Original limits](ORCHESTRATOR-REPORT.md) · [Failure studies](academia.md).

## Gaps

O'Reilly fetches deny access. The supplement does not establish authenticated full-book review.
Search rate limits restrict several public fallback checks.

Motta lacks a verified TOC. Professional CUDA C lacks verified chapter titles and complete format metadata.
Python and CUDA lacks a complete authoritative chapter-title list.
PMPP's older editions and later-edition status remain incompletely verified.
Bondi's TOC has a different identifier; its edition and format mapping remain unverified.

Do not interpret these gaps as proof that chapters or editions do not exist.
Keep companion evidence separate from book-text evidence.
Living companion revisions can change after publication.
The source notes record the exact access limits and metadata conflicts.
[Complete source notes](oreilly/README.md) · [Evidence review](oreilly/evidence-review.md).
