# GPU quality research index

Research date: 2026-10-11.

Question: Which device-level checks can measure GPU quality within two hours on a GB300-class rack?

Audience: rack-bench developers and rack tenants in Chennai, India.

The rack has 18 compute trays and 72 physical GPUs.
PASS requires measurements. Failures remain data. Every skip needs a reason.

## Files

All seven researchers return their briefs. The orchestrator checks decisive evidence and keeps each accepted brief.

| Node | Category | Complete brief | Accepted evidence |
| --- | --- | --- | --- |
| N01 | Neoclouds | [neoclouds.md](neoclouds.md) | [N01.md](nodes/N01.md) |
| N02 | Hyperscalers | [hyperscalers.md](hyperscalers.md) | [N02.md](nodes/N02.md) |
| N03 | AI labs | [ai-labs.md](ai-labs.md) | [N03.md](nodes/N03.md) |
| N04 | Large companies | [large-companies.md](large-companies.md) | [N04.md](nodes/N04.md) |
| N05 | ClusterMAX | [clustermax.md](clustermax.md) | [N05.md](nodes/N05.md) |
| N06 | Academia | [academia.md](academia.md) | [N06.md](nodes/N06.md) |
| N07 | Books and guides | [books.md](books.md) | [N07.md](nodes/N07.md) |

The category files keep the complete returned briefs.
The node files keep accepted evidence summaries and links to those briefs.

[Node map and seventeen lessons](research.md).
[O'Reilly supplement and ten source decisions](oreilly.md).
[Complete source notes](oreilly/README.md) and [supplement evidence checks](oreilly/evidence-review.md).
The supplement adds source nodes N08–N17. Each source node uses the accepted N07 scope.
The seven category studies remain complete. The supplement does not repeat them.
[Distilled failure catalog, checks, tickets, and reading list](docs/gpu-bench-research.md).
[Evidence checks](evidence-review.md).
[Deliverables, verdicts, and limits](ORCHESTRATOR-REPORT.md).

The report excludes east-west fabric tests. Per-GPU NVLink health remains in scope.
No researcher measures the target rack live.
All writes stay in this research directory.
The parent can copy the distilled document to project `docs/gpu-bench-research.md`.
