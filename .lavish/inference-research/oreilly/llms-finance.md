# Large Language Models in Finance — N11

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

The child checks Miquel Noguer i Alonso, Packt, 2026, identifier 9781837024537. Child-checked retailer records show July 30, 2026, and 554 pages. [observed child metadata] [Amazon](https://www.amazon.com/Large-Language-Models-Finance-hands/dp/1837024537) · [The Nile](https://www.thenile.co.nz/books/miquel-noguer-i-alonso/large-language-models-in-finance/9781837024537) The official companion repository shows the title and author. The O'Reilly page shows access denied. Packt chapter pages show a security block. No record shows full-book or chapter 10 text access. [observed child records + access gap] [Supplied catalog](https://learning.oreilly.com/library/view/-/9781837024537/?orm_source=mcp) · [Official repository](https://github.com/PacktPublishing/LLMs-in-Finance) · [Publisher chapter listing](https://subscription.packtpub.com/book/data/9781837024537/10/ch10lvl1sec98/103-deployment-strategies-for-production-systems)

The repository shows its current notebook suite as an additive educational layer. It keeps v1.1.0 separate from canonical release B32413-v1.0.0. The inspected `main` notebook does not show that release's content. [observed] [Edition-integrity statement](https://github.com/PacktPublishing/LLMs-in-Finance)

The public companion notebook shows stronger evidence than inaccessible chapter text. The orchestrator checks its code, teaching fixtures, printed outputs, caveat, and takeaways. Use these findings for the notebook, not the hidden book chapter. [observed] [Checked notebook 10](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)

## 2. Checked notebook content

“Chapter 10 Lab: Inference, Capacity, Cost, and SLOs” uses illustrative serving configurations. It shows precision, batch size, quality index, service rate, p95 latency, cost, and memory index. Notebook metadata explicitly shows default data as fictional teaching fixtures. No values show measured hardware performance. [observed] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)

The lab uses an M/M/1 queue-wait teaching approximation. It shows arrival rates at or above service rate as unstable. It makes a sum of estimated queue p95 and a service p95 field. It keeps only candidates inside declared constraints. It makes a Pareto set. The decision caveat shows workload replay of the total-latency distribution as required. [observed] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)

Do not use added p95 values as a measured total-latency percentile or a general percentile bound. The notebook shows its addition as a conservative screen. The notebook still shows replay as required. Do not use its fictional quality indices and costs for rack acceptance. [observed caveat + inference] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)

## 3. Five portable techniques

1. Show separate quality, latency, cost, memory, and capacity constraints. Use measured local values, not fictional fixtures. [observed concepts + inference] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)
2. Run a load-instability test with actual arrivals and outcomes. M/M/1 is not a model of every continuously batched LLM service. [observed teaching model + inference] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)
3. Check each deployed precision/batch configuration against its own workload targets. Keep task-quality screening together with measured capacity. [observed trade-off + inference] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)
4. Run a replay of the target workload. Keep its latency distribution. Do not show an interpolated or simulated capacity point as certified. [observed caveat + inference] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)
5. Run current-engine token-metric, startup, scheduler, and KV tests in addition. The inspected lab does not show these checks. [observed gap + inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html)

## 4. Canon relation and two-hour use

Use this source only for conceptual capacity/SLO planning. AI Engineering chapter 9 shows more direct inference topics. DMLS chapter 7 shows deployment context. Their public author summaries show topics, not comprehensive rack procedures. [observed summaries + inference] [AI Engineering](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization) · [DMLS](https://github.com/chiphuyen/dmls-book/blob/main/summary.md#chapter-7-model-deployment-and-prediction-service)

Use current engine documentation and benchmark rules for actual checks. Keep measurement validity separate from target compliance. MLPerf model/scenario quality targets are not universal rack tolerances. No source in this review shows local GB300/NVL72 performance. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/master/inference_rules.adoc)

## Gaps

- Book/chapter text is unverified. The companion lab does not show identical book content. [observed gap + inference] [Publisher chapter](https://subscription.packtpub.com/book/data/9781837024537/10/ch10lvl1sec98/103-deployment-strategies-for-production-systems)
- The lab runs no measurement of output tokens/s/GPU, TTFT, TPOT, or ITL. It also runs no measurement of p50/p99 token latency, scheduler interference, startup, or KV pressure. [observed gap] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)
- Fictional quality/cost fields do not show quantization fidelity or a verified cost basis. [observed gap + inference] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb)
