# TCP/IP Illustrated: ISBN resolution and rack-bench supplement N09

Research date: 2026-10-11. All claims below use a source URL.

## 1. Identity and access

1. **[observed]** The session ran a fetch of the supplied O'Reilly URL first. It showed HTTP 403. So this session makes no inspection of its catalog metadata/page text. [O'Reilly supplied catalog URL](https://learning.oreilly.com/library/view/-/020163354X/?orm_source=mcp)
2. **[observed]** The publisher's public page shows *TCP/IP Illustrated, Volume 2: The Implementation*. It shows the authors, Gary R. Wright and W. Richard Stevens, ISBN-13 978-0-201-63354-2. The page's TOC puts ISBN-10 0-201-63354-X at the end. The preface shows the signatures of Wright and Stevens and the date November 1994 [InformIT publisher page, TOC and preface](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)
3. **[calculated]** ISBN-13 978-0-201-63354-2: the standard conversion of ISBN-10 0-201-63354-X. [InformIT publisher page, ISBN-13 and ISBN-10](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)
4. **[observed]** The supplied catalog description shows 1995 and 1200pp. The publisher page shows the exact volume identity. The book preface shows the date November 1994; the scanned front matter shows copyright © 1995. The external scan shows an extraction of 1194 pages. Pagination formats show differences, so the extraction does not show the “1200pp” status: rounded or conflicting. [InformIT publisher page](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542); [full-text scan, front matter](https://elhacker.info/manuales/Redes/tcp_ip-illustrated-vol-2.pdf)

## 2. Verified edition and chapter evidence

- **[observed]** The publisher TOC shows Volume 2, *The Implementation*, and Chapters 1–32 plus appendices. Its preface puts the text forward as the 4.4BSD-Lite TCP/IP implementation, approximately 15,000 lines of C.

The preface shows an assumption of basic TCP/IP knowledge. It sends readers to Volume 1 for protocol fundamentals. [InformIT publisher page, TOC and preface](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)
- **[observed]** Relevant TOC entries show Chapter 3, “Interface Layer”; Chapters 18–20, “Radix Tree Routing Tables,” “Routing Requests and Routing Messages,” and “Routing Sockets”. They also show Chapter 21, “ARP: Address Resolution Protocol”, and Chapter 31, “BPF: BSD Packet Filter.” [InformIT publisher page, TOC](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)
- **[observed]** Other TOC entries show Chapters 4–5 on Ethernet, SLIP, and loopback; Chapter 6 on IP addressing. They show Chapters 23–30 on UDP/TCP implementation and Chapters 12–14 on IP multicast, IGMP, and multicast routing. Keep these as the book's subjects, not modern NCCL collective or SHARP guidance. [InformIT publisher page, TOC](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)

## 3. Relevance to N09 / 18-tray east-west certification

- **[observed]** Keep this as an implementation study of Berkeley 4.4BSD-Lite networking. Its preface shows that codebase by name. It does not put itself forward as Linux networking, RDMA verbs, or NCCL documentation. It also does not put itself forward as GB300/NVL72 topology, RoCE ECN/PFC, or SHARP documentation. [InformIT publisher page, preface](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)
- **[inference]** For the two-hour bench window, keep its narrow use as conceptual host/bootstrap triage. Trigger conditions: IP addressing, interface state, neighbor resolution, route choice, or packet visibility blocks to test startup/control traffic. It does not show RDMA data-path health. It does not show measured NCCL goodput/line rate. [Canon](../books.md)
- **[observed]** The existing network-research canon explicitly puts TCP/IP Illustrated outside the core RDMA-guide set. It shows a warning against TCP implementation material as NCCL payload-path evidence. [Local canon: `books.md`](../books.md)

## 4. Portable host/bootstrap checks (3–5)

Keep these as candidate, read-only checks for host/bootstrap triage, not certification pass criteria.

1. **[inference] Interface/link inventory:** make a record of interface name, administrative/operational state, address, MTU, and mapping to intended host/rail. A mismatch or down host interface can make a bootstrap block. It shows nothing about switch-path or RDMA health. [Linux `ip-link(8)`](https://man7.org/linux/man-pages/man8/ip-link.8.html)
2. **[inference] Address/route sanity:** check addresses and route selection to the intended peer/control endpoint. Check the expected source interface/address. Keep this as host IP routing evidence only, not proof of fabric topology or RDMA rail selection. [Linux `ip-route(8)`](https://man7.org/linux/man-pages/man8/ip-route.8.html)
3. **[inference] Neighbor resolution:** check ARP/neighbor state for the peer on Ethernet-based bootstrap networks. Unresolved/incomplete entries can show the cause of IP reachability failure. Do not put ARP assumptions on native InfiniBand data paths. [Linux `ip-neighbour(8)`](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html)
4. **[inference] Name/service bootstrap:** run name resolution for peer names with locally approved tools. Check the expected management/bootstrap endpoint and port. Keep a record of resolved addresses and endpoint. A successful TCP connection shows only that control endpoint, not NCCL/RDMA payload transport. [Linux `getent(1)`](https://man7.org/linux/man-pages/man1/getent.1.html)
5. **[inference] Packet-level spot check, if authorized:** use a bounded capture on the relevant host interface. Check expected bootstrap packets/errors. Wrong interface, permissions, offload, or capture loss makes absence inconclusive. A capture cannot make a fabric certification. [tcpdump manual](https://www.tcpdump.org/manpages/tcpdump.1.html)

**[inference] Limits and pass rule.** Keep these checks separate from per-rail `ib_write_bw`/`ib_read_bw` and NCCL 8 B–16 GB collectives. Keep them separate from transport/plugin logs, counter deltas, topology/routing, ECN/PFC, and SHARP evidence too. A host/bootstrap check can show a blocker. But it cannot make a rack PASS.

Use only measured workload and per-rail evidence, against explicit line-rate normalization and acceptance thresholds, for PASS. Keep unavailable telemetry as a stated limitation, never a pass. [Canon](../books.md)

## 5. Canon verdict

**[inference] SKIM / not core canon.** The volume shows value for legacy BSD TCP/IP implementation study. But do not use its full implementation walkthrough for this bench certification. Use selective skims of Chapters 3–6, 18–21, and 31 only for host bootstrap or packet-path debugging context.

**[inference] KEEP** the existing distinction: the canon puts TCP/IP Illustrated outside the core RDMA guides. Keep TCP implementation code out of the Linux-behavior and modern NCCL/RDMA protocol-evidence categories. [InformIT publisher page, TOC and preface](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542); [Local canon](../books.md)

**[inference] Decision:** **SKIM** as a conditional host/bootstrap reference. **SKIP** as a certification read or evidence source. Do not put it into the RDMA/NCCL canon. [InformIT publisher page](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542)

## Gaps

- **[observed]** The O'Reilly attempt ran first and showed 403. The supplied catalog page shows no read access in this session. [O'Reilly supplied URL](https://learning.oreilly.com/library/view/-/020163354X/?orm_source=mcp)
- **[observed]** The publisher TOC and preface show identity, chapter coverage, and 4.4BSD-Lite scope. The exact meaning of the supplied “1200pp” against the external scan's 1194 extracted pages: unresolved. Pagination formats show differences. This review makes no rounding claim. [InformIT publisher page](https://www.informit.com/store/tcp-ip-illustrated-volume-2-implementation-9780201633542); [full-text scan](https://elhacker.info/manuales/Redes/tcp_ip-illustrated-vol-2.pdf)
- **[observed]** This source shows no evidence for GB300-specific topology, NCCL version behavior, or modern Linux driver implementation. It shows no evidence for per-rail goodput, ECN/PFC, switch counters, or SHARP. Use current platform/vendor documentation and measured rack results for those. [Local canon](../books.md)
