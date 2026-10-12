# Training research handoff

Research date: 2026-10-11.
Status: seven accepted category briefs; seven completed independent category nodes.
Supplement: ten accepted source notes; ten completed independent source nodes.

## 1. Decision

Two hours can show measured behavior for a named workload and checkpoint path.
The test can also check approved process-recovery paths.
Two hours cannot show 30–90-day reliability or a 54-day completion probability.
No artifact shows a measured rack PASS.
The tenant must make these decisions: the workload, thresholds, numerical tolerances, and checkpoint target.

Target: one GB300-class NVL72-class rack, 18 trays, Chennai, India.
Branch: `research/training`.
Worktree: `/home/avirus/.herdr/worktrees/rack-bench/research-training`.

## 2. Category verdicts

“Accepted” shows an answer to the brief's bounded research question.
It does not show a rack PASS for the category.
Every brief keeps unresolved evidence under `## Gaps`.

| Node | Category | Research verdict | Result and remaining limit |
| --- | --- | --- | --- |
| N01 | neoclouds | Accepted | Provider tools and policies show differences. Public records do not show comparable multi-week job rates. |
| N02 | hyperscalers | Accepted | Check actual transport and resume support. The review keeps Azure ND-specific notice and recovery limits unresolved. |
| N03 | ai-labs | Accepted | Check interruption denominators and complete resume state. Public runs do not show rack survival. |
| N04 | large-companies | Accepted | Put rank timing and resource events together. The test must use longer intervals for fleet history and delayed-corruption evidence. |
| N05 | clustermax | Accepted | Published methods show real dense/MoE training. Public omissions do not show private-method omissions. |
| N06 | academia | Accepted | Check snapshot, persistence, publication, and recovery separately. Short exposure cannot show rare-event rates. |
| N07 | books | Accepted | Use current framework guides first. Visible book contents do not show executable rack acceptance procedures. |

The children use `agent="researcher"` and `model="openai-codex/gpt-6-luna"`.
The run uses exactly seven category researchers.
The orchestrator starts the same children again for corrections.
No child starts another agent.

## 3. Decisive evidence checks

The orchestrator checks the following source passages independently.
The orchestrator uses the source claims to check the briefs and proposed checks.
The checks do not run the published experiments.

| Source | Checked passage | Accepted meaning |
| --- | --- | --- |
| [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) | Training, burn-in, fault handling, provider observations. | Llama 3.1 8B and GPT-OSS MoE training; eight-hour burn-in; bounded recovery events. |
| [Public cmax](https://github.com/SemiAnalysisAI/clustermax) | README scope and exclusions. | Public audit and the full internal suite use different scopes. |
| [Llama 3](https://arxiv.org/html/2407.21783v3) | §3.3.4 and interruption table. | 466 total interruptions; 47 planned; 419 unexpected; more than 90% effective training time. |
| [PaLM](https://arxiv.org/html/2204.02311) | §4.1, §5, §5.1, Appendix B. | MFU does not use recomputation; checkpoint replay can make identical state in its deterministic stack. |
| [BLOOM chronicles](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md) | March–May 2022 incidents. | Optimizer, TP, RNG, loader, and hang defects can make otherwise active training invalid. |
| [MegaScale](https://www.usenix.org/system/files/nsdi24-jiang-ziheng.pdf) | §§4–6. | Heartbeats, rank timing, diagnostic recovery, and host staging run before durable persistence. |
| [Meta hardware methods](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable/) | Fault types and SDC detection. | Operators must use different tests for load-dependent and silent faults. Corruption checks can show in-range corruption after weeks of delay. |
| [Megatron Bridge](https://docs.nvidia.com/nemo/megatron-bridge/latest/training/resiliency.html) | Feature sections and practical caveats. | Check enabled features, launcher constraints, profiling conflicts, and experimental rerun limits. |
| [AWS EFA recipe](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa-start-nccl.html) | Installation, tests, and NCCL logs. | Check the selected transport. Generic versions do not make a GB300 compatibility matrix. |
| [MLPerf rules](https://github.com/mlcommons/training_policies/blob/master/training_rules.adoc) | Divisions, checkpoint rules, utilization appendix. | Quality scoring and crash-recovery certification use different criteria. |
| [CheckFreq](https://www.usenix.org/system/files/fast21-mohan.pdf) | §§3–4. | Overwrites and missing persistence can remove checkpoints. Check snapshot and persistence separately. |
| [Oobleck](https://arxiv.org/html/2309.08125v2) | §§3, 5. | Recovery makes missing state from pipeline replicas within its resource and failure assumptions. |
| [Varuna](https://www.microsoft.com/en-us/research/wp-content/uploads/2022/03/varuna-eurosys22.pdf) | §§4.5–4.6, 6. | Layer checkpoints use local SSD and background cloud copies. Heartbeats show slow workers. |
| [AEGIS](https://www.usenix.org/conference/osdi26/presentation/lei) | Abstract and deployment results. | Large-fleet SDC evidence shows detection limits, not a rack-specific two-hour threshold. |

Vendors can make changes to live documentation after this research date.
Keep source versions and software releases fixed before operators run the suite.
Publisher access limits keep some book findings within visible contents.

## 4. Corrections and conflicts

- The Llama hardware percentages use unexpected interruptions, not all 466 interruptions.

- Some printed subtype percentages do not show a match with the printed counts.

- The report keeps this conflict visible instead of a silent change to the source table.

- Meta's separate blog shows more than 95% effective training time.

- The 405B paper shows more than 90%; the reports use different contexts.

- Do not use synthetic-only or checkpoint-only labels for ClusterMAX 3.0.

- Its recovery endpoints do not show restored training-state equivalence.

- Nebius's one 8h40m GB300 event does not show provider-wide MTTR.

- Together's reported health-check timeout shows that diagnostics can remove active work.

- In MLPerf Open, submitters can use arbitrary stopping criteria with reported quality.

- General checkpoint optionality shows a Qwen3.5 post-training checkpoint-series exception.

- Oobleck uses replica reconstruction, not generic asynchronous checkpointing.

- Varuna uses elastic configurations and checkpoint-based recovery with background copying.

- The reading plan keeps DMLS and Reliable Machine Learning in one equal-priority reading tier.

- The orchestrator removes an unsupported DMLS failure-scope exclusion.

- The large-companies child puts checkpoint, SDC, thermal, and goodput sections back after a revision error.

ClusterMAX and academia each run into a `WebSocket closed 1000` delivery failure.
The orchestrator starts those same sessions again.
Both children make their remaining corrections.
The run does not remove either child.

## 5. Proposed suite

The distilled document shows 17 failure modes, 12 check families, and 12 proposed implementation tickets.
Its 120-minute schedule keeps provenance, reference steps, rack training, recovery, checkpoint rejection, and reporting separate.
Use the schedule as a proposal, not a measured duration for this rack.
Large checkpoints can run longer than the allocated recovery window.
Show incomplete coverage instead of an undisclosed small checkpoint.

MFU uses a declared FLOP convention and precision-specific peak.
Wall-clock goodput shows unique accepted progress across the complete elapsed window.
Do not make a second count of rollback or replay.
Show executed tokens separately.
Use paid GPU-hour goodput only with actual allocation and billing records.

The suite uses `PASS`, `FAIL`, `NOT_TESTED`, and `INCONCLUSIVE` per assertion.
Without a predefined numeric threshold, show the measurement instead of a performance PASS.
Process interruption starts only after operator approval.
The default suite does not use PCIe resets, hardware-error injection, or power removal.

## 6. Honest two-hour misses

- Rare or correlated failure rates over 30–90 days.

- All silent-error types or delayed numerical effects.

- Full model convergence and tenant-data correctness.

- Day/night and seasonal Chennai cooling or power behavior.

- Aging, recurring suspect-node history, and firmware changes.

- Recovery-time tail distributions and spare-capacity exhaustion.

- Long checkpoint retention and correlated storage/site failures.

- Multi-rack contention and scale-out behavior.

- Untested topology, precision, framework, or trainer configurations.

- The published eight-hour ClusterMAX burn-in.

## 7. Validation and scope checks

The report validator shows no errors for seven nodes and seven lessons below 50 physical lines.
A separate sentence-length check shows no orchestrator prose sentence with 20 or more words.
The seven briefs show the exact requested date line and final `## Gaps` heading.
The source-anchor review puts explicit bases in the neocloud and book recommendations.

The section-reference review checks the neoclouds §§8–9 and large-companies §§4–6 references.
All report links send readers to saved artifacts.
The orchestrator makes no changes to project code or hardware.

Validator command:

```sh
node /home/avirus/.agents/skills/research/scripts/check-report.mjs /home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/research.md
```

The harness makes no `mermaid` tool available in this session.
The report shows the full Mermaid source map.
The structural validator checks its node set.
This run shows no rendered-diagram check.

## 8. Absolute artifact paths and placement

Run directory: `/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/`.

- [research.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/research.md)

- [ORCHESTRATOR-REPORT.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/ORCHESTRATOR-REPORT.md)

- [Staged distilled document](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/docs/training-bench-research.md)

- [neoclouds.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/neoclouds.md)

- [hyperscalers.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/hyperscalers.md)

- [ai-labs.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/ai-labs.md)

- [large-companies.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/large-companies.md)

- [clustermax.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/clustermax.md)

- [academia.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/academia.md)

- [books.md](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/books.md)

The orchestrator keeps all writes inside the run directory.
The requested project destination uses this path: `/home/avirus/.herdr/worktrees/rack-bench/research-training/docs/training-bench-research.md`.
The project keeps a copy outside this run directory.
Its reading list does not show the supplement's platform chapters.
The parent must put the staged reading-list changes into that copy.

Keep other agents' project changes.
For a new project copy, use `../.lavish/training-research/<category>.md` for its seven opening brief links.
For the catalog-supplement link, put `../.lavish/training-research/oreilly.md` in the project copy instead of `../oreilly.md`.
Keep the staged document's current links unchanged.
The parent makes the project placement and commit decisions.

## 9. O'Reilly catalog supplement

The supplement uses ten parallel source researchers.
Each child uses `agent="researcher"` and `model="openai-codex/gpt-6-luna"`.
The ten source nodes show no dependencies.
This supplement keeps the seven original category nodes unchanged.
This phase makes changes to reading decisions, not to the proposed measured assertions.
It makes no rack measurement or measured PASS.

“Accepted” shows useful evidence and its limits in the source note.
It does not show that the researcher checks every chapter or video.
Each note shows three to five proposed checks and a final `## Gaps` section.
The notes keep source procedures separate from proposed rack checks.

| Source node | Source | Research verdict | Reading decision and limit |
| --- | --- | --- | --- |
| N01 | DMLS | Accepted with access limits | Keep general systems priority. Contents do not show executable rack recovery. |
| N02 | DMLS audiobook | Accepted with format limits | Alternate format, not new technical evidence. The review keeps narrator role and passage equivalence unresolved. |
| N03 | Machine Learning System Design | Accepted with sample limits | Put optional pipeline testing and monitoring on the reading list. Samples do not show complete resume state. |
| N04 | Reliable Machine Learning | Accepted with access limits | Keep beside DMLS. Evidence does not show an operational training headline. |
| N05 | DMLS in the Cloud | Accepted with metadata limits | Keep optional. The review keeps date, runtime, and playback unverified. |
| N06 | Parallelism Deep Dive | Accepted with playback limits | Put optional parallelism and checkpoint concepts on the reading list. The review keeps recovery results unverified. |
| N07 | Machine Learning Platform Engineering | Accepted with sample limits | Put selected platform chapters before older cloud-specific pipeline material. No full-book supersession. |
| N08 | Designing Deep Learning Systems | Accepted with metadata limits | Put optional training-service context on the reading list. Publisher and supplied coauthor records show different names. |
| N09 | Deep Learning for Vision Systems | Accepted with metadata limits | Low priority for pretraining reliability. The review keeps the supplied year and page count unverified. |
| N10 | System Design Video Edition | Accepted with explicit product gap | Alternate format. Platform Engineering Video Edition shows no supplied matching URL. |

The audiobook child runs into `WebSocket closed 1000` before result delivery.
The orchestrator starts the same child again; the child makes the source note complete.
The orchestrator also starts two completed source researchers again for evidence corrections.
One correction puts directly readable Manning samples in the System Design note.

The other keeps Reliable Machine Learning's pagination and date conflicts.
The Video Edition child separately makes a correction to the DMLS relationship.
No correction starts a replacement source researcher.
The saved notes keep the accepted results.

## 10. Supplement source checks

The orchestrator checks these decisive public passages independently.
The checks show source scope, not a reproduction of book examples or rack tests.

| Source | Checked passage | Accepted meaning |
| --- | --- | --- |
| [DMLS author repository](https://github.com/chiphuyen/dmls-book) | README and stated book purpose. | General systems design, not a tutorial or rack-acceptance procedure. |
| [Author book page](https://huyenchip.com/books) | DMLS audiobook announcement under the 2022 book. | Alternate audio format; no verified technical revision or exact passage equivalence. |
| [Google Research abstract](https://research.google/pubs/chapter-1b-data-management-principles-_reliable-machine-learning-applying-sre-principles-to-ml-in-production) | Data-management chapter abstract. | SLOs, SLIs, monitoring, and data handling, not an executable distributed recovery contract. |
| [Reliable ML author Q&A](https://datatalks.club/books/20221121-reliable-machine-learning.html) | Whole-system scope, framework independence, and code examples. | Author testimony shows general reliability context; no code examples. |
| [System Design Chapter 10](https://livebook.manning.com/book/machine-learning-system-design/chapter-10) | Public introduction and testing headings. | Training pipelines and property-based testing. |
| [System Design Chapter 14](https://livebook.manning.com/book/machine-learning-system-design/chapter-14) | Public introduction and monitoring headings. | Software health, data integrity, and model quality must use separate monitoring. |
| [Platform Engineering Chapter 8](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-8) | Public introduction and contents. | Modular training components, metrics, artifacts, validation, and pipeline integration. |
| [Platform Engineering Chapter 9](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-9) | Public introduction and contents. | PersistentVolumes, TensorBoard, MLflow, dataset management, and lineage. |
| [Platform Engineering Chapter 11](https://livebook.manning.com/book/machine-learning-platform-engineering/chapter-11) | Public introduction and contents. | Service monitoring and model drift, not GPU fault screening. |
| [Deep Learning Systems Chapter 4](https://livebook.manning.com/book/designing-deep-learning-systems/chapter-4) | Public introduction and contents. | Distributed training service and parallelism, not verified resume equivalence. |
| [Deep Learning Systems publisher](https://www.manning.com/books/designing-deep-learning-systems) | Author record and stated scope. | Chi Wang and Donald Szeto; training, dataset management, and hyperparameter optimization. |

Repeat O'Reilly fetches run into access denial for the parallelism course and Reliable Machine Learning's monitoring chapter.
The report makes no independent playback or full-chapter inspection claim for those sources.
The course-scope finding uses the researcher's saved catalog evidence and its explicit access limits.
The notes keep indexed metadata separate from directly readable primary text.

## 11. Reading changes and retained limits

- Keep current Megatron Bridge and PyTorch recovery guides first.

- Keep reliability papers for fault mechanisms and detection limits.

- Keep DMLS and Reliable Machine Learning at the same general reading priority.

- Put Machine Learning Platform Engineering Chapters 8, 9, and 11 in the reading list for selected platform work.

- Put these selected chapters before older cloud-specific pipeline material.

- Keep MLOps Engineering at Scale for its cloud-specific context.

- Make Machine Learning System Design Chapters 10 and 14 optional pipeline-testing and monitoring reading.

- Keep the parallelism course and Designing Deep Learning Systems optional.

- Keep the cloud video and vision book at lower priority for distributed pretraining reliability.

- Do not use alternate formats as independent technical corroboration.

The new platform book does not show full-book supersession of older MLOps reading.
No reviewed book passage shows a full distributed checkpoint-resume acceptance procedure.
Catalog chapter titles do not show enabled software features or measured recovery.
The supplement keeps operator approval and non-destructive default tests.
It also keeps expected checkpoint rollback separate from silent duplicate or skipped progress.

The Reliable Machine Learning note keeps 408, 466, and 410-page records and 2021/2022 date differences.
The reviewed evidence does not show a format or edition cause for these differences.
The review keeps the cloud-video date and runtime unverified.
It also keeps the vision-book year and page count unverified.
The supplied platform-video title shows no matching product URL.
These limits make no changes to the suite's honest two-hour misses in §6.

## 12. Supplement validation and paths

The supplement validator shows no errors for ten nodes and ten lessons below 50 physical lines.
The initial validator still shows no errors for seven nodes and seven lessons.
Local link checks show no missing Markdown targets.
The ten source notes show the exact requested date line and final `## Gaps` heading.
Their proposed-check sections show three to five entries each.

A prose-length check shows no checked orchestrator sentence with 20 or more words.
The check makes no claim of dictionary certification or factual validation.
The final map source uses ten independent nodes and no edges.
The harness still makes no Mermaid rendering tool available.

Supplement validator command:

```sh
node /home/avirus/.agents/skills/research/scripts/check-report.mjs /home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/oreilly/research.md
```

- [Supplement brief](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/oreilly.md)

- [Supplement map and lessons](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/oreilly/research.md)

- [Source notes](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/oreilly/)

- [Updated book canon](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/books.md)

- [Updated staged reading list](/home/avirus/.herdr/worktrees/rack-bench/research-training/.lavish/training-research/docs/training-bench-research.md#reading-list)

The orchestrator keeps all phase writes inside `.lavish/training-research/`.
The parent still makes the project placement and commit decisions.
Use the link changes in §8 when you put the staged reading list into the project copy.
The project copy already shows the original seven brief links.
This supplement makes no changes to that project copy.
