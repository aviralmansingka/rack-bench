# O'Reilly GPU source pass

Research date: 2026-10-11.

Question: Which catalog books add useful methods to the accepted GPU research?
The captain gives catalog-only results. The researchers cannot access the O'Reilly MCP.
Full text can require authentication. Do not bypass authentication.

Check public publisher pages and tables of contents instead.
Mark techniques from topic coverage as inferences unless public text states them directly.

Scope: device-level GPU health, performance, and correctness within two hours.
Keep ECC, XIDs, row remaps, SDC, thermals, power, clocks, and exact checks in scope.
PASS needs measured evidence. Keep failures and exact skip reasons.

The target has 18 trays and 72 GB300-class GPUs in Chennai.
Exclude east-west and collective performance. Include per-GPU NVLink health.

[The node map](../research.md) adds N08–N17 before source research starts.
Each source node uses the accepted [books brief](../books.md), not renewed category research.

| Node | Source | Note |
| --- | --- | --- |
| N08 | Cook, CUDA Programming | [cook.md](cook.md) |
| N09 | Gregg, Systems Performance 2e | [gregg2.md](gregg2.md) |
| N10 | Motta, GPU Programming with C++ and CUDA | [motta.md](motta.md) |
| N11 | Cheng et al., Professional CUDA C Programming | [cheng.md](cheng.md) |
| N12 | Sanders and Kandrot, CUDA by Example | [example.md](example.md) |
| N13 | Fregly, AI Systems Performance Engineering | [fregly.md](fregly.md) |
| N14 | Tuomanen, Python and CUDA | [python.md](python.md) |
| N15 | Kirk, Hwu, El Hajj, PMPP editions | [pmpp.md](pmpp.md) |
| N16 | Gregg, Systems Performance 1e | [gregg1.md](gregg1.md) |
| N17 | Bondi, Performance Engineering | [bondi.md](bondi.md) |

The children write only their assigned notes.
The orchestrator checks decisive passages and writes the supplement and lessons.

All ten source notes are ready. The existing Bondi child resumes once after a provider failure.
No duplicate child starts. [Integrated supplement](../oreilly.md) · [Evidence checks](evidence-review.md).
Completion messages give child results. No child-status polling occurs.
