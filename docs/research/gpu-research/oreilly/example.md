# N12 — *CUDA by Example*

Research date: 2026-10-11. All claims below carry a source URL.

## 1. Scope and source access

[observed] This note evaluates N12 only for the defined two-hour `bench gpu` scope.
The scope covers per-GPU GB300/NVL72 device health, measured performance and correctness on the Chennai 18-tray/72-GPU rack.
PASS needs measured evidence.
Failures and exact SKIP reasons stay visible.
The scope excludes east-west and collective performance.
Per-GPU NVLink health stays in scope. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/oreilly/README.md>

[observed] The supplied O’Reilly catalog URL denies access (“You don't have permission to access”).
The researcher does not try an authentication bypass. <https://learning.oreilly.com/library/view/-/9780132180160/?orm_source=mcp>

## 2. Edition identity and contents

[observed] InformIT/Pearson names the book *CUDA by Example: An Introduction to General-Purpose GPU Programming*.
The book’s authors are Jason Sanders and Edward Kandrot.
InformIT/Pearson gives the publication date as July 19, 2010.
The publisher metadata names it the 1st edition.
The publisher metadata gives copyright 2011, distinct from the publication date.
Its product page lists ISBN-13 978-0-13-138768-3 (print ISBN) and 320 pages, not 312.

The supplied O’Reilly catalog identifier, 9780132180160, is a different ISBN.
This research cannot verify its format-specific metadata.
The captain’s 312-page catalog figure does not match the public InformIT print listing.
Do not silently treat this figure as print pagination. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683>

[observed] The publisher’s full public contents list these chapters.
They start with 1 “Why CUDA? Why Now?”; 2 “Getting Started”; 3 “Introduction to CUDA C”; 4 “Parallel Programming in CUDA C”.
Next come 5 “Thread Cooperation”; 6 “Constant Memory and Events”; 7 “Texture Memory”; 8 “Graphics Interoperability”.
They end with 9 “Atomics”; 10 “Streams”; 11 “CUDA C on Multiple GPUs”; 12 “The Final Countdown.”
The publisher listing verifies these contents.
The O’Reilly catalog record does not verify them. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683>

[observed] InformIT offers sample pages including Chapter 4 and the index.
The publisher page verifies chapter names.
It does not show GB300-specific applicability. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683>

## 3. Relevant chapters and practical value

### Chapter 4 — parallel programming

[inference] Test authors can use this chapter as a compact introduction to parallel kernel launches.
It also helps them reason about thread/block organization.
Port a deterministic elementwise transform or reduction as a correctness probe.
Compare every output against an independent CPU reference.
Record launch configuration, input, output/checksum, errors and duration.
The chapter topic gives test authors a method, but it does not define a certification test or GB300 threshold. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

### Chapter 5 — thread cooperation

[inference] Use shared-memory cooperation and synchronization examples to motivate a second kernel class.
This class goes beyond independent per-thread arithmetic.
Compare exact outputs only for an explicitly deterministic integer/checksum contract.
Floating-point reduction order can change results, so define a justified tolerance where the contract does not guarantee bitwise identity.
Record mismatch counts and keep the first failing index/value.
This check gives selected-test coverage, not proof of SDC-free operation. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>

### Chapter 6 — constant memory and events

[inference] CUDA events give a simple way to time work on a GPU stream.
A bench can use event timing around a fixed, warmed workload.
The bench then reports per-GPU elapsed time and throughput with clocks, power, thermals and throttling evidence.
Timing alone does not identify a cause or set a pass threshold.
Measure with a declared workload and calibrated profile.

Current CUDA docs describe CUDA events.
This bench applies the chapter topic when it uses them as a measurement technique. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

### Chapter 9 — atomics

[inference] Atomic-operation examples suggest a useful contention/synchronization correctness case.
Initialize known state, execute a fixed update count, and synchronize.
Then verify exact final integer values and report errors.
This case can exercise a distinct execution path.
It is not an HBM capacity test, a comprehensive instruction test, or a GB300 performance standard. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

### Chapter 10 — streams; Chapter 11 — multiple GPUs

[inference] Stream and multi-GPU chapters explain concurrency and device selection concepts.
These concepts can inform isolated per-device workload scheduling, event timing and stable GPU identity handling.
Do not run multi-GPU communication or collective benchmarks under this task.
Chapter 11 is not a reason to include east-west grading.
Query per-GPU NVLink link state/error counters separately, and keep before/after values.
Do not infer link health from a multi-GPU compute result. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## 4. Portable measured techniques (and limits)

1. **Reference-checked kernel [inference].** Run a small deterministic integer transform/reduction and synchronize. Compare every result with an independent CPU reference. Record GPU UUID, build/runtime versions, inputs, mismatch count and first mismatch. This check tests only selected code paths and data. Do not claim SDC absence. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>

2. **Event-timed fixed workload [inference].** Use CUDA events for repeatable per-GPU timing after warm-up. Publish repetitions and dispersion with achieved performance. Sample clocks, power, temperature and throttling reasons at the same time. Set acceptance only from a SKU/workload-specific profile, not this book. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

3. **Synchronization/atomic check [inference].** Run a bounded shared-state or atomic update with a known exact integer result. Record launch parameters and outcome. Do not treat this check as broad memory or compute coverage. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/>

4. **Separate memory-path probe [inference].** A simple streaming kernel can report bytes moved and elapsed time with a documented working set. Choose a working set large enough for the intended HBM claim, and report its size. Do not label a small cache-resident example “HBM bandwidth.” Use current supported diagnostics for production memory/RAS checks. Compare measured rates against a pinned profile. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>

[observed] The book predates current Blackwell/GB300 GPUs and contemporary CUDA tooling.
[inference] Review its examples, API conventions and assumptions before reuse.
Check them against current CUDA programming documentation and the actual toolkit/driver.
Old sample code is educational input, not a validated GB300 diagnostic.
The reviewed public table of contents does not show coverage of ECC, XID, row-remap, HBM/RAS, thermal or power.
It also does not show coverage of firmware, NVLink health semantics, or rack thresholds. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/cuda/cuda-c-programming-guide/> <https://docs.nvidia.com/deploy/nvidia-smi/index.html>

## 5. Relationship to accepted research spine

[observed] The accepted spine ranks four source groups above educational CUDA books for operational and version-specific behavior.
These groups are Gregg’s *Systems Performance* methodology and current NVIDIA DCGM diagnostics/release notes.
They also include NVIDIA `nvidia-smi`/NVML/event documentation and current CUDA programming/best-practices guides.
The spine keeps PMPP 4e for architecture understanding. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>

[inference] *CUDA by Example* adds a pragmatic introductory source for engineers who write small CUDA correctness and timing probes.
It does not supersede or materially update the spine’s current operational guidance.
Its content is confirmatory rather than new.
Current CUDA docs cover kernel parallelism, cooperation, events, atomics and streams more authoritatively.
PMPP covers these topics more systematically. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md>

[inference] Verdict: optional, selective reading for bench test authors.
It is not required for operators and is not an acceptance authority.
Keep measured PASS/FAIL/SKIP semantics and ECC/XID/remap counters from the existing spine.
Keep thermal/power/clocks and per-GPU NVLink health from the existing spine too.
The sources establish no universal GB300 thresholds or SDC-free guarantee. <file:///home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/books.md> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html> <https://research.nvidia.com/publication/2020-04_estimating-silent-data-corruption-rates-using-two-level-model>

## Gaps

[observed] The O’Reilly catalog page is inaccessible without permission.
Public search is unavailable during this pass.
So this research cannot verify the supplied catalog identifier’s format or the exact 312-page count.
It also cannot verify the identifier’s relationship to the InformIT print ISBN.
The public InformIT listing gives a complete chapter list and print metadata, but it says 320 pages. <https://learning.oreilly.com/library/view/-/9780132180160/?orm_source=mcp> <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683>

[inference] The researcher does not consult the full text.
Technique mapping uses chapter titles/topics and current primary CUDA documentation.
So this note marks chapter-specific procedural recommendations as inference.
The researcher makes no live measurements on the Chennai rack.
Test durations, coverage, and acceptance limits need a timed pilot on the actual supported GB300 configuration. <https://www.informit.com/store/cuda-by-example-an-introduction-to-general-purpose-9780131387683> <https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/dcgm-diagnostics.html>
