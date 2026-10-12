# N15 — Systems Performance, second edition

Research date: 2026-10-11. Researcher: oreilly-gregg-N15.

## Evidence correction

The initial brief uses `https://www.gbv.de/dms/tib-ub-hannover/756958024.pdf` for detailed chapter headings.
That PDF is first-edition evidence. It ends with Chapter 13, Case Study, and includes Solaris material.
The orchestrator checks it and rejects its use for second-edition details.
The corrected brief uses the InformIT second-edition TOC. Do not carry forward the first-edition tool inventory.

## Observed edition identity

Gregg's official site identifies Addison-Wesley, second edition, 2020.
InformIT identifies edition 2, copyright 2021, 928 pages, ISBN 9780136820154.
These dates describe publication and copyright, not conflicting editions.
The book uses Linux as its main example. It also shows BPF, BCC, bpftrace, perf, and Ftrace coverage.
The supplied O'Reilly URL fails direct fetch. No independent platform-body evidence supports entitlement.
The central cross-track catalog context shows the candidate. Public publisher evidence confirms the edition.
No newer edition appears in the checked author pages and searches. This is a bounded finding.

## Complete second-edition chapter list — InformIT

1. Introduction
2. Methodologies
3. Operating Systems
4. Observability Tools
5. Applications
6. CPUs
7. Memory
8. File Systems
9. Disks
10. Network
11. Cloud Computing
12. Benchmarking
13. perf
14. Ftrace
15. BPF
16. Case Study

Chapter 10 starts on page 499. Its verified sections are:

10.1 Terminology; 10.2 Models; 10.3 Concepts; 10.4 Architecture; 10.5 Methodology;
10.6 Observability Tools; 10.7 Experimentation; 10.8 Tuning; 10.9 Exercises; 10.10 References.

The public TOC does not show lower-level Chapter 10 tool names.
Read chapters 2, 10, and 12. Do not attribute every current network tool to this limited TOC.

## Proposed bench techniques — inferences from methodology and scope

1. Check local load, saturation, and errors during transfers before you attribute a low rate to an ISP.
2. Keep idle and loaded latency distributions with timestamps and sample counts.
3. Keep path snapshots with end-to-end transfer evidence. A silent router does not prove data-plane loss.
4. Use bounded captures and independent TCP counters to investigate anomalous transfers.
5. Record endpoint, direction, concurrency, duration, and load state for controlled comparisons.

Example: local receiver saturation can lower measured ingress even when the WAN path remains healthy.
Gregg supplies the systems-method reason to check the measuring host.
Exact tools and semantics require current tool documentation or full chapter evidence.
These proposals do not come from a verified lower-level tool inventory.

## Canon verdict

The review confirms the rank-1 methodology spine. Keep the four-book division of work.
Gregg supports host and system diagnosis; Fall supports protocol mechanisms; Jain supports statistics.
The book does not establish cloud-object rates, Chennai routes, PeeringDB behavior, or certification cutoffs.

## Gaps

Direct O'Reilly access and detailed Chapter 10 text remain unverified.
The public second-edition TOC supports section-level claims only.

## Sources

- [Gregg's official edition page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html).
- [InformIT metadata and second-edition TOC](https://www.informit.com/store/systems-performance-9780136820154).
- [O'Reilly candidate URL](https://www.oreilly.com/library/view/systems-performance-2nd/9780136820154/).
- [Gregg's USE method](https://www.brendangregg.com/usemethod.html).
- Local canon: `.lavish/internet-research/books.md`, section 1.

The orchestrator fetches both primary pages and checks the edition, ISBN, pages, chapter titles, and Chapter 10 sections.
