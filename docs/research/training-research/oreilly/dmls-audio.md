# N02 — Designing Machine Learning Systems audiobook

Research date: 2026-10-11. All claims below use a source URL.

Bench safety: process interruption must not start without operator approval.
Default checks do not use power removal, PCIe reset, or hardware-error injection.
Show expected checkpoint rollback and replay separately from silent duplicate or skipped progress.

## 1. Verified identity, edition, chapters, access

1. [observed] O’Reilly’s supplied audiobook catalog shows *Designing Machine Learning Systems* by Chip Huyen and Kathleen Li. The record shows these data: July 2025, Ascent Audio performance, 12h 54m (774 minutes), English. The catalog shows 20 numbered chapters and a print/book edition link. [Audiobook catalog](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp)

2. [observed] The official book listing shows the print work as Chip Huyen’s May 2022 book, ISBN 9781098107956. The catalog shows the audiobook as a distinct ISBN/format. [O’Reilly book catalog](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956)

3. [observed] The author’s books page shows “Audiobook coming out in July 2025 on Audible” under *Designing Machine Learning Systems (O’Reilly, 2022)*. This shows an audio edition of the 2022 text. It does not show a newly updated technical edition. No inspected source can check every audio passage against the original text. [Chip Huyen, Books](https://huyenchip.com/books)

4. [inference] O’Reilly’s record shows both people in its “by” field. It does not show the narrator/author role split between the two people. The author’s book page shows Chip Huyen as the author. Do not put a narrator label on Kathleen Li without an explicit credit. [Audiobook catalog](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp) · [Author page](https://huyenchip.com/books)

5. [observed] The catalog chapter listing shows Chapter 1 through Chapter 20. The accessible page text does not show named chapter titles. [Audiobook contents](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp)

6. [observed] The audiobook page shows “Listen now Unlock full access”. The page keeps public catalog metadata accessible and listening gated. The chapter page and book catalog fetches show access-denied/403. This research does not check the audiobook or the underlying book text. [Audiobook access](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp) · [Book catalog](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956)

## 2. Training-validation and reliability coverage

[observed] The public catalog overview shows these topics: holistic system design, training-data processing, model evaluation, monitoring, ML platforms, and reliability/scalability/maintainability. Keep this as broad ML-systems material. It does not show a rack-acceptance or 54-day pretraining reliability procedure. [Audiobook overview](https://learning.oreilly.com/videos/-/9781663753076/?orm_source=mcp)

[inference] Use the audiobook for systems framing and compute/data/monitoring questions on the 18-tray GB300-class NVL72-class rack in Chennai. The metadata and overview do not show specific methods for MFU accounting, checkpoint/resume state, or interruption statistics. They also show no loss-spike diagnosis, flaky-node screening, or dataloader-stall methods. Do not put audiobook-specific technical assertions on unseen chapters. A PASS must use measured evidence on a named workload. Vendor specs and book coverage cannot make a PASS.

[calculated] The supplied rack context shows 466 interruptions total = 47 planned + 419 unexpected. Use 419 as the unexpected-interruption attribution denominator. Keep this as context for the training-validation work, not as an audiobook claim. [Llama 3, §3.3.4](https://arxiv.org/html/2407.21783v3)

[calculated] A 54-day run makes 648 two-hour observations (54×24 / 2). [inference] Two hours can make workload-specific short-window measurements and a bounded recovery exercise. It cannot show long-run reliability, rare-event rate, or convergence over 54 days. These proposals do not use destructive default fault injection.

## 3. Portable techniques (proposals; primary-source basis and measurable evidence)

The review keeps these items as [inference/proposal], not techniques verified in the audiobook. They use the book’s public system-level framing on the rack task. Current operational primary sources make their basis.

1. **Make the MFU accounting against a fixed recipe.** Keep model/configuration, precision, sequence length, global batch, parallelism, and warm-up exclusion in the record. Also keep the measurement interval, tokens/s, step-time distribution, and declared FLOP convention in the record. Check results only against a stated workload target/reference. Do not make a universal GB300 gate. Evidence: a reproducible configuration plus measured throughput and calculation. [NVIDIA Megatron-LM](https://github.com/NVIDIA/Megatron-LM)

2. **Check checkpoint and resume state safely.** Make a checkpoint during a representative run. Check it, then run a scheduled process/job restart in an isolated acceptance window. Keep save/load time, restored step, optimizer/model state, consumed-data position, sampler/RNG state where applicable, and lost work in the record. Run the silent duplicate/skipped-step check, and put expected checkpoint rollback and replay in separate report lines. Evidence: successful resumed steps and checkpoint integrity under the tenant’s trainer. [PyTorch Distributed Checkpoint](https://docs.pytorch.org/docs/stable/distributed.checkpoint.html) · [torchrun fault-tolerance tutorial](https://docs.pytorch.org/tutorials/beginner/ddp_series_fault_tolerance.html)

3. **Make interruption statistics explicit.** Put planned and unexpected counts in separate report lines. Use 419 as the denominator for unexpected-interruption attribution in the supplied history. Show missing/unknown attribution; do not silently remove cases. For new observations, keep exposure hours, event timestamps, cause confidence, and censored/unknown events in the record. Evidence: an auditable event ledger and denominator; keep this as accounting discipline, not a reliability forecast.

4. **Check loss spikes with corroborating signals.** Keep loss, gradient/parameter norms, rank identity, step/data position, hardware/error telemetry, and nearby collective/loader timing in the record. Check them against a run-specific baseline before the resume decision. Do not use loss alone as proof of hardware fault or health. Evidence: timestamp-correlated traces and a documented disposition. [SDC study](https://arxiv.org/html/2604.00726v1) · [NVIDIA Megatron Bridge resiliency](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html)

5. **Check stragglers and loader stalls under the actual workload.** Keep per-rank step latency/tokens per second, input wait time, storage read latency/throughput, and CPU utilization in the record. Check persistent outliers and their node-telemetry correlation. Evidence: rank-level distributions and stall attribution in the measured interval, not a generic hardware threshold. [NVIDIA Megatron Bridge resiliency](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html) · [PyTorch profiler recipe](https://docs.pytorch.org/tutorials/recipes/recipes/profiler_recipe.html)

## 4. Relation to canon

[observed] The canon, [books.md](../books.md), already puts DMLS beside *Reliable Machine Learning* as broad systems framing. It puts operational Megatron Bridge/PyTorch documentation and reliability papers above books for distributed-training failure engineering. It puts DMLS under these topics: distributed-training and debugging framing, monitoring/data-shift, and infrastructure/resource-management. The canon keeps this limit: verified contents do not show detailed checkpoint/restart procedures.

[inference] Keep this audiobook as format duplication of the same 2022 work, not independent technical evidence. Keep it as an accessibility/format option, not a new book or corroborating source. Its 2025 release and 774-minute runtime do not make the underlying text a 2025 technical revision. This note makes these additions beyond the canon: verified audiobook identity, access limits, chapter-count-only evidence, and role-attribution uncertainty. It keeps DMLS’s technical rank unchanged.

## Gaps

- The publisher’s public audiobook page does not show the narrator name or the author/performer role split. The review keeps Kathleen Li’s role unverified.

- This pass cannot check the audiobook’s numbered chapter titles or audio/text contents directly. This note makes no chapter-topic claims beyond the public overview.

- No evidence here shows rack-specific pass thresholds, long-run failure probability, convergence, or feature applicability to the installed tenant stack. Two hours cannot show 30–90-day reliability or 54-day training convergence.
