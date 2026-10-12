# Inference-serving quality: lab metrics, tools, and two-hour checks

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Executive finding

Use sustained output throughput, request latency, outcomes, workload identity, and a quality floor to check serving quality. Saturation alone does not always show waiting users. A concurrency-only test does not show behavior under independent arrivals. [inference] [vLLM CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/) · [Mooncake](https://arxiv.org/html/2407.00079v4)

A compact two-hour plan can show cold load, a baseline, rate sweep, cache contrast, KV pressure, and quality screening. Its feasibility is conditional on staged artifacts and bounded startup. [inference] [vLLM metrics](https://docs.vllm.ai/en/latest/design/metrics.html) · [SGLang](https://docs.sglang.ai/developer_guide/benchmark_and_profiling.html)

The initial evidence uses moving `latest`/`main` documentation. It does not show every tool's latest release. Keep actual client/runtime/model/tokenizer versions with every result. [observed + inference] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/) · [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

## 2. Metric definitions

### 2.1 Throughput denominators

The vLLM results show successful requests, duration, input/generated tokens, request throughput, input/output throughput, and combined throughput. Each basic rate is the successful-request total divided by benchmark duration. Input-plus-output rate is not generation rate. [observed] [CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)

For rack-bench, use aggregate output tokens/s divided by all GPUs allocated to the tested serving fleet. Keep aggregate output rate and allocated count beside that normalization. This is an explicit reporting choice, not a direct measurement of each GPU's output. [inference] [TensorRT-LLM output](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

TensorRT-LLM results separately show request, total output, per-user output, and per-GPU output rates. Token-rate labels alone do not show the rate type. [observed] [Benchmarking](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

### 2.2 Latency

The vLLM metrics show separate client benchmarking and server timing. Its server frontend arrival currently starts at tokenization. Its server end-to-end interval runs to final-token receipt by the frontend. [observed] [Metrics design](https://docs.vllm.ai/en/latest/design/metrics.html)

- TTFT is the time to first generated output from the declared arrival boundary. [observed] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)
- Request TPOT uses `(E2E - TTFT) / (output_tokens - 1)`. [observed] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)
- ITL is the set of wall-clock gaps between successive streamed output events. [observed] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)
- Request-level TPOT makes one entry per completed request. Longer outputs put more samples in ITL. [observed] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

The Prometheus TPOT histogram shows zero for requests with no more than one output token. `bench serve` removes them from TPOT statistics. The formula is undefined for one token. For these requests, rack-bench shows TPOT as unavailable. [observed + inference] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

### 2.2.1 Immutable client evidence

The checked vLLM client commit is `21da73343ad35f756e053ba4155dafb05229b0c5`, from September 2025. This is a historical code snapshot, not a claim about the latest release. [observed] [Pinned source](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/serve.py)

The client uses reported output-token counts, or retokenization of the generated text. It removes ≤1-token outputs from TPOT statistics. For goodput, it puts their TPOT at zero. Do not silently use that goodput edge case in rack-bench. [observed + inference] [Lines 299–323](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/serve.py#L299-L323)

The SSE client puts buffered bytes into complete messages. It keeps a timestamp for each content message. Therefore, ITL shows parsed-message gaps. [observed] [Buffer lines 20–52](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/lib/endpoint_request_func.py#L20-L52) · [Timing lines 153–203](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/lib/endpoint_request_func.py#L153-L203)

Gamma delays make the finite arrivals. Burstiness one makes the delays exponential. A semaphore puts a cap on in-flight requests. The benchmark timer starts before request generation. It runs until completion of all tasks. Rates use that duration, including the completion tail. [observed] [Arrivals lines 122–193](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/serve.py#L122-L193) · [Timer lines 602–663](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/serve.py#L602-L663) · [Rates lines 410–423](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/serve.py#L410-L423)

The pinned client also shows a peak-per-second series from one timestamp per streamed event. That reconstruction can show an undercount of bundled tokens. Its retokenization fallback shows slight token-count inflation. Use authoritative token totals and explicitly counted event buckets, not an unverified peak label. [observed + inference] [Lines 299–410](https://github.com/vllm-project/vllm/blob/21da73343ad35f756e053ba4155dafb05229b0c5/vllm/benchmarks/serve.py#L299-L410)

### 2.3 Chunks are not tokens

Speculative decoding can put multiple tokens in one event. Then event-gap ITL is not proof of individual token cadence. Keep event timestamps and token IDs/counts where available. Use the label event-gap ITL when one-token events are unverified. [observed + inference] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

A non-streaming client can show completion latency. It cannot make a reliable reconstruction of streamed TTFT or gaps. [inference] [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

## 3. Arrivals versus concurrency

vLLM finite request rates use Poisson/gamma arrivals with burstiness controls. Infinite request rate sends all work at time zero before concurrency gating. `--max-concurrency` can make the achieved send rate lower. [observed] [CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)

SGLang makes asynchronous HTTP rate and concurrency controls available. Its guide makes a recommendation: use at least five times the concurrency in prompts for steady-state throughput. This is a heuristic, not a universal statistical sufficiency rule. [observed + inference] [Guide](https://docs.sglang.ai/developer_guide/benchmark_and_profiling.html)

An open-loop driver sends requests on its schedule, regardless of completions. A closed-loop driver sends replacement requests after completions. It makes its send rate lower during slowdown. A simultaneous burst is a third load pattern. Keep configured arrivals, actual sends, completions, concurrency, burstiness, and failures. [inference] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/)

## 4. Goodput and percentiles

The vLLM CLI makes `--goodput` SLOs available, such as `ttft`, `tpot`, and `e2el`. Request goodput is successful completed requests, with all declared latency conditions met, divided by duration. Keep all submitted outcomes separate. [observed + inference] [CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/)

Mooncake runs effective-throughput optimization under TTFT/TBT limits. Its count keeps only fully completed requests. The paper also shows wasted work under overload. Keep raw partial-token counters separate. [observed] [Paper](https://arxiv.org/html/2407.00079v4)

The vLLM CLI makes selectable percentiles available. TensorRT-LLM examples show P50/P90/P95/P99 request latency. Keep counts, estimator, raw samples, and observation unit. Small-N p99 is not proof of a tail guarantee. [observed + inference] [CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/) · [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

## 5. Tool coverage

### 5.1 vLLM

Use `bench serve` with an existing endpoint. It makes rates, concurrency caps, warmups, datasets, percentile controls, detailed results, and SLO conditions available. Its metrics show running/waiting requests, KV usage, prefix counters, queue/prefill/decode intervals, and finish reasons. [observed] [CLI](https://docs.vllm.ai/en/latest/cli/bench/serve/) · [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

Use external request samples with server time series. Client latency shows the outcome. Use server metrics for causal diagnosis. Current V1 uses recomputation for preempted work, not the old swapped-request path. Do not use deprecated metrics. [inference + observed] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

### 5.2 SGLang

SGLang keeps these test types separate: online `bench_serving`, server one-batch tests, offline scheduler throughput, and lower-level model-runner tests. Its guide makes a recommendation: use online serving for realistic metrics. One-batch tests are not steady state. Cross-batch queueing is in some multibatch denominators. [observed] [Guide](https://docs.sglang.ai/developer_guide/benchmark_and_profiling.html)

Forced generation beyond EOS can show gibberish and a decaying-batch tail. Offline/kernel ceilings are not substitutes for endpoint/admission/streaming measurements. [observed + inference] [Guide](https://docs.sglang.ai/developer_guide/benchmark_and_profiling.html)

### 5.3 NVIDIA

TensorRT-LLM results show scheduling policy, KV-memory percentage, dataset shapes, latency percentiles, and output rates. Its executor throughput mode is not, by itself, a tenant HTTP serving test. [observed] [Benchmarking](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

GenAI-Perf makes streaming, arrival/concurrency control, synthetic/data inputs, output-length control, warmups, CSV/JSON, and telemetry available. Its docs show a phase-out. The docs make AIPerf the recommendation for new work. Keep the actual tool name with every result. Do not use an unqualified legacy default. [observed + inference] [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

### 5.4 DeepSeek and MLPerf

The MLPerf v6.0 update shows DeepSeek-R1 Server p99 TTFT/TPOT 2 s/80 ms and Interactive 1.5 s/15 ms. These are scenario limits, not generic rack thresholds. [observed] [MLCommons](https://mlcommons.org/2026/03/mlperf-inference-gpt-oss)

GPT-OSS performance tests use PubMed summarization with mean input/output around 5,000/1,250 tokens. Accuracy tests use math, code, and science tasks. Compliance tests check quality and output-length consistency. [observed] [MLCommons](https://mlcommons.org/2026/03/mlperf-inference-gpt-oss)

DeepSeek's primary deployment report shows a 24-hour H800 workload: 608B input tokens, 342B disk-KV-cache hits, and 168B output tokens. It shows average user output speed 20–22 tokens/s. Reported per-node rates are about 73.7k input tokens/s for prefill and 14.8k output tokens/s for decode. These figures use different denominators. [observed] [DeepSeek report](https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md)

The report shows expert parallelism, communication overlap, load balancing, FP8 matrix multiplication/dispatch, and BF16 MLA/combine. It shows no controlled client arrivals, percentile latency, or per-GPU benchmark denominator. Use it as production context, not as a GB300 acceptance baseline. [observed + inference] [DeepSeek report](https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md)

### 5.5 llama.cpp

`llama-bench` runs separate prompt processing (`pp`), generation (`tg`), and combined (`pg`) tests. It runs tests five times by default. Results show average tokens/s with standard deviation. Tokenization and sampling are not in the measurements. [observed] [README](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md)

Defaults use 512 prompt tokens and 128 generation tokens. `-d` puts KV state at a context depth. `--no-warmup` removes the default warmup. Context depth does not show production prefix-hit behavior. [observed + inference] [README](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md)

Use pp/tg as backend diagnostics. They do not show HTTP TTFT, queueing, arrival behavior, or goodput. Use an external serving client on `llama-server` for those results. Exact server timer semantics are unverified. [inference] [README](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md)

## 6. Workload and cache controls

### 6.1 Length distribution

Mooncake shows prefill, decode, and varying workloads. Its Kimi trace shows averages of 7,590 input and 182 output tokens. That is one service's mix, not a universal mix. [observed] [Paper](https://arxiv.org/html/2407.00079v4)

Keep tokenizer, model, actual length distributions, stop/EOS rules, sampling, and reuse settings. A requested maximum is not the actual generated count. Put separate labels on forced-length synthetic performance and natural EOS quality tests. [inference] [SGLang](https://docs.sglang.ai/developer_guide/benchmark_and_profiling.html) · [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

### 6.2 Prefix cache

The vLLM metrics show prefix query/hit counters. Use interval deltas, not unexplained cumulative percentages. Mooncake makes a trade-off: reuse benefit versus KV transfer, queueing, and congestion. [observed] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html) · [Paper](https://arxiv.org/html/2407.00079v4)

Run unique/no-reuse and controlled shared-prefix cases separately. Check resets and hit rates when possible. Otherwise, put an unverified label on the cache condition. [inference] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

### 6.3 KV pressure

Use more active contexts or longer concurrent sequences under a declared load. Keep occupancy, running/waiting requests, queue time, preemption/recompute, rejection, TTFT, ITL, and goodput. High occupancy alone is not proof of thrashing. [inference] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html) · [Mooncake](https://arxiv.org/html/2407.00079v4)

## 7. Quantization fidelity

MLPerf keeps quality and performance separate. It puts compliance constraints on output lengths and speculative decoding. Speed alone is not proof of unchanged quality. [observed + inference] [MLCommons](https://mlcommons.org/2026/03/mlperf-inference-gpt-oss)

Use a small fixed task-quality set with a named reference, weight/KV formats, decoding settings, and tolerance. Text similarity alone is not sufficient. A small set only shows gross regressions. Missing evaluators make quality evidence unavailable. [inference] [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc)

## 8. Cold load and warm state

Online tools use a running server. Download, engine compilation, graph capture, weight loading, and readiness are not automatically in their request measurements. [observed + inference] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/) · [GenAI-Perf](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/genai-perf/README.html)

Use separate measurements for process start to discovery readiness and first successful inference. Keep storage/process/kernel/prefix cache states distinct. Remove declared warmups from steady state. Keep the cold first-request latency in the report. [inference] [Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)

## 9. Two-hour plan

This is a proposed schedule. It is conditional on staged model/engine artifacts. [inference] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/)

| Minutes | Check | Artifacts |
| --- | --- | --- |
| 0–20 | Cold launch/load | Ready and first valid generation; cache state |
| 20–35 | Warmup and baseline | TTFT/TPOT/ITL/E2E; actual lengths |
| 35–85 | Rate sweep | Offered/sent/completed rate, errors, tails, goodput |
| 85–100 | Prefix contrast | Verified counters or explicit unavailable state |
| 100–112 | KV pressure | Occupancy, queue, preemption, outcomes |
| 112–120 | Quality screening/artifacts | Paired score, length sanity, versions |

Use measurements to show the operating knee. Keep one point below and one above it. If startup uses the whole budget, show the omitted checks. Do not put a pass verdict there. [inference] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/)

## 10. Pitfalls

Concurrency is not request rate. Event gaps are not always token gaps. One-token TPOT is not the same in histograms and benchmark statistics. Serving layers are not in offline rates.

Requested lengths are not always the same as output lengths. Cache warmth makes prefill cost different. Dropped requests and denominator changes can make false speedups. [observed + inference] [vLLM](https://docs.vllm.ai/en/latest/design/metrics.html) · [SGLang](https://docs.sglang.ai/developer_guide/benchmark_and_profiling.html)

## 11. Minimum evidence bundle

Keep these items: aggregate/allocated-GPU output throughput; request throughput; input/output totals; latency populations and counts; arrivals; outcomes; queues; cache. Also keep quality; load timing; model/runtime/client identities; topology; raw events. Use measurements for a PASS verdict. Keep performance-target verdicts separate from evidence status. [inference] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/) · [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc)

## Gaps

- Current tool documentation is mutable. §2.2.1 shows a historical immutable client. It does not check the deployment's current runtime. [observed gap] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/)
- Use pinned implementation checks for TensorRT-LLM timing edge cases. [observed gap] [Benchmarking](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)
- The sources show no general quantization tolerance or tenant SLO. [inference] [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc)
- The sources do not show an exact Chennai model, replica topology, request mix, or production trace. [inference] [vLLM](https://docs.vllm.ai/en/latest/cli/bench/serve/)
- llama.cpp HTTP-server timing internals are still unverified. §5.5 shows only its offline benchmark boundary. [observed gap] [llama.cpp benchmark source](https://github.com/ggml-org/llama.cpp/tree/master/tools/llama-bench)
