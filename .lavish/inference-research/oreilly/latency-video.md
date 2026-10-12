# Latency, Video Edition — N16

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

The child uses public search metadata for Pekka Enberg's Latency, Video Edition. The metadata shows Manning, October 2025, 9h 4m, and identifier 9781633438088VE. Both O'Reilly video fetches show an access denial. The video transcript, playback, and section list are still unverified. [observed search metadata + access gap] [Supplied record](https://learning.oreilly.com/videos/-/9781633438088VE/?orm_source=mcp) · [Video catalog](https://www.oreilly.com/videos/latency-video-edition/9781633438088VE)

The related Manning book is Latency: Reduce delay in software systems, by Pekka Enberg. The child report shows October 2025, 264 pages, and ISBN 9781633438088. The checked publisher description shows general latency modeling, measurement, and visualization. The description also shows Little's Law, Amdahl's Law, caching, concurrency, and asynchronous processing. The description is not proof of identical video coverage. [observed book description, not video] [Manning](https://www.manning.com/books/latency)

## 2. Relevant book sections, not confirmed video sections

Google Books shows chapter 2, “Modeling and measuring latency”. Google Books shows chapters 3–6, “Colocation,” “Replication,” “Partitioning,” “Caching”. Google Books shows chapter 9, “Exploiting concurrency”. Google Books shows chapter 10, “Asynchronous processing.” These are book chapter identities, not video timestamps. [observed adjacent-book record] [Google Books](https://books.google.com/books/about/Latency.html?id=u9SSEQAAQBAJ)

A ScyllaDB page shows an offer of an excerpt on caching, concurrency, and asynchronous processing. The offer page does not itself show access to the excerpt text or video. [observed landing page] [Excerpt offer](https://lp.scylladb.com/latency-book-offer)

## 3. Five portable techniques

1. Keep latency and throughput separate. The publisher explicitly shows a difference between latency and bandwidth. Use this difference for fleet output rate versus user experience. Engine docs, not unseen video, are the source of LLM definitions. [observed description + inference] [Manning](https://www.manning.com/books/latency) · [vLLM](https://docs.vllm.ai/en/latest/design/metrics.html)
2. Keep arrivals, concurrency, residence time, and queue evidence together. Little's Law is a consistency check only for a stable, consistently defined system. Do not use it as certification of a growing overload queue. This is a bench inference, not verified video instruction. [inference] [Manning](https://www.manning.com/books/latency)
3. Keep cold startup and warm steady-state windows separate. Explicit serving timers are a requirement for this portable recommendation. The video record is not proof of coverage. [inference] [TensorRT-LLM guide](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)
4. Put KV/cache and exact precision in the record with task-quality scores. AI Engineering's public author summary shows evidence for those LLM concerns. Latency's public description does not show them. [observed separate author summary + inference] [AI Engineering summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization)
5. Keep raw request/event records, window boundaries, counts, errors, and unfinished work. Use the label event-gap ITL for the gap metric. Events are not necessarily individual tokens. These are engine-based bench safeguards, not attributed video methods. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)

## 4. Canon relation

Put the related Latency book in the canon as a general measurement/concurrency supplement. Do not show the inaccessible video as verified LLM methodology. AI Engineering chapter 9 is still the direct inference source. DMLS chapter 7 is still deployment context. Use public author/publisher evidence in place of secondary chapter notes. [inference] [Manning](https://www.manning.com/books/latency) · [AI Engineering summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization) · [DMLS publisher](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html)

## Gaps

- Video sections, timestamps, transcript, and playback are still unverified. [observed gap] [Video catalog](https://www.oreilly.com/videos/latency-video-edition/9781633438088VE)
- Related book descriptions and chapter records are not proof of video contents or full-book access. [inference] [Manning](https://www.manning.com/books/latency)
- No checked Enberg source shows LLM token metrics, KV pressure, quantization fidelity, or a two-hour GB300 protocol. [observed gap] [Manning](https://www.manning.com/books/latency)
