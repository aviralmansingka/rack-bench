# N02 — High Performance Browser Networking

Research date: 2026-10-11. Researcher: oreilly-hpbn-N02.

## Edition and access

Ilya Grigorik writes this 2013 O'Reilly book.
The author provides the complete text at [hpbn.co](https://hpbn.co/).
The public O'Reilly identifier is 9781449344757.
The O'Reilly [errata page](https://www.oreilly.com/catalog/errata.csp?isbn=9781449344764) accepts ISBN 9781449344764.
The checked errata record does not explicitly name that ISBN's format.
Replace the invalid canon ISBN 978-1-4493-4763-0. Do not add an unsupported print-format claim.
The researcher finds no authoritative newer-edition announcement in the checked sources.
This bounded search does not prove that no newer edition exists.
Catalog visibility does not prove full-text entitlement. The author site supplies public text independently.

## Contents

1. Primer on Latency and Bandwidth
2. Building Blocks of TCP
3. Building Blocks of UDP
4. Transport Layer Security (TLS)
5. Introduction to Wireless Networks
6. WiFi
7. Mobile Networks
8. Optimizing for Mobile Networks
9. Brief History of HTTP
10. Primer on Web Performance
11. HTTP/1.X
12. HTTP/2
13. Optimizing Application Delivery
14. Primer on Browser Networking
15. XMLHttpRequest
16. Server-Sent Events (SSE)
17. WebSocket
18. WebRTC

Read Chapters 1–2 first. Read Chapter 4 and connection-reuse sections selectively.
The text explains latency components, flow control, congestion control, and bandwidth-delay product.
It does not supply current BBR, QUIC, or HTTP/3 diagnosis.

## TCP window correction — calculation and current primary evidence

The existing canon says one flow cannot have a 750 MB window. That statement is false.
At 25 Gbps and 250 ms RTT, BDP equals 781,250,000 bytes.
That value equals 781.25 MB decimal, or approximately 745.1 MiB.
At 5–10 ms RTT, BDP equals 15.625–31.25 MB decimal.
These RTT values are example inputs, not measurements from the rack.
[RFC 7323, Sections 2.2–2.3](https://www.rfc-editor.org/rfc/rfc7323) permits shift count 14.
The largest encoded receive window is 65535 × 2^14 = 1,073,725,440 bytes.
That maximum exceeds the example 250 ms BDP.
Both endpoints must exchange Window Scale options during the handshake.
The negotiated scale, socket buffers, receive window, congestion window, and path conditions still limit actual throughput.
BDP alone does not prove that the bench needs parallel flows.
The orchestrator checks the RFC's decisive passage and the errata record.

## Bench applications — inferences

1. Calculate BDP from measured RTT and a stated target rate. Record byte units.
2. Record live socket buffers and negotiated windows. Do not assume a universal Linux default.
3. Measure one-flow and parallel-flow rates separately. Keep duration, concurrency, direction, and endpoint with each result.
4. Separate DNS, TCP connection, TLS, first-byte, and transfer times.
5. Compare connection reuse with fresh connections. Use long transfers for sustained-rate checks.

Example: a slow 250 ms transfer does not prove a TCP protocol window limit.
Check the actual window and host constraints before you make that conclusion.

## Canon verdict and gaps

Keep rank 3 and the four-book spine. Correct ISBN and TCP window arithmetic.
Do not use the book as current cloud-endpoint or congestion-control documentation.
The print-format label for ISBN 9781449344764 remains unverified.
