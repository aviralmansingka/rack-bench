# N16 — Brendan Gregg, *Systems Performance*, 1e

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Catalog verification

- **[observed]** The researcher fetches the requested O’Reilly catalog URL first.
  The URL returns HTTP 403.
  No one attempts an authentication bypass. [O’Reilly catalog request](https://learning.oreilly.com/library/view/-/9780133390124/?orm_source=mcp)

- **[observed]** Gregg’s official first-edition page names the title as *Systems Performance: Enterprise and the Cloud, 1st Edition*.
  The author page lists Prentice Hall and 2013.
  The captain lists Addison-Wesley as catalog metadata.
  The page links the Safari/O’Reilly listing with ISBN 9780133390124 and the InformIT listing/sample with ISBN 9780133390094. [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html)

- **[observed]** The page supports the title/subtitle, edition, and year.
  No accessed source verifies the exact catalog publisher field.
  The ISBNs are source-linked identifiers.
  The accessed sources do not show their exact digital/print format designations.
  No accessed source verifies the 784-page count. [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html) [InformIT sample PDF](https://www.informit.com/content/images/9780133390094/samplepages/0133390098.pdf)

- **[observed]** The official first-edition chapter list has these entries, in order:
  1 Intro; 2 Methodology; 3 Operating Systems; 4 Observability Tools; 5 Applications;
  6 CPUs; 7 Memory; 8 File Systems; 9 Disks; 10 Network;
  11 Cloud Computing; 12 Benchmarking; 13 Case Study; appendices; glossary.
  The chapters end on page 635. Appendices and other matter follow. [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html)

## 2. Relationship to the accepted second edition

- **[observed]** The second edition is *Systems Performance: Enterprise and the Cloud*, Addison-Wesley, 2020.
  Its official contents add chapters on `perf`, Ftrace, and BPF.
  The author says it updates Linux/cloud coverage and mostly removes Solaris.
  Gregg lists durable models, architecture, and methodology first in its chapter structure.
  He lists implementation/tools later. [Gregg, 2e book page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html)

- **[inference]** N07 already uses 2e as the methodology/current-practice anchor.
  Treat N16 as a confirmatory predecessor, not a parallel required child.
  The 1e chapter map shows a persistent spine: methodology, observability, resource analysis, and benchmarking.
  The 2e is the better choice for updated Linux/cloud coverage and modern tracing tools. [1e page](https://www.brendangregg.com/sysperfbook.html) [2e page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html)

- **[observed]** The book covers general systems performance.
  Its chapter list has no GB300, NVLink health, CUDA correctness, ECC/remapping, XID, or GPU-specific RAS chapter. [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html)

- **[inference]** Select 2e for the rack-bench team if you choose one Gregg book.
  Keep 1e’s durable method, experimental discipline, resource accounting, and benchmark-design lessons as historical foundation.
  Do not use either edition as authority for current NVIDIA controls, thresholds, or GB300 behavior. [1e page](https://www.brendangregg.com/sysperfbook.html) [2e page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)

## 3. Portable techniques for the two-hour GPU bench

1. **Use a stated diagnostic method rather than a grab-bag of counters.**
   **[observed]** Chapter 2 is “Methodology”.
   Gregg’s USE method checks each resource for utilization, saturation, and errors.

   **[inference]** Use this method per GPU.
   Check compute, HBM, power/thermal headroom, and each GPU’s NVLink health.
   Record measures and errors together.
   For this bench, check only per-GPU NVLink link state/error counters.
   Do not check east-west throughput or collectives. [1e contents](https://www.brendangregg.com/sysperfbook.html) [USE method](https://www.brendangregg.com/usemethod.html) [NVIDIA `nvidia-smi`](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

2. **Make a reproducible experiment.**
   **[observed]** Chapter 12 is “Benchmarking”.
   The author’s book description covers benchmarking and performance methodology.

   **[inference]** Record device UUID/BDF, software/firmware, workload, precision, duration, concurrency, power policy, and thermal conditions.
   Keep raw samples and before/after counters.
   A two-hour PASS is a result under those recorded conditions.
   This result is not a universal guarantee. [1e contents](https://www.brendangregg.com/sysperfbook.html) [2e book overview](https://www.brendangregg.com/systems-performance-2nd-edition-book.html)

3. **Diagnose resource limits, not just low throughput.**
   **[observed]** The book covers CPU, memory, disk, and network analysis in separate parts.
   It also has observability/methodology chapters.

   **[inference]** For GPU checks, compare measured throughput with utilization, clocks, power, temperature, throttle reasons, and RAS events.
   A low rate alone does not show the cause.
   A faulty device, workload, policy, host, or cooling constraint can cause a low rate.
   Translate the general method to the GPU.
   Use current NVIDIA guides for GPU telemetry semantics. [1e contents](https://www.brendangregg.com/sysperfbook.html) [NVIDIA `nvidia-smi`](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

4. **Use distributions and compare like with like.**
   **[inference]** Keep per-device and time-series measurements.
   Do not use only a rack average or one instantaneous sample.
   Compare equivalent workloads and configurations, and flag outliers.
   Do not assume a peer-relative mean shows rack-wide degradation.

   You can use the method on other systems.
   The book gives no GB300 reference distribution or acceptance threshold. [Gregg, 2e overview](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)

5. **Treat absent evidence as a limitation, not a pass.**
   **[inference]** Separate PASS, FAIL, and reasoned SKIP.
   Keep the missing sensor/plugin/counter status.
   Finite checks cannot show that silent data corruption (SDC) is absent.
   Neither this book nor a short bench can guarantee SDC-free operation. [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html) [NVIDIA SDC modeling study](https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model)

## 4. Scope and recommendation

- **[inference]** Use this book for method and experimental design.
  Apply that method to the Chennai system’s 18 trays/72 GPUs and the two-hour measured PASS contract.
  This book is not an implementation manual for ECC/XID/remaps, SDC, HBM tests, thermal/power/clocks, bit-exact arithmetic, or per-GPU NVLink health.
  Consult current NVIDIA operational guides for those details. [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html) [NVIDIA GPU Operational Events](https://docs.nvidia.com/deploy/gpu-operational-events/latest/) [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)

- **[inference]** Verdict: **catalog-only, optional confirmatory reading**.
  Prefer N07’s accepted 2e for current Gregg methodology.
  Keep this 1e record to document lineage and durable techniques.
  Do not duplicate the 2e child or claim GPU-specific coverage. [Gregg 1e](https://www.brendangregg.com/sysperfbook.html) [Gregg 2e](https://www.brendangregg.com/systems-performance-2nd-edition-book.html)

## Gaps

- **[observed]** O’Reilly’s catalog page returns HTTP 403.
  No one attempts authenticated access.
  The official author page verifies the title, edition, year, source-linked ISBNs, and chapter list.
  It does not verify the catalog’s exact publisher field, ISBN format designations, or 784-page count. [O’Reilly catalog](https://learning.oreilly.com/library/view/-/9780133390124/?orm_source=mcp) [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html)

- **[observed]** The researcher attempts a web search fallback.
  The fallback returns HTTP 429.
  Thus the researcher cannot fetch another InformIT/Pearson catalog page in this session.
  The author’s official page links an InformIT sample PDF and lists the chapters. [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html) [InformIT sample PDF](https://www.informit.com/content/images/9780133390094/samplepages/0133390098.pdf)

- **[inference]** Check the exact catalog publisher field, ISBN format designations, and 784-page figure against an accessible publisher/retailer record.
  Treat them as verified metadata only after you check them.
  The official chapter list and author’s descriptions support some content-level claims.
  No one independently checks other content-level claims against the full book. [Gregg, 1e book page](https://www.brendangregg.com/sysperfbook.html)
