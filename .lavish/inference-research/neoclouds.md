# What do neocloud serving claims actually show?

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Executive finding

A headline tokens/s is incomplete without a denominator. The denominator can be per-user output speed. It can be aggregate input-plus-output throughput. It can be GPU-normalized throughput. Precision, workload, concurrency, cache, and stack make the result different. [observed + inference] [InferenceMAX](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking) · [Artificial Analysis](https://artificialanalysis.ai/methodology/performance-benchmarking)

Rack-bench must use measured operating points under declared arrivals. These points are per-user streaming speed, tails, aggregate output rate, outcomes, and SLO goodput. A two-hour check is not proof of production reliability. Without verified costs, it is not proof of economics. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [InferenceMAX](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)

## 2. Metric denominators

### 2.1 User speed versus fleet throughput

Artificial Analysis uses output speed after the first token. InferenceMAX keeps tokens/s/user interactivity separate from tokens/s/GPU throughput. InferenceMAX also runs a concurrency sweep. Larger batches can make aggregate throughput higher and per-user speed lower. [observed] [Artificial Analysis](https://artificialanalysis.ai/methodology/performance-benchmarking) · [InferenceMAX](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)

Show whether throughput uses input, output, or both. Keep allocated GPU count and topology. Normalization alone does not show the speed of any individual stream. [inference] [InferenceMAX](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)

### 2.2 TTFT, TPOT, ITL, and completion

Transport, queueing, and prefill are all part of client TTFT. Request TPOT normally uses `(E2E - TTFT) / (output_tokens - 1)`. ITL uses samples of consecutive output events. Speculative decoding can put several tokens in one event. Then event gaps and token gaps are different. [observed] [Together definitions](https://docs.together.ai/learn/ttft-and-tps) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

Keep p50/p99 TTFT, request TPOT, event-gap ITL, completion latency, counts, errors, and actual lengths. Median speed alone does not show tail quality. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

### 2.3 Goodput

vLLM can use TTFT, TPOT, and completion SLOs. In InferenceX, goodput is latency-qualified work. Show all gates before the measurement run. Keep successful compliant requests/s separate from output tokens/s from compliant requests. [observed + inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [Glossary](https://inferencex.semianalysis.com/glossary)

## 3. Vendor evidence

### 3.1 Cerebras

Cerebras shows Llama 3.1 405B at 969 output tokens/s for a 1,000-token prompt. The same report shows 240 ms TTFT, 128K context support, and 16-bit weights. The 100K-prompt result shows 539 tokens/s and six responding vendors. The post shows Artificial Analysis as the measurement source. [observed, vendor report] [Announcement](https://www.cerebras.ai/blog/llama-405b-inference)

These are output-speed claims, not aggregate tokens/s/GPU. The announcement shows no matched concurrency frontier, p99 tails, or declared SLO goodput. It does not show a GB300 result. [observed gap + inference] [Announcement](https://www.cerebras.ai/blog/llama-405b-inference)

### 3.2 Together

Together shows Kimi K2.5/EAGLE on four B200 GPUs against TensorRT-LLM on four and SGLang on eight. Inputs are roughly 45K–200K tokens. The output average is 450, with p50 293 and p99 2,230. At 2.5M total input TPM, Together shows 31% higher per-user TPS than TensorRT-LLM. Its p50 TTFT table shows 0.71/1.1/5.1 seconds for Together/TensorRT-LLM/SGLang. [observed, vendor report] [Coding benchmark](https://www.together.ai/blog/coding-agent-benchmarks)

The source shows this text: “625 TPM per GPU (2.5M TPM total).” For four GPUs, this figure is internally inconsistent. Arithmetic shows `2,500,000 / 4 = 625,000` input TPM/GPU. Keep this as a source-unit conflict. Do not silently make it a corrected measured figure. [observed + calculated] [Coding benchmark](https://www.together.ai/blog/coding-agent-benchmarks)

The post shows that SGLang TP4/EAGLE runs out of memory. For that reason, Together uses TP8. The post shows this as version one and puts emphasis on p50 TTFT. It does not show identical allocation or p99-goodput parity across engines. [observed + inference] [Coding benchmark](https://www.together.ai/blog/coding-agent-benchmarks)

### 3.3 Fireworks

The Fireworks guide shows these recommended practices: use realistic payloads, warmup, and concurrency ramps. The guide also shows checks of throughput, TTFT, completion time, generation speed, and errors. [observed] [Benchmarking guide](https://docs.fireworks.ai/deployments/benchmarking)

The Fireworks B200/NVFP4 DeepSeek V3 announcement shows over 250 tokens/s. It also shows a 3.5× comparison against SGLang/H200. The post shows eight NVLink GPUs with MTP off. The post also shows no complete TensorRT-LLM FP4 baseline validation. Hardware, precision, and engine are different. [observed, vendor report] [FireAttention](https://fireworks.ai/blog/fireattention-v4-fp4-b200)

The reviewed text does not clearly show the denominator of the headline >250 tokens/s. It also shows no p99/SLO curves. Do not show it as rack output tokens/s/GPU. [observed gap + inference] [FireAttention](https://fireworks.ai/blog/fireattention-v4-fp4-b200)

### 3.4 SambaNova

SambaNova’s SN50 post shows four H200 GPUs for prefill and a 16-RDU SambaRack for decode. It shows up to 850 tokens/s for short context and over 450 for long context. The post shows Artificial Analysis as the source of these figures. [observed, vendor report] [SN50](https://sambanova.ai/blog/sn50-runs-fastest-minimax-speeds-in-the-world)

This is heterogeneous disaggregated-system evidence, not standalone GPU/RDU speed. For a matched GB300 comparison, the announcement does not show enough traffic, concurrency, and tail data. [observed gap + inference] [SN50](https://sambanova.ai/blog/sn50-runs-fastest-minimax-speeds-in-the-world)

### 3.5 Nebius

Nebius’ vLLM guide shows PagedAttention, continuous batching, quantization, and speculation. It also shows chunked/disaggregated prefill and prefix caching. Its customer story shows throughput, QPS, TTFT, and token delay. Neither reviewed page shows a reproducible GB300 serving-result matrix. [observed + observed gap] [Guide](https://nebius.com/blog/posts/serving-llms-with-vllm-practical-guide) · [Customer story](https://nebius.com/customer-stories/vllm)

## 4. Hidden controls

### 4.1 Length and mix

Artificial Analysis keeps 1K, 10K, and 100K input workloads separate. It currently shows a default 10K performance workload. Long prompts make TTFT and speed different. [observed] [Methodology](https://artificialanalysis.ai/methodology/performance-benchmarking)

Keep actual input/output distributions, tokenizer, stop rules, reasoning-token treatment, and mix. A prefill-heavy coding case is different from sustained long-output decoding. [inference] [Together](https://www.together.ai/blog/coding-agent-benchmarks)

### 4.2 Scheduler and KV pressure

vLLM shows request rate, burstiness, concurrency, percentiles, and KV capacity. A cache shortage can start preemption and make completion latency worse. Lower sequence/token limits can make pressure and throughput lower together. [observed] [CLI](https://docs.vllm.ai/en/latest/benchmarking/cli) · [Optimization](https://docs.vllm.ai/en/latest/configuration/optimization)

Use finite independent arrivals for the main rate sweep. Keep closed-loop concurrency saturation separate. Keep a record of offered/sent/completed rates, queues, preemption, errors, latency, and goodput. [inference] [CLI](https://docs.vllm.ai/en/latest/benchmarking/cli)

### 4.3 Prefix reuse

vLLM shows a warning: repeated prompts make throughput too high through cache hits. Artificial Analysis keeps the cache-behavior measurement separate and uses unique performance prompts. Keep no-reuse and deliberate shared-prefix runs separate. Check interval hit counters, or show the cache state as unverified. [observed + inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [Artificial Analysis](https://artificialanalysis.ai/methodology/performance-benchmarking)

### 4.4 Cold startup

RunPod shows cold start as the interval from a request with no running workers to a ready worker. Container startup, model loading, and initialization are in this interval. Cached models, FlashBoot, and active workers make the path different. [observed] [RunPod](https://docs.runpod.io/serverless/overview)

Keep container/image/weight caches, snapshot hits, zero-worker state, and timer endpoints. Local process-to-ready timing does not show fleet scale-from-zero frequency. [inference] [RunPod](https://docs.runpod.io/serverless/overview) · [FlashBoot](https://www.runpod.io/blog/cut-vllm-cold-starts-runpod-serverless)

### 4.5 Quantization

Fireworks shows NVFP4 hardware benefits, quality evaluation, and QAT. “FP4” alone does not show scales, calibration, training changes, or model fidelity. Put each speed result with a fixed-task quality result against a named reference. Keep weight and KV precision separate. [observed + inference] [FireAttention](https://fireworks.ai/blog/fireattention-v4-fp4-b200)

### 4.6 Economics

InferenceMAX makes cost/million tokens from hourly cost and measured throughput at a chosen interactivity point. Use `rack_hourly_cost * 1e6 / (3600 * aggregate_output_tokens_per_second)` for generated-token cost. Show cost scope and idle/utilization assumptions. API prices and rack costs use different commercial bases. [observed + calculated + inference] [InferenceMAX](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)

## 5. Published GB300 evidence

The InferenceX May 22, 2026 run uses DeepSeek-V4-Pro FP4 with input/output 8,192/1,024. It uses Dynamo vLLM and disaggregated prefill/decode, with no speculation. It shows measured configurations and an interpolated iso-interactivity comparison. [observed] [GB300/GB200](https://inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4)

The article’s 27 tokens/s/user comparison shows 6,182 tokens/s/GPU for GB300. It also shows a 2.31× cheaper cost per million total tokens for this system. These are interpolated frontier values, not a directly measured 27-token/s point. The article explicitly shows total-token cost; do not show that throughput as output-only. It shows hourly assumptions of $2.65/$2.21 per GPU for GB300/GB200. It also shows a caution about sparse far-tail interpolation. [observed] [Numbers and iso-interactivity sections](https://inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4)

A measured GB300 configuration is useful context but is not a certification of the Chennai rack. Use local evidence for local hardware, stack, allocation, topology, and cooling. Keep rack-bench acceptance at measured discrete operating points. [inference] [GB300/GB200](https://inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4)

## 6. Two-hour diagnostic

This proposed fixed schedule starts from staged artifacts and a bounded startup. It uses one declared model/configuration. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [RunPod](https://docs.runpod.io/serverless/overview)

| Minutes | Check | Keep |
| --- | --- | --- |
| 0–15 | Identity and startup | Allocation, caches, readiness, first valid inference |
| 15–25 | Baseline | Short/long prompt shapes, stream latency, outcomes |
| 25–65 | Offered-rate sweep | Throughput, interactivity, tails, goodput, queue |
| 65–90 | Prefix/KV pressure | Separate reuse states, occupancy, preemption |
| 90–110 | Quality screening | Fixed tasks, exact precision, reference score |
| 110–120 | Artifacts | Raw samples, denominators, omissions |

The child’s initial variable ranges show a total of 105–130 minutes, not 105–120. This corrected fixed schedule keeps the total at 120 minutes before unbounded downloads/builds. If startup runs over, show the missing checks explicitly. [calculated + inference] [Benchmark controls](https://docs.vllm.ai/en/latest/benchmarking/cli)

## 7. Comparability and limits

Per-user, aggregate, combined-token, and per-GPU rates are different. Together’s unequal allocation and source-unit conflict put limits on comparison. Fireworks puts hardware, precision, and engine changes together. Cerebras/SambaNova announcements show no matched p99-goodput curves. Nebius’ mechanism guide does not show a rack score. [observed + inference] [Together](https://www.together.ai/blog/coding-agent-benchmarks) · [Fireworks](https://fireworks.ai/blog/fireattention-v4-fp4-b200) · [Cerebras](https://www.cerebras.ai/blog/llama-405b-inference) · [SambaNova](https://sambanova.ai/blog/sn50-runs-fastest-minimax-speeds-in-the-world) · [Nebius](https://nebius.com/customer-stories/vllm)

## Gaps

- Reviewed vendors do not uniformly show matched p99, errors, arrivals, or goodput. [observed gap] [Cerebras](https://www.cerebras.ai/blog/llama-405b-inference) · [Together](https://www.together.ai/blog/coding-agent-benchmarks)
- Before GPU comparison, SambaNova’s heterogeneous setup must use a matched protocol. [inference] [SN50](https://sambanova.ai/blog/sn50-runs-fastest-minimax-speeds-in-the-world)
- Nebius pages show mechanisms, not independently reproducible GB300 serving results. [observed gap] [Story](https://nebius.com/customer-stories/vllm)
- Documented cache/snapshot/worker state makes cold startup different. The pages show no universal RunPod startup time. [inference] [RunPod](https://docs.runpod.io/serverless/overview)
- Two hours do not show day-long tails, fleet autoscaling, or broad quality. Without costs, two hours do not show economics. [inference] [InferenceMAX](https://inferencex.semianalysis.com/blog/inferencemax-open-source-inference-benchmarking)
- No local rack-bench serving measurements or immutable repository findings show a local result. [inference] [vLLM methodology](https://docs.vllm.ai/en/latest/benchmarking/cli)
