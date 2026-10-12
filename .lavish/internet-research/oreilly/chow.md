# N10 — Packet Analysis Using Wireshark

Research date: 2026-10-11. Researcher: oreilly-chow-N10.

## Observed identity and agenda

O'Reilly lists Ming Chow as instructor. Event ID: 0636920075846.
This product is a live event, not a book. ISBN does not apply.
The accessible pages do not show a specific date or recording availability.
The supplied 2025 date remains unverified.

The public agenda contains these sections:

- Packet analysis, basic networking, and Wireshark: 30 minutes.
- Reconstructing files: 20 minutes.
- Finding and verifying plain-text credentials: 20 minutes.
- Large-capture filtering and content discovery: 20 minutes.
- Malware traffic: 20 minutes.
- Wrap-up and Q&A: 10 minutes.

The agenda covers PCAP files, TCP handshakes, address filters, and domain discovery.
The agenda mainly covers security analysis, not internet-quality certification.
O'Reilly recommends Practical Packet Analysis, third edition, as follow-up reading.

## Proposed bench techniques — inferences

1. Keep a bounded PCAP for one authorized S3/R2/GCS transfer.
   Record the capture point, direction, endpoint, time, and run ID.
2. Filter the benchmark flow by its five-tuple. Check its TCP handshake and visible options.
3. Review sequence behavior when kernel counters show an anomalous transfer.
   A short capture cannot establish path-wide loss. Keep TCP_INFO and counter evidence.
4. Compare DNS answers with transfer destination addresses.
   Encrypted DNS can hide names. Use explicit resolver instrumentation when necessary.
5. Start capture analysis after an anomaly, or for one representative transfer.
   Do not remove sustained transfers or loaded-latency measurements to make time for capture training.

These checks apply agenda topics to rack-bench. The agenda does not teach these exact checks.
The event does not establish PMTUD, jitter, AS-path, or congestion-control methods.

## Canon verdict

Use this as an optional introduction. The event confirms Sanders's capture workflow but does not replace Sanders 3e.
Keep Gregg, Fall and Stevens, HPBN, and Jain as the four-book spine.

## Gaps

- Event date and recording availability remain unknown.
- No recording or exercises support detailed quality-measurement methods in this review.
- The agenda does not specify capture-drop accounting or statistically valid loss estimates.
- Protect captures from credentials and tenant data. Use only authorized test traffic.

## Sources and evidence check

- [Supplied Learning URL](https://learning.oreilly.com/live-events/-/0636920075846/?orm_source=mcp).
- [Public agenda](https://www.oreilly.com/live-events/packet-analysis-using-wireshark/0636920075846).
- Local canon: `.lavish/internet-research/books.md`, section 6; `docs/internet-quality-research.md`, Reading list.

The orchestrator fetches the public agenda. It checks the instructor, topics, times, and Sanders follow-up link.
The page does not show a date. No source proves current playback access.
