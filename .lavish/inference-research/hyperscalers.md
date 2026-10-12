# Hyperscaler inference throughput contracts and benchmark methods

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Executive answer

Hyperscaler capacity units are not portable tokens/s/GPU guarantees. AWS uses model-specific MUs. Google uses model-specific GSUs with windowed accounting. Azure uses workload-dependent PTUs. Public docs show no common per-GPU rate or universal p99 contract. [observed] [AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) · [Google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput) · [Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency)

Quota, reserved capacity, measured throughput, and latency guarantees are different concepts. A rack certificate must use a measured workload operating point. It must not use a conversion from abstract commercial units. [inference] [Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency)

## 2. Capacity products

### 2.1 AWS Bedrock

For a named model, an MU shows the processable input tokens per minute across requests. It also shows the generatable output tokens per minute across requests. AWS sends users to an account manager for exact MU throughput, prices, and limits. The docs show no public fixed MU/GPU conversion. [observed] [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)

AWS keeps purchases by tokens separate from purchases by model units. Keep model, region, commitment, and product form. [observed] [Purchase guide](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-thru-purchase.html)

On-demand endpoint accounting is different. For applicable models, `bedrock-mantle` uses separate input/output TPM with no RPM enforcement. `bedrock-runtime` uses combined quotas, model-specific output burndown, and sometimes RPM. Admission can keep the requested `max_tokens` in reserve. Admission can then put unused amounts back. [observed] [Scaling guide](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html)

429 rate limits are different from 503 capacity/high-demand errors. They are also different from the 529 overload responses of some APIs. Immediate service is not certain for in-quota traffic. [observed] [Scaling guide](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html)

A provisioned entitlement does not show a public latency SLO unless the applicable contract shows one. [inference] [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)

### 2.2 Google Vertex/Agent Platform

PT quota is equal to purchased GSUs times the model-specific rate. At admission, Google makes an estimate of output use. After the request, Google makes a reconciliation with actual use. By default, Google sends excess requests to pay-as-you-go spillover. Google sends 429 for excess `dedicated` requests; `shared` requests do not use PT. [observed] [PT usage](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)

Google’s Gemini 2.5 Flash examples show 2,690 tokens/s per GSU and 67,250 for 25 GSUs. These figures show product accounting, not generated output rate per GPU. [observed + inference] [PT usage](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)

Documented enforcement windows are different by size. Small allocations use 40–120 seconds, medium use 5–30, and large use 1–5. The ranges and allocation boundaries can be different for each model. Brief bursts can be different from average capacity. [observed] [PT usage](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)

Monitoring shows GSU/token limits, consumption, invocation counts/latency, and first-token latency. Minute-grain reconciled dashboards can keep sub-minute spillover out of view. [observed] [PT usage](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)

Capacity entitlement is not a universal TTFT/TPOT/p99 guarantee. Keep an independent record of request-level outcomes. [inference] [PT usage](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)

### 2.3 Azure OpenAI/Foundry

PTUs keep model-processing capacity in reserve. Azure billing uses deployed capacity. Azure Reservations make billing lower. Azure explicitly shows that Reservations are not a deployment-capacity guarantee. A successful deployment creation shows that capacity is available. [observed] [PT onboarding](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/provisioned-throughput-onboarding)

Actual provisioned throughput is a function of input/output lengths, call rate, and cache-match rate. Azure uses a workload-sizing calculator, not a general PTU/TPM ratio. Standard quotas make the admission decision. Latency variation can keep achieved throughput below quota. [observed] [Latency guide](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency)

Azure keeps first response, average token spacing, and last byte separate. Its guide shows a recommendation: put latency together with token counts. Gateway timing is not client network timing. [observed] [Latency guide](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency) · [Metric catalog](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

### 2.4 Guarantee vocabulary

Send a request for exact contract clauses for model/version, region, token accounting, windows, and cache. The request must also show burst allowances, errors/spillover, percentiles, and remedies. Product adjectives are not a replacement for operational or contractual definitions. [inference] [AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) · [Google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput) · [Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/provisioned-throughput-onboarding)

## 3. Metrics

Output tokens/s is generated output divided by the declared duration. Combined tokens/s also uses prompt tokens. Request/s uses the count of completed requests. GPU-normalized rate is valid only with known allocation and topology. These metrics are not replacements for one another. [observed + inference] [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html) · [Google benchmarking](https://docs.cloud.google.com/docs/ai-ml/accelerator-performance-benchmarking)

TTFT must use a declared client/server start boundary. TPOT is the average post-first-token time per request. ITL uses samples of streaming intervals. Multiple tokens can be in one interval. One-token TPOT statistics are different from vLLM’s Prometheus zero convention. [observed] [vLLM metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

Keep p50/p99, counts, estimator, outcomes, and actual lengths. A gateway average or low-N p99 does not show client tail latency. [inference] [Azure catalog](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

Azure’s guide shows `TTLT = TTFT + TBT * Tokens Generated`. Exact vLLM request TPOT uses `N - 1` token intervals instead. Keep the convention difference; do not show these formulas as identical. [observed + inference] [Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency) · [vLLM](https://docs.vllm.ai/en/latest/design/metrics.html)

## 4. Benchmark recipes

### 4.1 Triton/GenAI-Perf

GenAI-Perf can run streaming endpoint tests with synthetic or dataset prompts. It can use concurrency/rate control, length distributions, warmups, and a request count. It can keep telemetry and CSV/JSON artifacts. It shows TTFT, ITL, request latency, lengths, request throughput, and output throughput. [observed] [Docs](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

Its current docs show GenAI-Perf as a tool in phase-out. The docs show AIPerf as the recommendation for new benchmarks. Keep the legacy methodology as evidence, not as an unqualified new-tool recommendation. [observed + inference] [Docs](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

Use rate sweeps. Check that the external generator does not put a limit on offered load. Concurrency ceilings do not make a copy of independent production arrivals. [inference] [Docs](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

### 4.2 TensorRT-LLM

`trtllm-bench throughput` sends offline executor work as fast as possible. The documented quickstart uses 3,000 synthetic requests, 128/128 lengths, and FP8. The page shows an upper-bound throughput benchmark and a work-in-progress API. [observed] [Benchmarking](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

Reports show model/runtime, dtype/quantization/KV dtype, TP/PP, scheduler, and KV-memory fraction. Reports also show lengths, count, output/request throughput, and example percentiles. The benchmark quantization menu is a subset of runtime support. Options such as none, FP8, and NVFP4 are in this menu. [observed] [Benchmarking](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

Executor ceilings do not show some endpoint, admission, traffic, and interference costs. Use online serving clients for tenant experience. [inference] [Benchmarking](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

### 4.3 Google’s capacity method

Google shows a recommendation: use the same representative model across hardware. Google uses TTFT, inter-token latency, and tokens/s/user as measurements. Then Google makes concurrency higher until the run shows a p99 target violation. Google keeps system throughput as sustained TPS/chip at the operating boundary. [observed] [Accelerator benchmarking](https://docs.cloud.google.com/docs/ai-ml/accelerator-performance-benchmarking)

Keep discrete measured passing and failing points. MLPerf Endpoints shows a preference for measured step curves over unverified smooth interpolation. [observed + inference] [MLPerf Endpoints](https://mlcommons.org/2026/03/mlperf-endpoints-gen-ai-benchmarking)

### 4.4 Cache, scheduler, and mix

Azure shows a warning about mixed workloads. In these workloads, requests use the same cache. The batch also puts short calls with longer calls. TensorRT-LLM keeps a record of scheduler policy and KV allocation. Its tuned engine settings can be different for different dataset lengths. [observed] [Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency) · [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

Keep no-reuse and controlled-prefix cases separate. Long outputs keep KV slots for a longer time. Keep a record of queueing, preemption, occupancy, admissions, and per-class latency. GPU utilization alone does not show the bottleneck. [inference] [vLLM metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

### 4.5 Quality

Quantized benchmark support shows a speed-test path, not unchanged quality. Check the deployed checkpoint and weight/KV formats against a reference on fixed tasks. A small two-hour quality set shows gross regressions, not broad capability parity. [inference] [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

## 5. Two-hour check mapping

This schedule is a proposed rack diagnostic, not a hyperscaler guarantee. [inference] [Google benchmarking](https://docs.cloud.google.com/docs/ai-ml/accelerator-performance-benchmarking)

| Check | Approximate minutes | Keep |
| --- | --- | --- |
| Identity | 10 | Model/runtime/client/topology/precision/limits |
| Cold load and warmup | 10–15 | Staging/load/engine-build distinctions; first inference |
| Baseline | 10 | Client stream samples, actual lengths, errors |
| Controlled ramp | 25–35 | Rates, tails, goodput, queue, KV, GPU telemetry |
| Cache/KV | 15–20 | Reuse contrast; pressure outcomes |
| Mixed/quality | 15–20 | Per-class effects; reference scores |
| Repeat/artifacts | 10 | Raw evidence and measured drift |

The range total is roughly 95–120 minutes, before unbounded model/engine builds. Put artifacts in place before the run, and keep a separate startup record. Missing checks: unmeasured. [calculated + inference] [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

## 6. Conflicts and traps

Quota is not achieved throughput. Capacity is not latency. Billing reservations are not deployment capacity. Input/output burndown is not generated-token accounting.

Synthetic short lengths and warm prefix hits can make the comparison result opposite. Saturation is not an interactive SLO. Differently tuned stacks do not show hardware-only comparisons. [observed + inference] [AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html) · [Google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput) · [Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency)

## 7. Established and missing evidence

Public sources show units, billing, quota/admission rules, workload dependence, and benchmark methods. They do not show a universal MU/PTU/GSU-to-GPU conversion or common contract-grade p99. Private model/region contracts can put more terms in place. [observed gap] [AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html) · [Google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput) · [Azure](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency)

## 8. Source policy

The brief keeps primary operational docs and project benchmark guides. It does not use third-party PTU/GSU ratio tables as contract evidence. Azure’s old sizing URL shows a 404 error. The current latency guide shows workload examples. [observed + inference] [Azure sizing URL](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/provisioned-throughput-sizing) · [Azure live guide](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/latency)

## Gaps

- Exact MU throughput and remedies are only in account quotes/contracts. [observed gap] [AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)
- Model/region/deployment terms can put more terms on top of public docs. [inference] [Google](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)
- This category shows no verification of the latest AIPerf/vLLM release flags. Use pinned versions of actual deployment tools. [observed gap] [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)
- No source shows the Chennai rack’s expected token rate or broad quality parity. Live tests must use a declared workload and reference. [inference] [Google benchmarking](https://docs.cloud.google.com/docs/ai-ml/accelerator-performance-benchmarking)
