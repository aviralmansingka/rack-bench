# N09 — Brendan Gregg, *Systems Performance*, 2nd edition

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Catalog access and identity

[observed] The researcher first tries the captain-provided O’Reilly catalog URL. The web fetch returns HTTP 403 Forbidden. The researcher does not try an authentication bypass or full-text access. <https://learning.oreilly.com/library/view/-/9780136821694/?orm_source=mcp>

[observed] Gregg’s official book page identifies *Systems Performance: Enterprise and the Cloud, 2nd Edition (2020)*. Addison-Wesley publishes it, and the page links to its public contents. The publisher’s InformIT listing identifies Brendan Gregg, 2nd edition, 928 pages, and eBook ISBN 9780136821649. InformIT states Published Dec 9, 2020. Its sample content includes Chapter 3 and a detailed contents list. Google Books independently gives Pearson, Dec 9, 2020, 928 pages, and ISBN 9780136821656.

These distinct ISBNs indicate separate formats/records. Do not silently treat the captain’s O’Reilly URL/ISBN 9780136821694 as the publisher’s eBook or print ISBN. InformIT separately labels Copyright 2021 and states Published Dec 9, 2020. Record copyright and publication date as distinct metadata fields, not as conflicting publication dates. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html> <https://www.informit.com/store/systems-performance-9780136821649> <https://books.google.com/books/about/Systems_Performance.html?id=VNnPEAAAQBAJ>

[observed] Gregg’s official page calls the draft “roughly 800 pages”. InformIT and Google Books list 928 pages. This difference reflects draft versus published/catalog counts. Do not resolve it by choosing one count. Gregg’s page gives the shorter display title. The official page heading gives the subtitle. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html> <https://www.informit.com/store/systems-performance-9780136821649> <https://books.google.com/books/about/Systems_Performance.html?id=VNnPEAAAQBAJ>

## 2. Contents and bench relevance

[observed] The public TOC lists Intro; Methodology; Operating Systems; Observability Tools; Applications; CPUs; Memory; File Systems. It also lists Disks; Network; Cloud Computing; Benchmarking; perf; Ftrace; BPF; Case Study; appendices. InformIT’s detailed TOC gives section headings and pagination. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html> <https://www.informit.com/store/systems-performance-9780136821649>

[observed] Chapter 2 covers models, concepts, methodology, modeling, statistics, monitoring, and visualizations. Chapter 4 covers tool coverage, tool types, and observability sources. Chapter 6 covers CPU models, methodology, tools, and experimentation. Chapter 7 covers memory concepts, architecture, methodology, and tools. Chapter 12 covers benchmarking background, types, methodology, and benchmark questions. Appendix A is the USE Method for Linux. <https://www.informit.com/store/systems-performance-9780136821649>

[inference] For GPU bench authors, read Chapters 2 and 12 first. Then use Chapters 4, 6, and 7 selectively for measurement design and bottleneck reasoning. TOC-level relevance does not show GPU-specific instructions. The book’s detailed tools are predominantly OS/Linux tools, not DCGM/NVML or CUDA certification procedures. <https://www.informit.com/store/systems-performance-9780136821649> <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>

## 3. Portable techniques for `bench gpu`

1. **[inference] Controlled benchmark contract.** Mechanism: Chapter 12 explicitly covers benchmarking methodology and benchmark questions. Chapter 2 covers modeling and statistics. Measurement: pin workload, precision, input/seed, duration, concurrency, GPU identity, software versions, and power/thermal conditions. Keep raw per-GPU values and distributions.

   Limit: the TOC supports topic relevance only. Exact GPU procedure and acceptance thresholds come from current NVIDIA/platform documentation and the site profile. <https://www.informit.com/store/systems-performance-9780136821649>

2. **[inference] Baseline, workload, then deltas.** Mechanism: methodology, observability, and experimentation sections suggest a split between initial state and changes during a controlled load. Measurement: snapshot ECC/remap/XID/NVLink counters and telemetry before and after, with timestamps. Calculate per-device deltas and correlate them with measured workload.

   Limit: Gregg’s book does not define GB300 counter semantics. Use current NVIDIA documentation. Keep lifetime counters separate from run deltas. <https://www.informit.com/store/systems-performance-9780136821649> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

3. **[inference] Resource-oriented diagnosis, not utilization-only grading.** Mechanism: USE (utilization, saturation, errors) directs diagnosis toward each resource’s use, queueing/saturation, and faults. Measurement: for each GPU separately, relate achieved throughput to clocks, power, thermal conditions, and memory behavior. Also relate it to ECC/remap/XID and available NVLink health counters.

   Limit: USE is a diagnostic framing, not a GPU pass threshold. Missing telemetry is not zero. Per-GPU link health is not east-west bandwidth certification. <https://www.brendangregg.com/usemethod.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

4. **[inference] Compare controlled peers and investigate outliers.** Mechanism: benchmarking and visualization topics support comparison of repeated results and distributions, not one point. Measurement: report each of the 72 devices. Identify within-cohort outliers under equivalent workloads. Include repetitions or time-series samples where the two-hour budget permits.

   Limit: a common-mode rack-wide degradation can look normal in peer-relative comparison. Keep measured values. Do not invent a universal GB300 threshold. <https://www.informit.com/store/systems-performance-9780136821649>

5. **[inference] Diagnose before tuning; preserve evidence.** Mechanism: methodology, observability, and experimentation are distinct listed topics. They support a hypothesis → observation → controlled test approach. Measurement: capture versions, command/plugin parameters, raw output, timestamps, exact skips, and failures before any configuration change. Keep certification read-only.

   Preserve configuration during approved active tests. Active workloads are not passive/read-only. They require exclusive GPU allocation plus approved power and cooling. Do not reset devices, clear counters, or change ECC, MIG, clocks, or power settings during certification.

   Limit: this note applies a general performance method. It does not claim that Gregg prescribes this GPU workflow. No finite two-hour screen proves a device SDC-free. <https://www.informit.com/store/systems-performance-9780136821649> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>

## 4. Relation to accepted research and edition choice

[observed] The accepted N07 book assessment already positions Gregg as the methodology spine. It positions current NVIDIA DCGM/NVML/CUDA guides as operational authority and PMPP 4e as support for kernel authors. It also rejects universal GB300 thresholds. It rejects any claim that a finite screen guarantees no SDC. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>

[observed] N09 confirms that division and does not supersede it. The 2e edition explicitly has methodology, observability, memory, and benchmarking content. Its public contents do not show device-level GPU RAS commands or GB300 thresholds. NVIDIA primary docs still govern current operational facts. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

[inference] Prefer 2e over 1e for this bench’s methodology reference. 2e is the later, revised edition. 2e explicitly adds BPF/BCC/bpftrace, perf/Ftrace, Linux, and cloud updates. Those additions improve host-side observability context around GPU runs. The core transferable value remains methodology and benchmarking, not GPU-specific procedures. N16 handles 1e separately; this note makes no 1e comparison beyond Gregg’s published description of 2e changes. <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>

## Gaps

[observed] O’Reilly catalog page access fails with HTTP 403. This failure blocks direct inspection of the record. Public publisher/author sources corroborate the title, author, edition, year, and TOC. Public publisher metadata gives multiple distinct ISBNs by format/record. <https://learning.oreilly.com/library/view/-/9780136821694/?orm_source=mcp> <https://www.informit.com/store/systems-performance-9780136821649> <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>

[observed] Public publisher sample pages include Chapter 3, not the chapters most relevant here. The detailed Chapter 2/4/6/7/12 section map comes from the catalog TOC, not from inspected full text. This note therefore marks all transfer of techniques to GPU bench as inference. <https://www.informit.com/store/systems-performance-9780136821649>

[inference] No conclusion here shows GB300 test thresholds, required DCGM plugins, rack-specific runtime, or SDC probability. Resolve those from the exact system’s supported NVIDIA/OEM documentation and measured rack pilots. Keep PASS only for measured evidence. Keep exact reasons for skips. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>
