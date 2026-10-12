# Inference research: orchestrator report

Research date: 2026-10-11.

## 1. Completion and delivery

The run keeps seven original category briefs and nine supplemental source notes.
The run also keeps sixteen checked extracts, sixteen combined lessons, and the complete staged design.
The original report shows a pass for the combined report check.
That check shows sixteen nodes and sixteen lessons, each below 50 physical Markdown lines.
The original report shows a pass for the supplement report check.
That check shows nine nodes and nine lessons, each below 50 physical Markdown lines.

Each category brief shows the exact research-date statement, numbered sections, source URLs, evidence markers, and a final Gaps section.
The original report shows 314 design lines in the initial delivery. The current staged document shows the supplemental reading list.
The supplement keeps the accepted metric contract, 120-minute schedule, suite requirements, and tickets unchanged.
It shows the failure-mode catalog, suite tables, implementation tickets, and reading list.

No local GPU measurements show rack performance.
This research makes no project code changes.

The original report shows a parent-confirmed plan: put a staged-design copy in the project docs directory.
The orchestrator makes no claim of a project-level copy yet.
Keep the source links valid during publication.

## 2. Actual deliverables

Run directory:
`/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/`

| Deliverable | Actual absolute path |
| --- | --- |
| Node report and lessons | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/research.md` |
| Staged bench design | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/docs/inference-bench-research.md` |
| Orchestrator report | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/ORCHESTRATOR-REPORT.md` |
| Scope and file index | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/README.md` |
| N01 checked extract | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/nodes/N01.md` |
| N02 checked extract | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/nodes/N02.md` |
| N03 checked extract | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/nodes/N03.md` |
| N04 checked extract | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/nodes/N04.md` |
| N05 checked extract | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/nodes/N05.md` |
| N06 checked extract | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/nodes/N06.md` |
| N07 checked extract | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/nodes/N07.md` |

Requested publication destination:
`/home/avirus/.herdr/worktrees/rack-bench/research-inference/docs/inference-bench-research.md`

The write boundary keeps changes only inside the research run directory.
The parent keeps ownership of the publication step.

## 3. Category verdicts

These verdicts show research evidence, not rack performance.
The complete category files keep accepted findings and limitations.
The node files keep checked extracts and links to the complete briefs.

| Category | Research verdict | Finding | Actual absolute brief path |
| --- | --- | --- | --- |
| neoclouds | Accepted; N01 done | Different token-rate denominators; incomplete matched tails and workload controls | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/neoclouds.md` |
| hyperscalers | Accepted; N02 done | Different quota, reserved capacity, achieved throughput, and latency guarantees | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/hyperscalers.md` |
| ai-labs | Accepted; N03 done | Separate definitions for client/server timing, request TPOT, event-gap ITL, and throughput populations | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/ai-labs.md` |
| large-companies | Accepted; N04 done | Production disclosures: mixed-load, KV-pressure, and quality diagnostics; no universal GB300 gates | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/large-companies.md` |
| clustermax | Accepted; N05 done | Current ClusterMAX serving tests; incomplete public protocol and raw evidence | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/clustermax.md` |
| academia | Accepted; N06 done | Papers and pinned rules show support for arrival discipline, scenario gates, quality checks, and percentile limits | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/academia.md` |
| books | Improved topic evidence; N07 gap | Public author summaries show specific inference/deployment topics; no complete-book access | `/home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/books.md` |

## 4. Decisive evidence checks

The orchestrator uses web_fetch to check decisive passages.
The briefs keep claim-level URLs and evidence markers.

| Checked source | Decisive passage or boundary | Effect on design |
| --- | --- | --- |
| [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) | AgentX single/multinode inference; separate `/v1/models` startup timer | Remove readiness-only premise; keep readiness and first generation separate |
| [Public cmax](https://github.com/SemiAnalysisAI/clustermax) | README: no benchmark implementations or provider results | Keep public-code claims within audit coverage |
| [vLLM metrics](https://docs.vllm.ai/en/latest/design/metrics.html) | Server/client boundaries; TPOT/ITL populations; one-token conventions | Keep timers and observation units separate |
| [Pinned vLLM client](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/serve.py) | Successful-token totals, TPOT exclusion, gamma arrivals, semaphore, completion-inclusive timer | Use explicit counting, actual sends, drain, and one-token rules |
| [llama-bench README](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md) | pp/tg/pg, warmup, context depth, tokenization/sampling exclusions | Keep offline diagnostics outside HTTP acceptance |
| [AWS MU docs](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) | Model-specific input/output capacity per minute; account-manager details | Do not make portable GPU-rate inferences |
| [Google GSU docs](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput) | Model-specific accounting, admission estimates, rolling windows | Keep quota and achieved serving evidence separate |
| [Azure latency](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency) | Workload lengths, call rate, cache-match dependence | Use workload-specific measured operating points |
| [Azure metrics](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics) | Gateway boundaries and minute-grain aggregation | Keep external request-level records |
| [Meta serving](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism) | TTFT/TTIT targets and communication effects | Keep targets as configuration-specific context |
| [Cloudflare precision](https://blog.cloudflare.com/smaller-faster-safer-models) | Weight/KV precision effects on concurrency, throughput, and task scores | Keep quality screening beside capacity measurements |
| [Sarathi-Serve](https://arxiv.org/html/2403.02310v1) | Prefill stalls; chunk-size overhead; median TTFT versus p99 TBT | Put a mixed-prefill test in the suite; keep metric populations |
| [Pinned MLPerf policy](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc) | Poisson scenarios, model-specific gates, cache rules, early stopping | Do not use universal gates or formal-compliance claims |
| [Together benchmark](https://www.together.ai/blog/coding-agent-benchmarks) | Four/eight-GPU allocations; input-TPM unit conflict | Keep unequal-resource comparison and arithmetic conflict visible |
| [Cerebras 405B](https://www.cerebras.ai/blog/llama-405b-inference) | 969 output tokens/s at 1K prompt; 240 ms TTFT | Keep as individual output-speed evidence |
| [InferenceX GB300](https://inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4) | Total-token cost; interpolated iso-interactivity table | Do not make interpolation a measured output-only point |
| [RunPod startup](https://docs.runpod.io/serverless/overview) | Zero-worker request to worker-ready definition | Keep local startup separate from fleet scale-from-zero behavior |
| [Huyen book records](https://huyenchip.com/books) | Book editions and author records | Keep verified bibliographic coverage |
| [O'Reilly chapter](https://www.oreilly.com/library/view/ai-engineering/9781098166298/ch09.html) | Repeat-fetch result: access denied | Keep the full-text evidence gap visible |

Some long source fetches show truncated output.
Use the briefs' section and immutable line references for specific code claims.
Do not use a historical pinned client as the current deployed release.
Do not use a policy commit as proof of a formal release tag.

## 5. Corrections and conflicts

- ClusterMAX is not readiness-only. Current public descriptions show serving benchmarks.
- InferenceX is separate. Its entire metric schema does not automatically show ClusterMAX AgentX.
- Orca is the OSDI 2022 paper. arXiv 2309.06180 is the vLLM/PagedAttention paper.
- The Together source shows 625 TPM/GPU and 2.5M total TPM for four GPUs.
  Arithmetic shows 625,000 input TPM/GPU. The brief keeps the source conflict explicit.
- The InferenceX 27 tok/s/user comparison uses interpolation and total-token economics.
  The brief does not show it as directly measured output-only throughput.
- The original neocloud child schedule shows a 105–130 minute total.
  The accepted brief keeps the corrected fixed 120-minute proposal.
- TPOT for one-token outputs shows no interval. Tools use different conventions.
  The design keeps unavailable TPOT and explicit goodput applicability.
- Event-gap ITL does not show individual token timing when streams send token groups.

## 6. Two-hour feasibility and misses

The proposed certify schedule shows a 120-minute total.
The schedule starts from staged model files, server image, evaluator, and a bounded launch.
It uses one declared model and serving configuration.
The schedule puts a separate drain/reset cost in each phase.

The suite can show coarse load sensitivity, selected scheduler interference, KV pressure, and cache-dependent results.
The suite can check selected-task quantization regressions with a matching reference.
The suite cannot make sure that every check runs to its end after slow startup or reference loading.
The report keeps budget exhaustion and missing samples visible.

Honest misses:

- Production availability, day-long tails, seasonality, and fleet autoscaling.
- Rare failures and silent cache-corruption probabilities.
- Precise p99 without enough independent request observations.
- Broad quantization fidelity beyond selected tasks.
- Every model, precision, topology, and tenant request mix.
- Full 18-tray serving coverage without participation evidence.
- Unbounded cold downloads, engine builds, and repeated fleet cold starts.
- Token economics without verified costs.
- Formal MLPerf compliance without the complete versioned procedure.

No party sends a tenant workload, numeric SLO, universal quality tolerance, or live rack measurement.
For this reason, the design keeps valid evidence separate from target verdicts.
Use measurement for PASS. PASS does not show a pass for an undeclared target.

## 7. Agent accounting and recovery

The original report shows exactly seven researcher sessions with the requested names.
Each uses `agent="researcher"` and `openai-codex/gpt-6-luna`.
Each researcher keeps one independent node. Each researcher sends findings without file changes.
The orchestrator puts artifacts inside the run directory.

The original report shows this Neoclouds error: `WebSocket idle timeout after 300000ms`.
The orchestrator starts the same session again. The session sends its complete brief.
The orchestrator does not start a duplicate researcher in its place.
The orchestrator also starts existing sessions again for narrow evidence corrections.

The original report shows accepted files for all seven category results.
The original report shows later parent authorization for exactly nine independent supplemental researcher sessions.
The supplement keeps those sessions, not replacement sessions.

## 8. Validation

Command:
`node /home/avirus/.agents/skills/research/scripts/check-report.mjs /home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/research.md`

Result:
`Passed: 16 nodes, 16 lessons, each below 50 lines.`

Supplement command:
`node /home/avirus/.agents/skills/research/scripts/check-report.mjs /home/avirus/.herdr/worktrees/rack-bench/research-inference/.lavish/inference-research/oreilly/research.md`

Supplement result:
`Passed: 9 nodes, 9 lessons, each below 50 lines.`

Local artifact checks show all seven brief headers, exact date lines, and numbered sections.
Those checks also show URLs, evidence markers, and final Gaps headings.
They also show all sixteen node extracts and the distilled document's required sections.
Supplement checks show nine source notes, the synthesis format, lesson lengths, and local Markdown links.
The original final check shows sixteen extracts and 106 local Markdown links, including file URLs.

The original report shows 331 staged-design lines.
The staged document shows links to all seven categories and the supplement synthesis.
Those local source files are present.

The structural check does not check vocabulary. It does not check every external claim.
The evidence review shows the decisive-source checks.

## 9. O'Reilly supplement completion

The original report shows nine accepted supplemental findings and no running child.
Each researcher uses `agent="researcher"` and `openai-codex/gpt-6-luna` in the requested worktree.
Children make no file changes and start no agents.
The orchestrator keeps their notes and checks decisive public passages.

A narrow follow-up to the same finance child checks metadata URLs and the repository edition boundary.
No duplicate finance session starts.

| Node | Child | State | Accepted source note |
| --- | --- | --- | --- |
| N08 | oreilly-ml-production-systems | gap | [ml-production-systems.md](oreilly/ml-production-systems.md) |
| N09 | oreilly-hands-on-ml | done | [hands-on-ml.md](oreilly/hands-on-ml.md) |
| N10 | oreilly-how-llms-work | done | [how-llms-work.md](oreilly/how-llms-work.md) |
| N11 | oreilly-llms-finance | done | [llms-finance.md](oreilly/llms-finance.md) |
| N12 | oreilly-streaming-systems | gap | [streaming-systems.md](oreilly/streaming-systems.md) |
| N13 | oreilly-grokking-streaming | done | [grokking-streaming.md](oreilly/grokking-streaming.md) |
| N14 | oreilly-tf-serving-video | gap | [tf-serving-video.md](oreilly/tf-serving-video.md) |
| N15 | oreilly-tfx-event | done | [tfx-event.md](oreilly/tfx-event.md) |
| N16 | oreilly-latency-video | gap | [latency-video.md](oreilly/latency-video.md) |

`done`: sufficient public evidence for the bounded source recommendation; not complete-book access.
`gap`: TOC-only methods or inaccessible video content.
N15 shows agenda topics, not course demonstrations.
N07: `gap` for complete-book access.
The combined report shows eleven `done` nodes and five `gap` nodes.
These states show evidence, not unfinished researcher work.

| Checked public evidence | Accepted passage | Limit |
| --- | --- | --- |
| [AI Engineering author summaries](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization) | TTFT/TPOT, utilization, quantization, KV, batching, parallelism, prompt caching | Summary, not complete chapter |
| [DMLS author summary](https://github.com/chiphuyen/dmls-book/blob/main/summary.md#chapter-7-model-deployment-and-prediction-service) | Chapter 7 deployment/prediction context | Summary, not current token benchmark |
| [Production-book description](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ) | LLM serving and GenAI pipelines | Description; not serving-example prose |
| [Géron repository](https://github.com/ageron/handson-ml3) | Third-edition examples | Examples; not full chapter 19 |
| [LLM chapter 7 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7) | General limits, latency/scale/availability overview | Overview/summary/FAQ; not complete chapter |
| [Finance notebook 10](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb) | Fictional fixtures, M/M/1 screen, separate constraints, required workload replay | Not measured hardware p95, cost, or quality |
| [Finance repository](https://github.com/PacktPublishing/LLMs-in-Finance) | Additive current suite v1.1.0; separate canonical B32413-v1.0.0 | Current `main` notebook does not show the original chapter |
| [Grokking chapter 6](https://livebook.manning.com/book/grokking-streaming-systems/chapter-6) and [chapter 7](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7) | Partial grouping/window prose and section headings | Many later methods are headings only |
| [TF Serving conference agenda](https://conferences.oreilly.com/tensorflow/tf-ca-2019/public/schedule/detail/78365.html) | October 30, 2019; payload, TensorRT, batching, testing, monitoring | Agenda, not video demonstrations |
| [TFX event agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880) | Evaluation slices, versioning, batching, test requests; 180-minute total | Exact session date/recording is unverified |
| [Latency description](https://www.manning.com/books/latency) and [chapter record](https://books.google.com/books/about/Latency.html?id=u9SSEQAAQBAJ) | Modeling, measurement, concurrency, Little's Law, Amdahl's Law | Related book, not verified video sections |

Important corrections:

- Machine Learning Production Systems explicitly shows LLM/GenAI additions. A wholly TF-era label is incorrect.
- How Large Language Models Work shows three authors. The supplied attribution does not show Edward Raff or Stella Biderman.
- The TF Serving catalog publication date and conference date are different.
- Related Latency book chapters do not show video sections or transcript access.
- The finance notebook uses fictional teaching fixtures in the current supplemental suite.
- Added p95 fields do not show the total-latency distribution or a general percentile bound.
- Public author summaries show a narrower N07 topic-evidence gap. They do not remove the complete-book access gap.

Keep access differences explicit.
Some children check catalog/TOC pages. The orchestrator cannot check those pages again.
Public Manning samples, agendas, descriptions, and author examples show bounded independent evidence.
Those sources do not make authenticated text or video access available.

Updated artifacts:

- [Supplement synthesis](oreilly.md): metadata, nine source sections, access matrix, portable checks, and final Gaps.
- [Supplement report](oreilly/research.md): nine-node map, states, and short lessons.
- [Combined report](research.md): all sixteen nodes and lessons.
- [Canon brief](books.md) and [N07 extract](nodes/N07.md): improved topic evidence, unchanged complete-book gap.
- [Staged design](docs/inference-bench-research.md): supplemented reading list and linked eighth brief.
- [README](README.md): updated file index and boundaries.

The parent must start publication of the updated staged design again.
The parent must also make the project-relative source links correct.
The orchestrator makes no project-file changes and makes no claim of project publication.
The report keeps these limits: full-book/video access, local measurements, tenant workload, numeric SLO, quality tolerance, and verified costs.
