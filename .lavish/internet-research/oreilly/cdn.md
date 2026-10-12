# N07 — Content Delivery Networks: Fundamentals, Design, and Evolution

Research date: 2026-10-11. Researcher: oreilly-cdn-N07.

## Observed edition and contents

Wiley lists Dom Robinson, edition 1, 2017, and 256 pages.
Print ISBN: 9781119249870. PDF: 9781119249887. EPUB: 9781119249894.
Wiley Online Books ISBN: 9781119249924.
The supplied O'Reilly page is inaccessible during this research. The central catalog supplies evidence of platform presence.

Chapter list from Wiley's TOC:

1. Welcome
2. Context and Orientation
3. Workflows
4. Publishing
5. Service Velocity
6. Charging for IP-Delivered Content
7. Competition and the Regulatory Environment
8. Cultural Change
9. Preparing for Change in Your Design
10. Multicast – the Sleeping Giant
11. Deep-Dives (Case Studies)
12. Wrap Up

Diagnostic-adjacent sections:

- 2.1.4 Physical Network Considerations; 2.1.5 Internet Layer Considerations.
- 2.1.6 Transport Layer Considerations; 2.1.7 Applications – Transport Protocols.
- 2.5.3 Request Routing.
- 3.2.7 Throughput vs. Goodput.
- 4.2 Small Objects, Large Objects, or Continuous Streams; 4.2.3 Latency.
- 4.4 Request Routing (The Dark Art of the CDN).
- 4.5 Logging Analytics and the Devil in the Detail.

Read chapters 2–4 selectively. Commercial and streaming chapters do not form an internet-diagnostic core.

## Proposed bench techniques — TOC-based inferences

1. Record DNS answers, redirects, destination addresses, and route context for each object transfer.
2. Compare controlled small and large objects. Keep size and test duration constant across comparisons.
3. Check byte count and checksum. A fast but incorrect transfer does not establish valid goodput.
4. Keep transfer results with TCP, MTR, DNS, and loaded-latency evidence.
5. Keep CDN-delivered artifact results separate from direct object-store results.

The TOC suggests these applications. It does not establish their exact procedures.
Goodput means useful application data per unit time, not all bytes on the wire.
Endpoint names, headers, and DNS answers alone do not prove physical cache location.

## Canon verdict

Add a new narrow CDN-context supplement. Do not add a diagnostic spine book.
The book explains serving-system effects on application delivery.
The existing AI-labs and large-companies briefs supply stronger current service-specific evidence.

## Gaps

Public metadata and TOC do not establish modern S3/R2/GCS procedures, PMTUD, or congestion-control diagnosis.
Direct O'Reilly access and detailed chapter text remain unverified.

## Sources

- [Wiley catalog](https://www.wiley.com/en-es/content-delivery-networks-fundamentals-design-and-evolution-p-9781119249924).
- [Wiley TOC](https://catalogimages.wiley.com/images/db/pdf/9781119249870.toc.pdf).
- [Wiley Online Books](https://onlinelibrary.wiley.com/doi/book/10.1002/9781119249924).
- [Supplied O'Reilly record](https://learning.oreilly.com/library/view/-/9781119249870/?orm_source=mcp).
- Local scope: `.lavish/internet-research/{books,ai-labs,large-companies}.md`.
