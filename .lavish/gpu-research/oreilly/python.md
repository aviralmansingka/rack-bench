# N14 — *Hands-On GPU Programming with Python and CUDA*

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Catalog identity and access

- **[observed]** Captain-supplied catalog metadata names Dr. Brian Tuomanen, Packt, 310 pages, 2018, at the O’Reilly listing ISBN 9781788993913.
  The supplied catalog URL is <https://learning.oreilly.com/library/view/-/9781788993913/?orm_source=mcp>.

- **[observed]** I try to fetch that O’Reilly URL.
  It returns an access-denied page (“You don't have permission”) and redirects to an Akamai error endpoint.
  This result is an access/authentication limit.
  I make no attempt to bypass it. <https://learning.oreilly.com/library/view/-/9781788993913/?orm_source=mcp>

- **[observed]** Packt’s public companion-code repository names the title and author and links the 9781788993913 product.
  It describes coverage of GPU feature queries, host/device transfers, Python-launched kernels, and cuFFT/cuBLAS/cuSolver.
  It also describes coverage of profiling/debugging, data-science applications, and warp shuffling. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA>

- **[observed]** The companion README lists the print ISBN-13 as 9781788995221 in its Packt product link.
  It names a software environment of Anaconda 5 / Python 2.7 and CUDA 9.2 or 10.x.
  The environment also has PyCUDA and (chapter 7) Scikit-CUDA.
  This README shows the listed print ISBN separately from the O’Reilly catalog ISBN.
  It does not show that these are the only formats or edition identifiers. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA>

- **[observed]** The repository’s “Chapter 1–12” instructions and Chapter01–style code layout show twelve numbered chapters.
  The publicly accessible material that I review does not show a reliable complete chapter-title list.
  It does not show a publication date beyond captain metadata.
  It does not show an authoritative print/e-book pagination statement.
  Treat 2018/310pp as supplied catalog metadata.
  Accessible primary text does not independently confirm it. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA>

- **[observed]** A Packt chapter landing page surfaces for chapter 11, “Performance Optimization in CUDA,” and chapter 8, “The CUDA Device Function Libraries and Thrust”.
  Packt blocks (403) direct fetches of Packt and Packt Subscription chapter pages.
  So this note verifies only their surfaced titles, not full chapter contents. <https://www.packtpub.com/en-us/product/hands-on-gpu-programming-with-python-and-cuda-9781788993913/chapter/assessment-13/section/chapter-11-performance-optimization-in-cuda?chapterId=13> <https://www.packtpub.com/en-us/product/hands-on-gpu-programming-with-python-and-cuda-9781788993913/chapter/the-cuda-device-function-libraries-and-thrust-8/section/the-cuda-device-function-libraries-and-thrust-8> 

## 2. Relevant chapters and evidential limits

- **[observed]** The sources give chapter 11 the title “Performance Optimization in CUDA.”
  Chapter 8 concerns CUDA device-function libraries and Thrust.
  The accessible sources show these titles only.
  This note does not assert detailed subsection or chapter-number mapping for the remaining topics. <https://www.packtpub.com/en-us/product/hands-on-gpu-programming-with-python-and-cuda-9781788993913/chapter/assessment-13/section/chapter-11-performance-optimization-in-cuda?chapterId=13> <https://www.packtpub.com/en-us/product/hands-on-gpu-programming-with-python-and-cuda-9781788993913/chapter/the-cuda-device-function-libraries-and-thrust-8/section/the-cuda-device-function-libraries-and-thrust-8>

- **[inference]** For N07, prioritize the performance-optimization chapter.
  Also prioritize the chapters that the repository description links to GPU queries/transfers and Python-launched kernels.
  Those descriptions also name libraries, profiling/debugging, and warp shuffling.
  These subjects plausibly help an engineer construct and interpret focused device workloads.
  Public summaries do not prove a particular diagnostic recipe or coverage guarantee. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA>

- **[inference]** Chapter 8/library material may inform a controlled library-backed compute smoke test.
  A library result alone is not a device-health verdict.
  Keep operation, datatype, inputs, algorithm, software versions, expected-result contract, timing, and per-GPU identity.
  The public listing does not specify the book’s exact tests, thresholds, or expected outputs. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA>

## 3. Portable techniques for a measured GPU bench

1. **Query capabilities and record environment. [inference]** The repository synopsis says the book teaches querying GPU features.

   Port this as inventory-before-test: map UUID/BDF and SKU.
   Record driver/runtime/tool versions and supported capabilities.
   Keep unavailable fields as exact SKIPs rather than assuming support.
   Use current NVIDIA management interfaces for authoritative GB300 fields.
   The book’s listed CUDA/Python environment is old. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

2. **Measure host/device transfer separately from kernel work. [inference]** The synopsis explicitly includes copying arrays to/from GPU memory.

   Time transfers independently from kernel execution.
   Report direction, bytes, repetitions, synchronization, and effective rate per GPU.
   This method can show a transfer-path bottleneck without conflating it with arithmetic throughput.
   It is not a substitute for HBM bandwidth testing.
   It does not measure east-west or collective fabric performance. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/>

3. **Use a small deterministic kernel with an explicit oracle. [inference]** The book has Python-launched CUDA kernels.
   The repository has a correctness-oriented example (cuBLAS result compared with NumPy via `allclose`).
   Both support a practical pattern: generate fixed inputs, run a known operation, and synchronize.

   Then compare output to an independent reference, and save mismatch counts/max error plus execution parameters.
   `allclose` is tolerance-based, not bit-exact.
   Do not claim bit-exactness unless the selected operation/build promises deterministic identical results. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/cublas/index.html>

4. **Profile to explain a measured outlier, not as the pass criterion. [inference]** The companion description names Nsight and Visual Profiler.
   A timeline/profile can help distinguish launch, transfer, synchronization, and kernel time.
   Profiling instrumentation and permissions can change behavior.
   For benchmark acceptance, keep unprofiled measured output and use current Nsight documentation. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/nsight-systems/UserGuide/index.html>

5. **Vary kernels/resources rather than extrapolate one score. [inference]** The listed topics include device functions, libraries, and warp shuffling.
   These topics suggest ways to make workloads with differing execution/resource behavior.

   A compute microbenchmark cannot certify HBM, ECC, remapping, SDC absence, or power/thermal stability.
   It cannot certify clocks or per-GPU NVLink health either.
   Combine workload measurements with current DCGM/NVIDIA telemetry, and publish exact coverage. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

**[observed]** These items are portable method adaptations, not measured results from the Chennai rack.
The publicly reviewed book listing and companion README show no 18-tray/72-GPU, two-hour run.
They show no GB300 qualification, universal performance threshold, or test PASS. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

## 4. Current applicability and comparison with accepted books

- **[observed]** The companion repository lists Python 2.7-era Anaconda 5, CUDA 9.2/CUDA 10.x, PyCUDA, and Scikit-CUDA.
  Those items are the repository’s stated historical requirements, not a current GB300-supported software recipe. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA>

- **[inference]** Treat code as pedagogical.
  Do not add PyCUDA, Python 2, or the book’s historical toolchain as a new bench dependency.
  Port useful ideas to the project’s already-approved/current CUDA stack.
  Before implementation, verify every API/library against current NVIDIA release and support documentation. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

- **[inference]** Relative to accepted Gregg methodology, this book adds concrete Python/CUDA implementation ideas.
  It does not add stronger experimental design or diagnostic classification.
  Relative to current NVIDIA operational documentation, it is much weaker on RAS counters, XIDs, and row remapping.
  It is also much weaker on NVLink health, release-specific support, and production recovery semantics. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://www.brendangregg.com/systems-performance-2nd-edition-book.html> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

- **[inference]** Relative to PMPP 4e, this book offers more direct Python and library-oriented implementation examples.
  PMPP is the accepted deeper architecture foundation.
  Neither book certifies universal GB300 thresholds or proves absence of SDC.
  Use current NVIDIA docs for supported operational checks.
  Keep the SDC claim bounded to tested patterns, precision, duration, and oracle. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>

- **Verdict [inference]:** OPTIONAL, for test authors who learn Python/CUDA kernel construction.
  Do not add it to the required operator reading path.
  It adds no qualification authority.
  It does not supersede Gregg, current NVIDIA operational docs, or PMPP’s architecture role. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

## Gaps

- **[observed]** O’Reilly returns access denial.
  Packt product/chapter pages and Packt Subscription fetches return 403.
  Tavily rate-limits later searches.
  So this pass has no full text, authenticated O’Reilly metadata, complete authoritative TOC, or detailed samples. <https://learning.oreilly.com/library/view/-/9781788993913/?orm_source=mcp> <https://www.packtpub.com/en-us/product/hands-on-gpu-programming-with-python-and-cuda-9781788993913>

- **[observed]** Packt’s public repository verifies the title, author, chapter numbering range, and described subject areas.
  It also verifies the listed software and sample code presence.
  The accessible evidence here does not independently verify the catalog’s 310-page count or 2018 date.
  It does not verify complete chapter titles or a distinct e-book ISBN. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA>

- **[inference]** A later authenticated catalog or print-book TOC/sample can refine chapter selection.
  It can verify format-specific ISBN/pages/date.
  It does not remove the need for current GB300/NVIDIA operational references.
  The reviewed materials support no universal GPU-health threshold or SDC-free claim. <https://github.com/PacktPublishing/Hands-On-GPU-Programming-with-Python-and-CUDA> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>
