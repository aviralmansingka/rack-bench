# N15 — Programming Massively Parallel Processors edition comparison

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Access and scope

- **[observed]** The researcher fetches the requested O’Reilly Learning URL (`https://learning.oreilly.com/library/view/-/9780323984638/?orm_source=mcp`) first.
  It returns HTTP 403 Forbidden.
  The researcher makes no authentication bypass attempt.
  So the researcher cannot inspect the O’Reilly title page directly. [O’Reilly URL](https://learning.oreilly.com/library/view/-/9780323984638/?orm_source=mcp)

- **[observed]** The local GPU-research brief describes the intended use.
  The bench checks GB300/NVL72 GPU health/performance/correctness across 18 trays/72 GPUs in Chennai.
  The bench runs for two hours and keeps measured PASS/failure data/reasoned skips.
  It covers ECC/XID/remaps/SDC/HBM/thermal/power/clocks/bit-exact checks and per-GPU NVLink health.
  It does not cover east-west or collective tests. [Local books brief](../books.md)

- **[inference]** N15 is solely a catalog and reading-value comparison of editions in the same PMPP title family.
  It does not establish a GB300 health test or any hardware threshold.

## 2. Edition and identifier evidence

1. **[observed] Second edition — ISBN 9780124159921.** Elsevier Shop gives the title as “2nd Edition”.
   An Elsevier Educate search result gives 2012, 514pp.
   The 2012/514pp values come from the search result, not fetched page fields.

   The earlier note links ISBN 9780123814722 to 2e from an unfetched WorldCat record.
   I withdraw that assignment.
   That ISBN may be 1e. [Elsevier Shop product](https://shop.elsevier.com/books/programming-massively-parallel-processors/kirk/978-0-12-415992-1) [Elsevier Educate product](https://educate.elsevier.com/book/details/9780124159921)

2. **[observed] Third edition metadata remains unverified in this run.** I link a WorldCat record but do not fetch its bibliographic fields.
   Do not treat the previous 2016/576pp/9780128119860 values as observed. [WorldCat record](https://search.worldcat.org/title/Programming-massively-parallel-processors-%3A-a-hands-on-approach/oclc/920017275)

3. **[observed] Fourth edition — 2022, 580 pages, three authors.** Elsevier’s publisher page names Wen-mei W. Hwu, David B. Kirk, and Izzat El Hajj.
   It gives the TOC and publisher ISBN 9780323912310.
   It names the edition “Fourth Edition.” [Elsevier publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

4. **[inference] O’Reilly identifier 9780323984638 format and edition relationship are unverified.** The supplied identifier differs from the publisher’s 4e ISBN.
   The requested O’Reilly page is inaccessible.
   The search service returns HTTP 429 for all queries.
   So this report cannot independently verify O’Reilly’s exact format label or product metadata. [O’Reilly URL](https://learning.oreilly.com/library/view/-/9780323984638/?orm_source=mcp) [Elsevier 4e publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

5. **[observed] Later edition status as of the requested date is unverified.** Publisher 4e evidence and failed search do not prove that no later edition exists by 2026-10-11.
   No primary later-edition catalog evidence is accessible in this run.
   **Verdict: no evidence here that a new edition supersedes 4e; do not assert that none exists.** [Elsevier 4e publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

## 3. Fourth-edition contents and chapter relevance

**[observed]** Elsevier’s contents list these chapters.
The list starts with 1 Introduction; 2 Heterogeneous data parallel computing; 3 Multidimensional grids and data.
Next come 4 Compute architecture and scheduling; 5 Memory architecture and data locality; 6 Performance considerations.
Next come 7 Convolution; 8 Stencil; 9 Parallel histogram; 10 Reduction and minimizing divergence; 11 Prefix sum (scan).
Next come 12 Merge; 13 Sorting; 14 Sparse matrix computation; 15 Graph traversal; 16 Deep learning.
Next come 17 Iterative MRI reconstruction; 18 Electrostatic potential map; 19 Parallel programming and computational thinking.

Next come 20 Heterogeneous computing cluster/CUDA streams; 21 CUDA dynamic parallelism.
Next come 22 Advanced practices and future evolution; 23 Conclusion and outlook.
The list ends with Appendix A Numerical considerations. [Elsevier publisher TOC](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

- **[inference]** For authors of the rack bench, prioritize chapters 4–6 (execution/scheduling, memory locality, performance).
  Also prioritize 10 (reduction/divergence) and Appendix A (numerical considerations).
  Chapters 2–3 provide programming/execution foundations.
  This item is a relevance recommendation.
  It does not claim that these chapters provide device-health procedures. [Elsevier publisher TOC](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

- **[inference]** Chapters 7–18 provide useful workload-pattern examples.
  They are selective implementation material.
  They do not cover all GB300 instructions, HBM addresses, fault modes, or precision paths.
  Chapter 20’s cluster programming is not a reason to add east-west/collective certification to N15’s scope. [Elsevier publisher TOC](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

## 4. Portable techniques for the bench

1. **[inference] Separate compute from memory tests.** Use a compute-heavy kernel and a streaming/copy workload as distinct measurements.
   Memory locality and compute scheduling are different bottlenecks.
   Value: this separation makes a slow result easier to localize.
   Limit: neither test alone identifies a defective component or supplies an acceptance threshold. [Elsevier, chs. 4–6](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

2. **[inference] Use more than one access pattern and data shape.** Compare coalesced streaming access with representative strided/structured patterns.
   Vary dimensions.
   Value: this method exposes some address/layout-sensitive regressions that one kernel may miss.
   Limit: sampled patterns do not cover all HBM cells or address interactions. [Elsevier, chs. 3, 5, 7–9](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

3. **[inference] Include reductions and synchronization-sensitive work.** A reduction/checksum workload exercises aggregation and synchronization behavior.
   This behavior goes beyond independent elementwise operations.

   Value: the workload adds a distinct execution pattern and a compact result for validation.
   Limit: floating-point reduction order can affect rounding.
   Exact comparison is appropriate only under a pinned deterministic implementation contract. [Elsevier, ch. 10 and Appendix A](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

4. **[inference] Validate outputs independently and report the arithmetic contract.** Use fixed inputs/seeds and a CPU or separately trusted reference.
   Use bitwise equality only where operation, compiler/library, algorithm, and math mode guarantee reproducibility.
   Otherwise, use a justified tolerance.
   Value: this check detects observed wrong answers rather than treating throughput as correctness.
   Limit: finite checks do not prove SDC-free operation. [Elsevier, Appendix A](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0) [NVIDIA CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)

5. **[inference] Measure under controlled, declared conditions.** Record workload, dimensions, precision, duration, clocks/power/thermal context and repeated measurements.
   Distinguish warm-up from measured interval.

   Value: this record makes results comparable and interpretable.
   Limit: textbook principles do not supply a universal GB300 pass limit.
   Use a site/SKU profile or mark absolute grading unavailable. [Elsevier, ch. 6](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

## 5. Decision

- **[inference] Confirm 4e as the relevant PMPP edition evidenced here.** The catalog record gives 2022/580pp/three authors.
  It comes with the publisher TOC and ISBN 9780323912310.
  The O’Reilly 9780323984638 URL is not evidence of a different edition.
  Access fails, so its format and relationship to 4e remain unverified. [Elsevier publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0) [O’Reilly URL](https://learning.oreilly.com/library/view/-/9780323984638/?orm_source=mcp)

- **[inference] Do not claim that a later edition supersedes 4e as of 2026-10-11.** This research confirms no later edition.
  Primary evidence sufficient to rule one out is unavailable. [Elsevier 4e publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

- **[inference] Bench value is selective and architectural.** Keep it as an optional resource for test authors, chiefly chapters 4–6, 10, and Appendix A.
  Current NVIDIA operational docs remain authoritative for ECC, XIDs, remapping, and NVLink state.
  They also remain authoritative for supported tools and platform behavior. [Elsevier publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0) [NVIDIA `nvidia-smi` guide](https://docs.nvidia.com/deploy/nvidia-smi/index.html)

## Sources

- Kept: [Elsevier, *Programming Massively Parallel Processors*, 4e](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0) — primary publisher edition identity and full chapter listing.
- Kept: [O’Reilly Learning requested product URL](https://learning.oreilly.com/library/view/-/9780323984638/?orm_source=mcp) — supplied catalog identifier. A direct fetch gets access denial (403). So format metadata remains unverified.
- Kept: [WorldCat 2e catalog](https://search.worldcat.org/title/Programming-massively-parallel-processors-%3A-a-hands-on-approach/oclc/762326567) and [WorldCat 3e catalog](https://search.worldcat.org/title/Programming-massively-parallel-processors-%3A-a-hands-on-approach/oclc/920017275) — publisher product identity. The researcher does not fetch fields from the WorldCat records. They are not observed evidence.
- Kept: [NVIDIA CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/) — operational contrast for correctness and numerical claims.
- Dropped: Search-result-derived edition assertions — Tavily rate-limits the searches (429). This note treats no unverified search snippets as evidence.

## Gaps

- **[observed]** O’Reilly page access returns 403, and web search returns 429.
  So the researcher cannot check its product-format metadata or any linked sample/TOC. [O’Reilly URL](https://learning.oreilly.com/library/view/-/9780323984638/?orm_source=mcp)

- **[observed]** No primary source in this run verifies whether a fifth or later edition exists by 2026-10-11.
  So the “not superseded” outcome is unproven, not a negative finding. [Elsevier 4e publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

- **[observed]** The 2e publisher product fetch exposes the TOC but not bibliographic metadata fields.
  An Elsevier Educate search result supports 2012/514pp.
  3e metadata and TOC remain unverified.
  The researcher does not fetch fields from the WorldCat record, and it is not observed evidence. [Elsevier Shop 2e](https://shop.elsevier.com/books/programming-massively-parallel-processors/kirk/978-0-12-415992-1) [Elsevier Educate 2e](https://educate.elsevier.com/book/details/9780124159921) [WorldCat 3e record](https://search.worldcat.org/title/Programming-massively-parallel-processors-%3A-a-hands-on-approach/oclc/920017275)

### Targeted catalog evidence correction

- **[observed]** The researcher fetches the Elsevier Shop 2e product page successfully.
  Its extracted body returns the TOC but not the title-page ISBN/authors/year/page-count fields.
  Elsevier Educate’s product result identifies ISBN 9780124159921.
  It lists the 2012/514pp Kirk/Hwu Morgan Kaufmann entry. [Elsevier Shop 2e](https://shop.elsevier.com/books/programming-massively-parallel-processors/kirk/978-0-12-415992-1) [Elsevier Educate 2e](https://educate.elsevier.com/book/details/9780124159921)

- **[observed]** The researcher does not fetch metadata fields for earlier WorldCat citations for 2e and 3e.
  They are not evidence in this note.
  This note withdraws the earlier 2e ISBN assignment 9780123814722.
  The 3e bibliographic particulars remain uncertain pending a primary publisher product fetch. [WorldCat 2e record](https://search.worldcat.org/title/Programming-massively-parallel-processors-%3A-a-hands-on-approach/oclc/762326567) [WorldCat 3e record](https://search.worldcat.org/title/Programming-massively-parallel-processors-%3A-a-hands-on-approach/oclc/920017275)

- **[observed]** The O’Reilly page fetch fails with HTTP 403.
  The researcher observes no metadata.
  This note does not label 9780323984638 an ebook ISBN. [O’Reilly URL](https://learning.oreilly.com/library/view/-/9780323984638/?orm_source=mcp)
