# ClusterMAX inference-serving coverage: published tests and gaps

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Bottom line

The current ClusterMAX version is 3.0. Its methodology shows InferenceX AgentX in single-node and multinode scenarios. Different models and profiling traces show compute-, memory-, and communication-bound regimes. It uses InferenceX results as comparison baselines and shows a discussion of lost goodput. A claim of model-readiness-only testing in ClusterMAX is incorrect. [observed] [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

ClusterMAX 2.0 shows a separate Kubernetes-only serving test. A multinode llm-d Qwen endpoint keeps prefill and decode separate. The test checks vLLM-suite throughput. It also checks throughput growth with added model replicas. [observed] [ClusterMAX 2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)

The public `cmax` CLI is an audit tool, not the performance harness. Its README shows no benchmark implementations or provider results. [observed] [Repository](https://github.com/SemiAnalysisAI/clustermax)

The useful distinction is reproducibility, not test existence. Public ClusterMAX text shows serving tests. It does not show their full run configuration or raw evidence. InferenceX is a separate project with richer public methodology. Do not silently put its entire metric schema on ClusterMAX. [inference] [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) · [InferenceX](https://inferencex.semianalysis.com/about)

## 2. Current published tests

ClusterMAX 3.0 shows Inference in its performance phase. Its requested allocation is 32 Blackwell-class GPUs: four eight-way HGX nodes or eight four-way NVL72 trays. This is not proof that every inference run uses all 32 GPUs or a full rack. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

The article shows AgentX runs with different models in single-node and multinode scenarios. Profiling traces show bottleneck regimes more clearly. That paragraph does not show the exact run matrix. [observed] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

Compute, RDMA, collectives, storage, and training tests show context for poor serving results. They are not a replacement for request latency or token-throughput measurements. The eight-hour GEMM/all-to-all burn-in is a hardware/fabric test, not a stated serving traffic test. [observed + inference] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

Lifecycle tests start `vllm serve` and check the time until `/v1/models` sends a response. The article shows small-model loading from shared storage in 10–40 seconds at some providers. At other providers, the article shows over two minutes. Endpoint discovery is not first successful generation. [observed + inference] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 3. Historical serving tests

ClusterMAX 2.0 uses a Kubernetes llm-d Qwen deployment with prefill/decode disaggregation. It checks expected throughput against the vLLM performance suite. It also checks throughput growth with more replicas. Its description does not show a controlled concurrency or request-rate frontier. [observed] [2.0 methodology](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)

Its itemized criteria also show expected-throughput llm-d serving. A criterion does not show identical models, loads, or GPU counts across providers. The article shows a roughly five-day general test period, not five days of inference load. [observed + inference] [2.0 methodology](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)

## 4. Public evidence boundary

The absence claims below are about the reviewed public descriptions only. They do not show what SemiAnalysis checks internally. [inference] [3.0 methodology](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

| Topic | Established evidence | Missing public protocol detail |
| --- | --- | --- |
| Token throughput | AgentX comparison; historical vLLM throughput test | Exact per-GPU metric, token counts, timer, provider raw data |
| TTFT/TPOT/ITL | Separate InferenceX overview shows serving metrics | ClusterMAX AgentX paragraph shows no percentiles or formulas |
| Scheduler | Replica scaling in 2.0; single/multinode AgentX in 3.0 | Arrival schedule, concurrency sweep, fairness, admission, queue telemetry |
| Cold start | `vllm serve` to `/v1/models` | First generation, repeated cold samples, load-phase decomposition |
| KV pressure | PostTrainingX discussion shows occupancy and prefix-hit metrics | No specified ClusterMAX AgentX occupancy/exhaustion sweep |
| Quantization | Low-precision GEMM tests | Paired model-output quality gates |
| Request mix | Different models and bottleneck regimes | Prompt/output distribution, trace, seeds, sampling |
| Topology | Single-node and multinode scenarios | GPUs per run, TP/PP/EP/DP layout, replica placement |

Table evidence: [observed] [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) · [2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard) · [InferenceX overview](https://inferencex.semianalysis.com/about).

PostTrainingX is a separate upcoming/post-training initiative. Its listed generator metrics are tokens/s per inference GPU, rollout latency, KV occupancy, prefix-cache hit rates, and others. This is not proof of the same schema for ClusterMAX AgentX. [observed + inference] [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 5. InferenceX relationship

InferenceX separately shows fixed-sequence serving and AgentX comparisons across accelerators and stacks. Its overview shows per-chip token throughput, tokens/s/MW, p99 TTFT, and AgentX session behavior. [observed] [Overview](https://inferencex.semianalysis.com/about)

Its fixed-sequence method uses vLLM's serving client and infinite arrival rate with capped concurrency. It uses random sequences and input/output pairs 1,024/1,024, 1,024/8,192, and 8,192/1,024. It runs sweeps of precision, parallelism, and concurrency. These details are part of that benchmark, not automatically part of ClusterMAX AgentX. [observed] [Methodology](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)

AgentX uses long-context, multi-turn coding-agent sessions. The overview shows session/subagent execution, context overflow, prefix-cache behavior, saturation, and scenario compliance. [observed] [Glossary](https://inferencex.semianalysis.com/glossary) · [Overview](https://inferencex.semianalysis.com/about)

An application session test can show important interactions. A controlled rack diagnostic must still use explicit workload seeds, arrival controls, model settings, quality gates, and raw timestamps. [inference] [Methodology](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)

## 6. Public CLI coverage

The README shows `cmax` as a GPU-cluster and standalone-machine audit CLI. Its initial release is a small subset of the full suite. Public profiles are for inventory, software, containers, orchestration, networking, storage, health, and security. [observed] [README](https://github.com/SemiAnalysisAI/clustermax)

The README explicitly shows no benchmark implementations or provider results. It also shows that the core audit does not run planned performance or reliability tests. [observed] [README](https://github.com/SemiAnalysisAI/clustermax)

The visible `cmax/` tree shows audit and reporting modules, such as `audit_runner.py`, `audit_report.py`, `audit_profiles.py`, and `criteria_links.py`. Together with the README boundary, this is evidence that the public audit is not the serving harness. This brief does not make a claim of an exhaustive immutable code grep. [observed + inference] [Tree](https://github.com/SemiAnalysisAI/clustermax/tree/master/cmax) · [README](https://github.com/SemiAnalysisAI/clustermax)

Audit success does not show serving performance. Likewise, `/v1/models` readiness does not show throughput or latency acceptance. [inference] [README](https://github.com/SemiAnalysisAI/clustermax) · [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 7. Two-hour differentiation

1. Show aggregate output throughput, allocated-GPU normalization, request throughput, and latency together. Batching can make throughput better and interactive latency worse. [inference] [InferenceX methodology](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)
2. Keep TTFT separate from average TPOT and event-gap ITL. Long prompts and long outputs put stress on different resources. [inference] [InferenceX overview](https://inferencex.semianalysis.com/about)
3. Keep low-load and overloaded points. Keep a record of offered arrivals, active/waiting requests, rejection, and queue growth. [inference] [ClusterMAX 2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard)
4. Keep readiness timing separate from first generation and warm serving. Keep a record of model source and cache state. [inference] [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
5. Put long-context KV pressure on the system deliberately. Do not use AgentX as proof of exhaustive cache-pressure coverage. [inference] [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
6. Check quantized model quality against a reference. GEMM precision results do not show model fidelity. [inference] [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
7. Keep prompts, outputs, tokenizer, stop rules, warmup, and cache state. Also keep client placement, model revision, engine, and topology. Keep a count of failures and actual generated lengths. [inference] [InferenceX methodology](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)
8. Show which GPUs and trays run in the test. Component results are useful for diagnosis. They alone are not proof of a serving bottleneck. [inference] [ClusterMAX 3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 8. Sibling research

The [storage sibling](../storage-research/clustermax.md), line 27, already keeps lifecycle/model-loading evidence in §1.2 item 9. The [internet sibling](../internet-research/clustermax.md) shows the format exemplar. This brief does not run a new derivation of their storage or internet findings. [observed, local] [3.0 primary source](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## 9. Answer for rack-bench

ClusterMAX shows real serving-benchmark descriptions. Its current source shows AgentX. Its historical source shows llm-d/vLLM throughput and replica scaling. Those performance implementations are not in its public audit. [observed] [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard) · [2.0](https://newsletter.semianalysis.com/p/clustermax-20-the-industry-standard) · [CLI](https://github.com/SemiAnalysisAI/clustermax)

Rack-bench can show a transparent two-hour acceptance protocol with request-level evidence and declared omissions. It must not make a claim that ClusterMAX runs no serving-throughput test. [inference] [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)

## Gaps

- The public 3.0 AgentX paragraph does not show its full trace, model list, or engine settings. It also does not show topology or metric schema. [observed gap] [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- The public CLI shows no benchmark implementations or results. Operators cannot use it to make an independent list of the internal suite. [observed gap] [README](https://github.com/SemiAnalysisAI/clustermax)
- Separate InferenceX metrics do not show identical ClusterMAX settings. [inference] [InferenceX](https://inferencex.semianalysis.com/about)
- The sources do not show the exact relationship between the historical llm-d test and current AgentX. Without evidence, do not show both tests as current. [observed gap] [3.0](https://newsletter.semianalysis.com/p/clustermax-30-the-industry-standard)
- The repository inspection uses a moving tree, not an immutable exhaustive code audit. [observed gap] [Tree](https://github.com/SemiAnalysisAI/clustermax/tree/master/cmax)
