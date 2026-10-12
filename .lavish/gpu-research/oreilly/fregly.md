# N13 — *AI Systems Performance Engineering*

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Access, identity, and evidentiary limits

[observed] The requested O’Reilly Learning URL returns HTTP 403 to an unauthenticated fetch.
This research does not access or bypass subscriber authentication.
This research does not inspect full book text.
The public O’Reilly catalog search result names *AI Systems Performance Engineering* and Chris Fregly.
Its chapter 13 page is also inaccessible (403). [O’Reilly catalog](https://learning.oreilly.com/library/view/ai-systems-performance/9798341627772/) [O’Reilly ch. 13 catalog page](https://www.oreilly.com/library/view/ai-systems-performance/9798341627772/ch13.html)

[observed] The author’s site names the book an O’Reilly 2025 publication.
The author’s site states 1,062 pages.
The public companion repository says “O’Reilly Book – November 2025”.
The repository independently lists the chapters and supplies code, labs, and a checklist.
So the requested 2025 publication is within scope.
This catalog/repository evidence is not book-text evidence. [Author site](https://fregly.com/) [Companion repository](https://github.com/cfregly/ai-performance-engineering)

[observed] The supplied O’Reilly identifier, ISBN 9798341627772, matches the online catalog URL and the author-site cover URL.
The companion and the O’Reilly catalog name Chris Fregly and O’Reilly.
The user-supplied `1062pp; 2025-11` agrees with those pages. [Author site](https://fregly.com/) [O’Reilly catalog](https://learning.oreilly.com/library/view/ai-systems-performance/9798341627772/)

[observed] 9798341627772 is the identifier in the supplied O’Reilly URL and matching catalog/cover URLs.
Call it the **catalog identifier**.
Its format remains unverified.
Without book access, I cannot verify a complete authoritative format-by-format ISBN list.
I also cannot verify a separately labeled edition number or title-page/copyright-page metadata.
This note makes no format inference. [O’Reilly catalog](https://learning.oreilly.com/library/view/ai-systems-performance/9798341627772/) [Companion repository](https://github.com/cfregly/ai-performance-engineering)

## 2. Public chapter list and relevance to GPU bench

[observed] The author’s public companion repository publishes this numbered 20-chapter list.
This list is a public TOC.
It does not prove that any particular technique or Blackwell-specific claim appears in the book’s inaccessible prose. [Companion repository](https://github.com/cfregly/ai-performance-engineering#book-chapters)

1. Introduction and AI System Overview
2. AI System Hardware Overview
3. OS, Docker, and Kubernetes Tuning
4. Tuning Distributed Networking Communication
5. GPU-based Storage I/O Optimizations
6. GPU Architecture, CUDA Programming, and Maximizing Occupancy
7. Profiling and Tuning GPU Memory Access Patterns
8. Occupancy Tuning, Warp Efficiency, and Instruction-Level Parallelism
9. Increasing CUDA Kernel Efficiency and Arithmetic Intensity
10. Intra-Kernel Pipelining and Cooperative Thread Block Clusters
11. Inter-Kernel Pipelining and CUDA Streams
12. Dynamic and Device-Side Kernel Orchestration
13. Profiling, Tuning, and Scaling PyTorch
14. PyTorch Compiler, XLA, and OpenAI Triton Backends
15. Multi-Node Inference Parallelism and Routing
16. Profiling, Debugging, and Tuning Inference at Scale
17. Scaling Disaggregated Prefill and Decode
18. Advanced Prefill-Decode and KV Cache Tuning
19. Dynamic and Adaptive Inference Engine Optimizations
20. AI-Assisted Performance Optimizations

[Inference] For this `bench gpu` scope, read chapters 1–2 for measurement framing and hardware context.
Read 6–12 for workload/kernel construction and performance analysis.
Read 13–14 for framework/compiler workload behavior.
Chapters 15–20 chiefly target serving, distributed scale, and adaptive optimization, not per-device RAS acceptance.
Chapter 4 is explicitly outside scope for east-west/collective performance.
Keep only per-GPU NVLink health per the task boundary. [Companion repository](https://github.com/cfregly/ai-performance-engineering#book-chapters) [Local scope](../research.md)

## 3. Portable techniques for the 18-tray / 72-GPU / two-hour bench

[inference] Run active workloads only when the GPU configuration stays unchanged from its approved baseline.
Active workloads also need exclusive allocation/quiescence for the tested devices.
They also need site-approved power and cooling conditions.
Record allocation and conditions.

Do not import companion-checklist suggestions to set/lock clocks, change power limits, or change MIG or persistence settings.
Do not import suggestions to tune OS/driver/platform state.
These actions are configuration changes outside this bench contract.
If the bench cannot collect a metric under the unchanged approved configuration, the metric is unavailable/SKIP.
This result does not give permission to alter the configuration. [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md) [NVIDIA `nvidia-smi`](https://docs.nvidia.com/deploy/nvidia-smi/index.html) [Local scope](../research.md)

1. **Matched, reproducible comparisons.** [observed] The public checklist prescribes identical shapes, precision, seeds, and staging for baseline/optimized runs.
   It prescribes warmups before steady-state timing, device-side CUDA events, and throughput plus latency.
   It also prescribes environment/command/version capture and archiving raw JSON/CSV artifacts. [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

   [inference] Apply this to each GPU’s fixed diagnostic workload.
   Do not import the book’s model benchmarks as health tests.
   Capture GPU UUID/BDF, tray mapping, driver/runtime/tool versions, and workload/config.
   Capture warmup and timed intervals, raw samples, and exact outcome.
   Under the fixed two-hour limit, limit repetitions explicitly and keep the actual duration.
   The repo does not show that its model recipes complete in two hours across 72 devices.

2. **Profile first; separate system-level and kernel-level diagnosis.** [observed] The public checklist says to begin with Nsight Systems and NVTX ranges for a CPU/GPU timeline.
   Next, it says to use Nsight Compute on selected kernels to inspect occupancy, stalls, and throughput.
   It recommends roofline analysis to distinguish compute- from memory-bound work. [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

   [inference] This method is portable when engineers diagnose a measured outlier or validate a workload harness.
   Use only bounded representative traces.
   Profilers perturb execution and do not replace the routine 72-device health/telemetry pass.
   Profiling adds a diagnostic method.
   It does not replace Gregg’s general experimental discipline or NVIDIA RAS/event semantics.

3. **Use distinct, representative memory and compute paths; measure the real working set.** [observed] Public chapter titles explicitly cover memory access, occupancy/ILP, arithmetic intensity, and pipeline techniques.
   The checklist describes coalescing, tiling/data reuse, double buffering, and asynchronous movement.
   It also describes keeping repeated-run data resident. [Companion TOC](https://github.com/cfregly/ai-performance-engineering#book-chapters) [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

   [inference] A bench can use a sustained HBM traffic workload and a compute/Tensor-Core workload as separate measurements.
   The bench records bytes/working-set size, precision, rates, and verified output.
   Do not infer full-HBM health from a small cache-resident buffer.
   Do not infer correctness from high throughput.
   The public source gives no GB300 `bench gpu` working-set requirement or universal pass rate.

4. **Correctness guard every optimization, with precision-specific comparison.** [observed] The companion checklist says to use CPU/FP32 references, checksums, or tolerance assertions.
   It says that engineers must validate fast paths. [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

   [inference] Transfer the principle to deterministic per-GPU CUDA kernels.
   Use fixed inputs/seeds, and check API and synchronization errors.
   Compare exact outputs only for an operation/build whose determinism guarantees it.
   Otherwise, use a justified precision-specific tolerance and record the contract.
   A finite selected-kernel suite is not exhaustive testing and does not test every HBM location/instruction.
   It cannot certify SDC-free hardware.

   This guard supplements rather than supersedes NVIDIA DCGM/RAS checks.

5. **Separate performance observations from health interpretation.** [observed] The repository frames performance around profile-first practice and useful throughput.
   Its checklist says to profile before and after and to pair throughput/latency.
   It also says to keep environment and raw results. [Companion repository](https://github.com/cfregly/ai-performance-engineering) [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

   [inference] For the rack, report per-GPU measured values and time-series telemetry.
   Report them with ECC/XID/remap state, clocks, power, and thermal readings.
   Report them with per-GPU NVLink status/counter deltas too.
   Label measured facts separately from policy verdicts.
   Use site-approved, SKU/config-specific limits or peer-relative outlier analysis.
   Do not turn a public performance-engineering checklist into a GB300 acceptance threshold.

[observed] The public checklist shows some numeric guidance.
It includes warm up before timing and average iteration time over 100 iterations as an example.
It includes 2–3 pipeline stages in one Triton tuning suggestion.
It includes sample figures such as “10%–40%” compile gains and “20%–50%” mixed-precision/compile gains.
These figures are general cookbook examples, not controlled GB300 measurements, target-device guarantees, or RAS limits. [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

[inference] Do not import them as bench thresholds or promise those speedups.
No consulted source establishes a universal GB300 performance floor from this book.
No consulted source establishes a two-hour SDC-free conclusion or a pass/fail ECC/remap count from this book.

## 4. Blackwell/GB300 evidence and limits

[observed] Public companion material explicitly describes its scope as modern NVIDIA GPUs.
It names Blackwell/GB200/GB300 in its overview/checklist.
Its public TOC includes hardware overview and CUDA/kernel chapters.
This material shows the companion’s stated hardware scope.
It does not show that the author tested every chapter’s code on GB300.
It does not show that the full text contains GB300-specific validation data.

The repository URL points to the living `main` branch, not a frozen book companion snapshot.
This review does not capture an immutable commit.
Treat observations as the public state accessed on the research date.
Pin a commit/release before you rely on version-sensitive code, tool, architecture, or performance claims. [Companion repository](https://github.com/cfregly/ai-performance-engineering) [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

[inference] N07 already accepts current NVIDIA operational documentation as authoritative for GB300 support and RAS semantics.
So this book does not supersede DCGM, `nvidia-smi`/NVML, operational-event documentation, or release notes.
It does not supersede OEM platform-specific instructions either.
Use it as a new GPU-workload construction and measurement-method spine.
It adds practical performance profiling, matched workload design, CUDA memory/kernel techniques, and correctness guardrails.
The repository’s broad checklist may confirm familiar methodology, but its prescriptions are not independent device-health specifications. [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html) [NVIDIA `nvidia-smi`](https://docs.nvidia.com/deploy/nvidia-smi/index.html) [NVIDIA GPU Operational Events](https://docs.nvidia.com/deploy/gpu-operational-events/latest/) [Companion checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

[inference] Relation to prior accepted sources: the book is **new** as a practical CUDA/PyTorch performance-workload guide for engineers.
It **confirms** disciplined profiling, reproducibility and reference-checked fast paths from accepted methodology.
It **does not supersede** Gregg for general systems performance reasoning.
It does not supersede NVIDIA for operational/RAS truth or PMPP 4e for CUDA architecture fundamentals.
No measured comparison is available to claim that this book materially improves or replaces those sources. [Companion repository](https://github.com/cfregly/ai-performance-engineering) [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html) [Gregg book page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) [PMPP publisher page](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

## 5. Sources and disposition

- [observed] **Kept:** O’Reilly catalog and chapter 13 catalog route — catalog identity and access-boundary reporting. This note does not treat them as book text. [Catalog](https://learning.oreilly.com/library/view/ai-systems-performance/9798341627772/) [Chapter 13](https://www.oreilly.com/library/view/ai-systems-performance/9798341627772/ch13.html)

- [observed] **Kept:** Chris Fregly author site — author attribution, O’Reilly/2025, 1,062 pages, cover identifier. [Author site](https://fregly.com/)

- [observed] **Kept:** Author’s living public GitHub companion — November 2025 publication statement, full numbered TOC, scope and public labs/checklist. It is not a frozen book edition. Pin a commit/release for date-sensitive claims. [Repository](https://github.com/cfregly/ai-performance-engineering)

- [observed] **Kept:** Public checklist — practical benchmark and CUDA recommendations. This note treats it as companion material. It is not proof of book-text coverage or GB300 certification. [Checklist](https://github.com/cfregly/ai-performance-engineering/blob/main/docs/appendix.md)

- [observed] **Kept for role comparison:** current NVIDIA DCGM and `nvidia-smi` manuals and GPU Operational Events. This group also has local N07 research and Gregg and PMPP publisher/author pages. They show relevant operational authority and accepted-source positioning. They give no evidence about inaccessible Fregly book text. [DCGM](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html) [nvidia-smi](https://docs.nvidia.com/deploy/nvidia-smi/index.html) [Operational Events](https://docs.nvidia.com/deploy/gpu-operational-events/latest/) [Local N07](../research.md) [Gregg](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) [PMPP](https://www.elsevier.com/books/programming-massively-parallel-processors/hwu/978-0-323-91231-0)

- [inference] **Dropped:** unauthorized full-text mirrors and non-primary review/retailer snippets for chapter content or Blackwell evidence. They cannot substitute for accessible authorized text or primary public companion material. [O’Reilly catalog](https://learning.oreilly.com/library/view/ai-systems-performance/9798341627772/) [Companion repository](https://github.com/cfregly/ai-performance-engineering)

## Gaps

[observed] O’Reilly returns 403.
This research does not independently verify the full text or a publisher-supplied complete format ISBN list.
It does not verify a separately stated edition number or precise printed publication-date/copyright metadata.
The user-supplied catalog metadata is consistent with the author and companion pages.
Metadata agreement is not book-text verification. [O’Reilly catalog](https://learning.oreilly.com/library/view/ai-systems-performance/9798341627772/) [Author site](https://fregly.com/) [Companion repository](https://github.com/cfregly/ai-performance-engineering)

[observed] The public repository gives a complete numbered TOC.
It does not give sufficient evidence to verify chapter body specifics or every code listing.
It does not give sufficient evidence to verify claims of GB300 execution or any GB300/RAS thresholds.
Its `main` branch is living, and this research captures no immutable revision.
So date-sensitive companion claims require a pinned revision. [Companion repository](https://github.com/cfregly/ai-performance-engineering)

[inference] Next step if authorized access becomes available: verify title/copyright pages and format-specific ISBNs.
Then inspect relevant chapters 1–2 and 6–14.
Test any proposed workload on a representative GB300 with pinned software and recorded results.
Do this test before you adapt the two-hour 72-GPU run.
Keep NVIDIA docs and the rack’s approved profile authoritative for pass/fail and health. [O’Reilly catalog](https://learning.oreilly.com/library/view/ai-systems-performance/9798341627772/) [NVIDIA DCGM diagnostics](https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html)
