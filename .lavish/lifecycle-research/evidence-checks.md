# Decisive evidence checks

Research date: 2026-10-11.

## N03

The orchestrator reads these primary passages with `web_fetch`:

- [Composer autoresume](https://docs.mosaicml.com/projects/composer/en/stable/examples/checkpoint_autoresume.html)
  uses Ctrl-C and a repeat command to show resume. It requires `run_name` and `save_folder`.
  The text supports a controlled process test. It does not show actual provider reclaim.
- [DCGM NCCL plugin](https://docs.nvidia.com/datacenter/dcgm/latest/reference/diagnostics/plugins/nccl-tests.html)
  states that the plugin supports only single-node NCCL tests. A separate runner must run multi-node tests.
- [PyTorch DCP](https://docs.pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html)
  supports parallel save and topology changes at load. The example includes model and optimizer state.
  This API does not prove correct resume for arbitrary applications.

Decision: accept these mechanisms. Keep workflow guarantees and two-hour test design as inferences.

## N01

- [Nebius preemptible VMs](https://docs.nebius.com/compute/virtual-machines/preemptible)
  states SIGTERM at 60 seconds before stop. Attached volumes persist; local SSD data does not.
  Preemptible recovery supports `FAIL`, not `RECOVER`.
- [CoreWeave Spot Node Pools](https://docs.coreweave.com/platform/capacity-plans/spot-node-pools)
  excludes Superchip instances, including GB300. The warning-to-removal maximum is seven minutes.
  Drain starts two minutes after warning. Pod termination grace can be only 30 seconds.
  The orchestrator sends this missing restriction to the researcher for correction.
- [Runpod Pod management](https://docs.runpod.io/pods/manage-pods)
  says stop releases GPUs and clears container disk. Start can return zero GPUs.
- The prior internet brief places egress economics at lines 142–162, not the returned anchor.
  The orchestrator sends this citation error to the researcher for correction.

## N05

- [Lifecycle criteria](https://www.clustermax.ai/criteria/lifecycle) lists 15 Key Requirements.
  Five requirements concern audit logs. These include API queries, export, and 90-day retention.
- [ClusterMAX 3.0 method](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
  describes fresh-cache installs per storage tier, imports, serving readiness, pod churn, and PVC cycles.
  The reboot timer requires a new boot ID and fresh-pod `nvidia-smi` success.
  Pod churn, PVC cycles, and reboot appear after the performance discussion, within reliability testing.

  The text keeps most test code internal. Support and delivery require other research methods.
  Provider anecdotes include provisioning times. They do not define a uniform provisioning benchmark.

Decision: accept the described tests. Keep omissions bounded to the published method.

## NIST revision

- [NIST SP 800-88 Rev. 2](https://csrc.nist.gov/pubs/sp/800/88/r2/final)
  states publication in September 2025 and supersedes Rev. 1.
  Sanitization makes access to target data infeasible for a stated effort.
  Tenant resource deletion does not prove this condition by itself.
- [NIST FAQ](https://csrc.nist.gov/files/pubs/sp/800/88/r2/final/docs/sp800-88r2-faq.pdf)
  Q7 defines verification and validation separately. Q5 limits selective cryptographic erase to a valid encrypted boundary.
  Q13 includes virtual/cloud media and calls for traceable key zeroization.
  Rev. 2 refers media-specific technique selection to evolving standards, including IEEE 2883.

## N02

- [GCP Spot](https://docs.cloud.google.com/compute/docs/instances/spot)
  excludes A4X and bare-metal instances. It gives zero default pre-notice and best-effort shutdown up to 30 seconds.
  The readable page does not show a Preview label. The child records current status uncertainty separately.
- [Google deletion](https://docs.cloud.google.com/docs/security/deletion)
  states May 2024 status, a staged deletion pipeline, and about 180 days for overall deletion.
  The source cites NIST Rev. 1. It does not prove current Rev. 2 adoption.
- [Microsoft disposal](https://learn.microsoft.com/en-us/compliance/assurance/assurance-data-bearing-device-destruction)
  describes on-campus device disposal, retained records, and chain of custody.
  This is provider-published practice, not direct evidence of deletion for one tenant.

## N04

- [Azure rollout](https://learn.microsoft.com/en-us/azure/kubernetes-fleet/concepts-rollout-strategy)
  gives conflicting `unavailablePeriodSeconds` defaults: 10 seconds and 60 seconds.
  It supports staged updates, approval, prior-snapshot rollback, and stuck status after retries.
  The child records the conflict. The report requires live configuration, not an assumed default.
- Company disposal passages above support published practice only.
- The orchestrator reads `rack_bench/bench/runner.py:12–15` directly.
  The current category registry contains only `internet`.

## N06

- [Borg 2020 abstract](https://research.google/pubs/borg-the-next-generation)
  specifies eight clusters in May 2019 and a comparison with 2011.
  It reports workload dependencies and between-cluster differences. It does not predict GB300 reliability.
- [Schroeder/Gibson](https://www.cs.toronto.edu/~bianca/papers/dsn06.pdf)
  sections 2.3 and 3 describe administrator-handled records, reporting limits, and distribution methods.
  Sections 5.3 and 6 describe simultaneous failures and variable repair times.
  The paper warns against an equal-mean Poisson assumption across nodes.
  Its method supports event definitions and uncertainty, not a rack-specific failure rate.

## N07

- [Workbook contents](https://sre.google/workbook/table-of-contents/)
  verifies chapters 6, 11, 16, and 18.
- [Workbook chapter 18](https://sre.google/workbook/engagement-model/)
  includes readiness, deprecation, abandonment, shutdown, and reference removal.
- [BSRS contents](https://google.github.io/building-secure-and-reliable-systems/raw/toc.html)
  places Data Sanitization within chapter 18. Chapter 9 includes explicit revocation and intended-state checks.
- [Kubernetes drain](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)
  respects configured disruption budgets but excludes some system pods and DaemonSets.
  Drain success does not mean that no process or pod remains.

## Second-pass checks: N03 and N07

The orchestrator checks these replacement-brief sources with `web_fetch`:

- [EleutherAI GPT-NeoX README](https://github.com/EleutherAI/gpt-neox)
  gives historical dependency ranges, isolated environments, container setup, and hostfile launch instructions.
  It separates slim weights from full weights with optimizer state.
  Its version section describes upstream migration. Its setup warning still names the legacy DeepSpeed fork.
  The brief must keep this version ambiguity visible.
- [Hugging Face Accelerate checkpointing](https://huggingface.co/docs/accelerate/en/usage_guides/checkpoint)
  names model, optimizer, RNG generators, and GradScaler state.
  Users must register custom objects. Mid-epoch data position needs explicit batch skipping.
- [Composer resumption](https://docs.mosaicml.com/projects/composer/en/stable/notes/resumption.html)
  requires `save_folder` and `run_name` for autoresume.
  It gives local, remote, and `load_path` search order.
  Spot termination appears as a recovery example, not a measured workload fraction.
- [MosaicML StreamingDataset](https://www.mosaicml.com/blog/mosaicml-streamingdataset)
  reports an 8→32→128 GPU resume demonstration with matching loss curves within numerical limits.
  It reports two-minute startup for a 128-A100 Stable Diffusion example.
  These are first-party historical examples, not measured GB300 thresholds.
- [Pearson third-edition preview](https://api.pageplace.de/preview/DT0400.9780133415070_A28528899/preview-9780133415070_A28528899.pdf)
  identifies chapter 26 as Running a Datacenter and chapter 34 as Maintenance Windows.
  It identifies chapter 20 as Service Launch: DevOps, not Maintenance Windows.
  Its contents give retirement sections 7.6, 26.2.4, and 56.7.
  The copyright page gives 2017. The researcher must check the separate release date.
- [Manning TOC](https://livebook.manning.com/book/kubernetes-in-action/table-of-contents)
  returns only early chapters through this fetch path.
  That extract cannot support guessed later chapter titles or chapter numbers.
  The orchestrator sends these book errors to the same child for correction.

The corrected briefs add these checked primary passages:

- [OpenAI preflight](https://openai.com/index/scaling-kubernetes-to-7500-nodes/)
  applies a taint and label before normal scheduling. Successful active GPU tests remove both.
  The workload section describes all-pod MPI membership and checkpoint restart after pod loss.
- [Meta reliability](https://engineering.fb.com/2025/07/22/data-infrastructure/how-meta-keeps-its-ai-hardware-reliable/)
  describes reductive triage through mini-training, node quarantine, and checkpoint continuation.
  The technique depends on fault reproduction. Short useful-work tests do not exclude every silent error.
- [DeepSeek-V3 v1](https://arxiv.org/html/2412.19437v1#S3)
  identifies 2,048 H800 GPUs and the training framework in sections 3.1–3.2.
  Its stable-training claim does not prove tested interruption recovery.
- [Anthropic environment review](https://www.anthropic.com/news/improving-alignment-security-efforts)
  describes a three-day RL rollback and continuation from an earlier checkpoint.
  It describes a change freeze, environment review, and recertification before reuse.
  These are training-environment controls, not a generic GPU image or checkpoint-state specification.
- [Manning chapter 9](https://livebook.manning.com/book/kubernetes-in-action/chapter-9)
  verifies sections 9.3.3–9.3.6: rollback, rollout rate, pause, and bad-version blocking.
- [Manning chapter 11](https://livebook.manning.com/book/kubernetes-in-action/chapter-11)
  verifies scheduler/controllers/kubelet sections 11.1.5–11.1.7 and event observation section 11.2.3.
- [Manning chapter 15](https://livebook.manning.com/book/kubernetes-in-action/chapter-15)
  verifies suitable scaling metrics in 15.1.5 and disruption limits in 15.3.3.
  Its text explicitly warns about historical version changes.
- [Limoncelli author announcement](https://everythingsysadmin.com/books.html)
  states that the third edition is due in November 2016.
  Keep this announcement separate from the preview's copyright 2017.

Decision: accept the corrected named-lab mechanisms and five-book canon.
N07 closes its chapter-evidence gap through an alternative Kubernetes book.
N03 keeps a bounded quantitative gap for MosaicML's spot-use fraction.
The replacement briefs keep proposed checks separate from source guidance.

## O’Reilly supplement checks

The [supplement check record](oreilly/evidence-checks.md) gives decisive passages and access differences.
The publisher confirms SRE second edition and its capacity/lifecycle/AI chapter headings.
The integrated canon uses verified contents, not unconfirmed limited body excerpts.
Primary Wiley-VCH contents close the facility book's mirror-only chapter gap.
Springer/Apress confirms the Go book's edition, December 2022 publication, and controller-testing chapters.

BSRS Data Sanitization concerns recovery integrity, not a physical-media wipe procedure.
Four supplement nodes retain material chapter, date, or course-identity gaps.
The earlier BSRS bibliography link names an unrelated notebook; the Workbook link returns 404.
The canon removes those citations and unsupported ISBN attributions, while retaining verified primary chapter citations.

## Acceptance boundary

The orchestrator checks the decisive passages used in short lessons and the distilled design.
The category briefs retain additional sources and explicit gaps.
The orchestrator does not independently reproduce every historical number in those briefs.
The final design uses historical papers for method, not GB300 thresholds.
No provider, simulator, or live-rack test runs during this research.
