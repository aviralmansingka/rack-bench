# N12 — Linux Networking Cookbook

Research date: 2026-10-11. Researcher: oreilly-cookbook-N12.

## Observed identity and evidence correction

Carla Schroder, O'Reilly. ISBN 9780596102487.
A third-party copy's front matter gives copyright 2008 and first printing November 2007.
Use 2007/2008 dates with this distinction. No newer Schroder edition appears in the checked sources.
A different same-title book uses ISBN 9781785287916. It does not prove a Schroder revision.

The researcher's first reply incorrectly treats Schroder as an existing SKIP entry.
The corrected reply confirms that books.md's SKIP entry concerns Sloan, not Schroder.
Treat Schroder as a new candidate.

## Chapter 19 evidence

O'Reilly public search evidence identifies Chapter 19, Troubleshooting Networks.
Direct catalog and chapter fetches fail. Detailed section evidence comes from the third-party copy.

- 19.0 Introduction.
- 19.1 Building a Network Diagnostic and Repair Laptop.
- 19.2 Testing Connectivity with ping.
- 19.3 Profiling Your Network with FPing and Nmap.
- 19.4 Finding Duplicate IP Addresses with arping.
- 19.5 Testing HTTP Throughput and Latency with httping.
- 19.6 Using traceroute, tcptraceroute, and mtr to Pinpoint Network Problems.
- 19.7 Using tcpdump to Capture and Analyze Traffic.
- 19.8 Capturing TCP Flags with tcpdump.
- 19.9 Measuring Throughput, Jitter, and Packet Loss with iperf.
- 19.10 Using ngrep for Advanced Packet Sniffing.
- 19.11 Using ntop for Colorful and Quick Network Monitoring.
- 19.12 Troubleshooting DNS Servers.
- 19.13 Troubleshooting DNS Clients.
- 19.14 Troubleshooting SMTP Servers.
- 19.15 Troubleshooting a POP3, POP3s, or IMAP Server.
- 19.16–19.17 SSL-key creation for Syslog-ng on Debian and Fedora.
- 19.18 Setting Up stunnel for Syslog-ng.
- 19.19 Building a Syslog Server.

Sections 19.2–19.9 and 19.12–19.13 have the closest internet-bench fit.
Mail and logging administration do not improve sustained object-store certification.
The returned brief does not supply a full book-wide chapter list.

## Proposed bench techniques — inferences

1. Keep MTR/traceroute output for each endpoint. A silent intermediate hop does not prove end-to-end loss.
2. Keep sustained transfer rate with latency, jitter, loss, destination, and interval metadata.
   iperf supplies a diagnostic precedent, not the S3/R2/GCS workload.
3. Use bounded captures and explicit resolver queries when a transfer fails.
   These checks isolate symptoms. The book does not set PASS thresholds.

## Canon verdict

New optional Chapter 19 SKIM. Do not change the four-book spine.
The direct MTR and HTTP-timing coverage offers a useful historical checklist.
Use current tool documents before any old command or configuration recipe.

## Gaps

- Full publisher TOC and detailed Chapter 19 headings remain inaccessible.
- Secondary copy evidence supports exact section names, not present-day command correctness.
- No definitive publisher statement excludes a newer edition.
- No bench measurement, current command validation, or certification method follows from this catalog review.

## Sources

- [O'Reilly catalog](https://www.oreilly.com/library/view/linux-networking-cookbook/9780596102487).
- [O'Reilly chapter record](https://www.oreilly.com/library/view/linux-networking-cookbook/9780596102487/ch19.html).
- [Different same-title record](https://www.oreilly.com/library/view/linux-networking-cookbook/9781785287916).
- Secondary copy: https://www.lions-wing.net/lessons/networking-1/schroder_-_linux_networking_cookbook_oreilly_2008.pdf
- Local comparison: `.lavish/internet-research/books.md`, Sloan section.
