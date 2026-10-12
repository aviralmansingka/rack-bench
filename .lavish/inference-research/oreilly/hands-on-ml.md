# Hands-On Machine Learning, third edition — N09

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

The checked O'Reilly catalog shows Aurélien Géron, third edition, October 2022, 864 pages, and ISBN 9781098125967. Catalog and TOC are readable. The child's report shows HTTP 403 for chapter 19. The author's repository shows third-edition examples, not full chapter text. [observed] [Catalog](https://learning.oreilly.com/library/view/-/9781098125967/?orm_source=mcp) · [Chapter 19](https://learning.oreilly.com/library/view/hands-on-machine-learning/9781098125967/ch19.html) · [Author repository](https://github.com/ageron/handson-ml3)

## 2. Relevant chapters

Chapter 2, “End-to-End Machine Learning Project,” shows problem framing, performance measures, assumptions, test sets, and error analysis. It also shows final evaluation and launch/monitoring. These are TOC topics, not verified detailed acceptance procedures. [observed] [TOC](https://learning.oreilly.com/library/view/-/9781098125967/?orm_source=mcp)

Chapter 19, “Training and Deploying TensorFlow Models at Scale,” shows TensorFlow Serving, Vertex AI prediction, and batch prediction. It also shows GPU RAM, device placement, and distributed training. The chapter 16 title shows attention and Transformers. That title does not show current LLM-serving scheduler coverage. [observed + inference] [TOC](https://learning.oreilly.com/library/view/-/9781098125967/?orm_source=mcp)

## 3. Five portable techniques

1. Show acceptance measures and assumptions before you run a test. Chapter 2 shows the project-validation topic. The bench keeps responsibility for workload-specific inference targets. [observed TOC + inference] [TOC](https://learning.oreilly.com/library/view/-/9781098125967/?orm_source=mcp)
2. Keep output throughput/GPU separate from user speed and latency populations. This is current engine guidance, not verified unavailable chapter prose. [observed separate docs + inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
3. Keep offered rate, actual sends, errors, counts, and incomplete outcomes. Put an uncertainty statement with a low-N p99. This is an inferred bench requirement, not a statistical rule from the book. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
4. Run a cold readiness/first valid inference measurement separate from warmed serving. The online benchmark starts the server before the test. [observed separate guide + inference] [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)
5. Keep prefix reuse, KV pressure, and weight/KV precision separate. Put speed together with a named task-quality reference. Use modern engine/quality sources for these, not this book's TOC. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf v5](https://mlcommons.org/2025/04/llm-inference-v5/)

## 4. Canon relation

Use this book as broad ML validation and TF deployment context. Do not use it as the headline modern serving reference. AI Engineering chapter 9 and DMLS chapter 7 are closer conceptual/deployment entries. Current serving docs and DistServe show more direct metric/scheduler guidance. No title alone shows a complete rack protocol. [inference] [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/ch09.html) · [DMLS](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html) · [DistServe](https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf)

## Gaps

- Catalog/TOC and examples do not show full chapter access or LLM-serving procedures. [observed gap] [Chapter 19](https://learning.oreilly.com/library/view/hands-on-machine-learning/9781098125967/ch19.html)
- No verified book source shows current token populations, continuous batching, KV-pressure tests, or a GB300 target. [observed gap] [Catalog](https://learning.oreilly.com/library/view/-/9781098125967/?orm_source=mcp)
- A two-hour run does not make sure of sufficient tails or broad quantization fidelity. PASS shows measured evidence, not target compliance. [inference] [MLPerf](https://mlcommons.org/2025/04/llm-inference-v5/)
