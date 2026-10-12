# Canonical books for certification engineering: GPU racks and storage

Researched: 2026-10-11. Scope: the books that make an engineer good at
*certifying* GPU racks (burn-in, kernel-level and multi-GPU benchmarks,
NCCL-scale runs) and storage systems (fsync durability, fsx/fio workloads,
error paths) -- methodology, benchmark statistics, GPU architecture, and
storage internals. Application-level MLOps books are explicitly out of
scope. Companion notes in this folder: `clustermax.md`, `parallel-fs.md`.

All editions, dates, and free-vs-paid status were verified online in
Oct 2026. Sources are linked at the end.

## TL;DR: the ranked reading order (8 books)

| #  | Book                                                                 | Edition / year          | Cost  | One-line role                                                     |
|----|----------------------------------------------------------------------|-------------------------|-------|-------------------------------------------------------------------|
| 1  | *Systems Performance* -- Brendan Gregg                               | 2nd ed., 2020           | paid  | Certification methodology: USE, latency analysis, FS/disk, benchmarking |
| 2  | *The Art of Computer Systems Performance Analysis* -- Raj Jain        | 1991, still in print    | paid  | The statistics of pass/fail: variance, CIs, comparing systems      |
| 3  | *Programming Massively Parallel Processors* -- Hwu/Kirk/El Hajj       | 5th ed., Feb 2026       | paid  | The GPU mental model + new multi-GPU and cluster chapters          |
| 4  | *Modern GPU Programming for MLSys* -- Tianqi Chen et al.              | 2026, online            | free  | Blackwell-era kernels + GPU kernel benchmarking appendix           |
| 5  | *CUDA C++ Programming Guide* -- NVIDIA                                | CUDA 13.4 (2026)        | free  | API ground truth for writing correct cert harnesses               |
| 6  | *Operating Systems: Three Easy Pieces* -- the Arpaci-Dusseaus         | v1.10, free online      | free  | Persistence: disks, RAID, crash consistency, SSDs, checksums      |
| 7  | *Database Internals* -- Alex Petrov                                   | 2019                    | paid  | WAL, buffer pools, B-tree vs LSM I/O patterns                     |
| 8  | *Machine Learning Systems, Vol. I* -- Vijay Janapa Reddi et al.       | MIT Press, 2026         | free  | The ML workloads and systems metrics a rack is certified against  |

Phases: #1-2 methodology and statistics; #3-5 GPU racks; #6-7 storage;
#8 the workloads that tie it together. Read the PostgreSQL "fsyncgate"
web set (below) alongside #6. Four of the eight are free.

---

## Part 1 -- GPU computing books

### 1. Programming Massively Parallel Processors (PMPP)

- Author / edition / year: Wen-mei W. Hwu (NVIDIA Senior Director of
  Research, UIUC emeritus), David B. Kirk (former NVIDIA Chief
  Scientist), Izzat El Hajj. **5th edition, Morgan Kaufmann, published
  Feb 27, 2026** -- the latest. The 4th ed. (May 2022, 551 pp.) is the
  copy still on most shelves; earlier editions were Kirk + Hwu only.
- Attribution fix: Hennessy was never a PMPP author -- he is the
  Patterson & Hennessy (COD / CAQA) co-author. PMPP is the Kirk-Hwu
  book (with El Hajj since the 4th ed.).
- Uniquely covers for certifying GPU racks: SIMT execution, warp
  scheduling, memory hierarchy and coalescing, and a dedicated
  "Performance considerations" chapter -- the vocabulary that burn-in
  results and profiler output are written in. The 5th ed. adds exactly
  rack-scale material: ch. 19 "Multi-GPU API", ch. 22 "Programming a
  heterogeneous computing cluster", ch. 23 "Advanced optimizations for
  matrix multiplication", ch. 16 "Wavefront algorithms".
- Verdict: **MUST** -- the GPU bible; get the 5th ed. (Feb 2026).

### 2. CUDA by Example: An Introduction to General-Purpose GPU Programming

- Author / edition / year: Jason Sanders & Edward Kandrot (NVIDIA CUDA
  team), Addison-Wesley, July 2010. Never revised; fixed in the CUDA 3.x
  era.
- Uniquely covers for certifying GPU racks: the gentlest example-driven
  on-ramp to CUDA C (still hosted on NVIDIA's developer site), but it
  predates Unified Memory, modern error handling, and even
  gather/scatter patterns; nothing cert-specific.
- Verdict: **SKIP** -- PMPP 5th ed. plus the free NVIDIA docs cover the
  same ground at current API vintage.

### 3. The CUDA Handbook: A Comprehensive Guide to GPU Programming

- Author / edition / year: Nicholas Wilt (CUDA driver-API architect,
  on the CUDA inception team), Pearson/Addison-Wesley, June 2013
  (CUDA 5.5 era). A 2nd edition was "under contract" around 2021 but
  never shipped; the full text is now free online at cudahandbook.com.
- Uniquely covers for certifying GPU racks: still the only book-length,
  deep treatment of the driver API -- contexts, modules, streams and
  events, pinned/mapped memory -- plus microbenchmark techniques for
  launch latency and peak memory bandwidth. But 13 years stale.
- Verdict: **SKIP** as a buy; bookmark the free web text only if a cert
  harness must go below the runtime API.

### 4. NVIDIA CUDA C++ Programming Guide

- Author / edition / year: NVIDIA, free, versioned with each toolkit
  release; current at **CUDA 13.4** (docs.nvidia.com/cuda). Note the
  2025-26 doc restructure: a language-agnostic "CUDA Programming Guide"
  umbrella now sits alongside the classic CUDA C++ guide (PDF at
  Release 13.3/13.4); the toolkit itself moves on a roughly monthly
  cadence.
- Uniquely covers for certifying GPU racks: exact, current semantics
  for memory management, streams, error handling, occupancy, and
  forward compatibility -- the ground truth a certification harness
  must be written against, since a cert tool that mishandles errors
  produces false passes.
- Verdict: **MUST** (free) -- keep open beside PMPP; it is a reference,
  not a linear read.

### 5. "Deep Learning Systems" (the Lipton / CMU attribution, resolved)

- What exists: (a) **CMU 10-414/714 "Deep Learning Systems: Algorithms
  and Implementation"**, Tianqi Chen & Zico Kolter -- a free course,
  not a book (dlsyscourse.org): lectures, slides, and assignments that
  build a PyTorch-class framework ("Needle") from scratch, autodiff
  through GPU kernels. (b) Zachary Lipton's actual book is *Dive into
  Deep Learning* (Zhang, Lipton, Li, Smola; free at d2l.ai) -- a deep
  learning *algorithms* text, not a systems text.
- Uniquely covers for certifying GPU racks: the CMU course is the best
  free explanation of why the framework layer drives GPU utilization
  the way it does -- useful when certifying against training
  workloads. D2L has nothing rack-specific.
- Verdict: the course is a **strong free companion** (not ranked; it
  is lectures + homework, not a book); D2L is a **SKIP** for this
  track.

### 6. "AI Systems" texts: Machine Learning Systems (MLSysBook)

- Author / edition / year: Vijay Janapa Reddi (Harvard), with the
  MLSys education community. **Two-volume textbook, MIT Press, 2026**:
  Vol. I *Introduction to Machine Learning Systems* (~1,000 pp.; free
  PDF May 2026) and Vol. II *Machine Learning Systems at Scale*. Free
  (HTML/PDF/EPUB) at mlsysbook.ai, actively maintained (last updated
  Sept 2026), with TinyTorch labs.
- Uniquely covers for certifying GPU racks: the whole stack between
  silicon and MLOps -- data pipelines, framework internals, training
  infrastructure, model compression, **hardware acceleration**, and
  dedicated **benchmarking** and **serving systems** chapters. This is
  the layer that defines the throughput/latency metrics a rack
  certification must actually measure.
- Verdict: **MUST** (free) -- read Vol. I's acceleration, benchmarking,
  and serving chapters; Vol. II when fleet-scale questions appear.

### 7. Modern GPU Programming for MLSys

- Author / edition / year: Tianqi Chen et al. (CMU), **free online
  book, 2026** (mlc.ai/modern-gpu-programming-for-mlsys, open source on
  GitHub). Grew out of the CMU MLSys course; a companion volume,
  *Agentic GPU Programming for MLSys*, exists alongside it.
- Uniquely covers for certifying GPU racks: the only 2026-current GPU
  kernel book, targeting **Blackwell (sm_100a / B200)** -- TMA and
  Tensor Memory, warpgroups, clusters, warp specialization. Part III
  builds a tiled GEMM to SOTA (TMA pipelining, persistent kernels,
  2-CTA clusters); Part IV builds FlashAttention-4; the appendices
  include **"Measuring and Analyzing GPU Kernel Performance"** -- a
  reproducible GPU benchmarking/profiling workflow -- and debugging
  warp-specialized kernels. Examples run via the TIRx DSL and need a
  Blackwell GPU.
- Verdict: **MUST** (free) for a B200/HGX-era certification program;
  the benchmarking appendix alone earns its slot.

### 8. Patterson & Hennessy GPU chapters (the "Kirk's COD" question)

- What exists: *Computer Organization and Design, RISC-V Edition*
  (Patterson & Hennessy, Morgan Kaufmann, 2020/21 -- the RISC-V
  successor to the 5th, MIPS, 2014 and ARM, 2016 editions) has a GPU
  section in ch. 6 ("Parallel Processors from Client to Cloud",
  sec. 6.6) plus the classic **Appendix B "Graphics and Computing
  GPUs"** (Appendix C in the 5th ed.; GeForce 8800 / G80 vintage:
  SIMT, warps, memory model).
  *Computer Architecture: A Quantitative Approach*, 6th ed. (2019) has
  the deeper treatment: ch. 4 "Data-Level Parallelism in Vector, SIMD,
  and GPU Architectures" (~40 pp. on GPUs) and ch. 7 "Domain-Specific
  Architectures" (Google TPU case study, systolic arrays).
- Attribution fix: COD/CAQA are by Patterson & Hennessy, not Kirk;
  Kirk's book is PMPP. (The "Kirk's COD" memory is best honored by
  reading PMPP plus CAQA's GPU chapter.)
- Uniquely covers for certifying GPU racks: architecture-level framing
  -- why utilization, peak-FLOPs, and bandwidth ceilings are shaped the
  way they are -- plus the TPU/DSA background needed for any
  non-NVIDIA inference silicon.
- Verdict: **SKIM** -- read CAQA 6th ed. chs. 4 + 7 from a library
  copy; do not buy COD just for its (2006-era hardware) appendix.

### 9. ML-engineering books with infra chapters

- *Designing Machine Learning Systems*, Chip Huyen, O'Reilly, June
  2022 (1st ed.). Infra-relevant: ch. 7 "Model Deployment and Prediction
  Service" (batch vs online, latency/throughput trade-offs, cloud vs
  edge) and ch. 10 "Infrastructure and Tooling for MLOps" (storage and
  compute layers).
- Uniquely covers for certifying GPU racks: the demand side -- what
  serving workloads expect from hardware (token throughput, latency
  SLOs). MLSysBook covers the same ground more rigorously and newer.
- Verdict: **SKIM** chs. 7 + 10 only. Related skips: Burkov's
  *Machine Learning Engineering* (2020, app-level MLOps) and Huyen's
  *AI Engineering* (2025, foundation-model app layer) -- **SKIP** for
  rack certification.

### 10. Groq / Cerebras architecture books

- Status: **no books exist.** Both companies publish whitepapers and
  conference talks instead: Cerebras' "Architecture Deep Dive" (Hot
  Chips 34, 2022) and WSE whitepapers (WSE-2: 850k cores, 40 GB
  on-chip SRAM, 20 PB/s; WSE-3: 44 GB SRAM, 21 PB/s memory bandwidth);
  Groq's LPU material (SRAM-only ~230 MB/chip, deterministic dataflow,
  GroqCard -> GroqNode (8 cards) -> GroqRack).
- Uniquely covers for certifying GPU racks: nothing in book form; if
  certification ever extends to non-NVIDIA inference silicon, start
  with the vendor whitepapers plus CAQA ch. 7 for the DSA framework.
- Verdict: **SKIP books** (there are none) -- vendor whitepapers only.

---

## Part 2 -- Storage / systems performance books

### 1. Systems Performance: Enterprise and the Cloud

- Author / edition / year: Brendan Gregg (Netflix/Intel performance
  engineer), **2nd edition, Addison-Wesley, 2020** (~800 pp.; no 3rd
  ed. announced as of Oct 2026). 16 chapters; the 2nd ed. added perf,
  Ftrace, and BPF chapters and largely dropped Solaris.
- Uniquely covers for certifying storage: ch. 2 Methodology (USE
  method, off-CPU analysis, workload characterization), ch. 8 **File
  Systems** (I/O stack, VFS, caches, latency analysis,
  micro-benchmarking), ch. 9 **Disks** (devices, I/O workloads,
  controllers, RAID, USE for disks), ch. 12 **Benchmarking** (benchmark
  types, methodology, and the ways benchmarks lie -- Gregg begs the
  industry to read it). This is the operating doctrine for turning a
  rack pass/fail into a measurement that means something.
- Verdict: **MUST** -- rank #1; the methodology backbone for both
  halves of the track.

### 2. Designing Data-Intensive Applications (DDIA)

- Author / edition / year: Martin Kleppmann; 1st ed. March 2017.
  **2nd ed. with Chris Riccomini published Feb 18, 2026** (O'Reilly,
  13 chapters, updated for AI-era workloads and cloud-native systems).
- Uniquely covers for certifying storage: the reliability vocabulary
  (ch. 1), storage-and-retrieval internals including B-tree vs LSM
  (ch. 3), replication (ch. 5), and consistency/consensus -- the
  durability semantics a distributed storage layer behind GPU racks
  promises. It is theory-first; no benchmarking methodology.
- Verdict: **SKIM** -- chs. 1, 3, 5 from the new 2nd ed.; first
  alternate (#9), not core rack-cert material.

### 3. The Art of Computer Systems Performance Analysis

- Author / edition / year: Raj Jain, Wiley, September 1991, 720 pp.
  Never revised, never out of print (print-on-demand); cited 8,600+
  times -- the benchmarking statistics bible.
- Uniquely covers for certifying storage (and everything else):
  measurement and error types, workload selection, probability and
  statistics (confidence intervals, comparing alternatives, paired
  tests), experimental design (2^k factorials), and queueing analysis
  (Little's law, operational analysis). The only book on this list
  that answers "how many runs, what variance, what confidence does a
  certification claim require?"
- Verdict: **MUST** -- rank #2; examples are pre-Linux but the math is
  timeless and directly applies to cert reports.

### 4. File System Forensic Analysis

- Author / edition / year: Brian Carrier, Addison-Wesley, 2005.
- Uniquely covers for certifying storage: on-disk structure
  archaeology for forensic recovery of deleted files -- explicitly
  outside a performance/durability certification scope.
- Verdict: **SKIP** (confirmed per scope: forensics, not performance).

### 5. Database Internals

- Author / edition / year: Alex Petrov, O'Reilly, September 2019.
  Part I "Storage Engines" (pp. 1-165) and Part II "Distributed
  Systems" (pp. 167-313).
- Uniquely covers for certifying storage: the I/O shapes database
  workloads impose -- B-tree variants and file formats, page/buffer
  management, **write-ahead logs and recovery**, LSM-trees and their
  many variants (Bw-Trees, FD-Trees, Bitcask, WiscKey), and
  transaction/recovery paths. This is what "database-grade" storage
  certification must reproduce.
- Verdict: **MUST-lite** -- Part I only, read selectively; the
  distributed half overlaps DDIA at lower rigor.

### 6. Operating Systems: Three Easy Pieces (OSTEP)

- Author / edition / year: Remzi & Andrea Arpaci-Dusseau
  (UW-Madison), **free online, version 1.10 (Nov 2023)**; print via
  Lulu/Amazon. The persistence "piece" (~chs. 36-48): I/O devices,
  hard disks, RAID levels, files and directories, file system
  implementation, FFS, **crash consistency: fsck and journaling
  (ch. 42)**, flash-based SSDs, log-structured file systems, data
  integrity and checksums, then NFS/AFS.
- Uniquely covers for certifying storage: crash consistency and
  checksum chapters are the conceptual core of power-loss and
  durability testing; free per-chapter PDFs with homework make it the
  cheapest rigorous on-ramp on this list.
- Verdict: **MUST** (free) -- rank #6; read the whole persistence
  part.

### 7. The PostgreSQL "fsync war" writeups (web, not a book)

- The canonical set: (1) Craig Ringer's pgsql-hackers thread
  "PostgreSQL's handling of fsync() errors is unsafe and risks data
  loss at least on XFS" (Mar 28, 2018) -- the original discovery that
  a retried fsync() can return success after EIO while the data was
  discarded (XFS AS_EIO page clearing); (2) LWN.net, "PostgreSQL's
  fsync() surprise" (April 2018, Jonathan Corbet); (3) the PostgreSQL
  wiki "Fsync Errors" page, which tracks the follow-ups including the
  USENIX ATC 2020 paper "Can Applications Recover from fsync
  Failures?"; (4) the PostgreSQL docs chapter "Reliability and the
  Write-Ahead Log" (ch. 30 in PG <= 16; renumbered ch. 28 in current
  PG 17/18 docs). Outcome: PostgreSQL PANICs on fsync() failure since
  PG 12 (commit 9ccdd7f6, Nov 2018, back-patched to 9.4).
- Uniquely covers for certifying storage: the definitive case study in
  why durability certification must inject EIO and power loss instead
  of trusting happy-path fsync -- the strongest argument for an
  error-injection rig in any storage cert program.
- Verdict: **MUST-READ** web set -- read alongside OSTEP ch. 42; not
  counted in the eight.

---

## Final ranked reading order for the certification-engineering track

Phase 1 -- Methodology: what "certified" has to mean

1. **Systems Performance, 2nd ed. (Gregg, 2020).** Read chs. 1-2 in
   full; chs. 8 (file systems), 9 (disks), and 12 (benchmarking)
   deeply; chs. 6-7 for GPU-host CPU/memory effects; keep 13-15
   (perf/Ftrace/BPF) as tooling reference. ~3 weeks.
2. **The Art of Computer Systems Performance Analysis (Jain, 1991).**
   Read the measurement, statistics, and comparison parts; use the
   queueing chapters when sizing cert soak durations. ~4 weeks; then
   it stays on the desk as the stats reference for every cert report.

Phase 2 -- GPU racks

3. **Programming Massively Parallel Processors, 5th ed. (Hwu, Kirk, El
   Hajj, 2026).** Chs. 1-6 for the model, then 19 (multi-GPU API), 22
   (heterogeneous cluster), 23 (matmul optimization). ~3 weeks.
4. **Modern GPU Programming for MLSys (Chen et al., 2026, free).**
   Part I for Blackwell organization; the "Measuring and Analyzing GPU
   Kernel Performance" appendix next; run the TIRx GEMM ladder if a
   B200 is available. ~1 week.
5. **CUDA C++ Programming Guide (NVIDIA, free, CUDA 13.4).** Not a
   linear read: memory management, streams, error handling, occupancy,
   and compatibility sections, consulted while writing cert harnesses.
   Ongoing reference alongside #3 and #4.

Phase 3 -- Storage

6. **OSTEP, persistence part (free, v1.10).** Chs. 36 onward through
   crash consistency (ch. 42), SSDs, and data integrity; pair ch. 42
   with the fsyncgate web set the same week. ~2 weeks.
7. **Database Internals, Part I (Petrov, 2019).** WAL and recovery,
   buffer pool, B-tree vs LSM -- the workload shapes storage certs
   must reproduce. ~1-2 weeks, selective.

Phase 4 -- The workloads that tie it together

8. **Machine Learning Systems, Vol. I (Reddi et al., MIT Press 2026,
   free).** The hardware-acceleration, benchmarking, and
   serving-systems chapters -- what the rack is certified *against*.
   ~2 weeks, selective. Vol. II optional for fleet-scale view.

Alternates, in order: DDIA 2nd ed. (Feb 2026) chs. 1/3/5; CAQA 6th ed.
chs. 4 + 7; Huyen's *Designing Machine Learning Systems* chs. 7 + 10;
the free CMU Deep Learning Systems course (dlsyscourse.org).

## Skip list (one line each)

- *CUDA by Example* (2010) -- CUDA 3-era intro; PMPP 5e + free NVIDIA
  docs supersede it.
- *The CUDA Handbook* (2013) -- never got its 2nd ed.; free text at
  cudahandbook.com if driver-API depth is ever needed.
- *File System Forensic Analysis* (2005) -- deleted-file forensics,
  out of scope.
- *Dive into Deep Learning* (Lipton et al.) -- DL algorithms, not
  systems.
- Burkov *Machine Learning Engineering* (2020) and Huyen *AI
  Engineering* (2025) -- application-level MLOps/GenAI layers.
- Groq / Cerebras "books" -- do not exist; whitepapers and Hot Chips
  talks only.

## Sources

All verified online Oct 2026.

| Topic                                              | Source                                                                                     |
|----------------------------------------------------|--------------------------------------------------------------------------------------------|
| PMPP 5th ed. (Feb 27, 2026)                        | <https://shop.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-443-43900-1> |
| PMPP 4th ed. record (2022, 551 pp.)                | <https://experts.illinois.edu/en/publications/programming-massively-parallel-processors-a-hands-on-approach> |
| Kirk/Hwu background, PMPP editions                 | <https://awards.acm.org/award-recipients/hwu_3270394>                                     |
| CUDA by Example (2010), still hosted by NVIDIA     | <https://developer.nvidia.com/cuda-example>                                                |
| The CUDA Handbook (2013; now free full text)       | <https://www.cudahandbook.com>                                                             |
| CUDA Toolkit docs, CUDA 13.4                       | <https://docs.nvidia.com/cuda/>                                                            |
| CUDA Programming Guide (restructured 2025-26)      | <https://docs.nvidia.com/cuda/cuda-programming-guide/index.html>                           |
| Modern GPU Programming for MLSys (2026, free)      | <https://mlc.ai/modern-gpu-programming-for-mlsys/>                                         |
| CMU 10-414/714 Deep Learning Systems (free course) | <https://dlsyscourse.org/lectures/>                                                        |
| Dive into Deep Learning (free)                     | <https://d2l.ai/>                                                                          |
| Machine Learning Systems, 2 vols (free, MIT Press) | <https://mlsysbook.ai/>                                                                    |
| Huyen DMLS chapter summaries                       | <https://github.com/chiphuyen/dmls-book/blob/main/summary.md>                              |
| Systems Performance 2nd ed. TOC                    | <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>                   |
| DDIA 2nd ed. publication (Feb 18, 2026)            | <https://news.ycombinator.com/item?id=45316520>                                            |
| DDIA 2nd ed. listing                                | <https://www.amazon.com/Designing-Data-Intensive-Applications-2nd-Maintainable/dp/B0H27BX5FH> |
| Jain book (720 pp., 8,600+ citations)              | <https://profiles.wustl.edu/en/publications/the-art-of-computer-systems-performance-analysis-techniques-for-e> |
| Database Internals (author site)                   | <https://www.databass.dev/>                                                                |
| OSTEP (free, v1.10)                                 | <https://pages.cs.wisc.edu/~remzi/OSTEP/>                                                  |
| fsyncgate: original pgsql-hackers thread (2018)    | <https://lwn.net/Articles/752093/>                                                         |
| fsyncgate: LWN "PostgreSQL's fsync() surprise"     | <https://lwn.net/Articles/752063/>                                                         |
| fsyncgate: PostgreSQL wiki                          | <https://wiki.postgresql.org/wiki/Fsync_Errors>                                            |
| PostgreSQL docs: Reliability and the WAL           | <https://www.postgresql.org/docs/current/wal-intro.html>                                   |
| COD RISC-V ed. (sec. 6.6 + Appendix B GPUs)        | <https://www.cse.iitd.ac.in/~rijurekha/col216_2025/HandP_RISCV.pdf>                        |
| COD ch. 6 GPU slides (RISC-V ed.)                  | <http://staff.ustc.edu.cn/~llxx/cod/reference_books/Computer%20Organization%20and%20Design%20RISC-V%20edition%20Slides.pdf> |
| COD "Graphics and Computing GPUs" appendix (ARM ed.) | <https://apprize.best/usability/interface/9.html>                                        |
| CAQA 6th ed. (GPU ch. 4, DSA ch. 7)                | <https://archive.org/details/computerarchitectureaquantitativeapproach6thedition>          |
| Cerebras whitepapers + Hot Chips 34 deep dive      | <https://www.cerebras.ai/whitepapers>                                                      |
| Groq/Cerebras system-level comparison              | <https://www.chipstrat.com/p/right-systems-for-agentic-workloads>                          |
