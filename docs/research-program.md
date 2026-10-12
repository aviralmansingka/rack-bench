# rack-bench research program: index

This index covers the sourced research base behind the rack-bench
bench categories. Seven tracks exist: gpu, network, internet, storage,
training, inference, and lifecycle. Six tracks follow the
customer-facing briefing pattern of `docs/customer/datacenter-briefing.md`.
The storage track is the earlier sibling effort and keeps its original
research-memo format.

Every claim in every document carries a source URL. PASS means
measured on the target rack, never vendor-claimed. Every fact we
could not verify is declared as a dated gap, not hidden.

## The briefings

| Track | Briefing | Concern |
| --- | --- | --- |
| Internet | [internet-bench](customer/internet-bench.md) | 45 TB pulls; no provider publishes sustained numbers. |
| GPU | [gpu-bench-research](customer/gpu-bench-research.md) | One bit-flip kills a 30-day run; bad clocks waste paid hours. |
| Network | [network-bench-research](customer/network-bench-research.md) | A healthy port does not prove a healthy collective. |
| Training | [training-bench-research](customer/training-bench-research.md) | Llama 3 saw 419 breaks; customers commit 30-90 days. |
| Inference | [inference-bench-research](customer/inference-bench-research.md) | Users feel p99 latency, not average tps. |
| Lifecycle | [lifecycle-bench-research](customer/lifecycle-bench-research.md) | Bring-up wastes days; data must not survive decommission. |
| Storage | [storage-bench-research](storage-bench-research.md) | A stalled checkpoint costs $200k/month; no fsync'd number exists. |

## How the research was built

Each track (except the earlier storage effort) fanned out into seven
category briefs: neoclouds, hyperscalers, ai-labs, large-companies,
clustermax, academia, and books. Researchers worked in parallel with
one brief per category.

## Numbers

| Track | Briefing lines | Section citations | Source files |
| --- | --- | --- | --- |
| Internet | 536 | 70 | 43 |
| GPU | 530 | brief-name style | 42 |
| Network | 581 | 97 | 45 |
| Training | 487 | 93 | 40 |
| Inference | 510 | 164 | 39 |
| Lifecycle | 647 | 142 | 44 |
| Storage | 224 | 12 | 7 |
| **Total** | **~3,500** | **~580** | **260** |

## Reading order

Start with the internet briefing. It is the most mature track and
shows the pattern in full. Then read the track that matches your
question: GPU for hardware health, network for fabric speed, training
for run resilience, inference for serving quality, lifecycle for lease
operations, storage for checkpoint durability.

Each briefing names its own reading spine in its reading-list section.
The shared spine across tracks: Gregg, Systems Performance 2e; Jain,
The Art of Computer Systems Performance Analysis; and the track-specific
protocol or operations classic named in each briefing.

## Related documents

- `docs/customer/datacenter-briefing.md` — the customer-facing briefing whose
  pattern the six tracks follow, and the source of the Google Doc.
- `docs/internet-performance.md` — the internet bench design document
  (definitions, provider matrix, CLI shape) that pairs with the
  internet briefing.
- `README.md` — the rack-bench pipeline overview and the bench
  category list this research program supports.
