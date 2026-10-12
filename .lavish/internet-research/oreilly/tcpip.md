# N01 — TCP/IP Illustrated editions

Research date: 2026-10-11. Researcher: oreilly-tcpip-N01.

## Observed edition identity

The supplied O'Reilly ID 020163354X points to the 1995 Stevens/Wright implementation volume.
The researcher reports January 1995 and 1,200 pages from that catalog record.
It is Volume 2: The Implementation, not Fall's revised Volume 1.

O'Reilly search evidence lists Fall and Stevens, Volume 1, second edition, under 9780132808200.
That record gives November 2011 and 1,056 pages.
Direct second-edition page fetches fail. Catalog presence does not establish subscription access.
The existing canon uses print ISBN 9780321336316 and 2011/2012 dates.
Pearson's product links also use 9780132808187. Keep format identifiers separate.
No evidence in this review supports replacing the recommended 2e with the supplied implementation volume.

## Complete 2e chapter list — Pearson TOC

1. Introduction
2. The Internet Address Architecture
3. Link Layer
4. ARP: Address Resolution Protocol
5. The Internet Protocol (IP)
6. System Configuration: DHCP and Autoconfiguration
7. Firewalls and Network Address Translation (NAT)
8. ICMPv4 and ICMPv6: Internet Control Message Protocol
9. Broadcasting and Local Multicasting (IGMP and MLD)
10. User Datagram Protocol (UDP) and IP Fragmentation
11. Name Resolution and the Domain Name System (DNS)
12. TCP: The Transmission Control Protocol (Preliminaries)
13. TCP Connection Management
14. TCP Timeout and Retransmission
15. TCP Data Flow and Window Management
16. TCP Congestion Control
17. TCP Keepalive
18. Security: EAP, IPsec, TLS, DNSSEC, and DKIM

The orchestrator fetches Pearson's complete TOC and checks these titles.
Key sections: 3.8 MTU and Path MTU; 10.8 UDP PMTUD; 13.3 TCP Options; 13.4 TCP PMTUD.
Chapter 14 separates timers, fast retransmit, SACK, spurious events, and reordering.
Chapter 16 includes Buffer Bloat, AQM, and ECN.
The TOC confirms topics. It does not confirm command semantics or certification thresholds.

## Proposed bench techniques — inferences

1. Separate fast-recovery evidence from timeout and stall evidence during transfers.
   Chapter 14 explains why one combined retransmission number loses diagnostic detail.
2. Record negotiated MSS, SACK, window scaling, and timestamps on actual test flows.
   Chapters 13 and 15 explain why flow options affect high-BDP transfers.
3. Compare PMTU probes and relevant ICMP errors with large-object stalls.
   Chapters 3, 8, 10, and 13 explain MTU and error signaling.
4. Record resolver identity, response codes, and lookup timing separately from transfer rate.
   Chapter 11 explains caching and resolution behavior.
5. Compare idle and loaded RTT with throughput and retransmissions.
   Chapter 16 explains queueing and congestion-control mechanisms.

Example: a transfer can keep high goodput while its loaded RTT increases substantially.
That result does not establish low queueing delay.
These proposals require current counter/tool documents and measured rack evidence.

## Canon verdict

This evidence confirms Fall and Stevens Vol. 1 2e as the protocol spine.
Correct the O'Reilly link, not the recommended edition.
Keep current RFCs and Linux documents for BBR, QUIC, counters, and implementation behavior.
The book does not establish Chennai paths, PeeringDB interpretation, or cloud-endpoint performance.

## Gaps

Direct authenticated access remains unverified. Public search evidence establishes the platform listing.
ISBNs differ by record and format. Do not silently replace a print ISBN with a platform identifier.
The review does not verify a full first-edition or implementation-volume TOC.
Those older titles do not control the recommendation.

## Sources

- [Supplied implementation-volume record](https://learning.oreilly.com/library/view/-/020163354X/?orm_source=mcp).
- [O'Reilly Vol. 1 2e record](https://www.oreilly.com/library/view/tcp-ip-illustrated-volume/9780132808200).
- [O'Reilly 2e TOC record](https://www.oreilly.com/library/view/tcp-ip-illustrated-volume/9780132808200/toc.xhtml).
- [Pearson 2e chapter evidence](https://www.pearson.com/en-us/subject-catalog/p/Fall-TCP-IP-Illustrated-Volume-1-The-Protocols-2nd-Edition/P200000000242?view=educator).
- Local canon: `.lavish/internet-research/books.md`, section 3.
