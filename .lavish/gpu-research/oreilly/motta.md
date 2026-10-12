# N10 — *GPU Programming with C++ and CUDA* (Paulo Motta)

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Scope and evidence

### 1.1 Catalog record and access

- **[observed]** The supplied O’Reilly catalog URL contains the supplied catalog identifier 9781805124542. This assignment supplies the catalog metadata Paulo Motta, Packt, 270 pages, publication 2025-08. The O’Reilly page returns HTTP 403 to the available fetcher. Therefore the researcher cannot inspect its contents. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp>
- **[observed]** The attempted Packt product page presents bot/security verification. It does not present readable product metadata or a table of contents. <https://www.packtpub.com/en-us/product/gpu-programming-with-c-and-cuda-9781805124542>
- **[observed]** Web search is unavailable during this pass (Tavily returns HTTP 429 for each search request). No source verifies an alternate public table of contents, sample chapter, author page, or source-code repository. The PacktPublishing GitHub organization and attempted title-filtered repository view do not expose a matching companion repository or TOC. <https://github.com/PacktPublishing> <https://github.com/PacktPublishing?tab=repositories&q=GPU%20Programming%20with%20C%2B%2B%20and%20CUDA>. The O’Reilly URL alone does not verify the identifier’s format. Accessible primary evidence does not let the researcher check an independent print identifier, publication date, and edition relationship. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp> <https://www.packtpub.com/en-us/product/gpu-programming-with-c-and-cuda-9781805124542>
- **[inference]** Therefore this note asserts no chapter numbers, chapter titles, book-specific procedures, or GB300 teaching claims. A title and catalog description alone do not establish chapter contents or platform-specific coverage. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp>

### 1.2 Rack-bench question

- **[observed]** The target is device health, performance, and correctness on an 18-tray / 72-GPU GB300/NVL72-class rack in Chennai. The work runs within a two-hour `bench gpu` window. PASS requires measured evidence, failures remain visible, and skips require reasons. East-west and collective performance stay excluded, while per-GPU NVLink health remains in scope. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/oreilly/README.md>
- **[observed]** The accepted N07 brief prioritizes current NVIDIA operational documentation for RAS and test semantics. It prioritizes Gregg for measurement method and PMPP 4e for architecture fundamentals. It states that no book supplies universal GB300 thresholds or proves absence of SDC. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>

## 2. Relevant chapters and reading recommendation

### 2.1 Chapter selection

- **[observed]** No reliable public table of contents or sample chapter is accessible in this research pass. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp> <https://www.packtpub.com/en-us/product/gpu-programming-with-c-and-cuda-9781805124542>
- **[inference]** Without verified contents, this note cannot responsibly number chapter recommendations. The publisher or library can later expose a TOC. Then inspect only chapters whose stated scope is CUDA execution, memory movement/hierarchy, synchronization, or error handling. Numerical correctness, profiling, or performance measurement scopes also qualify. Mark any selection based only on TOC wording as inference. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp>
- **[inference]** A current C++/CUDA programming book likely gives implementation fluency to an engineer who writes a CUDA test. That value is not operational RAS diagnosis. Validate any concepts against the current CUDA Programming Guide, Best Practices Guide, and relevant library documentation. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>

### 2.2 Decision

- **[inference]** Do not add this title as a required operator or certification reference on present evidence. Treat it as a potential CUDA-learning supplement for test authors, pending a verified TOC or sample. It does not supersede the accepted operational canon. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>

## 3. Portable test techniques for the bench

The following are **[inference] proposals**, not claims that the book teaches these methods. Use them only as small workload components under the site’s approved two-hour plan. Use the primary NVIDIA documentation for API semantics and acceptance policy. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

### 3.1 Deterministic arithmetic with an independent oracle

- **[inference]** Run a seeded, bounded set of integer or otherwise explicitly deterministic CUDA operations. Copy results to host. Compare every output with an independently written CPU oracle or known expected values. Record operation, data types, seed, build/library versions, exact mismatch count and first failing index. Use bit-exact comparison only where the operation/build contract guarantees it; otherwise define a justified tolerance. This probes selected executions, not all arithmetic modes or all SDC. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cublas/index.html>

### 3.2 Device-memory write/read patterns

- **[inference]** Allocate a declared working set and fill it with several address- and value-distinguishing patterns. Then synchronize, read back, and compare. Record allocation size, pattern, bytes checked, elapsed time, and mismatch locations. Also record before/after ECC and remap state. Respect the approved workload and memory budget; a finite allocation/pattern pass does not prove all HBM cells fault-free. DCGM documents its own memory plugin semantics, and that is preferable to inventing unsupported pass thresholds. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

### 3.3 Copy-path and kernel completion validation

- **[inference]** Exercise host-to-device/device-to-host copies and a simple transform over multiple buffers. Check every CUDA API return. Synchronize before you judge completion. Verify returned bytes against the host oracle. Record bytes, duration, effective rate, errors, and test parameters per GPU. This tests the selected allocation/copy/kernel path, not rack east-west bandwidth. <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>

### 3.4 Repeated compute with telemetry deltas

- **[inference]** Repeat a fixed compute workload during a bounded sustained interval. Record completed work/time per GPU with sampled clocks, power, and temperature where supported. Also record throttle/event reasons and before/after ECC/XID/remap state. Compare only against a declared SKU/workload/power-profile reference, or label the outcome a relative outlier screen. Do not invent a universal GB300 threshold. <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

### 3.5 Per-GPU NVLink health snapshot

- **[inference]** Capture per-device NVLink status and error counters before and after the active test. Retain link identifiers, state, raw counts, and deltas. This is a health observation, not a bandwidth/collective test. A sleeping link is not automatically failed. Record unavailable telemetry as a reasoned SKIP. <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## 4. Relation to accepted N07

### 4.1 New / potentially useful

- **[inference]** The only defensible possible addition is an accessible, modern C++/CUDA learning path. Its audience is people who write small independent correctness workloads. No source verifies that this book actually offers that depth. No source verifies which chapters do so or whether its examples are suitable. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

### 4.2 Confirms

- **[observed]** The accepted brief separates programming/architecture education from operational device diagnosis. Engineers can use CUDA and PMPP material to understand or make tests. Live NVIDIA docs define current DCGM, telemetry, RAS and product behavior. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>
- **[inference]** The catalog title’s subject is consistent with CUDA programming education. The accessible evidence does not establish any additional diagnostic method beyond the existing brief. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp>

### 4.3 Supersedes

- **[observed]** This note supersedes no existing N07 recommendation. No verifiable contents or technical claims from this book are available to compare. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>
- **[inference]** Its CUDA teaching can be current and useful. Even so, it does not replace Gregg’s measurement method, PMPP’s architecture treatment, or current NVIDIA operational documentation. Only direct evidence that it covers those distinct purposes can change this. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## Gaps

- **[observed]** O’Reilly returns HTTP 403, Packt serves a security-verification page, and web search returns HTTP 429. No source verifies an accessible primary table of contents, sample, or code repository. No source verifies an author/publisher metadata page. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp> <https://www.packtpub.com/en-us/product/gpu-programming-with-c-and-cuda-9781805124542>
- **[observed]** Captain-supplied catalog metadata is Paulo Motta, Packt, 270 pages, 2025-08, supplied catalog identifier 9781805124542. Accessible primary sources do not independently confirm edition, print ISBN, and exact publication-date relationship. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp>
- **[inference]** Revisit this note when an authorized O’Reilly session or public publisher contents page becomes available. Verify identifier format and any print identifier, edition and date. Also verify the full chapter list and any official sample/code. Do this before you recommend chapter numbers or attribute portable techniques to the book. Do not bypass authentication. <https://learning.oreilly.com/library/view/-/9781805124542/?orm_source=mcp> <https://www.packtpub.com/en-us/product/gpu-programming-with-c-and-cuda-9781805124542>
- **[observed]** No claims here establish GB300-specific support, universal thresholds, or absence of SDC. Those topics remain outside what this catalog-only evidence can answer. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>
