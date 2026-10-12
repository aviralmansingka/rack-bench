# N08 — Shane Cook, *CUDA Programming*
Research date: 2026-10-11. All claims below carry a source URL.

## 1. Bibliographic identity and access

### 1.1 Verified identity
- [observed] The publisher catalog identifies *CUDA Programming: A Developer's Guide to Parallel Computing with GPUs*, by Shane Cook. The catalog gives first edition, Morgan Kaufmann (Elsevier imprint), published November 13, 2012. The publisher lists paperback ISBN-13 `9780124159334`; the hyphenated form is `978-0-12-415933-4`. <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
- [observed] The O'Reilly supplied catalog URL is `https://learning.oreilly.com/library/view/-/9780124159334/?orm_source=mcp`. The fetch returns HTTP 403 Forbidden. Thus this is catalog-only evidence; the researcher accesses no O'Reilly full text. <https://learning.oreilly.com/library/view/-/9780124159334/?orm_source=mcp>
- [observed] An ACM catalog search result independently gives the subtitle, author, Morgan Kaufmann, and ISBN-13 `978-0-12-415933-4`. It also gives publication date December 28, 2012, and 600 pages. The ACM fetch itself returns 403. <https://dl.acm.org/doi/10.5555/2430671>
- [observed] The publisher catalog says 1st edition, November 13, 2012. A secondary retail catalog reports print ISBN-10 `0124159338`, ISBN-13 `978-0124159334`, November 27, 2012, 592 pages. The disagreement is date/page-count metadata. Use the publisher edition/date. Do not treat catalog page counts as verified pagination. <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://www.amazon.com/CUDA-Programming-Developers-Computing-Applications/dp/0124159338>
- [observed] The publisher assigns paperback ISBN-13 `9780124159334`; the supplied O’Reilly catalog identifier matches it. ISBN-10 `0124159338` and ISBN-13 `9780124159334` identify the same book. They are number representations, not print-versus-digital formats. No source verifies a distinct digital ISBN. <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://learning.oreilly.com/library/view/-/9780124159334/?orm_source=mcp> <https://www.amazon.com/CUDA-Programming-Developers-Computing-Applications/dp/0124159338>

### 1.2 Access limits
The O'Reilly page is not accessible (403). The Elsevier publisher page is accessible and gives the table of contents and product metadata. The researcher does not attempt or bypass authenticated full-text access. Therefore chapter-specific claims below stay limited to the publisher's TOC. This note makes no quotations or claims about detailed chapter instruction. [observed] <https://learning.oreilly.com/library/view/-/9780124159334/?orm_source=mcp> <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>

## 2. Publisher table of contents and relevance

### 2.1 TOC evidence
The publisher lists Preface; Chapters 1–12; References; Index. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>

1. **A Short History of Supercomputing** — architecture history and GPU hardware appear in TOC. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
2. **Understanding Parallelism with GPUs** — serial/parallel problems, concurrency, types/patterns of parallelism. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
3. **CUDA Hardware Overview** — GPU hardware, CPU/GPU, compute levels. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
4. **Setting Up CUDA** — installation, compilation model, error handling. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
5. **Grids, Blocks, and Threads** — threads, blocks, grids, warps, scheduling, histogram example. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
6. **Memory Handling with CUDA** — caches, registers, shared, constant, global, texture memory. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
7. **Using CUDA in Practice** — serial/parallel code, datasets, profiling, AES example. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
8. **Multi-CPU and Multi-GPU Solutions** — locality, multi-GPU algorithms, streams, single/multiple-node systems. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
9. **Optimizing Your Application** — memory, transfers, thread usage, divergence, algorithms, contention, self-tuning. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
10. **Libraries and SDK** — libraries, SDK, directives, writing kernels. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
11. **Designing GPU-Based Systems** — GPU device, PCIe, cooling, power and system components. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
12. **Common Problems, Causes, and Solutions** — programming/algorithm issues, finding/avoiding errors, developing for future GPUs. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>

### 2.2 Bench-gpu relevance
Chapters 4–7, 9–12 are the strongest TOC matches for test implementation, profiling, and resource-aware workload design. They also match error handling and power/cooling awareness. Chapter 8's multi-GPU content is not a basis for east-west or collective performance checks in this category. The TOC does not establish book coverage of ECC, XIDs, row remapping, SDC, or NVML/DCGM. It also does not establish coverage of GB300, NVLink health commands, or current CUDA behavior. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>

## 3. Portable techniques for bench-gpu

### 3.1 Separate compute correctness from performance measurement
Use a deterministic single-GPU workload with known inputs and independently checked outputs. Record correctness separately from throughput. Pin operation, precision, inputs, build/runtime, and comparison contract. [inference]

The TOC shows evidence for profiling/practice and error handling. No full text verifies an exact validation recipe. Floating-point results are not universally bit-exact across algorithm/compiler/library modes. Claim bit-exact only where the chosen computation guarantees it. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

### 3.2 Use distinct compute and memory probes
Measure a compute-heavy kernel and a streaming memory workload separately. Record per-GPU elapsed time, output verification, and achieved rate. Also record workload/working-set size and concurrent load. This method distinguishes resource paths and does not treat utilization as a performance result. The book TOC supports memory hierarchy and profiling topics, not a GB300-specific benchmark or acceptance threshold. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>

### 3.3 Control the measurement conditions
Warm up and define a fixed timed interval. Collect repeated samples and summarize the distribution. Record clocks/power/temperature context with the workload. Keep idle and loaded observations distinct. Do not infer device health from a lone clock or utilization sample. This is a portable measurement proposal, not verified Cook chapter procedure. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

### 3.4 Make failures explicit at the CUDA boundary
Check API/launch errors. Make sure that asynchronous work completes before you accept output or timing. Preserve the failing operation and error details. Missing capability or unsupported telemetry is a reasoned SKIP, not PASS. Chapter 4's TOC explicitly includes error handling. These exact mechanics require current CUDA documentation. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

### 3.5 Keep resource and scope boundaries visible
Run tests per physical GPU. Record mapping, workload concurrency, and memory footprint. Record whether other devices contend for power/cooling. Capture per-GPU NVLink status/error deltas as health telemetry only. Exclude peer throughput, collectives, and east-west performance. Chapter 9's TOC names resource contention. No source establishes support for NVLink health specifics. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## 4. Relationship to books.md and scope

### 4.1 New / confirm / supersede
- **New:** Cook provides an introductory, practical CUDA programming source. Its explicit TOC coverage includes setup/error handling, profiling, and memory handling. It also includes optimization/resource contention and system power/cooling. It adds an accessible implementation-oriented complement to the books.md architecture selection. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
- **Confirm:** It supports the existing division. Use programming texts for authoring controlled CUDA workloads. Use NVIDIA's current DCGM/NVML/CUDA references for current commands, support, RAS semantics, and constraints. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
- **Supersede:** None. It does not supersede Gregg's diagnostic method, PMPP's parallel architecture treatment, nor current NVIDIA documentation. Its 2012 publication date makes it unsuitable as evidence for GB300 specifics. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>

### 4.2 Recommendation
[Inference] This book is an optional reference for engineers who write or study simple CUDA correctness/performance probes. It is not an operator runbook or acceptance authority. In the two-hour Chennai category window, use it for workload-design concepts only. Pair all executable behavior with pinned current NVIDIA documentation. It establishes no universal GB300 thresholds and no SDC-free status. [inference] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

## 5. Sources, conflicts, and full-text gaps

### 5.1 Primary and corroborating sources
- Elsevier/Morgan Kaufmann publisher catalog (identity and TOC): <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>
- O'Reilly supplied catalog URL (fetch returns 403): <https://learning.oreilly.com/library/view/-/9780124159334/?orm_source=mcp>
- ACM catalog record (search result metadata; page fetch 403): <https://dl.acm.org/doi/10.5555/2430671>
- Retail ISBN/page/date corroboration, not primary publisher evidence: <https://www.amazon.com/CUDA-Programming-Developers-Computing-Applications/dp/0124159338>
- Current CUDA behavior reference: <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>
- Current device management/NVLink query reference: <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- Current DCGM diagnostic reference: <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

### 5.2 Conflicts and limitations
[Observed] Publisher metadata states first edition, November 13, 2012. The ACM search result says December 28, 2012. Amazon gives November 27, 2012 and 592 print pages, while ACM gives 600 pages. No retrieved source resolves the date/page-count differences. Identity and edition are consistent; prefer the publisher date. [observed] <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://dl.acm.org/doi/10.5555/2430671> <https://www.amazon.com/CUDA-Programming-Developers-Computing-Applications/dp/0124159338>

[Observed] The researcher does not access the full text. O'Reilly and ACM return 403. This note explicitly marks recommendations beyond the printed TOC as [inference]. The accessible publisher catalog is the primary evidence for title, edition, author, imprint, and ISBN-13. It is also the primary evidence for publisher date and chapter headings. [observed] <https://learning.oreilly.com/library/view/-/9780124159334/?orm_source=mcp> <https://dl.acm.org/doi/10.5555/2430671> <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4>

## Gaps

- [Observed] This research has no authenticated full text. Chapter details beyond TOC headings remain unverified. Examples, exact procedures, and quotations also remain unverified. <https://learning.oreilly.com/library/view/-/9780124159334/?orm_source=mcp>
- [Inference] Normal institutional/O'Reilly access can later authorize full-text review. In that case, verify the suggested chapters directly. Do not use this catalog-only note as evidence that the book teaches current GB300 procedures.
- [Observed] The sources do not resolve the discrepant publication dates/page counts. Neither discrepancy affects the verified title, first edition, author, or publisher ISBN-13. <https://shop.elsevier.com/books/cuda-programming/cook/978-0-12-415933-4> <https://dl.acm.org/doi/10.5555/2430671>
