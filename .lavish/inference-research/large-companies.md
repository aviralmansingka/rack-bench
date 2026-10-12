# Large-company inference-serving SLOs: what to check on a GPU rack

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Executive answer

Large companies use a balance of latency, throughput, capacity, availability, and output quality as inference quality. Their disclosures use TTFT, incremental token latency, token rate, request success, cache hit rate, and model-load time. Prefill, decode, scheduling, and cache state make the result different. [observed] [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism) · [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics) · [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

Rack-bench must use measured goodput under a declared workload and latency limits. A two-hour test does not show production availability. [inference] [Azure metrics](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

## 2. Serving SLOs and metric boundaries

### 2.1 Product-specific targets

Meta uses queries/s as throughput. Meta uses TTFT and time-to-incremental-token (TTIT) as latency. Its technical post shows ideal TTFT below 350 ms and TTIT below 25 ms. These are engineering targets, not universal contractual SLOs. [observed] [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism)

Google shows model priority for services with different latency sensitivity. Its Triton/GKE example uses `PRIORITY_MAX` to keep Tier-1 models safe. It shows no universal latency target. [observed] [Google](https://cloud.google.com/blog/products/compute/triton-inference-server-in-gke-nvidia-google-kubernetes)

Cloudflare keeps immediate-response traffic separate from asynchronous batch traffic. The batch API uses eventual completion as its target, not immediate response. [observed] [Cloudflare](https://blog.cloudflare.com/workers-ai-improvements)

### 2.2 Azure measurement boundaries

Azure shows these metrics in its docs. They do not show contractual percentiles. [observed] [Azure metric catalog](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

- `AzureOpenAINormalizedTBTInMS` shows streaming generation rate in milliseconds. [observed] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)
- Normalized time to first byte is for streaming and non-streaming requests. It is not automatically client TTFT. [observed + inference] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)
- Time to Response shows first response at the API gateway. Azure shows it as approximate, without client-to-endpoint latency. Prompt size and cache-hit size make it different. [observed] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)
- Tokens Per Second is response tokens divided by generation time. This is response rate, not aggregate rack throughput. [observed] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)
- The cited catalog uses one-minute time grains and average/minimum/maximum aggregation. Those fields do not show request-level p50/p99. [observed] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

Keep client timestamps separate from gateway or server timing. Check for generated content in the first byte. TTFT, average TPOT, and individual ITL gaps show answers to different questions. [inference] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics) · [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism)

## 3. Mechanisms with quality effects

### 3.1 Prefill and decode interference

Meta shows prefill as compute-bound and decode as memory-bandwidth-bound. It shows all-reduce contributions up to 30% of end-to-end latency. The report shows a possible 10–30% latency contribution from expert-parallel all-to-all, especially during decode. These values are for its tested configurations. [observed] [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism)

Google shows dynamic batching within latency requirements. Its post shows a timing mismatch: autoscaling uses minutes, but spikes start in seconds. The BERT/T4 example is not GB300 LLM performance evidence. [observed] [Google](https://cloud.google.com/blog/products/compute/triton-inference-server-in-gke-nvidia-google-kubernetes)

Check long-prompt interference with active decoding. High aggregate utilization can keep worse interactive latency out of view. [inference] [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism)

### 3.2 Scheduling and queueing

Cloudflare shows capacity-aware routing to another city instead of a queue in the current city. Its separate batch traffic makes competition with interactive work lower. [observed] [Routing](https://blog.cloudflare.com/workers-ai-ga-huggingface-loras-python-support) · [Batch](https://blog.cloudflare.com/workers-ai-improvements)

Keep a record of offered rate, concurrency, admissions, errors, throttling, and results by request class. External latency shows scheduler outcomes. Without telemetry, it is not proof of an internal mechanism. [inference] [Google](https://cloud.google.com/blog/products/compute/triton-inference-server-in-gke-nvidia-google-kubernetes)

### 3.3 KV-cache pressure and quantization

Cloudflare shows a comparison of BF16 and FP8 KV caches for Kimi K2.6 on disaggregated H200 serving. FP8 makes cache size half as large. BF16 runs at 1,558 tokens/s at concurrency 32 and shows OOM at 64. FP8 runs at 2,192 tokens/s at 64. BF16 is faster at matching concurrency. These are aggregate rates for that deployment, not GB300 per-GPU guarantees. [observed] [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

Cloudflare shows quality scores for those cache formats. The scores are evidence for the listed suite, not universal semantic equivalence. For example, the MMLU-Pro score is 80.29 before the change and 79.29 after it. [observed] [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

Cloudflare puts tags on physical cache pages. Before supported decode operations, it checks expected mappings. On a mismatch, the affected requests do not run to completion. Its integrity-check experiment shows under 1% difference in throughput and p95 latency. [observed] [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

Run long-context tests with rising concurrency. When the engine shows them, keep a record of cache occupancy, reuse, preemption, OOM, and rejection events. [inference] [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

### 3.4 Weight quantization

Cloudflare shows GLM 5.2 checkpoint compression from 705 GB to 421 GB with INT4. At concurrency 1, decode speed is 60 tokens/s before and 92 tokens/s after. At concurrency 64, the rates are 1,672 before and 1,933 tokens/s after. Prefill is about 10,160 tokens/s before and 8,660 tokens/s after. Its evaluation table shows small but nonzero score differences. [observed] [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

Meta shows selective FP8 quantization for its Adaptive Ranking Model. The source shows negligible recommendation-quality impact, not universal model fidelity. [observed] [Meta](https://engineering.fb.com/2026/03/31/ml-applications/meta-adaptive-ranking-model-bending-the-inference-scaling-curve-to-serve-llm-scale-models-for-ads)

Keep model, checkpoint, weight format, KV format, engine, and kernel identity. Put each speed result with a fixed task-quality comparison. Exact-output matching alone does not show semantic equivalence. [inference] [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

## 4. Observability limits

Azure shows counts, status codes, availability, token measurements, cache-match rate, and provisioned utilization. Availability is `(Total Calls - Server Errors) / Total Calls`, with server errors at HTTP ≥500. Provisioned utilization at or above 100% starts 429 throttling. [observed] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

Minute aggregates are useful for operations. Operators cannot use minute aggregates to make a request-level p99 again. Keep external request records. [inference] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

Cloudflare AI Gateway shows request-level latency breakdowns, token usage, and error rates. This application-facing view does not show GPU allocation per request. [observed + inference] [Cloudflare Gateway](https://blog.cloudflare.com/workers-ai-gateway-unification)

Per-response token speed, aggregate token throughput, per-worker metrics, and per-GPU metrics use different denominators. GPU utilization alone is not a certification of serving quality. [inference] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

## 5. Cold starts and request mix

Meta shows a load of its trillion-parameter Adaptive Ranking Model in under ten minutes. The load uses multistream downloading and remote cache. This is not a general cold-start target. [observed] [Meta](https://engineering.fb.com/2026/03/31/ml-applications/meta-adaptive-ranking-model-bending-the-inference-scaling-curve-to-serve-llm-scale-models-for-ads)

Google shows maxima of 4× faster node startup, 80% shorter pod startup, and 5× faster model loading. These platform claims do not show independent rack performance in advance. [observed] [Google Next ’26](https://cloud.google.com/blog/products/compute/ai-infrastructure-at-next26)

Input lengths make prefill and cache demand different. Output lengths make completion latency different. Keep length distributions, tokenizer, stop rules, and cache state with every result. [inference] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)

## 6. Two-hour rack-check mapping

This sequence is a recommendation, not the companies’ exact suite. [inference] [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism) · [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

| Minutes | Check | Record |
| --- | --- | --- |
| 10 | Cold/model load | Process, readiness, first valid inference; artifacts and cache state |
| 15 | Single-stream baseline | Short/long prompts; TTFT, ITL, TPOT, completion time |
| 25 | Load sweep | Offered rate, admitted load, tail latency, aggregate token rate, errors |
| 20 | Mixed prefill/decode | Results by class; interference versus isolated cases |
| 20 | KV pressure | Long contexts, occupancy, preemption, rejection, OOM |
| 15 | Quantization comparison | Fixed task scores and matched performance measurements |
| 15 | Repeat and evidence | Goodput, configuration, raw samples, error counts |

Show allocated GPU count and parallelism topology. A managed endpoint without GPU inventory cannot show verified per-GPU throughput. [inference] [Cloudflare Gateway](https://blog.cloudflare.com/workers-ai-gateway-unification)

## 7. Evidence limits and conflicts

Meta shows engineering targets, not a full production SLO contract. Google’s Triton example is older than current LLM stacks. Azure shows metric boundaries, not request-level distributions. Cloudflare shows specific configurations, not universal fleet results. [observed] [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism) · [Google](https://cloud.google.com/blog/products/compute/triton-inference-server-in-gke-nvidia-google-kubernetes) · [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics) · [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)

No cited disclosure shows one industry-wide p99 target, request mix, or minimum token rate per GPU. [inference] [Meta](https://engineering.fb.com/2025/10/17/ai-research/scaling-llm-inference-innovations-tensor-parallelism-context-parallelism-expert-parallelism)

## Gaps

- Public sources do not show full production traces or GPU allocation for managed endpoints. [observed gap] [Cloudflare Gateway](https://blog.cloudflare.com/workers-ai-gateway-unification)
- No source shows a universal GB300 pass threshold. Use model, precision, workload, and customer objective to make the threshold. [inference] [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)
- The cited Azure aggregates are not a replacement for client p50/p99 samples. [observed gap] [Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics)
- Two-hour measurements do not show availability or autoscaling seasonality. They also do not show quantization fidelity outside the tested tasks. [inference] [Google](https://cloud.google.com/blog/products/compute/triton-inference-server-in-gke-nvidia-google-kubernetes) · [Cloudflare](https://blog.cloudflare.com/smaller-faster-safer-models)
