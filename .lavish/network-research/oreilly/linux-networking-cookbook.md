# N07 source supplement: *Linux Networking Cookbook*

Research date: 2026-10-11. All claims below use a source URL.

## 1. Identity and access

[observed] The supplied O’Reilly Learning link shows ISBN 9780596102487. Its fetch shows HTTP 403. So this session shows no subscriber chapter access. [O’Reilly catalog](https://www.oreilly.com/library/view/linux-networking-cookbook/9780596102487).

A publicly accessible 634-page PDF copy shows the title page, copyright, ISBN, and printing history: first edition, November 2007. Its copyright page shows ©2008. This shows the first edition, not a distinct 2007 edition. [Public PDF, title/copyright pages](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf).

The catalog shows a Linux network-administrator recipe book for gateways, monitoring, and troubleshooting. Access level: catalog metadata publicly searchable. The supplied O’Reilly page shows no access in this session. The public PDF mirror (not publisher-hosted) shows TOC/preface access. This review makes no independent full-chapter-text check here. [O’Reilly catalog](https://www.oreilly.com/library/view/linux-networking-cookbook/9780596102487) [public PDF](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf).

## 2. Verified chapters (first-edition TOC)

[observed] Chapter 13, “Network Monitoring with Nagios” (page 371). Chapter 14, “Network Monitoring with MRTG” (page 408). The chapters show service/host checks and SNMP monitoring. Chapter 19, “Troubleshooting Networks” (page 515), shows ping (19.2), fping/Nmap (19.3), and arping duplicate-IP checks (19.4). The chapter shows HTTP throughput/latency (19.5), traceroute/tcptraceroute/mtr (19.6), and tcpdump (19.7–19.8). It shows iperf throughput/jitter/loss (19.9), ntop (19.11), and DNS/server troubleshooting.

This review checks these headings against the first-edition TOC. It makes no inference from another edition. [Public PDF, TOC pp. v–xiv](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf). The preface shows the utilities as quick troubleshooting tools. It sends readers to Chapters 13–14 for ongoing monitoring. [Public PDF, Preface pp. xvi–xx](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf).

## 3. Relevance to this bench

[inference] Keep this as a useful host-diagnosis supplement, not an RDMA-fabric authority. Its 2007 first-edition context puts it before GB300/NVL72, contemporary NCCL paths, and modern RoCE congestion tooling. TCP/IP reachability, packet capture, and generic iperf throughput do not show RDMA verbs performance or per-rail health. They do not show NCCL transport selection, SHARP use, or correct ECN/PFC operation.

Keep this boundary explicit. Modern NCCL guidance instead shows these checks: links, low-level RDMA tests, counters, and RoCE NIC/switch congestion signals. [NCCL Networking Troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).

## 4. Portable bench checks (3–5)

[inference] Keep these as short, read-only host-side triage checks before/after the measured run. Make a record of the timestamp, host/tray, interface, and tool version. Keep them as diagnostic clues, not PASS criteria by themselves.
   1. **Link inventory and state:** use `ip -br link` plus platform-available `ibstat`/`ibstatus`. Check the rail-to-HCA/port mapping, active state, and negotiated rate against expectations. A host link-up does not show fabric topology or end-to-end health. [inference] [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).
   2. [inference] **Address/neighbor conflict check:** use `ip -br addr`, `ip route`, and targeted `arping` for configured peer addresses where applicable. Check duplicate-IP or unexpected route/neighbor evidence. Keep this as ordinary host/IP diagnosis, not an RDMA test. [observed] Chapter 19.4 shows the explicit title “Finding Duplicate IP Addresses with arping.” [Public PDF TOC](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf).
   3. **Error-counter deltas:** check available NIC/RDMA counters before and after controlled load. Keep exact names and values. Keep attention on newly increasing errors/retries/drops, not old nonzero totals. Counter interfaces and semantics show driver/platform-specific behavior. No source here makes a universal-command promise. [inference] [NCCL troubleshooting](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html).
   4. **Targeted RDMA pair sanity:** use version-matched `ib_write_bw`, `ib_read_bw`, and latency test between selected endpoints. Put each test explicitly on its intended rail and direction. Check measured goodput against the documented per-port line-rate denominator. Keep the command/output; keep this as more relevant than generic iperf. It still does not show full-rack collective performance. [inference] [NCCL low-level tests](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html) [perftest](https://github.com/linux-rdma/perftest).
   5. [inference] **Capture narrow host evidence:** run brief, scoped `tcpdump` only for management/bootstrap traffic or a specifically authorized investigation. Do not make a lack of captured packets into proof of clean RDMA data plane. Keep the book’s tcpdump chapter as generic network troubleshooting. [observed] Chapter 19.7–19.8 TOC headings; limitations for this bench: inference. [Public PDF](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf).

## 5. Canon verdict and spine recommendation

**KEEP as an optional, clearly dated host-diagnosis supplement; do not put it into core N07 canon.** [inference]

Keep its most useful additions as simple IP/link triage and a diagnostic mindset: throughput/latency measurement and traffic inspection. Its generic TCP/iperf and monitoring recipes do not show per-rail RDMA or 8 B–16 GB NCCL collectives. They do not show rail/topology use, ECN/PFC behavior, flaps, SHARP, or rack-scale PASS.

Put one sentence under the book/canon discussion in the existing [books.md](../books.md) spine: “Schroder, *Linux Networking Cookbook*, 1e (2007/2008; ISBN 9780596102487), optional host-side troubleshooting supplement (TOC-confirmed chs. 13–14, 19); dated TCP/IP recipes, not RDMA/NCCL/PFC evidence.”

Keep Gregg/Jain/Kurose and the modern NCCL/vendor manuals in their current roles. Do not put them into new roles or a new order on this evidence.

## Gaps

- [observed] The O’Reilly fetch shows no access. This review uses no publisher chapter text. [Catalog](https://learning.oreilly.com/library/view/-/9780596102487/?orm_source=mcp)
- [observed] The PDF mirror shows matching ISBN and edition pages. Its publisher authorization: unknown. [PDF](https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf)
- [inference] Use target-rack validation for the proposed checks. They do not show fabric PASS. [NCCL guide](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/networking_troubleshooting.html)
