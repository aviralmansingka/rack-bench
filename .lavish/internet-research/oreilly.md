# O'Reilly INTERNET supplement

Research date: 2026-10-11.
Scope: Chennai GB300/NVL72-class rack, 18 trays, and a two-hour internet certification window.
Measure sustained S3/R2/GCS ingress and egress, idle and loaded latency, jitter, loss, routing, DNS, and TCP health.
A PASS requires measurements. This catalog review does not measure the rack.

Fifteen researchers each check one source in parallel. The orchestrator checks decisive evidence and writes this supplement.
See the [node map and lessons](oreilly/research.md) and [handoff report](oreilly/ORCHESTRATOR-REPORT.md).
The source notes retain chapter evidence, conflicts, and limits.

## Main decision

Keep the four-book spine: Gregg second edition, Fall and Stevens Volume 1 second edition, HPBN, and Jain.
Keep Sanders third edition as the main practical packet-analysis supplement.
Change Sloan from blanket SKIP to optional method SKIM. Schroder is a separate new optional candidate.
Add selective DNS and CDN reading. Hold VandenBrink's second edition until release and contents agree.
No catalog source establishes a new quantitative PASS threshold.

## Evidence rules

- **Observed fact:** a checked source states the metadata, topic, or protocol rule.
- **Calculation:** arithmetic uses stated inputs and units.
- **Bench application:** the orchestrator proposes a check from the source's diagnostic scope.
- **Gap:** available evidence does not establish a material claim.

Catalog presence, indexed contents, and subscription entitlement are different facts.
A permission-denied page does not prove that a title is absent.
An event agenda does not prove recording availability.
A chapter title does not prove an exact command, diagnostic example, or certification threshold.
All proposed checks below are bench applications, not verified book-specific rack-bench procedures.

## 1. TCP/IP Illustrated — correct the platform volume

**Verdict: MUST; keep Fall and Stevens Volume 1 second edition.**
The supplied identifier 020163354X names Stevens and Wright's 1995 implementation volume.
O'Reilly lists the recommended second edition under [9780132808200](https://www.oreilly.com/library/view/tcp-ip-illustrated-volume/9780132808200).
That record gives November 2011 and 1,056 pages.
The existing print record gives ISBN 9780321336316, 1,059 pages, and 2011/2012 dates.
Keep identifiers and extents separate for each record. Direct platform entitlement remains unverified.
[Pearson's TOC](https://www.pearson.com/en-us/subject-catalog/p/Fall-TCP-IP-Illustrated-Volume-1-The-Protocols-2nd-Edition/P200000000242?view=educator) confirms Chapters 10–16 and relevant MTU sections.

Bench applications:
1. Keep timeout and fast-recovery evidence separate during sustained transfers.
2. Record MSS, Window Scale, SACK, and timestamps on actual test flows.
3. Compare PMTU probes and ICMP evidence with large-object stalls.
4. Keep resolver results separate from transfer rate.
5. Compare idle and loaded RTT with rate and retransmission evidence.

Protocol mechanisms explain symptoms. They do not set automatic FAIL thresholds.
Read current sources for BBR, QUIC, and Linux counter semantics.
Full chapter list and limits: [tcpip.md](oreilly/tcpip.md).

## 2. High Performance Browser Networking — keep, with two corrections

**Verdict: MUST; keep the free fundamentals spine book.**
Ilya Grigorik, O'Reilly, 2013. The complete text remains available at [hpbn.co](https://hpbn.co/).
The [publisher errata record](https://www.oreilly.com/catalog/errata.csp?isbn=9781449344764) supports ISBN 9781449344764.
The public platform identifier is 9781449344757. The errata record does not name the ISBN format.
Replace the invalid canon ISBN 978-1-4493-4763-0. Do not add an unsupported print-format label.
Read Chapters 1–2 first. Read TLS and connection-reuse material selectively.
The checked sources show no authoritative newer-edition announcement.

**Calculation:** 25 Gbps at 250 ms gives BDP 781.25 MB decimal, or approximately 745.1 MiB.
At 5–10 ms, BDP equals 15.625–31.25 MB decimal. These RTT values serve as examples. They are not rack measurements.
[RFC 7323, Sections 2.2–2.3](https://www.rfc-editor.org/rfc/rfc7323) permits shift count 14.
The largest encoded receive window is 65,535 × 2^14 = 1,073,725,440 bytes.
That maximum exceeds the example BDP. One flow can have a 750 MB window.
Actual rate depends on negotiated scaling, buffers, receive window, congestion window, and path conditions.

Bench applications:
1. Calculate BDP from measured RTT and a stated target rate.
2. Record actual settings and per-flow state. Do not assume universal Linux buffer defaults.
3. Measure one-flow and parallel-flow rate separately. BDP alone does not prove mandatory parallelism.
4. Separate DNS, connection, TLS, first-byte, and sustained-transfer timing.
5. Compare fresh connections with connection reuse.

Use current congestion-control and HTTP/3 documents alongside this 2013 text.
Full contents and correction: [hpbn.md](oreilly/hpbn.md).

## 3. Practical Packet Analysis — retain third edition

**Verdict: MUST-lite; keep Sanders as the main practical packet-analysis supplement.**
Chris Sanders, No Starch Press, third edition, April 2017, 368 pages, ISBN 9781593278021.
[Publisher evidence](https://nostarch.com/packetanalysis3) confirms CLI, transport, and slow-network chapters.
Prioritize Chapters 2, 6, 8, and 11.
The [first-edition release](https://nostarch.com/releases/practical_packet_analysis_release.pdf) gives May 2007, 192 pages, ISBN 9781593271497.
That primary record replaces conflicting historical extent claims.
O'Reilly uses identifier 9781492020356. Direct full-text access remains unverified.
The checked sources show no authoritative fourth-edition listing.

[Current Wireshark guidance](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html) limits TCP classifier claims.
A last-ACK interval below 20 ms marks one fast-retransmission condition. It is not a universal TCP rule.
A label alone does not prove wire loss or an RTO.

Bench applications:
1. Keep bounded captures with independent counters and transfer timelines.
2. Inspect sequence, ACK, SACK, and window evidence before causal conclusions.
3. Record capture position, drops, tool version, preferences, and offloads.
4. Identify the endpoint that advertises each zero window, separately by direction.
5. Keep handshake timing separate from first-byte timing. The latter does not prove pure server processing time.

Full 13-chapter list and limits: [ppa.md](oreilly/ppa.md).

## 4. DNS and BIND — selective diagnostic reading

**Verdict: optional SKIM; add DNS diagnosis, not another spine book.**
Cricket Liu and Paul Albitz, fifth edition, O'Reilly, May 2006, 640 pages.
ISBN 0596100574 / 9780596100575. The overview names BIND 9.3.2 and 8.4.7.
The researcher checks the [Learning catalog](https://learning.oreilly.com/library/view/dns-and-bind/0596100574).
The orchestrator receives an access-denied redirect. Do not claim that everyone can access the full text.
The checked sources show no authoritative sixth-edition listing.
Prioritize Chapters 2, 6, and 12–14. Use Chapters 10–11 for advanced and security context.

Bench applications:
1. Keep resolver address, query name, record type, response code, and timing.
2. Separate NXDOMAIN, NODATA, SERVFAIL, and timeouts.
3. Use controlled names for warm and cold comparisons. Client flushing does not prove recursive-cache coldness.
4. Compare UDP and TCP behavior with EDNS settings and response sizes.
5. Compare recursive and authoritative answers when a delegation or validation fault appears.

Use current BIND documentation for configuration and security.
Complete 17-chapter list and limits: [dns-bind.md](oreilly/dns-bind.md).

## 5. Pro DNS and BIND — separate edition identities

**Verdict: optional DNS background; keep outside the spine.**
[Springer](https://link.springer.com/book/10.1007/978-1-4302-0050-5) lists Ron Aitchison, edition 1, 2005, 608 pages.
Print ISBN 9781590594940; ebook ISBN 9781430200505. Replace the supplied 605-page count.
Springer separately lists [Pro DNS and BIND 10](https://link.springer.com/book/10.1007/978-1-4302-3049-6), edition 1, 2011.
Its print ISBN is 9781430230489; ebook ISBN is 9781430230496. Its extent is XXX, 692 pages.
Do not call the separately titled book a verified second edition of the 2005 title.
Read the 2005 DNS operations, diagnostic tools, and message chapters selectively.

Bench applications:
1. Compare resolver answers, response codes, and timing.
2. Repeat lookups for actual artifact hosts during the window.
3. Compare EDNS and ordinary queries with truncation and TCP completion evidence.
4. Keep resolved addresses with transfer and route evidence.

The old BIND focus does not establish current transport policy.
Direct platform access and the 2011 complete TOC remain unverified.
Detailed evidence: [pro-dns.md](oreilly/pro-dns.md).

## 6. DNS and BIND on IPv6 — separate three address-family questions

**Verdict: optional SKIM for IPv6-DNS diagnosis.**
Central catalog metadata lists Cricket Liu, O'Reilly, 2011, 52 pages, identifier 9781449308025.
Public indexed [contents](https://www.oreilly.com/library/view/dns-and-bind/9781449308025/cover.html) show five chapters.
The review shows limits in direct public metadata and full-text access.
Read Chapters 1 and 5. Read Chapter 4 only for DNS64 deployments.
AAAA data, IPv6 DNS transport, and IPv6 application transport are different concepts.

Bench applications:
1. Compare A and AAAA outcomes. Keep NODATA separate from NXDOMAIN and SERVFAIL.
2. Send the same query through each available resolver transport family.
3. Test application connections separately by family. IPv4 fallback can hide an IPv6 failure.
4. Compare controlled large-response UDP behavior with TCP completion.
5. Test DNS64 only when production uses IPv6-only/NAT64 behavior.

[RFC 10001](https://www.rfc-editor.org/rfc/rfc10001) supplies current mixed-family DNS guidance.
[RFC 9715](https://www.rfc-editor.org/rfc/rfc9715) supplies informational fragmentation guidance, not a universal PASS gate.
Do not require reverse DNS on all endpoints.
Five-chapter list and limits: [dns-ipv6.md](oreilly/dns-ipv6.md).

## 7. Content Delivery Networks — narrow delivery context

**Verdict: optional SKIM of Chapters 2–4; no spine promotion.**
Dom Robinson, Wiley, first edition, 2017, 256 pages, print ISBN 9781119249870.
[Wiley's TOC](https://catalogimages.wiley.com/images/db/pdf/9781119249870.toc.pdf) confirms request routing, goodput, object-size, and latency topics.
Direct O'Reilly access and detailed chapter text remain unverified.
Goodput means useful application data per unit time. It does not mean all wire bytes.

Bench applications:
1. Keep DNS answers, redirects, destination addresses, and route context with transfers.
2. Compare controlled small and large objects with constant test conditions.
3. Check useful byte counts and checksums.
4. Keep CDN-delivered artifact results separate from direct object-store results.

DNS answers and headers do not alone prove physical cache location.
Use current service documentation for object-store behavior and regional limits.
Complete 12-chapter list and limits: [cdn.md](oreilly/cdn.md).

## 8. Packet Analysis with Wireshark — bounded Nath selection

**Verdict: optional SKIM; not a Sanders replacement.**
The researcher reports Anish Nath, Packt, first edition, December 2015, 172 pages, ISBN 9781785887819.
Indexed [O'Reilly contents](https://www.oreilly.com/library/view/packet-analysis-with/9781785887819/index.html) expose TCP troubleshooting and latency material.
The [Packt page](https://www.packtpub.com/en-ee/product/packet-analysis-with-wireshark-9781785887819?type=print) presents bot verification.
Complete chapter hierarchy, exact examples, and present free-access terms remain unverified.
Prioritize TCP troubleshooting and latency topics; then DNS and HTTP analysis.

Bench applications:
1. Keep transfer captures with independent counters.
2. Inspect SYN options, advertised windows, and sequence behavior.
3. Compare idle and loaded packet timing with independent RTT probes.
4. Separate DNS, connection, TLS, and sustained-transfer timing.
5. Use deliberate probes to test a PMTUD explanation for stalls.

The catalog does not confirm these exact procedures.
Use current Wireshark capture and classification guidance.
Partial contents and limits: [nath.md](oreilly/nath.md).

## 9. Wireshark 101 video — useful guided labs, conflicting metadata

**Verdict: optional guided practice; keep Sanders as the practical book.**
Chris Greer teaches this Pearson video.
[InformIT](https://www.informit.com/store/wireshark-101-packet-analysis-essentials-video-course-9780138240936) gives first edition, copyright 2024, ISBN 9780138240936, and four hours.
The supplied O'Reilly record uses 9780138240882, 2023, and 233 minutes.
Do not silently merge those records. Exact product relationship and runtime remain unresolved.
Relevant lessons cover capture placement, filters, packet loss, congestion, application latency, and TCP issues.

Bench applications:
1. Record capture placement, direction, timestamps, and capture drops.
2. Compare transfer packet evidence with counters and throughput.
3. Compare congestion symptoms with idle and loaded latency measurements.
4. Keep endpoint and time filters with exported evidence.

The public outline confirms training topics. It does not confirm measurement thresholds or playback entitlement.
Lesson evidence and limits: [greer.md](oreilly/greer.md).

## 10. Packet Analysis Using Wireshark event — security-focused introduction

**Verdict: optional introduction; not certification authority.**
The [O'Reilly agenda](https://www.oreilly.com/live-events/packet-analysis-using-wireshark/0636920075846) names Ming Chow.
Event ID 0636920075846 identifies a live event, not a book ISBN.
Its two-hour agenda covers capture basics, file reconstruction, credentials, filtering, and malware traffic.
The supplied 2025 date and recording availability remain unverified.

Bench applications:
1. Use a bounded capture of authorized test traffic for introductory practice.
2. Filter the actual transfer flow and inspect its handshake.
3. Compare sequence symptoms with TCP counters after an anomaly.
4. Keep visible DNS evidence with instrumented resolver results.

Protect credentials and tenant data. Do not remove sustained measurement time for capture training.
The event recommends Sanders third edition as follow-up reading.
Agenda and limits: [chow.md](oreilly/chow.md).

## 11. Network Troubleshooting Tools — change the rejection reason

**Verdict: optional method SKIM; replace blanket SKIP.**
Joseph D. Sloan, O'Reilly, first edition, 2001, ISBN 9780596001865.
The printing history gives August. The existing canon gives September. Keep this date distinction visible.
The supplied 364-page extent differs from a scan's 366 PDF pages. PDF page count does not prove book extent.
[Google Books](https://books.google.com/books/about/Network_Troubleshooting_Tools.html?id=VyZTAAAAMAAJ) describes normal baselines and combined tools.
A [contemporary review](https://www.linuxjournal.com/article/4894) supports path, capture, and application diagnosis.
Read Chapter 4, Path Characteristics, and Chapter 12, Troubleshooting Strategies, selectively.

Bench applications:
1. Keep an idle baseline before load.
2. Separate reachability, path observations, and TCP evidence.
3. Compare throughput with RTT and loss for the same endpoint and load state.
4. Test service behavior, not host reachability alone.

The method supports selective reading despite old commands.
Keep Sloan off the spine. Use current tool documents.
Detailed chapter evidence partly uses a secondary scan: [sloan.md](oreilly/sloan.md).

## 12. Linux Networking Cookbook — new candidate, not Sloan's SKIP

**Verdict: new optional Chapter 19 SKIM.**
Carla Schroder, O'Reilly, ISBN 9780596102487.
Secondary front matter gives first printing November 2007 and copyright 2008.
The [Chapter 19 record](https://www.oreilly.com/library/view/linux-networking-cookbook/9780596102487/ch19.html) names Troubleshooting Networks.
The researcher uses secondary-copy evidence for detailed sections because publisher fetches fail.
Relevant topics include MTR, httping, tcpdump, iperf, and DNS diagnosis.
The existing rejection concerns Sloan's different book.

Bench applications:
1. Keep path snapshots with endpoint-transfer evidence.
2. Compare sustained rate with latency, jitter, and loss under stated test conditions.
3. Use captures and resolver queries after a transfer anomaly.

An iperf test does not certify the actual object-store service path.
Use current documents before old commands. Complete primary TOC remains unverified.
Chapter 19 details and limits: [cookbook.md](oreilly/cookbook.md).

## 13. Linux for Networking Professionals — hold second edition

**Verdict: HOLD; do not recommend purchase as a released 2026 title.**
Rob VandenBrink, Packt, second-edition candidate.
Print ISBN 9781835881101; ebook ISBN 9781835881118.
The researcher reports an [O'Reilly](https://www.oreilly.com/library/view/linux-for-networking/9781835881101) August 2026 record with 512 pages.
[Amazon](https://www.amazon.com/Linux-Networking-Professionals-Strengthen-networking-ebook/dp/B0D6DSQZ9D) reports August 10, 2027.
[OverDrive](https://www.overdrive.com/media/11007262/linux-for-networking-professionals) reports July 23, 2027.
The researcher cannot access direct publisher pages or the complete second-edition TOC.
Do not transfer first-edition chapter numbers into second edition.

Conditional bench applications:
1. Keep interface, route, resolver, and capture state in an evidence bundle.
2. Keep command timestamps with each transfer result.
3. Repeat controlled resolver and RTT samples with response codes and sample counts.

These general applications do not establish second-edition coverage or justify new certification requirements.
Release conflicts and limits: [linux-pro.md](oreilly/linux-pro.md).

## 14. Modern Network Troubleshooting event — useful method scope

**Verdict: optional method training; no spine replacement.**
The [O'Reilly agenda](https://www.oreilly.com/live-events/modern-network-troubleshooting/0790145043580) names Russ White and Pearson.
Event ID 0790145043580 identifies a live event. ISBN does not apply.
The agenda covers resilience, the half-split method, causation, and Internet slow performance.
The supplied 2025 date, recording availability, and detailed exercises remain unverified.

Bench applications:
1. Compare controlled cases. Change one destination or load condition at a time.
2. Keep repeated path observations with end-to-end transfer results.
3. Separate DNS, connection, transfer, and TCP evidence.
4. Keep initial evidence and test one explanation before a controlled repeat.

Correlation does not prove fault location. Public agenda topics do not establish quantitative thresholds.
Agenda and limits: [white.md](oreilly/white.md).

## 15. Systems Performance — retain the correct edition evidence

**Verdict: MUST; retain rank 1 and the methodology spine.**
Brendan Gregg's [official page](https://www.brendangregg.com/systems-performance-2nd-edition-book.html) names second edition, 2020.
[InformIT](https://www.informit.com/store/systems-performance-9780136820154) gives copyright 2021, 928 pages, ISBN 9780136820154.
Read Chapters 2, 10, and 12.
The publisher confirms that Chapter 10 covers methodology, observability, experimentation, and tuning.
The public TOC does not show the detailed Chapter 10 tool inventory.
The initial researcher brief uses a first-edition TOC. The orchestrator rejects that edition-specific evidence.
Do not reuse that inventory as second-edition proof.

Bench applications:
1. Check local utilization, saturation, and errors during transfers.
2. Keep idle and loaded latency distributions with timestamps and sample counts.
3. Keep path observations with end-to-end evidence.
4. Use bounded captures and TCP counters after transfer anomalies.
5. Record endpoint, direction, concurrency, duration, and load state for controlled comparisons.

A saturated local receiver can lower ingress without a WAN fault.
Use current documents for exact tools and counters. Direct platform access remains unverified.
Corrected TOC and limits: [gregg.md](oreilly/gregg.md).

## Coverage and certification limits

| Check family | Reading support | Remaining requirement |
| --- | --- | --- |
| Sustained ingress and egress | HPBN; Gregg; CDN context | Measure actual S3/R2/GCS paths, payloads, durations, and concurrency |
| Idle and loaded latency | Gregg; Fall; HPBN; Sloan | Keep time series, sample counts, and load state |
| Jitter and loss | Protocol and capture supplements; Schroder topic list | Define estimators; record vantage, sampling, and confidence limits |
| Routing and path evidence | Fall; Sloan; Schroder; White agenda | Use current path-tool documents and control-plane evidence |
| DNS | Liu/Albitz; Aitchison; IPv6 supplement | Control names, caches, family, transport, and response outcomes |
| TCP health | Fall; Sanders; Gregg; Nath/Greer practice | Check current counters, captures, offloads, and negotiated flow state |

No book or agenda confirms Chennai path quality, physical CDN cache location, or peering presence.
A two-hour window cannot confirm long-term availability, diurnal duty cycle, or failover behavior.
Keep uncertainty and unmeasured conditions with every certificate.

## Gaps

- O'Reilly authentication and publisher bot checks prevent several direct metadata or full-text checks.
- Nath's complete contents and exact examples remain unverified.
- Greer's identifiers, supplied date, and exact runtime differ from accessible publisher evidence.
- Chow's and White's dates and recording availability remain unverified.
- VandenBrink's second-edition release dates conflict; complete contents remain unverified.
- HPBN's corrected ISBN lacks an explicit format label in the checked errata record.
- Sloan and Schroder use secondary evidence for detailed historical chapters.
- Aitchison's separately titled 2011 book lacks a complete checked TOC.
- Current cloud-object procedures, BBR/QUIC behavior, and measurement thresholds require separate primary evidence.
- The distilled project's BDP sentence still needs the staged correction. The orchestrator does not edit project documents.

See [reading-list-update.md](oreilly/reading-list-update.md) for publication text and additional correction flags.
