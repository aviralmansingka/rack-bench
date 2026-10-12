# Staged reading-list update

Research date: 2026-10-11.
Publication target: `docs/internet-quality-research.md`, `## Reading list`.
The parent publishes this change. The orchestrator leaves the project document unchanged.
The replacement below keeps the four-book spine and adds selected supplements.

## Replacement text

```markdown
## Reading list

`.lavish/internet-research/books.md` keeps the ranked eight and the four-book internet-bench spine:

1. **Gregg, Systems Performance, second edition:** methodology; Chapters 2, 10, and 12.
2. **Fall and Stevens, TCP/IP Illustrated, Volume 1, second edition:** TCP options, retransmission, windows, congestion control, and PMTUD.
3. **Grigorik, High Performance Browser Networking:** free text at https://hpbn.co/; Chapters 1–2 for latency and BDP.
4. **Jain, The Art of Computer Systems Performance Analysis:** statistics and experimental design for measured PASS decisions.

Keep Sanders's Practical Packet Analysis, third edition, as the main practical capture supplement.
The publisher confirms Chapters 6, 8, and 11 for CLI analysis, transport, and slow-network diagnosis.
Use current Wireshark documentation for classifier rules. Its labels alone do not prove wire loss or an RTO.

The 15-source catalog supplement lives at `.lavish/internet-research/oreilly.md`.
Selective additions:

- DNS and BIND, fifth edition: Chapters 2, 6, and 12–14 for resolver behavior and DNS fault evidence.
- DNS and BIND on IPv6: Chapters 1 and 5; Chapter 4 only when DNS64 applies.
- Pro DNS and BIND: optional DNS background. Its separately titled 2011 BIND 10 book is not a verified second edition.
- Content Delivery Networks: Chapters 2–4 for request routing, goodput, object size, and latency context.
- Sloan, Network Troubleshooting Tools: optional method SKIM of Chapters 4 and 12, not blanket SKIP.
- Schroder, Linux Networking Cookbook: new optional Chapter 19 SKIM, separate from Sloan's book.
- Nath's packet-analysis book and Greer's video: optional practice, not Sanders replacements.
- Chow's event: optional introduction. White's event: optional troubleshooting-method training.
- VandenBrink, Linux for Networking Professionals, second edition: HOLD until release dates and complete contents agree.

Catalog visibility does not prove entitlement to full text or recordings.
Use current configuration, tool, and protocol documents before you use old recipes.
No catalog source proves rack performance or a new PASS threshold.

Read the modern web set alongside the spine.
Read BBR's ACM Queue paper and Making Linux TCP Fast.
Read RFCs 6349, 7323, 9000, 6298, 1191, and 4821.
Read current CUBIC guidance, tcp(7), ss(8), and current ip-sysctl documentation.
Use current IPv6 and DNS transport guidance for applicable checks.
```

## Additional required correction: BDP sentence

Location: `docs/internet-quality-research.md:57–64`, the Window/BDP failure-mode bullet.
The current text says a 750 MB window is structurally impossible for one flow.
[RFC 7323, Sections 2.2–2.3](https://www.rfc-editor.org/rfc/rfc7323) contradicts that claim.
Use this replacement bullet:

```markdown
- **Window/BDP constraints mistaken for slow internet.** At 25 Gbps and 250 ms RTT, BDP equals 781.25 MB decimal.
  This is an example calculation, not a Chennai measurement.
  RFC 7323 permits a maximum encoded receive window of 1,073,725,440 bytes. This value exceeds this BDP.
  Thus, TCP's protocol window maximum does not inherently prevent one flow from meeting this example target rate.
  Negotiated scaling, socket buffers, receive window, congestion window, and path conditions affect actual throughput.
  A configured tcp_wmem maximum alone does not prove a throughput ceiling for one flow.
  2h: **yes** — record live settings and flow state; measure one-flow and parallel-flow rates separately.
  Calculate BDP from measured RTT. Keep host constraints separate from measured path constraints.
  Sources: books §4; RFC 7323 §§2.2–2.3; tcp(7); current ip-sysctl documentation.
```

A hypothetical 4 MiB effective flight limit at 250 ms gives approximately 134.2 Mbps.
Do not equate that effective flight limit with a configured `tcp_wmem` maximum.

## Additional publication review flags

These flags remain outside the reading-list replacement. The parent decides the broader document changes.

1. `docs/internet-quality-research.md:119–122`: the RTO-heavy bullet makes an automatic fail-side claim.
   The book review supports investigation. It does not support a quantitative automatic FAIL threshold.
   Fast-recovery symptoms do not uniquely prove single-packet loss. Use current counter definitions and the certification profile.
2. `docs/internet-quality-research.md:123–126`: DSACK evidence does not uniquely identify reordering.
   Duplicate receipt can have several causes. Keep sequence evidence, capture conditions, and independent counters.
3. `docs/internet-quality-research.md:216–219`: endpoint names do not prove physical CDN cache location.
   Do not treat an R2 auto endpoint as measured proof of a Chennai cache.
4. The existing modern web set cites historical RFC 8312 for CUBIC.
   Use current CUBIC guidance for present behavior. The catalog review does not re-audit that separate web set.

Do not publish these flags as new measured findings.

## Evidence links

- [Supplement](../oreilly.md).
- [Updated canon](../books.md).
- [HPBN correction](hpbn.md).
- [TCP/IP identity correction](tcpip.md).
- [Sanders and Wireshark limits](ppa.md).
- [DNS edition and contents](dns-bind.md).
- [Sloan reconsideration](sloan.md).
- [Schroder's separate identity](cookbook.md).
