# rack-bench research program: index

This index covers the sourced research base behind the rack-bench
bench categories. Seven tracks exist: gpu, network, internet, storage,
training, inference, and lifecycle. Six tracks follow the
customer-facing briefing pattern of `docs/datacenter-briefing.md`.
The storage track is the earlier sibling effort and keeps its original
research-memo format.

Every claim in every document carries a source URL. PASS means
measured on the target rack, never vendor-claimed. Every fact we
could not verify is declared as a dated gap, not hidden.

## The briefings

| Track | Briefing | Sources | Customer concern | What two hours cannot certify |
| --- | --- | --- | --- | --- |
| Internet | [internet-quality-research](internet-quality-research.md) | [.lavish/internet-research](../.lavish/internet-research) | Customers pull 45 TB datasets and push 4.5 TB checkpoints. The internet path decides whether that takes hours or days. No provider publishes a sustained number. | Loss tails below 0.1%; diurnal duty cycle; WAN failover; DDoS absorption. |
| GPU | [gpu-bench-research](gpu-bench-research.md) | [.lavish/gpu-research](../.lavish/gpu-research) | A silent bit-flip can corrupt a 30-day training run. A degraded clock wastes every hour paid for. | Silent-data-corruption absence; long-horizon wear; lifetime certification. |
| Network | [network-bench-research](network-bench-research.md) | [.lavish/network-research](../.lavish/network-research) | A healthy port does not prove a healthy collective. Slow GPU communication makes training runs longer. | Endurance; rare faults; scale beyond 13 nodes; switch-internal behavior; failure recovery. |
| Training | [training-bench-research](training-bench-research.md) | [.lavish/training-research](../.lavish/training-research) | Meta's Llama 3 runs saw 419 unplanned interruptions. Customers commit 30 to 90 days. The bench proves recovery before they pay. | Multi-week reliability; duty cycle of interruptions; full-scale convergence. |
| Inference | [inference-bench-research](inference-bench-research.md) | [.lavish/inference-research](../.lavish/inference-research) | Users feel p99 latency, not average tokens per second. Vendor rate claims are incomparable. The bench measures tail behavior under load. | Production availability; precise low-sample p99; broad quantization fidelity. |
| Lifecycle | [lifecycle-bench-research](lifecycle-bench-research.md) | [.lavish/lifecycle-research](../.lavish/lifecycle-research) | Customers lose days to broken bring-up. Customer data must not survive decommissioning. The bench times each step and verifies the wipe. | Long recovery periods; fleet-scale drift; contract SLA enforcement. |
| Storage | [storage-bench-research](storage-bench-research.md) | [.lavish/storage-research](../.lavish/storage-research) | A stalled checkpoint costs more than $200k per month in idle GPUs. The durability void: no neocloud publishes an fsync'd number. | Wear-out; power-cut truth; the latent-sector-error tail; fairness/QoS. |

## How the research was built

Each track (except the earlier storage effort) fanned out into seven
category briefs: neoclouds, hyperscalers, ai-labs, large-companies,
clustermax, academia, and books. Researchers worked in parallel with
one brief per category. A second pass searched the O'Reilly Learning
catalog for each domain and produced a supplement plus per-source
notes. All prose was then converted to Simplified Technical English
and reformatted into the customer-facing briefing pattern.

The sources directory for each track holds the full evidence trail:
the seven category briefs, the O'Reilly supplement and notes, node
maps, verification reports, and declared gaps. The briefings link
into them.

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

- `docs/datacenter-briefing.md` — the customer-facing briefing whose
  pattern the six tracks follow, and the source of the Google Doc.
- `docs/internet-performance.md` — the internet bench design document
  (definitions, provider matrix, CLI shape) that pairs with the
  internet briefing.
- `README.md` — the rack-bench pipeline overview and the bench
  category list this research program supports.
