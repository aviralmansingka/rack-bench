# N09 — Wireshark 101: Packet Analysis Essentials

Research date: 2026-10-11. Researcher: oreilly-greer-N09.

## Observed product identity

Chris Greer teaches this Pearson video course.
O'Reilly catalog search evidence shows product ID 9780138240882 and the same title and instructor.
The supplied Learning URL fetch fails for the researcher.
InformIT lists a first-edition online video, copyright 2024, ISBN 9780138240936.
InformIT describes four hours of video instruction.
The supplied 2023 date and 233-minute runtime do not match this accessible record.
The two product identifiers can refer to different formats. Their relationship remains unverified.
This review does not check playback access.

## Published lessons

InformIT lists an introduction and Lessons 1–6.
Relevant named sections include:

- 1.2 Your First Packet Capture.
- 1.3 Where to capture on the network.
- 1.4 Lab: How to Capture Network Traffic.
- 1.5 Packet Capture Best Practices.
- 3.4 The TCP Header.
- Lesson 4: capture and display filters, TCP conversations, time filters, and packet export.
- Lesson 5: The Top Five Network Problems.
- 5.1 Lab: How to Identify Packet Loss.
- 5.2 Lab: Network Congestion Slows Applications.
- 5.4 Lab: Application Latency and Turns.
- 5.5 Lab: Protocol Problems TCP Issues.

The catalog describes downloadable trace files and assignments.
The researcher does not inspect those files or video lessons.
The note does not claim a complete subsection list.

## Proposed bench techniques — inferences

1. Record capture placement, interface, direction, timestamps, and capture-drop statistics.
   Lesson 1 covers placement and capture best practices.
2. Compare transfer retransmission evidence with kernel counters and throughput.
   Lessons 3 and 5 cover TCP headers, packet loss, and TCP issues.
3. Compare packet timing with idle and loaded latency.
   Lesson 5 names congestion and application latency, but gives no public threshold.
4. Save endpoint and time filters with exported packet evidence.
   Lesson 4 names conversation filters and packet export.
5. Use protocol inspection for anomalous transfers. Do not use it instead of measured loss or jitter.
   The public outline does not establish PMTUD or CUBIC/BBR measurement methods.

## Canon verdict

Use this as an optional practical supplement. Keep Sanders 3e as the packet-analysis book.
The named labs add guided practice. They do not replace the wider measurement canon.

## Gaps

- Direct Learning metadata and playback access remain unverified.
- O'Reilly ID 9780138240882 differs from InformIT ISBN 9780138240936.
- InformIT's four-hour description does not verify 233 minutes.
- The public outline does not establish jitter, mtr, AS-path, PeeringDB, PMTUD, or CC-pair checks.

## Sources

- [O'Reilly catalog](https://www.oreilly.com/videos/wireshark-101-packet/9780138240882).
- [InformIT course and lesson list](https://www.informit.com/store/wireshark-101-packet-analysis-essentials-video-course-9780138240936).
- [InformIT author profile](https://www.informit.com/authors/bio/9303e1d8-5c28-445a-b680-30372bee0f0c).
- Local comparison: `.lavish/internet-research/books.md`, section 6; `docs/internet-quality-research.md`, Reading list.

Dropped evidence: unrelated video descriptions and presumed recording content.
