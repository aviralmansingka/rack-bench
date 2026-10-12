# O'Reilly inference reference supplement

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Scope, decision, and access rules

Keep AI Engineering chapter 9 as the primary inference book. Public author summaries now show specific inference topics. They do not show complete-book access. [observed + inference] [AI Engineering author summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization)

Use current engine documentation, source code, and benchmark rules for runnable checks. None of these nine supplied records shows a two-hour GB300 acceptance protocol. No record shows a local rack measurement. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html) · [Pinned MLPerf rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)

Target rack: 18 trays, NVL72-class topology, Chennai. Use the accepted workflow: audit → bench → smoke. PASS shows valid measurement. Keep target compliance separate. These are supplied design conditions, not source performance claims. [inference under supplied conditions] [Accepted metric contract](docs/inference-bench-research.md) · [Original evidence](research.md)

A catalog shows identity. A TOC shows topics, not procedures. A preview shows only visible material. An agenda shows advertised topics, not demonstrations. Related book chapters do not show video sections. We use only authorized source access. [observed access limits + inference] [Source notes and lessons](oreilly/research.md) · [Denied video record](https://learning.oreilly.com/videos/-/9781633438088VE/?orm_source=mcp)

## 2. Machine Learning Production Systems — N08

The child catalog shows Robert Crowe, Hannes Hapke, Emily Caveness, and Di Zhu. It shows October 2024, 474 pages, and identifier 9781098156008. Google Books shows ISBN 9781098155988. Format mapping: unverified. [observed child catalog + checked record] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [Google Books](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ)

The child checks TOC topics for chapters 6, 11–14, and 22. These topics show resource management, serving, infrastructure, examples, and Generative AI. Google Books explicitly shows LLM serving and GenAI pipelines. Thus a wholly TF-era classification is incorrect. [observed] [Catalog/TOC](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [Checked description](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ)

Use chapters 11–14 and 22 for production-lifecycle context. The visible examples use TF Serving and TorchServe. The TOC does not show TTFT/TPOT/ITL formulas, KV-pressure tests, or precision-fidelity gates. Repeat catalog access shows permission denied. [observed limits + inference] [Full N08 note](oreilly/ml-production-systems.md) · [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp)

## 3. Hands-On Machine Learning, third edition — N09

The checked record shows Aurélien Géron, October 2022, 864 pages, and ISBN 9781098125967. Chapter 2 shows an end-to-end ML project. Chapter 19 shows TensorFlow training and deployment at scale. These are verified TOC topics. [observed] [Catalog/TOC](https://learning.oreilly.com/library/view/-/9781098125967/?orm_source=mcp)

The author shows third-edition examples, including `19_training_and_deploying_at_scale.ipynb`. Use this source for general validation assumptions and conventional TensorFlow deployment context. The Chapter 19 fetch shows 403. Examples do not show full chapter access or modern LLM scheduler methods. [observed + inference] [Author examples](https://github.com/ageron/handson-ml3) · [Chapter 19](https://learning.oreilly.com/library/view/hands-on-machine-learning/9781098125967/ch19.html) · [Full N09 note](oreilly/hands-on-ml.md)

## 4. How Large Language Models Work — N10

The child publisher record shows Edward Raff, Drew Farris, and Stella Biderman. It shows Manning, June 2025, 200 pages, and ISBN 9781633437081. The supplied Drew Farris attribution does not show two coauthors. [observed child metadata] [Publisher](https://www.manning.com/books/how-large-language-models-work) · [Supplied record](https://learning.oreilly.com/library/view/-/9781633437081/?orm_source=mcp)

Public chapter 2 material shows tokenizers. Chapter 7 shows model limits, including latency, scale, and availability. The orchestrator checks public overviews, summaries, figures, and FAQs. These pages do not show complete chapter access. [observed] [Chapter 2 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-2) · [Checked chapter 7 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7)

Use this source for tokenization and conceptual model limits. Keep it below inference-specific references. Its conceptual startup discussion does not show cold-load timing. No checked preview shows a scheduler, KV-pressure, or quantization-fidelity protocol. [observed gap + inference] [Chapter 7 preview](https://www.manning.com/preview/how-large-language-models-work/chapter-7) · [Full N10 note](oreilly/how-llms-work.md)

## 5. Large Language Models in Finance — N11

The official repository shows Miquel Noguer i Alonso, Packt, 2026, and ISBN 9781837024537. Child-checked retailer records show July 30, 2026, and 554 pages. The O'Reilly fetch shows access denied. The Packt chapter fetch shows a security block. [observed] [Official repository](https://github.com/PacktPublishing/LLMs-in-Finance) · [Amazon metadata](https://www.amazon.com/Large-Language-Models-Finance-hands/dp/1837024537) · [The Nile metadata](https://www.thenile.co.nz/books/miquel-noguer-i-alonso/large-language-models-in-finance/9781837024537)

The orchestrator checks the public chapter 10 companion notebook. The notebook uses fictional precision/batch configurations and an M/M/1 queue-wait screen. The notebook keeps quality, latency, cost, memory, and capacity separate. The current suite is an additive educational layer, v1.1.0. The repository shows this layer as separate from canonical companion release B32413-v1.0.0. [observed] [Checked notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb) · [Edition-integrity statement](https://github.com/PacktPublishing/LLMs-in-Finance)

The notebook instructions show workload replay of the total-latency distribution as a requirement. Added queue/service p95 fields do not show a measured total p95 or a general percentile bound. Use constraint separation, not fictional costs or quality indices. The inspected notebook does not show original book/chapter content. [observed caveat + inference] [Notebook](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb) · [Full N11 note](oreilly/llms-finance.md)

## 6. Streaming Systems — N12

The child catalog shows Tyler Akidau, Slava Chernyak, Reuven Lax, July 2018, and 349 pages. Its identifier is 9781491983867. Chapters 1–5 show time semantics, windows, watermarks, and exactly-once side effects. Chapter 5 shows accuracy versus completeness. [observed child catalog/TOC] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp)

Use these topics only as request-ledger context. A reporting cutoff does not show completion of every request. Watermarks do not show decoder completion or token latency. Full chapter methods: unavailable. The orchestrator cannot check the catalog again. [observed gap + inference] [Catalog](https://learning.oreilly.com/library/view/-/9781491983867/?orm_source=mcp) · [Full N12 note](oreilly/streaming-systems.md)

## 7. Grokking Streaming Systems — N13

Manning shows Josh Fischer, Ning Wang, March 2022, 312 pages, and ISBN 9781617297304. The public description shows backpressure, grouping, parallelization, and delayed events. [observed] [Publisher](https://www.manning.com/books/grokking-streaming-systems)

The orchestrator checks sample prose in chapter 6 and introductory material in chapter 7. Many later sections show only headings. Use these samples for general grouping/window context, not as proof of complete-book access. [observed] [Chapter 6 sample](https://livebook.manning.com/book/grokking-streaming-systems/chapter-6) · [Chapter 7 sample](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7)

Use this introduction for generator parallelism, reporting windows, and backpressure context. Use the inference label for the serving application. Delivery semantics do not show token percentiles, KV-pressure tests, or statistical validity. [inference] [Samples](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7) · [Full N13 note](oreilly/grokking-streaming.md)

## 8. Advanced TensorFlow Serving video — N14

The child catalog shows Hannes Hapke, February 2020, and 41 minutes. The public conference agenda shows October 30, 2019, as the session date. The agenda session date and catalog publication date are different. [observed] [Catalog](https://learning.oreilly.com/videos/-/0636920372608/?orm_source=mcp) · [Checked conference agenda](https://conferences.oreilly.com/tensorflow/tf-ca-2019/public/schedule/detail/78365.html)

The agenda shows metadata requests, payload tuning, TensorRT, batching, A/B testing, and monitoring. Use it as historical server-configuration context. Playback, transcripts, timestamped sections, and demonstrations: unverified. Do not use those agenda topics as proof of LLM metric procedures. [observed gap + inference] [Agenda](https://conferences.oreilly.com/tensorflow/tf-ca-2019/public/schedule/detail/78365.html) · [Full N14 note](oreilly/tf-serving-video.md)

## 9. TensorFlow Extended event — N15

The public O'Reilly agenda shows Armen Donigian and a three-hour intermediate/advanced event. It shows evaluation slices, custom metrics, and multiple-model analysis. Its serving section shows export, ServerCore versioning, batching, and test requests. Agenda durations show a total of 180 minutes, including breaks. [observed + calculated] [Checked agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)

Use this event as lifecycle context. Keep model-quality evaluation separate from service readiness. Separate TFX documentation shows that distinction, not proof of every course demonstration. Exact event date and recording: unverified. [observed limits + inference] [TFX Evaluator](https://www.tensorflow.org/tfx/guide/evaluator) · [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880) · [Full N15 note](oreilly/tfx-event.md)

## 10. Latency, Video Edition — N16

Child search metadata shows Pekka Enberg, Manning, October 2025, 9h 4m, and identifier 9781633438088VE. Direct video fetches show access denied. These metadata claims do not show playback, transcripts, or a video section list. [observed child metadata + gap] [Video record](https://learning.oreilly.com/videos/-/9781633438088VE/?orm_source=mcp)

The related book record shows October 2025, 264 pages, and ISBN 9781633438088. Its chapters show modeling, measurement, caching, concurrency, and asynchronous processing. Its publisher description shows Little's Law and Amdahl's Law. These are book records, not video evidence. [observed] [Checked publisher description](https://www.manning.com/books/latency) · [Google Books](https://books.google.com/books/about/Latency.html?id=u9SSEQAAQBAJ)

Use the related book as general latency context. Keep stable operation and consistent system boundaries for this Little's Law check. Do not use it for certification of a growing overload queue. No checked Enberg source shows LLM token-metric or KV-pressure procedures. [inference + observed gap] [Manning](https://www.manning.com/books/latency) · [Full N16 note](oreilly/latency-video.md)

## 11. Access matrix and reading priority

The following access levels show observed public evidence. They do not show complete source access. Priorities are recommendations, not performance claims. [observed + inference] [Linked source notes](oreilly/research.md)

| Priority among these sources | Node | Verified access | Use | Limit |
| --- | --- | --- | --- | --- |
| 1 | N08 | Child catalog/TOC; checked public description | Production lifecycle and GenAI serving context | No chapter procedures |
| 2 | N16 | Related-book description/TOC; child video metadata | General latency modeling | No verified video sections |
| 3 | N11 | Current supplemental notebook code/outputs | Capacity/SLO constraint planning | Fictional fixtures; not canonical chapter |
| 4 | N13 | Publisher description and partial sample prose | Driver/window/backpressure context | Not token-stream protocol |
| 5 | N09 | Catalog/TOC and author examples | General validation and TF deployment | No full chapter 19 |
| 6 | N12 | Child catalog/TOC | Time/window/completeness vocabulary | TOC-only methods |
| 7 | N10 | Public overviews/summaries/FAQs | Tokenization and model limits | Not serving-performance canon |
| 8 | N15 | Public event agenda | Quality/readiness lifecycle distinction | Not verified demonstrations |
| 9 | N14 | Child catalog and public conference agenda | Historical TF server controls | No playback/transcript |

## 12. N07 topic evidence and access gap

AI Engineering's author repository explicitly shows its chapter summaries as book summaries. Chapter 9 shows latency, throughput, utilization, TTFT, TPOT, quantization, KV cache, batching, parallelism, and prompt caching. This is stronger evidence than titles alone. It is not the complete chapter. [observed] [Checked author summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization)

DMLS's author repository also shows book chapter summaries. Chapter 7 shows model deployment and prediction services. Its summary shows batch/online prediction and optimization context. This shows more deployment-topic evidence, not current token-level procedures. [observed + inference] [Checked author summary](https://github.com/chiphuyen/dmls-book/blob/main/summary.md#chapter-7-model-deployment-and-prediction-service)

Keep N07 at `gap` for complete-book access. Put the public summaries and bounded supplements in the reading list. Do not use inaccessible books as proof of the accepted measurement contract. [inference] [Updated canon brief](books.md) · [N07 extract](nodes/N07.md) · [Bench design](docs/inference-bench-research.md)

## 13. Portable checks within two hours

1. Put model, tokenizer, actual lengths, precision, arrivals, and cache policy in the record. Use general validation context for assumption statements. Engine sources show the field definitions. [inference] [N09 author examples](https://github.com/ageron/handson-ml3) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
2. Keep output tokens/s/GPU separate from user speed, TTFT, request TPOT, and event-gap ITL. Show p50/p99 populations and counts. Use all allocated serving GPUs. [inference] [Accepted denominator](docs/inference-bench-research.md) · [vLLM](https://docs.vllm.ai/en/latest/design/metrics.html)
3. Keep scheduled/send/completion timestamps, errors, unfinished requests, and drain cutoffs. Use streaming-system concepts for ledger discipline, not LLM completion rules. [inference] [N13 samples](https://livebook.manning.com/book/grokking-streaming-systems/chapter-7) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
4. Keep startup, warm load, mixed-prefill interference, KV pressure, and intended prefix reuse separate. Use current engine guides and papers for these checks. [inference] [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/performance/perf-benchmarking.html) · [DistServe](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
5. Keep candidate-quality scores, reference, tolerance, workload targets, and verified costs separate. Fictional lab indices do not show fidelity. Use only measured operating points for certification. [inference] [N11 notebook caveat](https://raw.githubusercontent.com/PacktPublishing/LLMs-in-Finance/main/notebooks/10_inference_and_capacity.ipynb) · [Pinned MLPerf rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc)

These checks keep the existing 120-minute schedule and tickets. The supplement shows reading context, not new mandatory phases. Keep long-tail reliability, broad quantization fidelity, and unbounded downloads outside that window. [inference] [Accepted schedule and limits](docs/inference-bench-research.md) · [Original source limits](academia.md)

## Gaps

- Authenticated O'Reilly full text and video playback/transcripts: unverified. Catalog access shows differences between children and repeat checks. [observed gap] [N08 catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [N16 video](https://learning.oreilly.com/videos/-/9781633438088VE/?orm_source=mcp)
- Public previews and author summaries do not show complete-book access. Agenda claims do not show demonstrations. [observed gap] [Author summaries](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md) · [TFX agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)
- N08 ISBN format mapping and the exact TFX event date: unverified. Video sections: unavailable. [observed gap] [N08 record](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ) · [TFX agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880) · [N16 record](https://learning.oreilly.com/videos/-/9781633438088VE/?orm_source=mcp)
- No source shows a universal GB300 SLO, quality tolerance, or local cost basis. This research runs no rack measurements. [inference] [MLPerf rules](https://github.com/mlcommons/inference_policies/blob/d3eba2f21026d868ad65cdcad2bb81e4a17ce3d3/inference_rules.adoc) · [Accepted boundary](docs/inference-bench-research.md)
