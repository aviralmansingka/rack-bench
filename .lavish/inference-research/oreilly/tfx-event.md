# TensorFlow Extended: Model build, analysis, and serving

Research date: 2026-10-11. Use the source URL for each claim.

## 1. Identity and access

The readable public O'Reilly page shows Armen Donigian and a three-hour, intermediate-to-advanced live course. The course is about TFX model analysis, evaluation, serving, and profiling. The supplied learning URL shows the same event. Public agenda access does not show recording or participant-material access. [observed] [Supplied record](https://learning.oreilly.com/live-events/-/0636920251880/?orm_source=mcp) · [Checked public agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)

The public page does not show a specific session date. A notebook repository record puts the material with 2019. This record is evidence for the supplied year, not a particular event date. [observed + inference] [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880) · [Notebook record](https://resources.oreilly.com/binderhub/tensorflow-extended/-/commits/master/notebooks/V2_Part3_Model_Build_Analysis.ipynb)

## 2. Verified sections and coverage

The agenda shows an overview, end-to-end notebook, TensorFlow Estimator training, and TensorFlow Model Analysis. The analysis topics are metric slices, visualization, custom metrics, multiple-model analysis, and multiple-data analysis. [observed] [Schedule](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)

The 40-minute serving section shows export, ServerCore model versioning, batching configuration, serving requests, and running/testing the service. The full agenda total is 180 minutes with breaks. These are agenda claims, not verified recording content. [observed + calculated] [Schedule](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)

The reviewed agenda does not show autoregressive token metrics, KV pressure, cold-load timing, or quantization-fidelity methods. Keep this event as TF-era lifecycle context, not a modern LLM acceptance protocol. [observed gap + inference] [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)

## 3. Five portable bench techniques

1. Keep model-quality evaluation separate from service readiness. TFX Evaluator checks candidate metrics against baseline metrics. InfraValidator checks serving in a sandbox. Neither tool shows rack throughput. Use of this distinction for inference is a proposed check, not verified course procedure. [observed separate docs + inference] [Evaluator](https://www.tensorflow.org/tfx/guide/evaluator) · [TFX guide](https://www.tensorflow.org/tfx/guide)
2. Keep metrics by workload slice and candidate version. The agenda explicitly shows slicing and multiple-model analysis by name. For inference, keep short/long requests and precision configurations separate instead of using one average. [observed agenda + inference] [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)
3. Run a batching test under declared offered load. The agenda shows batching. Use current engine sources for LLM arrival controls and TTFT/TPOT/ITL definitions. [observed agenda + inference] [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880) · [vLLM metrics](https://docs.vllm.ai/en/latest/design/metrics.html)
4. Keep launch/readiness/first valid inference separate from warm performance. This technique is a rack recommendation. The course agenda does not show cold-start timer coverage. [inference] [TensorRT-LLM online benchmark](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/commands/trtllm-serve/run-benchmark-with-trtllm-serve.md)
5. Check precision changes against a named task reference. TFX evaluation thresholds show general context. These thresholds are not evidence for KV/weight quantization equivalence. [observed separate docs + inference] [Evaluator](https://www.tensorflow.org/tfx/guide/evaluator) · [MLPerf LLM methodology](https://mlcommons.org/2025/04/llm-inference-v5/)

## 4. Canon relation and two-hour fit

The existing canon shows Huyen's AI Engineering chapter 9 and DMLS chapter 7. This child does not make an independent check of their full chapter text. The event puts verified evaluation/batching/testing agenda detail beside their book-level context. The event is not a replacement for that context. [observed limited records + inference] [AI Engineering chapter](https://www.oreilly.com/library/view/ai-engineering/9781098166298/ch09.html) · [DMLS chapter](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/ch07.html)

vLLM and TensorRT-LLM documentation and MLPerf rules show more direct autoregressive metric and runnable-benchmark guidance. Use the event only as lifecycle background. Its three-hour duration is not a definition of the two-hour rack test. Valid local measurements are still a PASS requirement. [inference] [vLLM](https://docs.vllm.ai/en/latest/benchmarking/cli) · [MLPerf](https://github.com/mlcommons/inference) · [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)

## Gaps

- Specific event date, recording access, and complete hands-on materials are still unverified. [observed gap] [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)
- No checked event source shows LLM latency populations, KV pressure, quantization fidelity, or a GB300 acceptance target. [observed gap] [Agenda](https://www.oreilly.com/live-events/tensorflow-extended-model-build-analysis-and-serving/0636920251880)
- General TFX documentation shows proposed mechanisms. This documentation is not proof that this event shows all of them. [inference] [TFX guide](https://www.tensorflow.org/tfx/guide)
