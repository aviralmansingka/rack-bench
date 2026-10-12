# Machine Learning Production Systems — N08

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

The researcher checks O'Reilly catalog/TOC metadata. It shows Robert Crowe, Hannes Hapke, Emily Caveness, Di Zhu; October 2024; 474 pages; identifier 9781098156008. Google Books shows the same title/authors and a broader production-ML description. Its record shows ISBN 9781098155988. The exact format mapping is unverified. [observed] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [Google Books](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ)

The child checks catalog/TOC, not chapter prose. The orchestrator's repeat catalog fetch shows permission denied. Google Books is readable. Its description explicitly shows serving patterns/infrastructure for ML models and LLMs and GenAI pipelines. No record shows authenticated full-text access. [observed access difference] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [Checked description](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ)

## 2. Relevant chapters and LLM-versus-TF boundary

The child's checked TOC shows these chapters and topics. The orchestrator cannot check the full TOC again. [observed, child catalog evidence] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp)

| Chapter | Verified TOC title | Listed topics |
| --- | --- | --- |
| 6 | Model Resource Management Techniques | Quantization, pruning, TensorFlow Lite example |
| 11 | Introduction to Model Serving | Latency, throughput, cost/resources, accelerators, model servers |
| 12 | Model Serving Patterns | Batch/real-time inference, sync/async delivery, GenAI routers |
| 13 | Model Serving Infrastructure | TensorFlow Serving, Triton, TorchServe, containers, observability |
| 14 | Model Serving Examples | TF Serving/TorchServe, REST/gRPC, batch inference, TF Profiler |
| 22 | Generative AI | Prompting, RAG, evaluation, benchmarking, LMOps |

Do not put a wholly TF-era label on the book. Its description and TOC explicitly show LLM/GenAI material. Conventional serving examples make most of the verified serving-example topics. The available evidence does not show TTFT/TPOT/ITL, continuous batching, prefill/decode scheduling, KV pressure, or a two-hour LLM bench recipe. [observed + inference] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [Description](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ)

## 3. Five portable techniques

1. Keep latency, throughput, and serving cost separate. Chapter 11 shows these topics. Current engine docs show actual token/latency definitions. [observed TOC + inference] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
2. Run a separate load test for real-time and batch-like loads. Keep declared arrivals and actual input/output lengths. This is a proposed application, not a verified book procedure. [inference] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli)
3. Run a profile measurement of mixed-prefill/decode interference. Use class-specific latency and queue evidence. DistServe shows the mechanism. The TOC does not show that diagnostic as book content. [observed separate paper + inference] [DistServe](https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf)
4. Show the cache-reuse setting. Run a separate KV-pressure test. These are engine-specific checks, not documented book methods. [inference] [vLLM prefix caching](https://docs.vllm.ai/en/stable/design/prefix_caching) · [vLLM benchmark](https://docs.vllm.ai/en/latest/benchmarking/cli)
5. Keep startup separate from warm serving. Put precision changes together with task-quality scores. Generic quantization/profiling coverage does not show LLM fidelity gates. [inference] [TensorRT-LLM online guide](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md) · [MLPerf quality](https://mlcommons.org/2025/04/llm-inference-v5/)

## 4. Canon relation

Keep this as the strongest supplied production-lifecycle candidate, especially chapters 11–14 and 22. AI Engineering chapter 9 shows a more direct focus on autoregressive optimization. DMLS chapter 7 is deployment context. No full-text comparison shows superiority between the books. [inference] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp) · [AI Engineering author summary](https://github.com/chiphuyen/aie-book/blob/main/chapter-summaries.md#chapter-9-inference-optimization) · [DMLS](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html)

Current vLLM/TensorRT-LLM/MLPerf and scheduler papers are the operational authorities. None shows a universal rack SLO. A two-hour PASS shows valid local measurements, not an inferred vendor result. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf](https://github.com/mlcommons/inference)

## Gaps

- Full chapter text is unverified. Repeat catalog access is not the same for child and orchestrator. [observed gap] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp)
- The reviewed TOC does not show current LLM token metrics, KV-pressure tests, quality gates, or arrival/censoring methods. [observed gap] [Catalog](https://learning.oreilly.com/library/view/-/9781098156008/?orm_source=mcp)
- The exact mapping between catalog and Google Books ISBN formats is unverified. [observed gap] [Google Books](https://books.google.com/books/about/Machine_Learning_Production_Systems.html?id=iTEmEQAAQBAJ)
