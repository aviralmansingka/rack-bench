# N11 — Network Troubleshooting Tools

Research date: 2026-10-11. Researcher: oreilly-sloan-N11.

## Observed identity and sources

Joseph D. Sloan, O'Reilly, first edition.
A scan's printing history gives August 2001. The existing canon gives September 2001.
ISBN-10: 059600186X. ISBN-13: 9780596001865.
The supplied 364-page extent and scan's 366 PDF pages use different pagination.
Do not infer a different edition from PDF page count.
O'Reilly search results identify the catalog. Direct fetch access fails.

## Diagnostic chapter evidence

The scan and public catalog excerpts support these relevant chapters:

- Chapter 3: Connectivity Testing.
- Chapter 4: Path Characteristics.
- Chapter 5: Packet Capture.
- Chapter 8: Performance Measurement Tools.
- Chapter 10: Application-Level Tools.
- Chapter 12: Troubleshooting Strategies.

The preface describes information collection, normal-behavior baselines, and combined tools.
A contemporary Linux Journal review describes path asymmetry, throughput, capture, and application diagnosis.
The review also notes little routing discussion and no real-world case studies.
The returned brief does not give all 12 chapter titles.

## Proposed bench techniques — inferences

1. Measure an idle baseline before load. Keep RTT, variation, loss, and counter evidence for comparison.
2. Separate reachability probes, path observations, and TCP evidence.
   Sloan names ping, traceroute, and capture. Modern MTR/AS-path rules require separate sources.
3. Compare throughput with RTT and loss for each destination and load state.
4. Use a bounded capture to inspect stalls and sequence behavior.
   The historical text uses tcpdump and Ethereal. Check current Wireshark procedures before use.
5. Check service behavior as well as host reachability.
   Keep DNS and connect timing separate from sustained object-store goodput.

Example: a host can answer a probe while its artifact download fails.
Application-path evidence checks the service that the tenant actually uses.

## Canon verdict

Change blanket SKIP to optional method SKIM. Keep Sloan off the spine.
Chapter 4 and chapter 12 give a stronger method reason than a list of old commands.
Do not claim unique modern diagnostics or move Sloan above current tooling sources.
The existing 'every tool covered newer' explanation overstates the case for complete exclusion.

## Gaps

- Direct publisher catalog access fails.
- The scan is secondary evidence. Google Books and the independent review support the bounded method verdict.
- Full command correctness on current Linux does not form part of this review.
- Sloan does not establish S3/R2/GCS certification, modern CC, AS-path interpretation, or quantitative PASS gates.

## Sources

- [O'Reilly catalog](https://www.oreilly.com/library/view/network-troubleshooting-tools/059600186X/).
- [Google Books](https://books.google.com/books/about/Network_Troubleshooting_Tools.html?id=VyZTAAAAMAAJ).
- [Linux Journal review](https://www.linuxjournal.com/article/4894).
- Secondary scan reported by researcher: http://www.nylxs.com/docs/networktroubleshootingtools.pdf
- Local comparison: `.lavish/internet-research/books.md`, Network Troubleshooting Tools and Skip list.

Dropped: generic modern tool summaries and less detailed historical reviews.
