# N03 — Practical Packet Analysis editions

Research date: 2026-10-11. Researcher: oreilly-ppa-N03.

## Edition and access

Chris Sanders, No Starch Press, third edition, April 2017.
Publisher metadata gives 368 pages and ISBN 9781593278021.
The O'Reilly platform identifier is 9781492020356. Direct fetch fails.
The publisher's first-edition release gives May 2007, 192 pages, ISBN 9781593271497.
That primary record replaces the supplied 178-page count and the initial 164-page catalog uncertainty.
The second edition dates to 2011. The publisher still lists the third edition as current.
The researcher finds no authoritative fourth-edition listing. This is a bounded search result.
Catalog visibility does not prove full-text entitlement.

## Complete third-edition chapter titles — publisher

1. Packet Analysis and Network Basics
2. Tapping into the Wire
3. Introduction to Wireshark
4. Working with Captured Packets
5. Advanced Wireshark Features
6. Packet Analysis on the Command Line
7. Network Layer Protocols
8. Transport Layer Protocols
9. Common Upper-Layer Protocols
10. Basic Real-World Scenarios
11. Fighting a Slow Network
12. Packet Analysis for Security
13. Wireless Packet Analysis

Read Chapters 2, 6, 8, and 11 first.
They cover capture position, CLI analysis, transport protocols, and slow-network diagnosis.
The catalog does not prove every detailed rule attributed to the third edition in the existing canon.

## Current technical correction

Wireshark processes packets in capture order. It uses several TCP classification conditions.
The fast-retransmission classifier includes a last-ACK interval below 20 ms.
That condition alone does not prove loss, a TCP fast-retransmit mechanism, or an RTO.
Wireshark documents ambiguous classifications and capture-position differences.
Treat its labels as diagnostic evidence, not ground truth.
Record capture position, dropped packets, tool version, preferences, and NIC offloads.
A zero-window advertisement identifies the receiver for that direction.
During downloads, that receiver can be the bench host. During uploads, it can be the remote endpoint.
Do not attribute all zero windows to the bench client.
A request-to-first-byte interval can include path, protocol, and service delay.
One endpoint capture does not prove pure server processing time.

## Proposed bench techniques — inferences

1. Keep bounded transfer captures with kernel counters and timestamped throughput samples.
2. Inspect sequence numbers, ACKs, SACK, and windows before you classify a stall.
3. Compare idle and loaded captures under the same capture conditions.
4. Use TShark for repeatable summaries. Keep filters and tool versions with results.
5. Check both transfer directions. Identify the endpoint that sends each zero-window advertisement.

Example: a capture drop can produce a missing-segment label without wire loss.
Independent counters and a second capture can test that explanation.

## Canon verdict

Keep rank 6 and MUST-lite. Sanders remains the main practical packet-analysis supplement.
Correct the Wireshark classification claims. Do not move packet analysis into the four-book spine.

## Sources and limits

- [No Starch third-edition page](https://nostarch.com/packetanalysis3).
- [No Starch first-edition release](https://nostarch.com/releases/practical_packet_analysis_release.pdf).
- [O'Reilly third-edition record](https://www.oreilly.com/library/view/practical-packet-analysis/9781492020356/).
- [Wireshark TCP analysis](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html).
- [Wireshark checksum and offload guidance](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvChecksums.html).

The orchestrator checks the publisher release and current Wireshark classifier passage.
The publisher page extraction shows reviews; the researcher supplies the publisher TOC check.
Full third-edition text access remains unverified.
