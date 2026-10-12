# Academic methods and rules for valid inference-serving measurements

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Executive answer

Check a workload envelope, not a peak score. Keep aggregate output throughput, GPU normalization, request rate, p50/p99 latency, and outcomes. Useful capacity is only the capacity inside declared workload, latency, and quality conditions. [inference] [Sarathi-Serve](https://arxiv.org/html/2403.02310v1) · [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)

Use independent arrivals for the main serving test. Keep closed-loop saturation as a separate diagnostic. Keep a record of errors, rejections, timeouts, and unfinished work. A slowdown makes closed-loop clients send less load. [inference] [Orca](https://www.usenix.org/system/files/osdi22-yu.pdf) · [MLPerf](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#3-scenarios)

MLPerf uses no universal TTFT/TPOT threshold. Gates are different for each model, scenario, dataset, and release. Keep a separate task-quality check for precision changes. [observed + inference] [Pinned rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#411-constraints-for-the-closed-division)

## 2. Serving mechanisms

### 2.1 PagedAttention, SOSP 2023

KV state is larger at each step of generation. Contiguous reserved cache capacity and fragmentation put limits on batching. PagedAttention uses fixed-size blocks, block tables, on-demand allocation, and sharing where applicable. For its workloads, the paper shows 2–4× throughput over compared systems at similar latency. This is not a predicted GB300 result. [observed] [Kwon et al.](https://arxiv.org/html/2309.06180)

Where the engine shows them, keep a record of cache blocks/occupancy, active sequences, allocation failures, preemptions, and recomputation. High occupancy can show useful capacity or pressure. Latency and outcomes show which one it is. [inference] [PagedAttention](https://arxiv.org/html/2309.06180)

### 2.2 Orca, OSDI 2022

Orca runs scheduling per model iteration. It does not keep a request batch until all sequences are complete. New work can start after an iteration. The datasets show no timestamps, so the evaluation uses synthetic Poisson arrivals. Most traces are one hour long. [observed] [Yu et al., §6.1](https://www.usenix.org/system/files/osdi22-yu.pdf)

Orca shows normalized latency: mean request completion latency divided by output length. This is not TTFT or p99 token-gap latency. The vLLM paper at arXiv 2309.06180 is not an Orca citation. [observed] [Orca](https://www.usenix.org/system/files/osdi22-yu.pdf) · [vLLM](https://arxiv.org/html/2309.06180)

Keep queue/admission timing where available. External request timestamps show delay. They are not proof of internal fairness mechanisms. [inference] [Orca](https://www.usenix.org/system/files/osdi22-yu.pdf)

### 2.3 Sarathi-Serve, OSDI 2024

Long prefill work can make ongoing decode iterations late. Sarathi-Serve puts prefill into chunks and keeps per-iteration token budgets bounded. Smaller chunks make disruption lower. But smaller chunks also put more repeated KV reads and scheduling overhead on the system. Its results are different for each workload and setting. [observed] [Agrawal et al.](https://arxiv.org/html/2403.02310v1)

Send long prompts during the decode phase of short requests. Keep a record of short-class ITL/TTFT tails, chunk size, token budget, and admissions. Decode-only runs do not show prefill interference. [inference] [Sarathi-Serve](https://arxiv.org/html/2403.02310v1)

### 2.4 Splitwise and Mooncake

Prefill and decode demands are different, so Splitwise keeps separate prefill/decode resource pools. Splitwise sends KV state between pools. Mooncake puts KV reuse, transfer, queueing, and TTFT/TBT limits at the core of routing and scheduling. [observed] [Splitwise](https://arxiv.org/abs/2311.18677) · [Mooncake, FAST 2025](https://www.usenix.org/system/files/fast25-qin.pdf)

Put routing and KV transfer in service timing. For fleet normalization, use the GPU count of both pools. A local-engine benchmark does not show the disaggregated service path. [inference] [Splitwise](https://arxiv.org/abs/2311.18677) · [Mooncake](https://www.usenix.org/system/files/fast25-qin.pdf)

## 3. Metric contract

| Metric | Definition | Limit |
| --- | --- | --- |
| Output throughput | Successful completed output tokens / declared duration | Show drain and incomplete-work policy |
| Output throughput/GPU | Aggregate rate / declared allocated GPU count | Normalization, not per-device output measurement |
| Request goodput | Successful requests within all declared conditions / duration | Keep a separate count of all submitted outcomes |
| TTFT | Declared arrival boundary to first generated output | Queueing is in TTFT only if queueing is in the timer scope |
| TPOT | `(last_token_time - first_token_time) / (N - 1)`, N > 1 | One value per request; individual stalls are not visible |
| ITL/TBT | Consecutive output-token/event gaps | Show whether the token count in each event is one |
| p50/p99 | Quantiles of named population | Show count, estimator, weighting, and independence limits |

Definitions are [inference] operational choices. They use [Sarathi-Serve](https://arxiv.org/html/2403.02310v1), [Mooncake](https://www.usenix.org/system/files/fast25-qin.pdf), and [MLPerf](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#51-loadgen-operation) as their base.

Sarathi-Serve shows median TTFT and p99 TBT. Mooncake shows p90 TTFT/TBT experiments. Different percentiles and populations make direct comparison invalid. Request TPOT uses one sample per request. Token gaps put more samples on long outputs. [observed + inference] [Sarathi-Serve §5](https://arxiv.org/html/2403.02310v1) · [Mooncake §8](https://arxiv.org/html/2407.00079v4)

## 4. MLPerf version, scenarios, and quality

### 4.1 Pinned boundary

Policy commit `d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3` is an immutable checked snapshot. It is not itself proof of a formal release tag. Keep separate pinned versions of the implementation and LoadGen. [observed + inference] [Pinned rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)

The MLCommons September 16, 2026 announcement shows published Inference v6.1 results. Do not use a moving `master` policy page as silent proof of exact v6.1 submission rules. [observed + inference] [v6.1 results](https://mlcommons.org/2026/09/mlperf-inference-v6-1-results)

### 4.2 Scenario and timing rules

Server/Interactive uses Poisson arrivals, benchmark-specific limits, and a 99th-percentile target. Its result is the maximum supported Poisson throughput. Single stream starts each query after the previous query is complete. Offline sends all queries together. The table shows 600-second durations with query-count/early-stopping provisions. [observed] [Rules §3](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#3-scenarios)

LoadGen latency starts at scheduled dispatch and stops at reply receipt. LoadGen makes results only after all queries are complete. Under the rules, reproducibility is mandatory. Benchmark detection and content-specific shortcuts are not valid. [observed] [Rules §§2,5.1](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#51-loadgen-operation)

Keep equivalent client schedule/send/reply timestamps in rack-bench. Do not put host-internal timing and API timing in one comparison. [inference] [Rules §5.1](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#51-loadgen-operation)

### 4.3 Example workload gates

| Workload | Server TTFT / TPOT | Interactive TTFT / TPOT | Quality example |
| --- | --- | --- | --- |
| Llama 3.1 405B | 6,000 / 175 ms | 4,500 / 80 ms | 99% FP16; task-specific scores and length parity |
| DeepSeek-R1 | 2,000 / 80 ms | 1,500 / 15 ms | 99% FP16 exact-match reference |
| GPT-OSS-120B | 3,000 / 80 ms | 2,000 / 20 ms | 99% of stated reference score |

These are [observed] examples from the [pinned datacenter table](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#411-constraints-for-the-closed-division). They are not rack-bench defaults.

### 4.4 Quantization and cache rules

Under closed-division rules, reproducible mathematical quantization with specified weights/calibration and quality constraints is valid. Retraining is not valid. Perplexity alone does not show multidomain fidelity. Quantization can also make unsupported kernels slower. [observed + inference] [Rules §8](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#81-weight-definition-and-quantization) · [Jin et al.](https://arxiv.org/abs/2402.16775)

Under the rules, query/response caching is not valid. The LLM FAQ shows per-query KV decoding as valid, but not cross-query reuse. The system must run full computation of every input query. Reuse of PagedAttention blocks is valid only within the allowed batch scope. [observed] [Rules §9.4](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#94-llm-benchmarks)

Cross-query prefix KV reuse and response caching are different mechanisms. Under these closed rules, neither is valid across queries. Keep deliberate prefix-reuse rack diagnostics separate from MLPerf-style no-reuse measurements. Do not make a claim of MLPerf compliance for the rack suite. [inference] [Rules §§8.2,9.4](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#94-llm-benchmarks)

## 5. Benchmark traps

### 5.1 Length sensitivity

Input lengths make parallel prefill work different. Output lengths make decode duration and active KV state different. Orca uses different distributions and shows normalized completion latency. Sarathi-Serve shows that capacity is different for different prompt shapes. [observed] [Orca](https://www.usenix.org/system/files/osdi22-yu.pdf) · [Sarathi-Serve](https://arxiv.org/html/2403.02310v1)

Use short/short, long/short, short/long, and mixed cases. Keep actual lengths and stop rules. Requested maximums can keep early EOS or truncation out of view. Under MLPerf rules, lower output limits for speed are not valid. MLPerf also makes workload-specific length parity mandatory. [inference + observed] [Rules §9.4](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#94-llm-benchmarks)

### 5.2 Prefix cache

Prompt Cache shows TTFT benefits from reusable prompt state. Mooncake shows transfer and load trade-offs in addition. A warm repeated-prefix score is not no-reuse capacity. [observed + inference] [Prompt Cache, MLSys 2024](https://proceedings.mlsys.org/paper_files/paper/2024/file/a66caa1703fe34705a4368c3014c1966-Paper-Conference.pdf) · [Mooncake](https://arxiv.org/html/2407.00079v4)

### 5.3 Load and censoring

Open-loop schedules show queue growth. Closed-loop clients make the offered rate lower when response time is longer. Keep offered/completed rates, scheduling delay, and all outcomes. Run in-flight work to completion, or show the censoring. Statistics from fast completions only make results skewed. [inference] [Orca](https://www.usenix.org/system/files/osdi22-yu.pdf) · [MLPerf §5.1](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#51-loadgen-operation)

### 5.4 p99 uncertainty

The MLPerf example table shows 262,742 inferences for its illustrated 99% percentile, 99% confidence, 0.05% margin. This is not a universal two-hour minimum. Early stopping is a different acceptance method. [observed] [Rules §3 and Appendix A](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#3-scenarios)

At N=1,000 independent observations, about ten are beyond population p99 on average: `1000 * 0.01 = 10`. At N=100, that expectation is one. Token intervals within requests are correlated. Do not use them as independent requests in the count. [calculated + inference] [Rules Appendix A](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#appendix-early_stopping)

Keep sample counts and request-cluster confidence methods. A quick empirical p99 can be exploratory, not a production tail guarantee. [inference] [Rules Appendix A](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#appendix-early_stopping)

### 5.5 Startup and warmup

LoadGen starts the timed queries after readiness. Keep cold load, first inference, and warm serving separate. Keep compilation, graph capture, model files, and prefix state explicit. [observed + inference] [Rules §5.1](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#51-loadgen-operation)

## 6. Two-hour plan

This is a proposed compact design, not a published standard. [inference] [Sarathi-Serve](https://arxiv.org/html/2403.02310v1) · [MLPerf](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)

| Minutes | Check | Evidence |
| --- | --- | --- |
| 0–15 | Identity, readiness, warmup | GPU/model/runtime/config; separate load timer |
| 15–30 | Quality screening | Reference/candidate scores, lengths, settings |
| 30–50 | Low-rate baseline | Offered/completed, tokens, latency, outcomes |
| 50–85 | Open-loop sweep | Queue, tails, goodput, drain |
| 85–105 | KV and mixed-prefill pressure | Occupancy, preemption, per-class latency |
| 105–115 | Prefix contrast | Explicit cache policy and interval hits |
| 115–120 | Artifacts | Raw samples, configuration, omissions |

## 7. Conflicts and limits

Papers use different workloads, percentiles, and timer scopes. Scheduler designs make different trade-offs among latency, throughput, and memory. Check the selected engine with measurements. Do not use an assumed architecture as its grading reference. [observed + inference] [Orca](https://www.usenix.org/system/files/osdi22-yu.pdf) · [Sarathi-Serve](https://arxiv.org/html/2403.02310v1) · [Mooncake](https://www.usenix.org/system/files/fast25-qin.pdf)

A pinned policy snapshot does not keep runtime or LoadGen versions fixed. A small quality set does not show broad fidelity. A low-rate two-hour sample is not a guarantee of precise p99. [inference] [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)

## Gaps

- No live rack measurements show GB300 performance or full-tray coverage. [inference] [MLPerf system definition](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)
- The available inputs show no tenant workload, quality tolerance, or latency SLO. [inference] [Rules §4](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)
- This brief uses a pinned policy snapshot. Actual implementation/LoadGen versions: deployment choices. [observed gap] [Rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)
- No paper shows independent validation of the complete proposed two-hour suite or arbitrary p99 sample sufficiency. [inference] [Rules Appendix A](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc#appendix-early_stopping)
