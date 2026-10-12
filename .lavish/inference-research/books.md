# Books and canonical references for inference validation

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Executive ranking

Books show the conceptual frame. Current engine documentation and benchmark rules show the operational procedure. No reviewed book shows a complete two-hour GB300 acceptance protocol. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf](https://github.com/mlcommons/inference)

| Rank | Reference | Use | Limit |
| --- | --- | --- | --- |
| 1 | Huyen, AI Engineering (2025), ch. 9 | Model, hardware, service trade-offs | Not rack certification |
| 2 | vLLM Benchmark CLI | Metrics, arrivals, cache, workload controls | Engine-specific, moving docs |
| 3 | TensorRT-LLM serving benchmark guide | NVIDIA serving procedure and profiling | Vendor implementation, not neutral standard |
| 4 | MLPerf Inference rules | Reproducibility, quality, scenario discipline | Workload-specific, not universal SLA |
| 5 | DistServe, OSDI 2024 | Goodput and prefill/decode separation | Conditional research results |
| 6 | Huyen, Designing Machine Learning Systems (2022), ch. 7 | Deployment and prediction service | General ML, not modern token-level canon |
| 7 | Fregly, AI Systems Performance Engineering, ch. 15 | Multinode inference and parallelism | Preview does not show full workbook suitability |
| 8 | Production LLMOps | Lifecycle and application observability | Contents do not show rigorous rack benchmarking |

Rankings are [inference]. Sources: [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/ch09.html), [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli), [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md), [MLPerf](https://github.com/mlcommons/inference), [DistServe](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin), [DMLS](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html), [Fregly](https://www.oreilly.com/library/view/ai-systems-performance/9798341627772/ch15.html), [LLMOps](https://leanpub.com/productionllmops).

## 2. Book editions and visible coverage

### 2.1 AI Engineering

The author shows AI Engineering as O’Reilly, 2025. Google Books shows ch. 9, Inference Optimization, at page 405 and ch. 10 at page 449. Its bibliographic record shows ISBN 978-1-098-16627-4. [observed] [Author](https://huyenchip.com/books) · [Google Books](https://books.google.com/books/about/AI_Engineering.html?id=S7M1EQAAQBAJ)

The researcher’s publisher preview shows model-, hardware-, and service-level optimization. The orchestrator’s repeat O'Reilly fetch shows access denied. The supplement checks the author's public book summary. Chapter 9 explicitly shows latency, throughput, utilization, TTFT/TPOT, quantization, KV cache, batching, parallelism, and prompt caching. This shows specific topics, not complete chapter access. [observed] [Publisher](https://www.oreilly.com/library/view/ai-engineering/9781098166298/ch09.html) · [Checked author summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization)

Use this book as the strongest starting point. Service-level traffic and cost framing shows the limits of one unloaded token rate for serving quality. Do not use a preview as proof of a complete metric or cache-stress recipe. [inference] [Publisher](https://www.oreilly.com/library/view/ai-engineering/9781098166298/ch09.html)

### 2.2 Designing Machine Learning Systems

The author's record shows the book as O’Reilly, 2022. The record shows its repository with contents and chapter summaries. Chapter 7 is Model Deployment and Prediction Service. [observed] [Author](https://huyenchip.com/books) · [Publisher](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html)

The supplement checks the author's public chapter 7 summary, not only its title. The summary shows batch/online prediction and deployment optimization. Use it for deployment context. The summary does not show current TTFT, continuous-batching, or KV-pressure benchmark procedures. [observed + inference] [Checked author summary](https://github.com/chiphuyen/dmls-book/blob/main/summary.md#chapter-7-model-deployment-and-prediction-service)

### 2.3 Specialist and LLMOps supplements

The Fregly chapter preview shows multinode inference, parallelism, speculative decoding, and disaggregated prefill/decode. Full-text suitability for this exact rack procedure: unverified. [observed + inference] [Chapter 15](https://www.oreilly.com/library/view/ai-systems-performance/9798341627772/ch15.html)

Production LLMOps shows 222 pages, complete status, and update date 2026-08-27. Its contents show architecture, evaluation, CI/CD, and observability. This is background, not proof of token-throughput or scheduler-validation methodology. [observed + inference] [Leanpub](https://leanpub.com/productionllmops)

## 3. Operational canon by check

### 3.1 Metric definitions

vLLM uses client TTFT from request send to first streamed output. ITL uses gaps between streamed outputs as samples. Request TPOT uses `(E2E - TTFT) / (output_tokens - 1)`. vLLM shows a warning about nonstandard terminology. Speculative decoding can put multiple tokens in one output event. [observed] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

Keep formulas, timestamps, observation units, and raw request records. TPOT and ITL percentiles can show differences because their sample weights are different. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

### 3.2 Offered load and capacity

vLLM shows request rate, burstiness, concurrency, and load ramp controls. TensorRT-LLM shows concurrency sweeps, repeated runs, percentile metrics, and profiling across tensor-parallel ranks. [observed] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)

Use finite offered arrivals for queueing behavior. Keep saturation/concurrency results separate. Keep a record of output tokens/s, input tokens/s, and requests/s without substitution. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

### 3.3 Scheduler evidence

Put client latency beside available queue, running/waiting, and iteration evidence. A throughput plateau with rising TTFT and decode stalls with stable TTFT show different behaviors. These guides do not show universal scheduler thresholds. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)

### 3.4 KV and prefix-cache pitfalls

vLLM shows a warning about possible prefix-cache hits and inflated throughput from repeated benchmark prompts. Common prefixes can make hits inside one run. vLLM shows seed changes, cache resets/restarts, and cache-resetting sweeps as controls for unintended reuse. [observed] [vLLM cache warning](https://docs.vllm.ai/en/latest/benchmarking/cli)

Keep no-reuse and deliberate reuse results separate. Show capacity, context lengths, occupancy, and engine-exposed preemption. Low-concurrency short prompts do not show cache-pressure behavior. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

### 3.5 Cold load

TensorRT-LLM starts the server before its serving benchmark. Its profiling steps keep warmup and steady state separate. Therefore, online token timing does not automatically show download, checkpoint load, engine build, or readiness time. [observed + inference] [Guide](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)

### 3.6 Quantization quality

MLPerf v5.0’s Llama 3.1 405B quality gate uses a minimum of 99% of its FP16 reference. Its task scores use ROUGE-L and exact match. These are benchmark-specific gates, not universal quality tolerances. [observed] [MLPerf v5.0](https://mlcommons.org/2025/04/llm-inference-v5)

Put weight/KV precision changes beside a named task-quality reference. Faster tokens do not show fidelity. [inference] [MLPerf v5.0](https://mlcommons.org/2025/04/llm-inference-v5)

### 3.7 Workload shapes

vLLM uses real, custom, and synthetic datasets with length statistics. MLPerf’s Llama 3.1 405B workload shows reported mean input/output lengths 9,400/680. Other workloads use different targets. [observed] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf v5.0](https://mlcommons.org/2025/04/llm-inference-v5)

Keep actual lengths, stop rules, tokenizer, arrival pattern, cache policy, and seeds. Use one fixed synthetic shape for controlled comparison, not all-traffic certification. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

## 4. Two-hour implications

Keep the model/configuration and metric contract fixed. Run a separate cold-load measurement. Run a low-load point and a load sweep. When the budget shows sufficient time, run cache-pressure and paired quality tests. Keep omissions explicit. This is a proposed design, not a book-prescribed schedule. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)

## 5. Conflicts and limits

Do not use DMLS or a general LLMOps title as the sole performance authority. Do not use a vendor comparison blog as a neutral acceptance standard. Publisher previews show visible coverage, not unpreviewed procedures. [inference] [DMLS](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html) · [LLMOps](https://leanpub.com/productionllmops)

No source shows a universal GB300 p99 target independent of model and workload. Show counts and explicit observation units with short-window percentiles. [inference] [MLPerf v5.0](https://mlcommons.org/2025/04/llm-inference-v5)

## 6. Reading order

Use AI Engineering ch. 9 for context. Use pinned vLLM/TensorRT-LLM sources for actual measurement. Use MLPerf rules for reproducibility and quality discipline. Use DistServe for disaggregation and goodput. [inference] [Author](https://huyenchip.com/books) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf](https://github.com/mlcommons/inference) · [DistServe](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin)

## 7. Source policy

The brief keeps primary publisher/author records, project documentation, benchmark rules, and proceedings. Do not use reviews as proof of hidden chapter content. Do not use vendor comparisons as neutral methodology. [inference] [Author](https://huyenchip.com/books) · [MLPerf](https://github.com/mlcommons/inference)

## 8. O'Reilly sources

The [nine-source supplement](oreilly.md) keeps per-source metadata, access levels, chapter/agenda topics, portable checks, and limits. Keep AI Engineering as the primary inference book. Use the following sources only within their checked boundaries. These priorities are recommendations, not full-text comparisons. [inference] [AI Engineering author summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization)

| Priority | Source | Checked use | Boundary |
| --- | --- | --- | --- |
| A | Machine Learning Production Systems, ch. 11–14, 22 | Production lifecycle and GenAI serving topics | TOC/description; no chapter procedures |
| B | Latency, related book | General modeling, measurement, concurrency | Book description/TOC; not video sections |
| C | LLMs in Finance, current supplemental lab 10 | Capacity/SLO constraints and queue-stress context | Fictional fixtures; not canonical book chapter |
| D | Grokking Streaming Systems, ch. 6–7 samples | Parallelization, windows, backpressure context | Partial prose; not token-stream metrics |
| E | Hands-On ML third edition, ch. 2, 19 | General validation and TF deployment | TOC/author examples; no full chapter 19 |
| F | Streaming Systems, ch. 1–5 | Time/window/completeness vocabulary | TOC-only methods |
| G | How Large Language Models Work, ch. 2, 7 previews | Tokenizers and conceptual deployment limits | Public overviews/summaries/FAQs |
| H | TFX event | Evaluation slices, versioning, batching agenda | No verified recording/demonstrations |
| I | TF Serving video | Historical configuration agenda | No verified playback/transcript |

Sources: [production-book description](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ), [Latency book](https://www.manning.com/books/latency), [finance lab](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb), [streaming samples](https://livebook.manning.com/book/grokking-streaming-systems/chapter-6), [Géron examples](https://github.com/ageron/handson-ml3), [Streaming Systems catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp), [LLM preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7), [TFX agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880), [TF Serving agenda](https://conferences.oreilly.com/tensorflow/tf-ca-2019/public/schedule/detail/78365.html). [observed access/topics + inference priorities]

Public author summaries show more detail for N07's topic evidence. Complete-book access: gap. Do not use related Latency book chapters as evidence for its inaccessible video. Do not use the current finance lab as the canonical chapter. [observed + inference] [Author summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md) · [Finance edition boundary](https://github.com/PacktPublishing/LLMs-in-Finance) · [Latency video](https://learning.oreilly.com/videos/-/9781633438088VE/?orm_source=mcp)

## Gaps

- Full-text access to all books: unverified. The orchestrator cannot check the O’Reilly chapter preview again. [observed gap] [Publisher](https://www.oreilly.com/library/view/ai-engineering/9781098166298/ch09.html)
- No cited reference shows a universal GB300 acceptance threshold. [inference] [MLPerf](https://mlcommons.org/2025/04/llm-inference-v5)
- Model staging, initialization, and the chosen workload make the two-hour feasibility different. [inference] [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)
- Use pinned engine-document versions and archived commands before certification. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
