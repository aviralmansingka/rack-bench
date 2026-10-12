# Grokking Streaming Systems — N13

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

Manning shows Josh Fischer and Ning Wang as the authors of Grokking Streaming Systems: Real-time event processing. The child report shows March 2022, ISBN 9781617297304, and 312 pages from publisher metadata. The supplied O'Reilly route shows an access denial. The public Manning description and chapter samples are readable. Full-book access is still unverified. [observed] [Publisher](https://www.manning.com/books/grokking-streaming-systems) · [Supplied record](https://learning.oreilly.com/library/view/-/9781617297304/?orm_source=mcp)

## 2. Relevant checked content

Chapter 6, “Streaming systems review and a glimpse ahead,” shows readable prose. The readable prose is about events, streams, sources, operators, parallelization, grouping, and DAGs. The chapter shows delivery semantics as headings. This fetch does not show their complete argument. [observed] [Checked chapter 6 sample](https://livebook.manning.com/book/grokking-streaming-systems/chapter-6)

Chapter 7, “Windowed computations,” shows readable introductory prose. The chapter also shows headings for timestamps, watermarks, late events, fixed/sliding windows, and time-versus-count windows. The orchestrator's repeat fetch shows headings rather than full section prose. Do not make a claim of full chapter access. [observed] [Checked chapter 7 sample](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7)

The publisher description explicitly shows backpressure, parallelization, grouping, and delayed events by name. [observed] [Publisher](https://www.manning.com/books/grokking-streaming-systems)

## 3. Five portable techniques

1. Put generator parallelism and routing in the record. The sample shows grouping under parallelization. The transfer to generator health is an inference. [observed sample + inference] [Chapter 6](https://livebook.manning.com/book/grokking-streaming-systems/chapter-6)
2. Put the choice of fixed-duration versus fixed-count windows in the record. The two window types are for different measurement questions. This bench transfer uses verified section topics, not a quoted LLM procedure. [observed headings + inference] [Chapter 7](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7)
3. Keep offered load and queue/backpressure signals beside completions. The publisher shows backpressure by name. Use for inference servers is still an analogy. [observed description + inference] [Publisher](https://www.manning.com/books/grokking-streaming-systems)
4. Check the agreement of the counts of submitted, completed, failed, timed-out, and unfinished requests. Delivery/late-event topics show a reason for the check. These topics do not show its statistical validity. [inference] [Chapter 6](https://livebook.manning.com/book/grokking-streaming-systems/chapter-6) · [Chapter 7](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7)
5. Keep event-gap ITL separate from request TPOT and authoritative token counts. Current engine docs show these definitions. The streaming book does not. [inference with separate observed docs] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

## 4. Canon relation and domain boundary

A streaming watermark is not a token-latency percentile. A streaming watermark is also not proof of completed decoding. The book puts driver/window/backpressure context in the canon. The book is not a replacement for inference-specific metric, KV, or quality sources. [inference] [Chapter 7](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

The child checks AI Engineering's 2025 identity and chapter 9 title against author/Google records. For the chapter 7 title, the child uses a third-party DMLS summary. The integration uses stronger author/publisher records instead. Use AI Engineering before this supplementary streaming introduction. [observed limited records + inference] [Author](https://huyenchip.com/books) · [AI Engineering record](https://books.google.com/books/about/AI_Engineering.html?id=S7M1EQAAQBAJ) · [DMLS publisher chapter](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html)

## Gaps

- O'Reilly full text is still inaccessible. Manning samples do not show full-book access. [observed gap] [Supplied record](https://learning.oreilly.com/library/view/-/9781617297304/?orm_source=mcp)
- The checked samples do not show LLM-specific TTFT/TPOT/ITL, cache, quantization, or two-hour acceptance methods. [observed gap] [Chapter 6](https://livebook.manning.com/book/grokking-streaming-systems/chapter-6) · [Chapter 7](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7)
