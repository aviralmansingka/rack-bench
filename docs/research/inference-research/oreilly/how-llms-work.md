# How Large Language Models Work — N10

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

The child checks Manning's June 2025, 200-page title, identifier 9781633437081. The title shows Edward Raff, Drew Farris, and Stella Biderman as authors. The supplied metadata does not show two coauthors. Public Manning preview pages are readable. O'Reilly chapter pages show 403. No check shows full-book access. [observed] [Manning preview/metadata](https://www.manning.com/preview/how-large-language-models-work/chapter-4) · [Supplied catalog](https://learning.oreilly.com/library/view/-/9781633437081/?orm_source=mcp)

## 2. Relevant checked material

Chapter 2, “Tokenizers,” shows token representation, cross-language counts, and resource/cost effects. Chapter 7, “Misconceptions, limits, and eminent abilities of LLMs,” shows high-level context. That context is latency/scale/availability and startup cost. The orchestrator checks chapter 7's public overview, figures, summary, and FAQ. This is accessible preview material. It does not show complete chapter text. [observed] [Chapter 2 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-2) · [Checked chapter 7 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7)

The reviewed material does not show serving metric formulas, scheduler analysis, or a benchmark protocol. “Startup cost” in conceptual discussion does not show a timed cold-start measurement. [observed gap + inference] [Chapter 7 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7)

## 3. Five portable techniques

1. Keep the tokenizer fixed. Keep actual token counts. A different tokenizer makes a different representation and different counts. The use of this for workload identity is an inference. [observed preview + inference] [Chapter 2](https://www.manning.com/preview/how-large-language-models-work/chapter-2)
2. Keep fleet output rate/GPU separate from user latency. Engine documentation shows the measurement contract. Conceptual latency prose does not show it. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
3. Keep request TPOT separate from event-gap ITL. Show p50/p99 sample populations. The server can send multiple tokens in one streaming event. [observed separate docs + inference] [vLLM](https://docs.vllm.ai/en/latest/design/metrics.html)
4. Keep a record of arrivals, lengths, prefix-reuse policy, and KV capacity. These are current serving controls, not procedures verified in the book samples. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
5. Keep documented startup and task-quality comparison separate from warm performance. The conceptual book preview shows context, not cold-load timing or quantization tolerance. [inference] [Chapter 7](https://www.manning.com/preview/how-large-language-models-work/chapter-7) · [MLPerf](https://github.com/mlcommons/inference)

## 4. Canon relation

Keep this title as low-priority model/tokenization context. AI Engineering's author summary directly shows chapter 9's inference optimization coverage. DMLS's author summary shows chapter 7's deployment/prediction focus. Use these stronger primary records in place of the child's third-party DMLS summary. [observed author summaries + inference] [AI Engineering](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization) · [DMLS](https://github.com/chiphuyen/dmls-book/blob/main/summary.md#chapter-7-model-deployment-and-prediction-service)

Current engine docs, rules, and scheduler papers are better operational references. A two-hour PASS must use local measured evidence, not the book's general scale/availability claims. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf](https://docs.mlcommons.org/inference)

## Gaps

- Public previews do not show full-book or complete chapter access. [observed gap] [Chapter 7 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7)
- No checked source shows mixed-prefill tests, KV-pressure experiments, quantization-fidelity gates, or a GB300 protocol. [observed gap] [Chapter 7 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7)
