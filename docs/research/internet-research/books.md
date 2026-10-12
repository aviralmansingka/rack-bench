# Canonical books for diagnosing internet quality: the ranked reading order for a certification bench

Research date: 2026-10-11. O'Reilly supplement: [oreilly.md](oreilly.md).
The supplement checks 15 catalog sources and records access limits.
Keep observed facts, calculations, and proposed bench checks separate.

Scope: the books that make an engineer good at *diagnosing internet
quality* on a datacenter node. These books serve the `bench internet`
track of rack-bench.

The track certifies north-south throughput to public object stores (S3,
R2, GCS). It also certifies idle and loaded latency, jitter, packet
loss, and path audit (mtr, AS paths). It also certifies DNS and TCP
health (retransmits, PMTUD blackholes, congestion-control behavior).

The rack sits in Chennai, India. The certification window is ~2 hours.
PASS means measured, never vendor-claimed.

Companion brief in this research base: the sibling storage-track book
canon (`/home/avirus/rack-bench/.lavish/storage-research/books.md`).
This brief mirrors that canon in format.

The original canon checks sources in October 2026. The supplement adds bounded catalog checks and explicit gaps.
Several direct publisher fetches fail. Do not read catalog presence as proof of subscription entitlement.
The source notes separate observed facts, calculations, and proposed bench checks.

## TL;DR: the ranked reading order (8 books)

| #  | Book                                                                | Edition / year      | Cost  | One-line role                                                        |
|----|---------------------------------------------------------------------|---------------------|-------|----------------------------------------------------------------------|
| 1  | *Systems Performance* -- Brendan Gregg                              | 2nd ed., 2020       | paid  | Certification methodology: USE, latency outliers, ch. 10 Network     |
| 2  | *TCP/IP Illustrated, Vol. 1* -- Fall & Stevens                      | 2nd ed., 2011/2012  | paid  | The diagnostic reading of retransmits, RTO, SACK, PMTUD, congestion  |
| 3  | *High Performance Browser Networking* -- Ilya Grigorik              | 2013, free online   | free  | BDP math, TCP tuning, measuring RTT/bandwidth from the application   |
| 4  | *The Art of Computer Systems Performance Analysis* -- Raj Jain      | 1991, in print      | paid  | The statistics of pass/fail: variance, CIs, comparing alternatives   |
| 5  | *BPF Performance Tools* -- Brendan Gregg                            | 2019                | paid  | Kernel-event evidence beyond counters: retransmit/drop/RTT tracing   |
| 6  | *Practical Packet Analysis* -- Chris Sanders                        | 3rd ed., 2017       | paid  | Reading retransmissions, dup-ACKs, zero-window from a live capture   |
| 7  | *UNIX and Linux System Administration Handbook* -- Nemeth et al.    | 5th ed., 2017       | paid  | Sysadmin tool discipline: ping/traceroute/tcpdump/SmokePing/dig      |
| 8  | *Computer Networking: A Top-Down Approach* -- Kurose & Ross         | 8th ed., 2021       | paid  | The academic baseline; 8e adds BBR/QUIC; skim only                   |

Phases: #1 methodology, #2 protocol ground truth, #3 free measurement
math, #4 benchmark statistics, #5-6 evidence-gathering tools. #7-8 cover
ops context and the classroom fallback. Three of the eight (Grigorik,
plus the Kurose Wireshark labs and the RFC set) are free or
free-online.

The final section gives the 4-book spine for the internet track. This
spine runs parallel to the storage spine of Gregg / Jain / OSTEP /
TOS'08. The spine:

**Gregg *Systems Performance* 2e + Fall & Stevens *TCP/IP Illustrated* Vol. 1 2e
+ Grigorik *HPBN* (free) + Jain.**

---

## Part 1 -- Methodology and statistics

### 1. Systems Performance: Enterprise and the Cloud (2nd ed.)

- Author / edition / year: Brendan Gregg (Netflix/Intel performance
  engineer). **2nd edition, Addison-Wesley, 2020**, 928 pp., ISBN
  978-0-13-682015-4. The checked author and publisher pages show no third-edition announcement.
  InformIT gives copyright 2021: <https://www.informit.com/store/systems-performance-9780136820154>.
  The 2nd ed.
  adds perf/Ftrace/BPF chapters and largely drops Solaris. The author's
  site verifies this: <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>
  (TOC: 1 Intro, 2 Methodology, 3 OS, 4 Observability Tools, 5
  Applications, 6 CPUs, 7 Memory, 8 File Systems, 9 Disks, **10 Network**,
  11 Cloud, 12 Benchmarking, 13 perf, 14 Ftrace, 15 BPF, 16 Case Study)
- Chapters that teach internet-quality diagnosis: **ch. 2 Methodology**,
  **ch. 10 Network**, and **ch. 12 Benchmarking**. The methodology
  chapter covers the USE method, workload characterization, and latency
  analysis -- distributions and outliers, not averages.
  InformIT confirms Chapter 10 sections on methodology, observability, experimentation, and tuning.
  Its public TOC does not verify a lower-level tool inventory.
  The following slides supply separate tool evidence. They do not prove the second-edition chapter's exact contents.
  Gregg's own USE-for-TCP framing appears in his slides:
  <https://www.brendangregg.com/Slides/MacIT2014_Analyzing_OSX_Perf_USE_Method.pdf>.
  The framing treats TCP as a software resource. It reads use /
  saturation / errors from `netstat -s`. Note: over 50 TCP metrics live
  in `netstat -s`. They include retransmitted data packets, resends
  started by MTU discovery, duplicate ACKs, window updates. His tool
  walkthroughs show `ss -i` printing per-socket
  `cubic wscale:6,6 rto:208 rtt:9/6 ato:40 cwnd:10`:
  <https://www.brendangregg.com/Slides/Velocity2015_LinuxPerfTools.pdf>.
- Port these techniques from this book into rack-bench:
  1. **USE-method counters as a delta check.** Snapshot `netstat -s`
     (or `nstat`) before and after each 2-hour cert window. Report
     deltas: segments retransmitted / data packets sent, TCP timeouts,
     listen-queue drops, resets received. This is the Gregg discipline
     of checking Errors and Saturation, not just throughput.
  2. **`ss -ti` per-socket reading during the S3/R2/GCS transfer.** Log
     cwnd, rtt/rttvar, retrans count, pacing rate, and the active
     congestion-control algorithm per flow. Gregg treats `ss` as the
     intermediate-level lens on the same sockets the benchmark owns.
     (Observed fact: `ss -i` exposes exactly these fields.)
  3. **Latency-outlier analysis (ch. 2).** Report p50/p99/p999 of RTT and
     TTFB with histograms, not means. Gregg's performance goal is
     explicitly "reducing latency outliers."
  4. **Active benchmarking (ch. 12).** While the throughput test runs,
     verify with `ss`/`ethtool -S`/`ip -s link` that the bottleneck is
     the path. Rule out local NIC errors, zero-window from the bench's
     own receiver, and kernel drops. Otherwise the cert measures the
     harness, not the internet.
  5. **Static performance tuning check.** Before certifying, read the
     kernel's TCP sysctls (`ip-sysctl`), NIC offloads, and ring sizes.
     Record them in the report so a PASS is reproducible.
- Verdict: **MUST** -- rank #1; the methodology backbone, exactly as in
  the storage track. Here, read ch. 10 in place of chs. 8-9.

### 2. The Art of Computer Systems Performance Analysis

- Author / edition / year: Raj Jain, Wiley, Sept 1991, 720 pp., ISBN
  978-0-471-50336-1. Wiley publishes no revision. The book stays in print.
  The book is the benchmarking statistics bible. It already forms the
  spine of the storage bench. Author's book page and full chapter list:
  <https://www.cse.wustl.edu/~jain/books/perfbook.htm>.
  Chapter-indexed slides: <https://www.cse.wustl.edu/~jain/books/perf_sli.htm>.
- What it adds for *network* measurement specifically:
  1. **Summarizing and comparing (chs. 12-13).** Confidence intervals on
     mean throughput/latency from N runs. Comparing two nodes or two
     windows with sample data. This is the math behind
     "PASS means measured."
  2. **Ratio games (ch. 11).** Jain's famous warning applies directly to
     vendor egress claims. A vendor can present the same measurement as
     a favorable ratio by choosing the baseline. Report absolute numbers
     plus CIs in the cert report.
  3. **Outlier and variance discipline.** Jain's treatment of outliers
     and of variance in measured data is the honest basis for our
     storage-bench "N-run discard-average" habit. Note: that discard
     rule is *our* port, not Jain's terminology. His actual material is
     outlier treatment plus confidence intervals. (Observed fact from
     the chapter list; the port is our inference.)
  4. **Experimental design (chs. 16-23).** A 2-hour cert window across
     three object stores is a factorial problem: destination x time-of-day
     x parallelism. Jain's 2^k factorial chapters tell you how many runs
     each check needs to separate destination effects from noise.
  5. **Variance reduction (simulation part, chs. 24-29).** For
     measurement (not simulation), Jain's practical answer is more
     samples / longer windows / paired designs. Use this answer when
     sizing the idle-latency soak inside the 2-hour window.
- Verdict: **MUST** -- rank #4; carried over from the storage spine
  unchanged. The examples are pre-Linux but the math is timeless.

---

## Part 2 -- Protocol ground truth

### 3. TCP/IP Illustrated, Volume 1: The Protocols (2nd ed.)

- Author / edition / year: W. Richard Stevens is the author of the
  original. Kevin R. Fall is the author of the revision. **2nd edition, Addison-Wesley, first printing Nov 2011
  (© 2012), 1,059 pp., ISBN 978-0-321-33631-6.** Keep this second edition as the protocol reference.
  Pearson supplies the primary TOC:
  <https://www.pearson.com/en-us/subject-catalog/p/Fall-TCP-IP-Illustrated-Volume-1-The-Protocols-2nd-Edition/P200000000242?view=educator>.
  O'Reilly lists it under 9780132808200, with a 1,056-page catalog extent:
  <https://www.oreilly.com/library/view/tcp-ip-illustrated-volume/9780132808200>.
  Keep record-specific extents and identifiers separate.
  The supplied platform identifier 020163354X names the 1995 implementation volume, not Fall's revised Volume 1.
- The chapters that teach internet-quality diagnosis (observed from the
  TOC): **ch. 10 UDP and IP Fragmentation** (sec. 10.7 IP fragmentation,
  10.8 Path MTU Discovery with UDP). **ch. 11 DNS** (resolver behavior,
  caching, message format). **ch. 13 TCP Connection Management**: sec
  13.3 TCP options (MSS, SACK, window scale, timestamps). Sec 13.4
  PMTUD with TCP; sec 13.5 state transitions; sec 13.6 resets. **ch. 14
  TCP Timeout and Retransmission**: 14.3.1 classic RTO; 14.3.2 standard
  method [RFC 6298]; 14.3.3 the Linux method. The chapter also covers
  14.4 timer-based retransmission, 14.5 fast retransmit, and 14.6
  SACK-based recovery. It also covers 14.7 spurious timeouts: DSACK,
  Eifel, F-RTO; and 14.8 packet reordering. **ch. 15 TCP Data Flow and
  Window Management**: 15.3 delayed ACK, 15.4 Nagle. The chapter also
  covers 15.5.2 zero windows and the persist timer, and 15.5.4 large
  buffers and auto-tuning. **ch. 16 TCP Congestion Control**: 16.2
  classic slow start / AIMD / Tahoe / Reno; 16.3 NewReno and SACK. The
  chapter also covers 16.5 an extended worked example of a lossy
  transfer, and 16.8.2 BIC and **CUBIC**. It further covers 16.9
  delay-based: Vegas/FAST, 16.10 **bufferbloat**, and 16.11 AQM and
  ECN.
- Attribution fix: the common claim that "Stevens/Fall pre-dates CUBIC
  being the Linux default" is wrong for the 2nd edition. The Linux
  change record shows the default congestion control switching to CUBIC
  in kernel 2.6.19 (2006). The
  2011 second edition already covers CUBIC in sec. 16.8.2 (observed
  fact from the TOC). The CUBIC RFC confirms the Linux-default history:
  <https://www.rfc-editor.org/rfc/rfc8312>. The 2e genuinely pre-dates
  **BBR** (2016; in Linux since 4.9) and **QUIC** (RFC 9000, 2021).
  Read instead for those: the BBR paper in ACM Queue
  (<https://queue.acm.org/detail.cfm?id=3022184>). Also read "Making Linux TCP
  Fast" from netdev 2.1
  (<https://netdevconf.org/2.1/papers/brakmo.pdf>). Also read RFC 9000
  (<https://www.rfc-editor.org/rfc/rfc9000>). The 1994 first edition
  pre-dates everything modern. Buy the 2e.
- Port these techniques from this book into rack-bench:
  1. **RTO-vs-loss inference (ch. 14).** Classify retransmit events:
     fast-recovery evidence versus timeout-driven evidence.
     Neither category alone proves a unique loss pattern or fault severity. Fall shows
     the classic vs standard vs Linux estimators. The bench port reads
     kernel counters for timeout-driven retransmits separately from fast-recovery evidence.
     An RTO-heavy window requires investigation. The book does not establish an automatic FAIL threshold.
     Check current counter definitions before use. These bench checks are inferences from Chapter 14.
  2. **Duplicate-receipt evidence via DSACK (sec. 14.7).** DSACK reports duplicate receipt.
     Reordering or a spurious retransmission can explain that evidence, but DSACK alone does not prove the cause.
     Compare sequence evidence, capture conditions, and DSACK-related counters before causal conclusions.
  3. **TCP-options sanity on the SYN (sec. 13.3).** Check MSS,
     SACK-permitted, window scale, and timestamps on the bench's own
     connections. *Both* ends must negotiate them. A connection without
     window scaling cannot exceed a 64 KB window. That connection is
     structurally throughput-capped (calculation: 64 KB / 0.25 s ≈ 2
     Mbps).
  4. **PMTUD and blackhole reading (sec. 13.4, 10.8).** PMTUD's failure
     mode: ICMP "fragmentation needed" filtered -> retransmit stalls.
     The bench port is the classic probe: send DF-set packets at
     decreasing sizes and confirm the effective path MTU. Count
     "resends initiated by MTU discovery" as a first-class metric.
  5. **Bufferbloat signature (sec. 16.10).** Loaded RTT inflation
     *without* proportional loss = queue buildup somewhere on the path.
     The bench port: measure idle RTT, then RTT under the full egress
     load. FAIL or WARN on large inflation even when throughput
     passes. This single check separates "fast pipe" from "good
     internet."
  6. **The ch. 16.5 worked example** is the model for the cert report
     format. It shows a timeline of one transfer. The timeline marks
     slow-start exit, each loss event, and each cwnd change. Our
     per-flow `ss -ti` log should tell the same story.
- Verdict: **MUST** -- rank #2. This is the reference a certifier reads
  twice and then keeps open while writing TCP-health checks.

### 4. High Performance Browser Networking

- Author / edition / year: Ilya Grigorik (Google web-performance
  engineer, W3C co-chair). O'Reilly, 2013, ISBN 978-1-4493-4476-4.
  The publisher's errata record supports this ISBN:
  <https://www.oreilly.com/catalog/errata.csp?isbn=9781449344764>.
  The public platform record uses 9781449344757:
  <https://www.oreilly.com/library/view/high-performance-browser/9781449344757/>.
  The checked errata record does not explicitly identify the ISBN's format.
  **The full text is free and legally online at <https://hpbn.co/>**
  under CC BY-NC-ND 4.0 (verified on the site: "Copyright © 2013 Ilya
  Grigorik. Published by O'Reilly Media").
  The checked sources show no authoritative newer-edition announcement.
- The chapters that teach internet-quality diagnosis: **ch. 1 "Primer on
  Latency and Bandwidth"** (the components of latency: propagation,
  transmission, queueing, processing; last-mile vs core; the
  speed-of-light floor). **ch. 2 "Building Blocks of TCP"** (three-way
  handshake, slow start and initial cwnd, flow control vs congestion
  control, **bandwidth-delay product**, head-of-line blocking). The
  chapter also covers tuning server configuration: TCP options, socket
  buffers, keep-alive, and a performance checklist. The book adds ch.
  4 on TLS handshake/session costs and the HTTP chapters on connection
  reuse.
- Port these techniques from this book into rack-bench:
  1. **The BDP formula and its throughput ceiling** (observed from ch.
     2: throughput = window / RTT). Port as a computed expectation in
     every cert report: window_needed_bits = link_bps x RTT_s.
     Example calculation: 25 Gbps at 5–10 ms RTT gives 15.625–31.25 MB BDP.
     At 250 ms, BDP equals 781.25 MB decimal, or approximately 745.1 MiB.
     These RTT values are example inputs, not rack measurements.
     RFC 7323 permits shift count 14: <https://www.rfc-editor.org/rfc/rfc7323>.
     The largest encoded receive window equals 65,535 × 2^14 = 1,073,725,440 bytes.
     That maximum exceeds this example BDP. One flow is not inherently below line rate because of this protocol limit.
     Actual throughput depends on negotiated scaling, socket buffers, receive window, congestion window, and path conditions.
     BDP alone does not prove a need for parallel flows.
  2. **Actual-buffer constraint check.** Record live settings and per-flow state. Do not assume universal Linux defaults.
     Check current `ip-sysctl` documentation:
     <https://www.kernel.org/doc/html/latest/networking/ip-sysctl.html>.
     A hypothetical 4 MiB effective flight limit at 250 ms gives approximately 134.2 Mbps.
     A configured `tcp_wmem` maximum alone does not prove that effective flight limit.
     Keep buffer constraints separate from measured path constraints.
     Reference: <https://man7.org/linux/man-pages/man7/tcp.7.html>.
  3. **Object size chosen by BDP, not convenience (ch. 2 slow start).**
     Slow start begins with initial cwnd 10. A transfer must push
     roughly a BDP-multiple of bytes to reach steady state. Port as:
     minimum test object size per destination = f(link rate, RTT). A
     "5 MB object
     to us-east-1" test can never certify anything about line rate.
  4. **Latency decomposition from the application side.** Port as the
     fetch-timeline breakdown: DNS time, TCP connect (1x RTT), TLS
     handshake, time-to-first-byte, transfer. This is Grigorik's
     breakdown. Timing instrumentation around the object-store client
     supports it directly.
  5. **Keep-alive / connection reuse vs fresh connections.** Port as a
     paired check. Compare sustained transfer over a warm connection
     with the cost profile of per-object fresh connections (handshake +
     TLS). This matters because S3/R2/GCS clients differ in pooling
     behavior.
- What has aged (observed from the free text): everything protocol-side
  stops at HTTP/2-over-TCP and TLS 1.2-era handshakes. The book has no
  BBR, no QUIC, no HTTP/3. The mobile chapters describe LTE and RRC
  state machines of the 2013 era. SPDY-era history.

  What is still current: the entire latency primer, BDP math, TCP
  tuning basics, and the measurement mindset. Read it free at hpbn.co.
  Read RFC 9000 and the BBR paper alongside.
- Verdict: **MUST** (free) -- rank #3. It is the fastest way to BDP
  intuition, and the free counterpart to the paid spine.

---

## Part 3 -- Evidence-gathering tools

### 5. BPF Performance Tools: Linux System and Application Observability

- Author / edition / year: Brendan Gregg, Addison-Wesley, 2019, ISBN
  978-0-13-655482-2. Book site with TOC:
  <https://www.brendangregg.com/bpf-performance-tools-book.html>. The
  networking content is **ch. 10 "Networking"** within Part II. Part II
  covers 10 CPUs, 7 Memory, 8 File Systems, 9 Disk I/O, **10
  Networking**, 11 Security, ... The book covers over 150 BPF tools.
- What TC/packet/TCP-state probes add beyond counters. Sources: the
  book's tool set and the bcc tool inventory,
  <https://github.com/iovisor/bcc>. The bcc networking tools include
  `tcpretrans` (trace retransmits and TLPs) and `tcpdrop` (kernel-based
  TCP packet drops with reasons). They also include `tcprtt` (RTT
  distribution) and `tcpstates` (session state-change durations). They
  further include `tcpconnlat` (active-connect latency), `tcplife`,
  `tcptop`, and `tcpcong` (congestion-control state duration). The
  tools also include `tcpsynbl` (SYN backlog), `tcpsubnet`, and
  `gethostlatency` (DNS resolution latency).

  The difference vs counters: **per-event attribution with timestamps,
  cause codes, and socket state**. A cumulative retransmit counter says
  "loss happened". A `tcpdrop` / `tcpretrans` trace says which flow,
  which state, which cause, when.
- Port these techniques from this book into rack-bench. Use them as an
  optional eBPF debug mode for nodes that permit loading BPF programs:
  1. **`tcpretrans` during the loaded window**: record retransmit
     events with kernel state and flags. Correlate them against the
     throughput timeline.
  2. **`tcpdrop`**: distinguish drops that never become retransmits
     (e.g., out-of-order queue prune) from loss-triggering drops.
     Counters cannot give that nuance.
  3. **`tcprtt` / `tcpsynbl` / `tcpconnlat`**: RTT histogram from the
     kernel's own estimator. Check SYN backlog saturation. Check
     connect-latency distribution to each object-store endpoint. These
     checks give the egress-path health signal beyond ICMP.
  4. **`tcpcong`**: time spent per congestion-control state per flow.
     This is direct evidence for the "congestion-control behavior"
     check. Ask: is the flow in CUBIC recovery constantly? Is BBR
     available?
- Verdict: **MUST-lite** -- rank #5; read ch. 10 only. The tools
  require kernel privileges. The cert may not always have those
  privileges. Design checks to degrade gracefully to `ss`/`nstat`.

### 6. Practical Packet Analysis: Using Wireshark to Solve Real-World Network Problems (3rd ed.)

- Author / edition / year: Chris Sanders (security researcher,
  author of *Applied Network Security Monitoring*). **3rd edition, No
  Starch Press, April 2017, 368 pp., ISBN 978-1-59327-802-1**,
  <https://nostarch.com/packetanalysis3>. The edition updates the
  content for Wireshark 2.x. It adds IPv6/SMTP coverage and a
  tcpdump/TShark command-line chapter. That chapter is relevant since
  rack-bench is a CLI.

  **No authoritative fourth-edition listing appears in the checked sources.**
  The third-edition publisher page remains the checked current listing. Edition history: 1e May 2007 (192 pp.),
  2e 2011. The open PDF copies verify both ISBNs:
  <https://nostarch.com/releases/practical_packet_analysis_release.pdf>
  and <https://repository.root-me.org/Reseau/EN%20-%20Practical%20packet%20analysis%20-%20Wireshark.pdf>.
- The publisher confirms Chapter 6, Packet Analysis on the Command Line.
  It confirms Chapter 8, Transport Layer Protocols, and Chapter 11,
  Fighting a Slow Network. Detailed classifier rules need current
  Wireshark documentation:
  <https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html>.

  Wireshark processes packets in capture order. Its TCP labels are
  heuristic evidence, not direct proof of wire loss. The
  fast-retransmission classifier uses several conditions, including a
  last-ACK interval below 20 ms. That timing condition alone does not
  prove an RTO or a fast-retransmit mechanism.

  Record capture position, dropped packets, tool version, preferences,
  and offloads. Check sequence evidence and independent kernel counters
  before causal conclusions.
- Port these techniques from this book into rack-bench:
  1. **TShark symptom summaries.** Keep separate TCP analysis labels during the loaded window.
     Compare retransmission, out-of-order, and zero-window evidence with independent counters.
     Do not infer timeout cause from a generic retransmission label.
  2. **Classifier limits.** Do not turn the 20 ms condition into a universal TCP rule or loss threshold.
  3. **Zero-window attribution.** Identify the endpoint that advertises the zero window for each direction.
     Downloads can expose bench-host receive constraints. Uploads can expose remote receive constraints.
     A zero window does not itself prove a path fault.
  4. **Baseline comparison.** Store an idle-window reference capture's
     summary and diff loaded-window metrics against it.
  5. **Timing separation.** Keep handshake timing separate from request-to-first-byte timing.
     Request-to-first-byte timing includes path, protocol, and service effects. One endpoint capture does not prove pure server processing time.
- Verdict: **MUST-lite** -- rank #6. It is the cheapest rigorous
  on-ramp to capture-based diagnosis. It pairs with Fall & Stevens for
  the "why" of every expert-info line.

### 7. Wireshark Network Analysis (2nd ed.) -- alternate, not ranked

- Laura Chappell, *Wireshark Network Analysis: The Official Wireshark
  Certified Network Analyst Study Guide*, 2nd edition. Chappell
  University, 2012, ISBN 978-1-8939-9494-3, ~500 pp. The book includes
  49 case studies ("Death by Database", etc.). Publisher page with TOC
  and preview pages: <https://www.chappell-university.com/studyguide>.
- Uniquely covers: deeper Wireshark operation than Sanders (custom
  profiles, advanced IO graphs, expert-config tables). It also includes
  many worked performance case studies. The book shows its age:
  Wireshark 1.x-era UI. Some case-study protocols are dated.
- Verdict: **SKIM** as the deeper alternate to #6 if the bench team
  wants certified-level Wireshark fluency; not core.

---

## Part 4 -- The ops baseline and the academic baseline

### 8. UNIX and Linux System Administration Handbook (5th ed.)

- Author / edition / year: Evi Nemeth, Garth Snyder, Trent R. Hein, Ben
  Whaley, Dan Mackin, with James C. Zawodny and contributions. **5th
  edition, Addison-Wesley, 2017**, ISBN 978-0-13-427755-4; publisher
  site and full TOC PDF: <https://www.admin.com/> and
  <https://www.admin.com/samples/TOC.pdf>. (~1,180 pp; the checked
  sources show no 6th edition as of the research date.)
- The networking chapters (observed from the 5e TOC): **ch. 13 TCP/IP
  Networking** (p. 375): network troubleshooting (ping p. 429,
  traceroute p. 431, packet sniffers p. 434, tcpdump p. 435, Wireshark
  and TShark p. 436), network monitoring (SmokePing p. 437, iPerf p.
  437, Cacti p. 438), Linux TCP/IP sysctls (p. 422), cloud networking
  (AWS VPC, GCP); **ch. 15 IP Routing** (BGP section p. 490, routing
  daemons); **ch. 16 DNS** (resolver config, "debugging with query
  tools" p. 509, lame-delegation checks); **ch. 29 Performance
  Analysis** (perf, fio, sar).
- Attribution fix: the candidate list assumes an "mtr discipline" in
  this book. **mtr does not appear in the 5e TOC** (observed fact from
  the TOC PDF). The troubleshooting ladder is ping → traceroute →
  packet sniffer. The mtr-specific interpretation discipline must come
  from the traceroute/mtr man pages and the notes below, not from
  ULSAH. It combines ping statistics with traceroute path discovery.
  It treats intermediate 100%-loss hops that still forward traffic as
  non-responding routers.
- Port these techniques from this book into rack-bench:
  1. **The troubleshooting ladder as bench sequencing:** reachability
    (ping) → path (traceroute/mtr) → capture (tcpdump/tshark) → DNS
    (dig). This is the same order a NOC engineer trusts.
  2. **Traceroute-reading rules:** asymmetric paths. Per-hop loss that
     disappears at later hops = non-responding routers, not loss. Only
     destination-correlated loss is real. Port these into the mtr path
     audit's interpretation layer.
  3. **SmokePing-style idle statistics:** report ping/RTT distributions
     and loss over a soak window rather than one-off probes. Jitter and
     idle latency need time-series. SmokePing exemplifies them.
  4. **iPerf-style load discipline:** active throughput measurement
     with explicit client/server roles. The bench already does this via
     the object stores. This book documents the pattern and its
     pitfalls.
  5. **DNS debugging with dig:** record which resolver answers, its
     latency, and NXDOMAIN vs SERVFAIL vs delegation problems. Port
     ch. 16's query-tool discipline as the DNS check's evidence set.
- Verdict: **SKIM** -- rank #7. Read chs. 13 and 16 (and ch. 15's BGP
  pages) only. It is the ops frame, not the certification math.

### 9. Computer Networking: A Top-Down Approach (8th ed.)

- Author / edition / year: James F. Kurose and Keith W. Ross, Pearson,
  **8th edition, 2021**. US ed. ISBN 978-0-13-668155-7; global ed. ISBN
  978-1-292-405-51-3. Both come from the Pearson catalog and global
  edition preview: <https://www.pearson.com/en-us/subject-catalog/p/computer-networking/P200000003334/9780135928615>
  and <https://api.pageplace.de/preview/DT0400.9781292405513_A42098360/preview-9781292405513_A42098360.pdf>.
  The open PDF supplies the TOC:
  <https://ebooks.karbust.me/Technology/Computer%20Networking%20A%20Top-Down%20Approach,%208th%20Edition%20by%20James%20F.%20Kurose,%20Keith%20W.%20Ross-Pearson-9780136681557.pdf>:
  ch. 1 sec. 1.4 "Delay, Loss, and Throughput in Packet-Switched
  Networks" (nodal processing / queuing / transmission / propagation
  delay, queuing delay and loss, end-to-end delay, throughput), ch. 2
  DNS, ch. 3 transport (TCP, congestion control), and the per-chapter
  Wireshark labs. The 8e specifically adds BBR and QUIC coverage
  (observed from the global-edition preface text: "including the new BBR
  protocol deployed in Google's backbone network, and studies the QUIC
  protocol").
- What a certifier actually gains: the cleanest classroom model of
  delay and the bottleneck-link throughput law. This book gives the
  only *book* treatment of BBR and QUIC on this list. The free
  Wireshark labs are guided practice for capture reading.
- What it does not give: no measurement methodology, no statistics, no
  Linux tooling, no cert-shaped judgment. A certifier who reads Gregg
  ch. 2 + Fall & Stevens chs. 14-16 gains little beyond the delay model
  and the BBR/QUIC overview.
- Verdict: **SKIM** -- rank #8. It is the on-ramp for a team member
  without a networking background. It also serves as the BBR/QUIC
  primer until you read the primary sources. It is not part of the
  spine.

---

## Part 5 -- Evaluated and mostly rejected

### Network Algorithmics (2nd ed.)

- George Varghese and Jun Xu, *Network Algorithmics: An
  Interdisciplinary Approach to Designing Fast Networked Devices*, 2nd
  edition. Morgan Kaufmann/Elsevier, 594 pp., ISBN 978-0-12-809-927-8.
  Publisher page with full part/chapter list:
  <https://educate.elsevier.com/book/details/9780128099278>. UCLA CS
  announces the second edition:
  <https://www.cs.ucla.edu/george-varghese-releases-second-edition-of-his-book-network-algorithmics>.
- The measurement-relevant content (observed from the TOC): Part II ch.
  7 "Maintaining Timers" (timing wheels, hashed and hierarchical
  wheels) and Part IV ch. 16 "Measuring Network Traffic" (packet/byte
  counters, reducing counter overhead, sampling).
- Is it worth the internet track? Inference: **SKIM-to-SKIP.** It is
  device-implementation design: how to make counters and timers cheap at
  router scale. A cert *reads* counters; it does not build them. Give it a
  look only if rack-bench ever needs to build a high-rate in-kernel
  measurement pipeline itself (then ch. 16's counter-architecture
  tricks and ch. 7's timer mechanics are the reference).

### Internet Routing Architectures (2nd ed.)

- Sam Halabi with Danny McPherson, Cisco Press, Aug 23, 2000, 528 pp.,
  ISBN 978-1-5787-0233-6 (1-57870-233-X):
  <https://www.ciscopress.com/store/internet-routing-architectures-9781578702336>.
  The classic BGP/interdomain text. Every BGP reading list still cites
  it (<https://orhanergun.net/top-10-must-read-bgp-protocol-books-for-network-engineers>).
- Does it belong for a north-south internet-quality certifier? Partial
  inference: the durable 10% is the conceptual core. The core covers AS
  numbers, AS paths, peering vs transit, multihoming and route
  selection. A certifier needs exactly this vocabulary to read an mtr
  AS-path column. The same vocabulary lets the certifier judge whether
  a Chennai rack's upstreams look healthy. The rest is 25-year-old
  Cisco IOS configuration lore.
- Verdict: **SKIM** from a library copy (chs. on addressing/routing
  concepts and multihoming only). Do not buy. Read instead for AS-path
  audit work: bgp.tools / PeeringDB for upstream research. Read RFC
  4271 (<https://www.rfc-editor.org/rfc/rfc4271>) for protocol ground
  truth.

### BGP: Building Reliable Networks with the Border Gateway Protocol

- Iljitsch van Beijnum, O'Reilly, 2002
  (<https://www.oreilly.com/library/view/bgp/9780596002541>). The author
  himself notes it is 20 years old and moots a rewrite
  (<http://www.iljitsch.com/2022/09-29-time-to-write-a-new-bgp-book.html>).
  The troubleshooting chapter is genuinely diagnostic-minded, but it
  has the same age problem as Halabi.
- Verdict: **SKIP** -- Halabi's concepts or the web set cover this
  better for a certifier.

### Linux Kernel Networking: Implementation and Theory

- Rami Rosen, Apress, 2013 (O'Reilly catalog view:
  <https://www.oreilly.com/library/view/linux-kernel-networking/9781430261964>).
  The book gives a guided tour of the kernel's networking
  implementation. It covers netfilter, IPsec, wireless, IPv4/v6 at the
  3.x-era source level.
- Verdict: **SKIP** -- implementation archaeology, not diagnosis. The
  tools layer (`ss`, `nstat`, bcc) plus tcp(7)/ip-sysctl docs give the
  certifier everything it needs at current vintage.

### Network Troubleshooting Tools

- Joseph D. Sloan, O'Reilly, Sept 2001, 364 pp., ISBN 978-0-596-00186-5
  (<https://www.amazon.com/Network-Troubleshooting-OReilly-System-Administration/dp/059600186X>).
  The O'Reilly book a NOC engineer of 2001 keeps at the desk (ping,
  traceroute, netstat, sniffers, tcpdump).
- Verdict: **optional method SKIM**. Read Chapter 4, Path Characteristics, and Chapter 12, Troubleshooting Strategies.
  Sloan's baseline and combined-tool method supports selective reading.
  Keep it off the spine. Use current tool documentation for commands.

  Evidence: <https://books.google.com/books/about/Network_Troubleshooting_Tools.html?id=VyZTAAAAMAAJ>
  and <https://www.linuxjournal.com/article/4894>.
  Source note: [oreilly/sloan.md](oreilly/sloan.md).

---

## Final ranked reading order for the internet-bench track

Phase 1 -- Methodology: what "certified" has to mean

1. **Systems Performance, 2nd ed. (Gregg, 2020).** Chs. 1-2 in full;
   ch. 10 (network) deeply, with `netstat -s`/`ss`/`ethtool` open in a
   terminal; ch. 12 (benchmarking) before writing any throughput check;
   ch. 11 for cloud-path realities. ~2-3 weeks.
2. **The Art of Computer Systems Performance Analysis (Jain, 1991).**
   Chs. 10-13 (data presentation, ratio games, summarizing, comparing)
   before the bench issues the first PASS. Read the experimental-design
   chapters when deciding the 2-hour window's run matrix. ~4 weeks.
   Then it stays on the desk as the stats reference for every cert
   report.

Phase 2 -- Protocol ground truth

3. **TCP/IP Illustrated, Vol. 1, 2nd ed. (Fall & Stevens, 2011/2012).**
   Chs. 12-16 in full (preliminaries, connection management, timeout &
   retransmission, data flow & windows, congestion control); ch. 13.4 +
   10.8 for PMTUD; ch. 11 for DNS internals. Pair sec. 16.8.2 (CUBIC)
   with the BBR paper and RFC 9000 (below). ~3-4 weeks.
4. **High Performance Browser Networking (Grigorik, 2013, free).** Chs.
   1-2 in one sitting; the TLS and HTTP chapters selectively; copy the
   performance checklists into the bench design doc. ~1 week.

Phase 3 -- Evidence gathering

5. **BPF Performance Tools (Gregg, 2019).** Ch. 10 only, run against the
   bench's own transfers; design checks to degrade to `ss`/`nstat` where
   BPF is not permitted. ~1 week.
6. **Practical Packet Analysis, 3rd ed. (Sanders, 2017).** The TCP
   error-control material and slow-network chapter; wire it to tshark in
   the harness. ~1 week. (Chappell 2e as the deeper alternate.)

Phase 4 -- Ops context

7. **UNIX and Linux System Administration Handbook, 5e (2017).** Ch. 13
   (troubleshooting + monitoring), ch. 16 (DNS debugging), ch. 15's BGP
   pages. ~1 week, selective.
8. **Kurose & Ross, 8e (2021).** Only for team members new to
   networking: ch. 1's delay/throughput model plus the free Wireshark
   labs; everyone else reads the BBR/QUIC primary sources instead.

## Optional O'Reilly supplements

The [15-source supplement](oreilly.md) keeps the ranked eight and the four-book spine.

- *DNS and BIND* 5e: SKIM Chapters 2, 6, and 12–14 for resolver and fault evidence.
  Catalog metadata: May 2006, 640 pages, ISBN 9780596100575, BIND 9.3.2 and 8.4.7.
  The checked sources show no authoritative sixth-edition listing.
  See [the complete chapter list and access limits](oreilly/dns-bind.md).
- *DNS and BIND on IPv6*: SKIM Chapters 1 and 5; use Chapter 4 only for DNS64 deployments.
- *Pro DNS and BIND*: optional DNS background, not a second DNS core text.
- *Content Delivery Networks*: SKIM Chapters 2–4 for request routing and goodput context.
- Nath's *Packet Analysis with Wireshark*: optional SKIM; complete contents remain unverified.
- Greer's video: optional guided labs; metadata conflicts and playback access remain unresolved.
- Chow's event: optional introduction; White's event: optional troubleshooting method.
- Sloan's *Network Troubleshooting Tools*: optional method SKIM, not blanket SKIP.
- Schroder's *Linux Networking Cookbook*: new optional Chapter 19 SKIM, not Sloan's old SKIP entry.
- VandenBrink's *Linux for Networking Professionals* 2e: HOLD until release dates and contents agree.

Catalog presence does not prove playback or full-text entitlement.
Use current tool and protocol documents before old configuration recipes.

## The recommended spine (4 books, parallel to the storage spine)

The storage track's spine is *Gregg Systems Performance* + *Jain* +
*OSTEP* (free fundamentals) + *TOS'08* (classic internals). The internet
track's spine maps one-to-one:

1. **Systems Performance, 2nd ed. (Gregg, 2020)** -- methodology spine
   (identical book, different chapters: ch. 10 here, chs. 8-9 there).
2. **TCP/IP Illustrated, Vol. 1, 2nd ed. (Fall & Stevens)** -- the
   protocol classic. It plays the role TOS'08 plays for storage. It
   gives the internal mechanics a certifier must know to interpret
   retransmits, window behavior, and congestion control.
3. **High Performance Browser Networking (Grigorik, free)** -- the free
   fundamentals volume. It plays the role OSTEP plays. It gives BDP
   math, latency decomposition, TCP tuning, zero acquisition cost,
   read online.
4. **The Art of Computer Systems Performance Analysis (Jain, 1991)** --
   the statistics spine. The storage track carries it over unchanged.

## Skip list (one line each)

- *Network Algorithmics 2e* (Varghese & Xu, 2022) -- device-design
  (timing wheels, counter architectures). Skim it only if the bench
  builds its own high-rate measurement pipeline.
- *Internet Routing Architectures 2e* (Halabi, 2000) -- 25-year-old
  Cisco config lore around a durable 10% core. Library skim only.
- *BGP* (van Beijnum, 2002) -- author-mooted rewrite. Halabi's concept
  chapters and bgp.tools/RFC 4271 supersede it for us.
- *Linux Kernel Networking* (Rosen, Apress 2013) -- kernel source tour,
  not diagnosis.
- *Network Troubleshooting Tools* (Sloan, O'Reilly 2001) leaves the blanket SKIP list.
  Keep an optional method SKIM for Chapters 4 and 12, not a spine role.
- *Understanding Linux Network Internals* (Benvenuti, O'Reilly 2005) --
  kernel archaeology, out of cert scope.
- *UNIX Network Programming* (Stevens et al.) -- sockets API reference,
  not diagnosis.

## What to read instead of books (the modern-congestion-control web set)

These sources do not count in the eight. Read them alongside Fall &
Stevens ch. 16:

- BBR: Cardwell, Cheng, Jacobson, Vahdat, "BBR: Congestion-Based
  Congestion Control," ACM Queue 14(5), 2016,
  <https://queue.acm.org/detail.cfm?id=3022184>.
- BBR in Linux: Brakmo, "Making Linux TCP Fast," netdev 2.1, 2017,
  <https://netdevconf.org/2.1/papers/brakmo.pdf> (BBR merged for 4.9).
- CUBIC: RFC 8312 (Linux default since 2.6.19, 2006),
  <https://www.rfc-editor.org/rfc/rfc8312>.
- QUIC: RFC 9000, <https://www.rfc-editor.org/rfc/rfc9000>; HTTP/3:
  RFC 9114, <https://www.rfc-editor.org/rfc/rfc9114>.
- RTO standard method: RFC 6298, <https://www.rfc-editor.org/rfc/rfc6298>.
- PMTUD: RFC 1191 (IPv4), <https://www.rfc-editor.org/rfc/rfc1191>;
  RFC 8201 (IPv6), <https://www.rfc-editor.org/rfc/rfc8201>.
- Interarrival jitter definition: RFC 3550 Appendix A.8,
  <https://www.rfc-editor.org/rfc/rfc3550>.
- Linux TCP knobs and diagnostics: tcp(7)
  <https://man7.org/linux/man-pages/man7/tcp.7.html>, ss(8)
  <https://man7.org/linux/man-pages/man8/ss.8.html>, ip-sysctl
  <https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt>.

## Sources

Checked sources and declared limits: October 2026. See the supplement for access and edition conflicts.

| Topic                                                     | Source                                                                   |
|------------------------------------------------------------|---------------------------------------------------------------------------|
| Systems Performance 2e TOC, ISBN, 928 pp. | <https://www.brendangregg.com/systems-performance-2nd-edition-book.html>; <https://www.informit.com/store/systems-performance-9780136820154> |
| Gregg USE-for-TCP, netstat -s retransmit reading           | <https://www.brendangregg.com/Slides/MacIT2014_Analyzing_OSX_Perf_USE_Method.pdf> |
| Gregg Linux tool walkthroughs (ss -i per-socket fields)    | <https://www.brendangregg.com/Slides/Velocity2015_LinuxPerfTools.pdf>     |
| BPF Performance Tools TOC (ch. 10 Networking)              | <https://www.brendangregg.com/bpf-performance-tools-book.html>            |
| bcc networking tool inventory (tcpretrans, tcpdrop, ...)   | <https://github.com/iovisor/bcc>                                          |
| TCP/IP Illustrated Vol. 1 2e primary TOC and platform identity | <https://www.pearson.com/en-us/subject-catalog/p/Fall-TCP-IP-Illustrated-Volume-1-The-Protocols-2nd-Edition/P200000000242?view=educator>; <https://www.oreilly.com/library/view/tcp-ip-illustrated-volume/9780132808200> |
| HPBN free full text (CC BY-NC-ND) + TOC                    | <https://hpbn.co/>                                                        |
| HPBN corrected ISBN and platform record | <https://www.oreilly.com/catalog/errata.csp?isbn=9781449344764>; <https://www.oreilly.com/library/view/high-performance-browser/9781449344757/> |
| TCP Window Scale maximum | <https://www.rfc-editor.org/rfc/rfc7323> |
| Jain book page + chapter-indexed slides                    | <https://www.cse.wustl.edu/~jain/books/perfbook.htm>                      |
| Practical Packet Analysis 3e (April 2017, 368 pp., ISBN 9781593278021) | <https://nostarch.com/packetanalysis3>                          |
| Current Wireshark TCP classifier rules and limits | <https://www.wireshark.org/docs/wsug_html_chunked/ChAdvTCPAnalysis.html> |
| PPA 1e record (2007, ISBN 978-1-59327-149-7)               | <https://nostarch.com/releases/practical_packet_analysis_release.pdf>     |
| Chappell Wireshark Network Analysis 2e (WCNA study guide)  | <https://www.chappell-university.com/studyguide>                          |
| ULSAH 5e full TOC (ch. 13 networking, troubleshooting pages) | <https://www.admin.com/samples/TOC.pdf>                                  |
| Kurose & Ross 8e TOC (open PDF, ISBN 978-0-13-668155-7)    | <https://ebooks.karbust.me/Technology/Computer%20Networking%20A%20Top-Down%20Approach,%208th%20Edition%20by%20James%20F.%20Kurose,%20Keith%20W.%20Ross-Pearson-9780136681557.pdf> |
| Kurose & Ross 8e global edition (BBR/QUIC additions)       | <https://api.pageplace.de/preview/DT0400.9781292405513_A42098360/preview-9781292405513_A42098360.pdf> |
| Network Algorithmics 2e (Varghese & Xu, 594 pp., ISBN 9780128099278) | <https://educate.elsevier.com/book/details/9780128099278>        |
| Network Algorithmics 2e announcement                       | <https://www.cs.ucla.edu/george-varghese-releases-second-edition-of-his-book-network-algorithmics> |
| Internet Routing Architectures 2e (Cisco Press, 2000)      | <https://www.ciscopress.com/store/internet-routing-architectures-9781578702336> |
| BGP (van Beijnum, O'Reilly 2002) + author's 20-year note   | <https://www.oreilly.com/library/view/bgp/9780596002541>; <http://www.iljitsch.com/2022/09-29-time-to-write-a-new-bgp-book.html> |
| Linux Kernel Networking (Rosen, Apress)                    | <https://www.oreilly.com/library/view/linux-kernel-networking/9781430261964> |
| Network Troubleshooting Tools (Sloan, 2001)                | <https://www.amazon.com/Network-Troubleshooting-OReilly-System-Administration/dp/059600186X> |
| BBR paper (ACM Queue)                                      | <https://queue.acm.org/detail.cfm?id=3022184>                             |
| Making Linux TCP Fast (netdev 2.1)                         | <https://netdevconf.org/2.1/papers/brakmo.pdf>                            |
| CUBIC RFC 8312                                             | <https://www.rfc-editor.org/rfc/rfc8312>                                  |
| QUIC RFC 9000                                              | <https://www.rfc-editor.org/rfc/rfc9000>                                  |
| tcp(7) / ss(8) / ip-sysctl                                 | <https://man7.org/linux/man-pages/man7/tcp.7.html>; <https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt> |

## Gaps

- **No book covers BBR-era congestion-control diagnosis.** Fall &
  Stevens 2e stops before BBR. Grigorik stops before both BBR and QUIC.
  Kurose & Ross 8e is the only book that even mentions them. The
  primary sources (ACM Queue, netdev, RFCs) are mandatory reading
  alongside the spine. This is a structural gap in the book canon, not
  in our research.
- **No book teaches object-store-specific egress measurement** (S3/R2/
  GCS endpoint behavior, CDN-fronted endpoints, per-region RTT). The
  hyperscaler and neocloud researcher briefs in this track should carry
  that. Books cannot.
- **RTT values in the BDP calculations are examples**, not Chennai rack measurements.
  Measure RTT to each object-store endpoint before the certification run. Calculate BDP again from those measurements.
- **Linux settings vary by distribution and kernel release.**
  Read live values and actual per-flow constraints. A configured buffer maximum does not alone prove a throughput ceiling.
- **Catalog access limits remain.** Several publisher fetches require authentication or bot verification.
  The supplement records indexed evidence, metadata conflicts, and unverified contents separately.
- **mtr interpretation discipline must come from man pages and
  traceroute lore** (ULSAH does not cover mtr). A short bench-internal
  note should formalize the "intermediate loss that passes is
  not loss" rule. Write it from traceroute(8)/mtr(8) docs.
- **The academic-measurement literature** includes IMC/PAM papers on
  path performance, loss inference, and bufferbloat measurement such as
  netperf-vs-bloat methodology. The academia researcher in this track
  covers that literature. Books do not. Expect overlap on bufferbloat
  and jitter definitions.
