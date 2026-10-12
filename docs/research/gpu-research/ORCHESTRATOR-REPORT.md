# GPU research completion report

Research date: 2026-10-11.

## Result

Seven independent researchers complete nodes N01–N07.
The orchestrator keeps all seven accepted briefs after evidence checks and corrections.
The seven category nodes have no dependency edges.
The O'Reilly supplement adds ten source nodes, N08–N17.
Each source node uses the accepted N07 scope.

Ten researcher sessions use `openai-codex/gpt-6-luna` and names `oreilly-<shortslug>`.
No duplicate researcher starts. The existing Bondi child resumes once after a provider failure.
Each of the seventeen nodes has one short lesson and an accepted evidence summary.

The category files keep the complete returned briefs.
The node summaries link to those complete records. They do not replace them.

The distilled document has a failure catalog, a two-hour schedule, check tables, implementation tickets, and a reading list.
No researcher runs a live GPU test.
No executable GPU bench code changes.
All research writes stay inside `.lavish/gpu-research/`.

## Deliverables

- Research report: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/research.md`
- Distilled document: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/docs/gpu-bench-research.md`
- Brief index: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/README.md`
- Evidence review: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/evidence-review.md`
- Accepted node summaries: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/nodes/N01.md` through `N17.md`
- O'Reilly supplement: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/oreilly.md`
- Complete source notes: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/oreilly/`
- Supplement evidence review: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/oreilly/evidence-review.md`
- Complete briefs: `/home/avirus/.herdr/worktrees/rack-bench/research-gpu/.lavish/gpu-research/{neoclouds,hyperscalers,ai-labs,large-companies,clustermax,academia,books}.md`

The research role cannot write to project `docs/`.
The parent can copy the internal distilled document to `docs/gpu-bench-research.md`.

## Category verdicts

| Category | Verdict |
| --- | --- |
| Neoclouds | Providers use screening. Tenant visibility does not show device-specific GB300 results. |
| Hyperscalers | Use published DCGM/XID triage. Platform recovery does not show GPU correctness. |
| AI labs | Reference comparisons show some incorrect results. Peer agreement and short tests have important limits. |
| Large companies | Use layered fleet methods for repeated screening. CPU evidence does not show GPU detector sensitivity. |
| ClusterMAX | GPU workloads and eight-hour mixed burn-in show evidence. Injection mainly checks provider response. |
| Academia | Studies show heterogeneous failures and batch effects, not GB300 failure-rate estimates. |
| Books | Gregg shows the method. Matched NVIDIA guides show current operational semantics. |

## O'Reilly supplement result

All ten source notes return. The orchestrator keeps the complete notes and checks decisive public passages.
The supplement does not repeat category research or measure live GPUs.

- Use Gregg 2e as the general method reference.
- Keep current matched NVIDIA guides for commands, RAS, and platform support.
- Add Fregly's public companion as practical GPU measurement reading for test authors.
- Keep PMPP 4e as the verified architecture reference in this pass.
- Do not use a different catalog identifier as evidence of a new edition.
- Use 9780124159921 as the correct PMPP 2e product identifier.
- Keep publication dates, copyright years, page counts, and ISBN formats separate.
- Treat Cook, Professional CUDA C, CUDA by Example, Python/CUDA, and Bondi as optional reading.
- Keep Motta pending for contents verification.
- Do not copy configuration tuning from book companions into the bench.

The books brief and internal distilled reading list include these decisions.
No verified edition change replaces an existing preferred reference.
The supplement adds methods, not acceptance thresholds or measured two-hour feasibility.
[Source decisions](oreilly.md) · [Evidence checks](oreilly/evidence-review.md).

## Main decisions

- Count 72 physical GPUs across 18 trays. Do not count MIG instances as physical GPUs.
- Use the actual host map. Do not assume one host per tray.
- Keep collection status separate from quality assessment.
- Keep measurements from failed devices.
- For quality PASS, use declared, applicable rules.
- Keep missing thresholds separate from missing measurements.
- Keep unsupported fields, skipped checks, and exact reasons.
- Use bounded, supported diagnostics. Do not use one plugin override as a whole-suite duration limit.
- Keep configurations unchanged. Do not use automatic resets, counter clearing, or fault injection.
- Run active loads only with exclusive allocation and approved power/cooling policy.
- Keep per-GPU NVLink health. Exclude east-west and collective-performance tests.
- Do not apply A3 temperatures or historical GPU rates to GB300.

## Honest two-hour misses

The proposed schedule does not show measured rack feasibility.
The target rack still needs a representative-tray pilot and a controlled rack pilot.

A clean screen cannot show:

- Rare SDC absence or a useful field failure rate.
- Complete coverage of all HBM addresses, operations, and operating conditions.
- Eight-hour burn-in equivalence or lifetime reliability.
- Prior-use history or certified-pre-owned provenance.
- RMA eligibility or automatic repair success.
- Fabric performance or data-transfer correctness from passive link counters alone.
- Universal performance, temperature, clock, power, ECC, or NVLink acceptance limits.

## Source gaps

Public Microsoft evidence does not give a complete GPU screening recipe.
“Florence” remains unverified as a GPU screening tool.
AWS support-page details about XID-specific recovery remain partly unverified.
Current ClusterMAX TinyMeg2 use on GB300 remains unverified.
Provider thresholds and per-serial screening records remain largely unpublished.

O'Reilly denies access. The source pass does not include a full-book review.
Motta's TOC and several format/edition fields remain unverified.
Professional CUDA C and Python/CUDA lack complete verified chapter-title lists.
PMPP older-edition metadata and later-edition status remain incomplete.

Bondi's TOC identifier differs from the supplied record. Its edition/format mapping remains unverified.
Living companions can differ from published books.
[Exact source gaps](oreilly.md#gaps).

## Checks

The report checker finds seventeen nodes. It finds seventeen lessons below 50 physical lines.
All 42 Markdown artifacts exist. All relative Markdown links work.
All ten source notes have the exact date line, inference labels, and a final Gaps section.

The supplement lessons have 18–22 physical lines.
Each complete brief has the exact research-date line and a final Gaps section.
The orchestrator checks decisive provider, NVIDIA, OCP, study, and public-code passages.
The evidence review records corrections and source limits.
