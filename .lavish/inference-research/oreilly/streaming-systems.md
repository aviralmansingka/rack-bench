# Streaming Systems as an inference-bench supplement — N12

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

The child checks O'Reilly catalog metadata: Tyler Akidau, Slava Chernyak, Reuven Lax; July 2018; 349 pages; ISBN 9781491983867. Catalog/TOC are visible. “Unlock full access” shows the reading gate. No check shows full chapter prose. [observed] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp)

## 2. Relevant verified contents

Chapter 1, “Streaming 101,” shows event time versus processing time. Chapter 2, “The What, Where, When, and How of Data Processing,” shows five topics. They are windowing, triggers, watermarks, lateness, and accumulation. Chapter 3, “Watermarks,” and chapter 4, “Advanced Windowing,” show more of those topics. Chapter 5, “Exactly-Once and Side Effects,” shows accuracy versus completeness and determinism. These are TOC topics, not full-text procedures. [observed] [Catalog/contents](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp)

## 3. Five portable techniques

1. Keep clock meanings and observation boundaries explicit. A stream-processing time model is not the LLM client timer. This transfer is an inference. vLLM shows actual metric definitions. [inference] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
2. Use declared reporting windows with counts and outcomes. The end of a window does not show completion of all admitted requests. This is a bench recommendation from window topics, not verified chapter prose. [inference] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp)
3. Make completeness explicit. Keep request IDs, pending/error states, cutoff, and drain policy. The TOC's accuracy/completeness topic is the start point for the analogy. It does not show a validated censoring protocol. [observed topic + inference] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp)
4. Keep scheduled arrivals, actual sends, and completions separate. Engine/client controls show the operational procedure, not the book's general time semantics. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
5. Keep event counts separate from token counts. Speculation can put more than one token in one event. Watermarks do not show decoder completion or token cadence. [observed separate docs + inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

## 4. Canon relation

Huyen's public chapter-summary repository shows AI Engineering chapter 9. It explicitly shows latency, throughput, TTFT/TPOT, and quantization. It also shows KV cache, batching, parallelism, and prompt caching. This accessible author summary makes the original canon-coverage gap smaller. It does not show the complete chapter. [observed] [Author summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization)

DMLS chapter 7 shows deployment context. Streaming Systems shows time/window/completeness vocabulary, not modern LLM serving definitions. Current engine docs still show the runnable measurement contract. [observed limited identity + inference] [DMLS publisher](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

## 5. Two-hour fit

Use these ideas for ledger/window discipline in the two-hour rack bench. Do not use event-time watermarks as inference completion rules. PASS shows valid measurement. Keep the target verdict separate. The book does not show a GB300 threshold. [inference] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

## Gaps

- Full chapter text is unverified. Only the visible contents show relevance. [observed gap] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp)
- No verified book source shows LLM token metrics, KV-pressure tests, quantization-fidelity criteria, or a rack acceptance threshold. [observed gap] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp)
