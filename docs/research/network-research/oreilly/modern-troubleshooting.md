# Modern Network Troubleshooting

Research date: 2026-10-11. All claims below use a source URL.

## 1. Identity, date, and access

1. **[observed] Identity:** The O’Reilly Learning listing shows *Modern Network Troubleshooting* from publisher Pearson. It shows Russ White as instructor and event ID `0790145043580`. It shows a live online course. [O’Reilly listing](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp)
2. **[observed] Date evidence:** White’s original course-specific post explicitly shows the training “for 2023”. It shows his plan to teach it January 26, “in three weeks”. Its archive shows that post on January 2, 2023. The archive shows his announcement on December 4, 2023. This evidence shows an advertised January 26, 2023 session for the linked event ID. It does not remove the possibility of later sessions with the same ID. [Course post](https://rule11.tech/modern-network-troubleshooting) [2023 archive](https://rule11.tech/2023/) [announcement](https://rule11.tech/upcoming-pearson-class-modern-network-troubleshooting)
3. **[observed] Keep date separate from catalog metadata:** The supplied catalog shows 2025. The author explicitly shows an advertisement for a 2023 session. Public evidence shows no cause for the supplied 2025 year. It shows no evidence for a unique session for the listing. O’Reilly’s public event page shows no year. It now shows an ended live course and no scheduled sessions. [O’Reilly event page](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580)
4. **[observed] Access limits:** Public pages show the agenda and announcement. They show no evidence for recording availability. They show no delivery details beyond the author’s announcement. They show no evidence for researcher attendance/viewing. [O’Reilly event page](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580) [author announcement](https://rule11.tech/upcoming-pearson-class-modern-network-troubleshooting)

## 2. Verified agenda

**[observed]** The public agenda shows resilience, half-split diagnosis, and network models. It shows “Flapping BGP in a DC fabric,” correlation/causation, and slow Internet performance. It also shows LLMs, ping, traceroute, and MTR. This content shows advertised agenda, not checked delivered content. The sources show no evidence for a transcript or recording. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp) [author course post](https://rule11.tech/modern-network-troubleshooting)

## 3. Relevance to rack-bench

**[observed]** The listing shows a BGP data-center example and general troubleshooting methods. It shows no advertisement for NCCL, InfiniBand/RoCE, or per-rail RDMA tests. It also shows no advertisement for ECN/PFC, GPU collective goodput, or rail-optimized topology. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp)

**[inference]** Use it as a method supplement for the two-hour east-west GB300 NVL72-class, 18-tray rack certification. Do not use it as a technical authority for RDMA interpretation or PASS. Use measured rack evidence for PASS. Keep protocol-specific criteria in line with the existing canon. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp) [network canon](../books.md)

## 4. Conditional portable techniques

These techniques show **inferences from the public agenda**, not claims about delivered content. Do not use them in place of rack measurements. Do not use them to change PASS criteria.

1. [inference] **Use half-split for failure-location checks:** On a failed collective or perftest, put implicated hosts/rails or path scope into partitions. Check subsets against each other and keep test conditions unchanged. Run the split again only where topology and binding make the comparison meaningful. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp)
2. [inference] **Use a network model for the next test:** Make a sketch of expected tray–rail–fabric connectivity. Use observed reachability and per-rail results for the selection of a test boundary. Run a boundary check. A model does not show route/path selection. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp)
3. [inference] **Keep correlation separate from cause:** Put timestamps in line for goodput, rail error/retry deltas, congestion counters, and fabric events. Use controlled comparisons before you put the cause of a regression on a flap, ECN/PFC, or rail. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp) [canon](../books.md)
4. [inference] **Do not use resilience as a mask for a bad rail:** Where safe and supported, check alternate paths. Also check rail-specific evidence. Aggregate collective goodput can keep degraded redundancy hidden. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp) [canon](../books.md)
5. [inference] **Keep hypotheses evidence-bound:** If you use an LLM during triage, send it sanitized measurements/logs. Check its suggestions against local tool help and current vendor docs. Do not use generated advice to change a measured PASS. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp) [canon](../books.md)

## 5. Canon verdict

**SKIM [inference]:** The agenda shows method background on half-split diagnosis, models, resilience, and causation. It shows no established fabric-specific rules for the NCCL/perftest, rail, topology, ECN/PFC, or goodput canon. This page shows no course content beyond the public agenda. No source shows measured target-rack PASS. [O’Reilly agenda](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp) [network canon](../books.md)

## Gaps

- [observed] The author shows an advertised January 26, 2023 session linked to this ID. The live listing shows no year. [Course post](https://rule11.tech/modern-network-troubleshooting) [O’Reilly listing](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580)
- [observed] Missing fields: unique session for the supplied 2025 catalog year, recording, transcript, and delivered-content evidence. Retrieval status: not publicly retrievable as of 2026-10-11. Checked sources: [O’Reilly event page](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580), [O’Reilly learning listing](https://learning.oreilly.com/live-events/-/0790145043580/?orm_source=mcp), [author course post](https://rule11.tech/modern-network-troubleshooting).
