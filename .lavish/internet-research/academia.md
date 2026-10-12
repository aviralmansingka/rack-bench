# Academia and standards: the measurement science of diagnosing internet quality

Research date: 2026-10-11. All claims below carry a source URL.

This brief uses peer-reviewed measurement papers and standards (IETF IPPM, ITU-T). The brief extracts three things per source. (a) The brief records the metric and the method each source defines. (b) The brief records the scale of evidence (N samples, N hours, N probes). (c) The brief records the signal a **2-hour `bench internet` certification run** can reuse.

The run operates on a GB300-class rack in Chennai. The brief also states what such a run cannot honestly conclude in that window. The research record confirms full reading of the primary PDFs (USENIX, ACM, SIGCOMM sites, ITU, IETF). Regulator methodology pages stay primary for the regulator programs. Companion notes: `neoclouds.md`, `hyperscalers.md`, `ailabs.md`, `bigco.md`, `clustermax.md`, `books.md`.

Epistemic markers appear below. **[Observed]** marks a measured or reported fact from the cited source. **[Calculation]** marks arithmetic that comes from a source's own numbers. **[Inference]** marks my reasoning about what rack-bench can conclude from it. Each method states its own sample-size honesty.
---

## 1. The IPPM measurement canon (IETF RFCs and ITU-T recommendations)

### 1.1 RFC 2330 — the IPPM framework
**Citation:** V. Paxson, G. Almes, J. Mahdavi, M. Mathis. *Framework for IP Performance
Metrics*. RFC 2330, IETF, May 1999. https://datatracker.ietf.org/doc/html/rfc2330

**Metric/method:** the RFC defines no metric itself. The RFC supplies the framework every later IPPM metric builds on. The framework covers Type-P metrics (condition on protocol, TTL, packet size). The framework also defines the singleton → sample → statistic lattice. The framework sets wire-time vs host-time measurement points. The framework demands that every result reports its measurement error (clock sync, path changes, Poisson sampling). https://datatracker.ietf.org/doc/html/rfc2330

**Why it matters to a certifier:** a PASS claim is only as good as its stated error bounds. RFC 2330 makes three core demands. State the packet size (Type-P). State the sampling schedule. State the clock-error bounds. These demands set the minimum metadata `bench internet` should attach to every measured number.

Poisson sampling spaces probes by a Poisson process. The framework prescribes it to get unbiased path samples. https://datatracker.ietf.org/doc/html/rfc2330

**2-h cert signal:** adopt the singleton→sample→statistic discipline. Never report a single ping as "the latency". Report a sample (N probes over the window) instead. Give min/p50/p95/p99 and the probe size. Poisson-schedule the idle pings. [Inference]
---

### 1.2 RFC 2679 — one-way delay (and its update RFC 7679)
**Citation:** G. Almes, S. Kalidindi, M. Zekauskas. *A One-way Delay Metric for IPPM*. RFC 2679,
IETF, Sept 1999. https://datatracker.ietf.org/doc/html/rfc2679 (revised registration:
RFC 7679, https://datatracker.ietf.org/doc/html/rfc7679)

**Metric:** Type-P one-way delay `dT` takes the wire-time at the destination. The metric subtracts the wire-time at the source. The difference applies to a single packet. A sample of these singletons yields statistics.

**Method:** the metric requires *synchronized clocks at both endpoints*. The RFC mandates reporting clock error alongside the result.

**What it can conclude:** the metric shows absolute one-way delay asymmetry (e.g., Chennai→S3 vs S3→Chennai). Round-trip ping fundamentally cannot decompose this asymmetry.

**What it cannot:** without clock sync (GPS/PTP/NTP-grade), one-way delay stays unusable. The RFC itself treats unquantified clock error as a disqualifier.
https://datatracker.ietf.org/doc/html/rfc2679

**2-h cert signal:** discipline the bench peer with NTP or PTP when possible. Then collect one-way delay samples per object-store endpoint. Otherwise fall back to RTT. The certificate must say so. [Inference]
---

### 1.3 RFC 2680 — one-way loss (and its update RFC 7680)
**Citation:** G. Almes, S. Kalidindi, M. Zekauskas. *A One-way Packet Loss Metric for IPPM*.
RFC 2680, IETF, Sept 1999. https://datatracker.ietf.org/doc/html/rfc2680 (revised registration:
RFC 7680, https://datatracker.ietf.org/doc/html/rfc7680)

**Metric:** the singleton is binary. The singleton takes 1 if a Type-P packet fails to arrive within a defined timeout `T_max`. The singleton takes 0 otherwise. Sample statistics give the loss ratio. The metric is direction-specific. So the metric distinguishes lossy egress from lossy ingress on the Chennai rack's north-south path.

**Method:** the metric carries the same clock-sync requirement as RFC 2679. Loss is conditional on the timeout threshold. So the report must state `T_max`.

**Cannot conclude:** the metric cannot show why the network loses a packet. For that, see §2.4 (congestion vs wireless vs policing).

**Sample-size honesty:** at 1e-4 loss rates, a tight bound needs ~10⁴–10⁵ probes. **[Calculation]** a Poisson 95% confidence interval of ±1e-4 on a 1e-3 estimate needs roughly (1.96)²·p(1−p)/e² ≈ 3.8×10⁶ probes. That count lies far beyond a 2-hour window. A 2-hour loss measurement honestly certifies only "loss ≥ observed" for rare-loss regimes. Report the observed count and the confidence bound. [Inference]
---

### 1.4 RFC 3393 + RFC 5481 — delay variation: IPDV vs PDV
**Citation:** C. Demichelis, P. Chimento. *IP Packet Delay Variation Metric for IPPM*. RFC 3393,
IETF, Nov 2002. https://datatracker.ietf.org/doc/html/rfc3393 — A. Morton, B. Claise.
*Packet Delay Variation Applicability Statement*. RFC 5481, IETF, March 2009.
https://datatracker.ietf.org/doc/html/rfc5481

**Metrics:** RFC 3393 defines IP Packet Delay Variation (IPDV).
IPDV is the difference in one-way delay between two packets from a stream.
Classically, the two packets are consecutive.
RFC 5481 compares IPDV with **PDV (Packet Delay Variation)**.
PDV is the delay of each packet minus the *minimum* delay over a test interval.
The RFC recommends PDV to assess if a network can carry jitter-sensitive streams (buffer sizing for de-jittering).

The reason is stability. PDV relative to the minimum is stable and one-sided.
Consecutive-packet IPDV is noisy and signed.
IPDV is also sensitive to reordering and coarse packet spacing. https://datatracker.ietf.org/doc/html/rfc5481

**Why each exists:** ITU-T Y.1540-style IPDV comes from the telephony heritage.
That heritage uses inter-arrival jitter for VoIP de-jitter buffers.
PDV is what a certifier wants: "how much worse than the best case
does this path get under load." **[Inference]**

**2-h cert signal:** Compute **PDV against a window-minimum baseline** as the headline variation number.
Do not use consecutive-packet jitter for the headline.
If the certificate needs VoIP-like semantics, report both.
Sample-size honesty: PDV percentiles need on the order of hundreds of samples to be stable.
A 5 Hz ping stream for 120 s gives 600 samples.
That count is adequate for p95 and marginal for p99.
**[Calculation]** [Inference]
---

### 1.5 RFC 4656 OWAMP / RFC 5357 TWAMP — active measurement protocols
**Citation:** S. Shalunov et al. *A One-way Active Measurement Protocol (OWAMP)*. RFC 4656,
IETF, Sept 2006. https://datatracker.ietf.org/doc/html/rfc4656 — K. Hedayat et al. *A Two-Way
Active Measurement Protocol (TWAMP)*. RFC 5357, IETF, Oct 2008.
https://datatracker.ietf.org/doc/html/rfc5357

**Metric/method:** OWAMP measures one-way delay/loss.
OWAMP has the same clock-sync requirement.
TWAMP measures round-trip delay/loss. TWAMP needs **no clock sync**.

Both timestamps come from the sender's clock.
The control client negotiates the session.
The reflector echoes test packets and embeds receive/transmit timestamps in them.
TWAMP Light strips the responder logic to a pure reflector for router/embedded implementations.

**What it can conclude in 2h:** a continuous session-per-endpoint stream gives loss (sequence-number gaps).
The stream also gives RTT sample statistics with standard protocol machinery.
**Cannot:** it cannot do direction attribution.
The impairments of both directions fold into the round trip.
An attacker can spoof unauthenticated TWAMP.
So use the authenticated mode for a cert result. https://datatracker.ietf.org/doc/html/rfc5357

**2-h cert signal:** run twamp/twamp-light toward the bench peer for the whole window.
The protocol is a low-cost, standards-native carrier of the idle-latency and loss numbers.
The FCC/SamKnows program uses simple ICMP instead (§5.1).
ICMP is equally defensible. In either case, state which one the bench uses.
[Inference]
---

### 1.6 RFC 6349 — TCP throughput testing: the three diagnostic metrics
**Citation:** B. Constantine et al. *Framework for TCP Throughput Testing*. RFC 6349, IETF,
Aug 2011. https://datatracker.ietf.org/doc/html/rfc6349 (authorship includes JDSU — now VIAVI —
with Bell Canada and Deutsche Telekom representatives:
https://www.viavisolutions.com/en-us/literature/rfc-6349-testing-truespeed-application-notes-en.pdf)

**Method (three steps):** (1) Find the **path MTU**.
Check MTU integrity before any TCP test (layer-2/3 sanity first).

(2) Find the **baseline RTT** and the **bottleneck bandwidth (BB)** in each direction.
From them, calculate the **BDP = BB × RTT**. The BDP sets the required TCP window.
Size send/receive buffers to ≥ BDP. In practice, use 2× or more as a safety margin.

(3) Run **single- and multiple-connection TCP throughput tests** in each direction until they reach steady state.

Test-equipment implementations default to 60 s per direction (30–600 s
configurable).
The equipment auto-calculates the connection count from the BDP.
https://app.netrounds.com/static/0.0/support/task-types/netw-perf/rfc6349.html

**The three metrics and why each exists:**
- **TCP Transfer Time Ratio (TTR)** = actual transfer time / ideal transfer time for the BDP
  bound. TTR equals BB-limited throughput over measured throughput — "how far from physics is this path." https://app.netrounds.com/static/0.0/support/task-types/netw-perf/rfc6349.html
- **TCP Efficiency %** = (bytes sent − bytes retransmitted) / bytes sent × 100 — a **loss**
  detector. A value below 100% means the sender retransmits segments.
  This metric exists because throughput alone cannot tell a window-limited flow from a loss-limited one.
  Retransmit accounting can tell them apart.
  https://app.netrounds.com/static/0.0/support/task-types/netw-perf/rfc6349.html
- **Buffer Delay %** = (mean RTT during transfer − baseline RTT) / baseline RTT × 100.
  This is a **bufferbloat** detector (§3). The metric shows how much standing queue the loaded path builds.
  VIAVI's app note gives an example: efficiency 96.87% with buffer delay only 0.54%.
  ⇒ *Loss, not buffering*, causes the throughput gap. The two metrics triangulate the cause.
  https://www.viavisolutions.com/en-us/literature/rfc-6349-testing-truespeed-application-notes-en.pdf

**2-h cert signal:** This framework is the closest thing to a turnkey spec for one test.
That test is the sustained-egress/ingress-to-S3/R2/GCS test of `bench internet`.

Per endpoint and direction, run this chain in order.
Do the MTU check.
Then find the baseline RTT with a small-packet ping train.
Then find the BB, for example from a short burst or the SLA rate.
Then set BDP-sized windows.
Then run single and multi-connection 60-s transfers.

Example BDPs: for a 1 Gbps × 200 ms intercontinental path, **[Calculation]** BDP = 25 MB.
For 10 Gbps × 30 ms intra-India, BDP = 37.5 MB.
Run ≥5 iterations of each transfer.
Report throughput + TTR + efficiency + buffer delay.

Sample-size honesty: 60 s × 5 iterations per direction per endpoint ≈ 10 min per endpoint.
Three object stores × both directions fit the window but leave little room.
The multi-connection runs are the expensive part. [Inference]
---

### 1.7 RFC 2544 (and RFC 6815) — the lab benchmark that service turn-up borrows and outgrows
**Citation:** S. Bradner, J. McQuaid. *Benchmarking Methodology for Network Interconnect
Devices*. RFC 2544, IETF, March 1999. https://datatracker.ietf.org/doc/html/rfc2544 —
M. Constantine et al. *Applicability Statement for RFC 2544*. RFC 6815, IETF, 2012.
https://datatracker.ietf.org/doc/html/rfc6815

**Metric/method:** The RFC benchmarks devices.
The RFC uses fixed frame sizes (64, 128, 256, 512, 768, 1024, 1280, 1518 B).
The RFC defines **throughput = highest rate with zero loss over a 60-second trial**.
A binary search on offered load finds that rate.

The RFC adds latency-under-load, frame-loss, and back-to-back trials.
RFC 6815 adapts it to telecom services.
The applicability statement gives explicit caveats about the duration of the full suite and about UDP/lab assumptions. https://datatracker.ietf.org/doc/html/rfc2544

**Why it exists / cannot do:** the RFC measures a *box* (L2/L3 forwarding), not a *service*.
The box has no TCP, no congestion, and no RTT coupling.
The zero-loss binary search across 8 frame sizes takes tens of minutes.
Service providers want a faster, contract-relevant turn-up test.
Y.1564 fills exactly that niche (§1.8). https://datatracker.ietf.org/doc/html/rfc6815

**2-h cert signal:** Use RFC 2544-style zero-loss binary search only as the *first* stage.
That stage checks layer-2/3 integrity between the rack and the bench peer.
RFC 6349 itself recommends this order.
Run it at a couple of frame sizes, not the whole suite.
All sustained-throughput claims must come from TCP-level tests, not 2544. [Inference]

---

### 1.8 ITU-T Y.1564 (EtherSAM) — service activation: configuration test + 1-hour performance soak
**Citation:** ITU-T Rec. Y.1564, *Ethernet service activation test methodology* (first approved
2011). https://www.itu.int/rec/T-REC-Y.1564

**Metric/method (two phases):** (1) **Service configuration test**.
The tester tests each service in sequence at its CIR (committed information rate).
The tester also checks excess/burst handling.
Then the tester runs all services **simultaneously**.
This step verifies that the aggregate does not degrade any single service.

(2) **Service performance test**.
The tester runs a single service at CIR for **1 hour**.
During that hour, the tester measures **frame transfer delay (FTD), frame delay variation (FDV), and frame loss ratio (FLR)**.
These are the QoS parameters that SLAs use. https://www.itu.int/rec/T-REC-Y.1564

**Why the 1 hour exists:** carriers find that short tests pass.
But sustained congestion/policer interaction appears only after some minutes.
The soak is the sample-size honesty mechanism, hardcoded. **[Inference]**

**2-h cert signal:** This standard is the closest published standard to the exact situation of rack-bench.
That situation is to certify a circuit in a bounded window.

Plan ~30–40 min of Y.1564-style multi-target configuration tests.
Add a 1-hour per-target performance soak at the committed egress rate.
That plan fits a 2-hour budget for *one* headline path, not all three object stores.
So rack-bench must consciously trade soak duration for endpoint coverage and state its choice. [Inference]

---

### 1.9 What the canon can and cannot conclude in a 2-hour window — summary
| Standard | Metric | Can conclude in 2 h | Cannot conclude in 2 h |
|---|---|---|---|
| RFC 2330 | framework | metadata discipline, Poisson samples | — |
| RFC 2679/7679 | one-way delay | direction asymmetry (needs clock sync) | anything without sync |
| RFC 2680/7680 | one-way loss | loss above ~1e-3 regime; observed count | tight bounds on 1e-4+ tails (needs 10⁶ probes) |
| RFC 3393/5481 | IPDV/PDV | PDV p95 vs window-min baseline | p99 stability with <~10³ samples |
| RFC 5357 | TWAMP RTT/loss | continuous session stats, spoof-resistant with auth | direction attribution |
| RFC 6349 | TTR, TCP efficiency, buffer delay | cause triangulation (loss vs buffering vs window) per endpoint | <~1 h per endpoint-direction without crowding the window |
| RFC 2544 | zero-loss rate | L2/L3 integrity | service-quality claims (no TCP) |
| Y.1564 | FLR/FTD/FDV | 1-service 1-hour soak at CIR | multi-service soak in the same hour |

---

## 2. Diagnostic landmark papers

### 2.1 Netalyzr (Kreibich, Weaver, Nechaev, Paxson — IMC 2010): the edge-network diagnostic suite
**Citation:** C. Kreibich, N. Weaver, B. Nechaev, V. Paxson. *Netalyzr: Illuminating The Edge
Network*. IMC '10, Melbourne, Nov 2010. PDF (read in full):
http://conferences.sigcomm.org/imc/2010/papers/p246.pdf

**Scale of evidence:** 130,436 sessions from 99,513 public IPs, June 2009–June 2010, 6,884
organizations, 186 countries. A Java-applet client runs against ~20 EC2 back-ends. The back-ends run 38 test types. [Observed] http://conferences.sigcomm.org/imc/2010/papers/p246.pdf

**What it probed:** NAT behavior and port renumbering. IP fragmentation. **Directional path
MTU and ICMP-frag-needed black holes**.

Latency/bandwidth/**bottleneck-buffer capacity** (the UDP self-induced-congestion trick: fill the access buffer, measure added delay, buffer =
rate × extra delay).

Transient outages (5 Hz background stream). Packet replication/reordering. 25-service port blocking/proxying.

A deep DNS suite covers resolver identity, EDNS, glue policy, TTL compliance, and port randomization. The suite also covers **DNS MTU by padded 1300/1700
B replies**, NXDOMAIN wildcarding, NAT DNS proxies, and open resolvers.

HTTP proxying/caching fidelity (alternating inverse images). Content filtering. [Observed]
http://conferences.sigcomm.org/imc/2010/papers/p246.pdf

**Key numbers (all [Observed]):**
- **Bufferbloat:** uplink buffers cluster at powers of two. **128 KB and 256 KB dominate**.
  At 8 Mbps uplink, that is ~125–250 ms of added latency under load.
  At 1 Mbps, "well over 1
  sec." Vertical banding by service tier follows (Comcast's fleet shows the same 128/256 KB cluster).
- **Fragmentation/PMTU:** 8% of sessions cannot send a 2 KB UDP datagram. 8% cannot receive
  one. **79% of server→client paths show MTU 1500, 16% show 1492 (PPPoE)**.
  For sessions with
  MTU < 1500, **only 59% receive a proper "fragmentation needed" ICMP**. ~41% of those
  paths are ICMP black holes.
- **DNS:** 52% of sessions use EDNS-aware resolvers. **13% of sessions advertising EDNS
  ≥1800 B fail to fetch a 1700 B reply**. **15% have a measured DNS MTU of 1472 B**
  (cannot receive fragmented DNS). This is the DNSSEC deployment alarm of its day.

  **29% show
  NXDOMAIN wildcarding** (22% excluding OpenDNS/Comcast). 5% still use monotone/fixed DNS
  source ports (post-Kaminsky). 11% of DNS-capable sessions show DNS-aware middleboxes on
  port 53.
- **Middleboxes/ports:** NetBIOS 139tcp interferes for 50.6% of sessions. Middleboxes block
  SIP 5060tcp for 5.5% of sessions and proxy it for 4.6%. Middleboxes filter the EICAR test file (AV) for 10% of sessions. 8.4% of sessions
  show HTTP proxying.
- **Loss/reordering/outages:** 10% of sessions experience ≥1 transient outage (≥3 lost 5 Hz
  packets). Reordering appears in 16% of uplink and 33% of downlink bandwidth tests.
  UDP
  checksum error rate ≈ 1.6×10⁻⁵ (bursty, few hosts). **No TCP/IP checksum errors appear at all**.
- **Latency context:** mean quiescent latency 110–180 ms depending on context (home/work/
  public). Average download 6.7 Mbps / upload 2.7 Mbps (2010-era access).

**2-h cert signal:** Netalyzr is the template for the "path hygiene" block of rack-bench.
The specific probes worth cloning are below.

Directional PMTU + ICMP-frag-needed check (§2.8 has the
scamper automation). DNS MTU vs advertised EDNS. NXDOMAIN wildcarding. DNS port randomization.
Fragmentation send/receive. Egress port reachability for the exact ports the bench needs
(443/8443, DNS, S3 endpoints).

Its single-session runtime is minutes.
The whole pathology suite is cheap. The expensive part of `bench internet` is the throughput soaks. [Inference]

Sample-size honesty: each Netalyzr pathology verdict is categorical (works/broken).
A handful of probes typically settles one verdict.
Binary-search MTU convergence in Luckie's scamper needs ~14
probes (§2.8). [Observed, per Fig. 1 there]

---

### 2.2 Hubble (Katz-Bassett et al. — NSDI 2008): reachability black holes
**Citation:** E. Katz-Bassett, H. V. Madhyastha, J. P. John, A. Krishnamurthy, D. Wetherall,
T. Anderson. *Studying Black Holes in the Internet with Hubble*. NSDI '08.
https://www.usenix.org/conference/nsdi-08/studying-black-holes-internet-hubble

**Method:** hybrid passive/active. Hubble mines BGP updates +Looking Glass+ public traceroute data for
*suspicious* unreachability. Hubble then verifies with targeted probes from PlanetLab + spoofed-source
probing to isolate direction. Hubble monitors prefixes that cover **89% of the Internet's edge address
space at 15-minute granularity**. [Observed]

**Key numbers (3-week study, [Observed]):**
Hubble estimates it finds **85% of the reachability problems that pervasive probing
finds**. Hubble uses only **5.5% as many probes**. **67% of detected outages are partial** (some vantage
points can reach the destination). **>60% of outages last longer than 2 hours, ~10% longer
than a day**.

Direction isolation works with spoofed packets in **84% of analyzed cases**.
Many problems **do not correlate with BGP updates**.
The control plane stays silent while the data plane breaks.

**2-h cert signal:** Two lessons: (a) reachability failure is common, persistent, and
*direction-specific*. A bench that only tests the forward path misses reverse-path
blackholes. Hubble/LIFEGUARD finds 25% of failures reverse-only and 47% bidirectional.
(b) **[Inference]** a 2-hour window samples reachability at one moment.
But >60% of real outages last >2 h.

So a failure found during certification is very likely a real,
reportable event rather than a blip.
Conversely, a PASS is a statement about the window, not
the month. Continuous RIPE Atlas monitoring (§5.4) gives the complementary evidence between cert
windows. Sources: https://www.usenix.org/conference/nsdi-08/studying-black-holes-internet-hubble ;
https://s3-us-west-2.amazonaws.com/www-cse-public/ugrad/thesis/TR11-05_Scott.pdf

---

### 2.3 iPlane (Madhyastha et al. — OSDI 2006) and iPlane Nano (NSDI 2009): path prediction as a service
**Citation:** H. V. Madhyastha, T. Isdal, M. Piatek, C. Dixon, T. Anderson, A.
Krishnamurthy, A. Venkataramani. *iPlane: An Information Plane for Distributed Services*.
OSDI '06. https://homes.cs.washington.edu/~arvind/papers/iplane.pdf — iPlane Nano. NSDI '09.
https://www.usenix.org/event/nsdi09/tech/full_papers/madhyastha/madhyastha.pdf
(Venue note: the task brief says "NSDI 2006". The information-plane paper is OSDI '06 — NSDI '09
is the Nano successor. https://www.usenix.org/event/nsdi09/tech/full_papers/madhyastha/madhyastha.pdf)

**Method:** iPlane is a *structural* predictor. iPlane continuously collects traceroutes from a PlanetLab
overlay (~thousands of destinations). iPlane decomposes the Internet into path segments (clustered
PoP-to-PoP links). iPlane then **composes** predictions for unseen (src,dst) pairs.

Latency = sum of
segment latencies. Bandwidth = min over segments. This beats black-box coordinate systems. [Observed] https://homes.cs.washington.edu/~arvind/papers/iplane.pdf

**Why a certifier cares:** iPlane validates the idea that an **mtr/traceroute path audit has
predictive content**. Knowing the PoPs and interdomain links on a Chennai→S3 path lets
you reason about shared fate.
You can predict which *other* endpoints share it (correlated failures/congestion).
The same knowledge lets you compare the measured path against a crowd-sourced prior for the same segment.
**[Inference]**

**2-h cert signal:** Capture full traceroutes (IPv4+IPv6) to each object-store endpoint at
several times in the window. Record AS path and PoP sequence.
Flag any path that changes between iterations (load balancing, flap).
iPlane-era evidence says path stability itself is
a health signal. Cannot conclude: iPlane-style *prediction* for arbitrary endpoints needs an
overlay fleet a single rack does not have. For that, query RIPE Atlas (§5.4). [Inference]

---

### 2.4 The congestion-diagnosis line: DiffProbe → ShaperProbe → TSLP → TCP congestion signatures
*(This section corrects the task brief's "Kanuparthy & Dovrolis, 'Measuring Internet Congestion: A
No-Man's Land Between Edge and Core' + SIGCOMM 2012 LDCE/CLE signatures".
No index lists such a paper or such signature acronyms. The real, citable line is below. See §9.)*

#### 2.4.1 DiffProbe (Kanuparthy & Dovrolis — INFOCOM 2010) and ShaperProbe (IMC 2011)
**Citations:** P. Kanuparthy, C. Dovrolis. *DiffProbe: Detecting ISP Service Discrimination*.
IEEE INFOCOM 2010. — *ShaperProbe: End-to-End Detection of ISP Traffic Shaping using Active
Methods*. IMC '11. PDF: https://conferences.sigcomm.org/imc/2011/docs/p473.pdf

**Method:** DiffProbe sends two equal traffic classes. DiffProbe compares loss/delay to detect
differentiation. **ShaperProbe** uses the token-bucket signature of shaping.
ShaperProbe sends a burst at line rate.
Then ShaperProbe observes whether throughput steps down to a **shaping rate** after the sender exhausts the
**burst size**. The shaper shows itself as a rate staircase. [Observed]
https://conferences.sigcomm.org/imc/2011/docs/p473.pdf

**2-h cert signal for a rack:** the same burst-then-observe pattern shows if a policer exists.
The policer enforces a rate below the physical/port line rate.
The policer can be the datacenter uplink or a provider policer between the rack and the object store.
So **certify the committed rate, not the link speed of the NIC**.
A 25 GbE port behind a 10 Gbps policer shows exactly the ShaperProbe
staircase. [Inference] Sample-size honesty: a token-bucket detection needs one to a handful of
~10-s burst trains. [Inference]

#### 2.4.2 Luckie et al. (IMC 2014) — TSLP: inferring interdomain congestion from latency tomography
**Citation:** M. Luckie, A. Dhamdhere, D. Clark, B. Huffaker, kc claffy. *Challenges in
Inferring Internet Interdomain Congestion*. IMC '14. (Referenced and described in the IMC '17
signatures paper: https://conferences.sigcomm.org/imc/2017/papers/imc17-final99.pdf — see also
the operational successor: https://www.caida.org/catalog/papers/2018_inferring_persistent_interdomain_congestion/inferring_persistent_interdomain_congestion.pdf)

**Method (as the IMC '17 paper describes it, [Observed]):** use a vantage point *inside* a network.
From there, continuously ping **the near router and the far router of each interdomain
(interconnect) link** in the traceroutes.
**Elevated latency to the far end with no elevation
to the near end = congestion on that interconnect**.
The authors validate this against diurnal load (peaks
in evening hours). The 2018 CAIDA successor runs this method at scale.
Its authors manually validate every asserted congestion event. https://www.caida.org/catalog/papers/2018_inferring_persistent_interdomain_congestion/inferring_persistent_interdomain_congestion.pdf

**Why it matters to rack-bench:** **interconnects** (ISP↔transit, transit↔cloud) often decide the north-south quality of the Chennai rack.
mtr already gives you the two routers around
each AS-boundary hop.
Ping both for the whole window.

The IMC '17 paper measures one such
Comcast↔TATA interconnect. The baseline is ~18 ms and rises above 30 ms during evening congestion.
**A ~15 ms buffer is the visible congestion signature of that peering link.** [Observed]
This localizes congestion to *a specific
interdomain link* rather than "the internet is slow."
https://conferences.sigcomm.org/imc/2017/papers/imc17-final99.pdf

**2-h cert signal:** In the bench window, run continuous near/far pings.
Cover every AS-hop in the mtr path to each object store.
Report the interdomain links (if any) that show
far-side-only latency inflation.
Sample-size honesty: the papers make TSLP-style verdicts from **days-to-weeks** of series correlated with diurnal load.
2 hours give you "this
link was/wasn't congested during the window," not its congestion duty cycle.
If the certificate must bound worst-case, run the bench
during Indian evening peak (§6.1). [Inference]

#### 2.4.3 Sundaresan et al. (IMC 2017) — TCP congestion signatures: self-induced vs external
**Citation:** S. Sundaresan, A. Dhamdhere, M. Allman, kc claffy. *TCP Congestion Signatures*.
IMC '17, London. DOI 10.1145/3131365.3131381. PDF (read in full):
https://conferences.sigcomm.org/imc/2017/papers/imc17-final99.pdf

**Method:** the paper answers the key question that a speed test cannot answer.
Is the flow **self-induced**
congested? Then the flow saturates its own bottleneck (e.g., the last mile / the committed rate of the rack).
Or is it **externally** congested? Then the flow meets an already-full link (e.g., a peering interconnect).
Two
slow-start-period statistics of the RTT series of the flow answer it.

**NormDiff** = (maxRTT −
minRTT)/maxRTT over slow start.
**CoV** = coefficient of variation of slow-start RTT.
Self-induced: the buffer starts empty and fills ⇒ large NormDiff + high CoV.
External: the buffer is
already full ⇒ small variation, elevated baseline.
A depth-4 decision tree on the pair
classifies the flow. [Observed]

**Scale of evidence / accuracy (all [Observed]):** the evidence mixes a controlled testbed and real-world data.
The testbed uses 10/20/50 Mbps access,
a 950 Mbps interconnect, and 20–100 ms buffers. In the testbed, the classifier reaches up to **90% precision and recall**.

Real-world: the authors use M-Lab NDT 2014 Cogent peering-dispute data.
The classifier reproduces the known event
(Cogent↔Comcast/TWC/Verizon congested Jan–Feb 2014, resolved Mar–Apr).
A focused 10-week
Comcast↔TATA experiment (2,593 NDT tests) gives **99% accuracy on self-induced congestion,
75–85% on external congestion**.
A model retrained on real-world data gets 90%+ / 100%.

**Key numbers worth reusing:** the method discards flows with **fewer than 10 RTT samples during slow start**.
The method treats them as statistically unusable (sample-size honesty, hardcoded).
Gray zone = high
throughput without access saturation + low interconnect buffer.
Multiplexing degrades
external-congestion detection (93% → 50% as concurrent cross-traffic flows drop 100 → 10).

**2-h cert signal:** This method is directly reusable at low cost.
Each time rack-bench opens a bulk
transfer to an object store, packet-capture (or TCP_INFO-sample) the slow-start RTT series.
Then compute NormDiff + CoV.
Then the certificate can say *why* the throughput takes its value:
- self-induced ⇒ the bottleneck is the committed rate of the rack (good — you certified it);
- external ⇒ a congested upstream/interconnect (bad — the vendor can take the blame).
  The result depends on
  time of day. [Inference] The paper itself states these caveats. The authors train on CUBIC-era Linux TCP.
  **BBR confounds the technique** because BBR controls the very buffering that the signature reads.
  So
  run the signature test with CUBIC (or measure BtlBw/minRTT of BBR directly, §4.1). [Observed]

#### 2.4.4 Sundaresan et al. (IMC 2017) — Challenges in Inferring Internet Congestion
**Citation:** S. Sundaresan, D. Lee, X. Deng, Y. Feng, A. Dhamdhere. *Challenges in Inferring
Internet Congestion Using Throughput Measurements*. IMC '17.
https://www.caida.org/catalog/papers/2017_challenges_inferring_internet_congestion/challenges_inferring_internet_congestion.pdf

**Key methodological point for rack-bench:** throughput-only crowdsourced data cannot
reliably localize congestion.
Its statistical assumptions (diurnality, access-limited clients)
often fail.
The paper codifies the limits that push the field to latency-based (TSLP) and
flow-internal (signatures) methods. **[Inference]**
**Lesson:** `bench internet` should never
certify "congestion" from a throughput number alone.
Pair every throughput measurement with
the RTT series that explains it. [Inference]

---

### 2.5 The Tail at Scale (Dean & Barroso — CACM 2013): why p99 governs
**Citation:** J. Dean, L. A. Barroso. *The Tail at Scale*. Communications of the ACM 56(2):74–80,
Feb 2013. DOI 10.1145/2408776.2408796. https://dl.acm.org/doi/10.1145/2408776.2408796

**Core argument ([Observed], as stated in the paper):** large-scale services are fanout
systems. A single user request touches tens–thousands of servers/components.
So **the
latency of the request is the max over its fanout**.
The tail percentiles of components become
the typical experience of the aggregate.

The canonical arithmetic: **[Calculation]** each
component misses its 99.9th-percentile SLO with probability 10⁻³.
Then a request that touches 1,000
components has probability 1 − 0.999¹⁰⁰⁰ ≈ **63%** to meet a >p99.9 component.
For large fanouts, the tail
*is* the median.

The paper cites the business evidence.
Amazon reports
~1% sales impact per 100 ms added latency.
Google measures a drop in search queries/user of
0.2–0.6% with 100→400 ms latency. https://dl.acm.org/doi/10.1145/2408776.2408796

**Why a rack certifier cares:** a GB300 rack does exactly this.
One training run fans out
millions of object-store GETs (data loading) and checkpoint PUTs.
A certificate of *mean* north-south latency certifies the wrong thing.
**A data-loading loop feels p99/p99.9 egress latency and loaded-latency tails.** [Inference]

**2-h cert signal:** Report latency distributions with p50/p95/p99/max, never means alone.
Size the sample so that p99 is at least the 100th-largest sample (≥10⁴ samples for a usable p99).
**[Calculation]** [Inference]

---

### 2.6 Packet reordering: Bennett et al. (ToN 1999) and Jaiswal et al. (INFOCOM 2003 / ToN 2007)
**Citations:** J. Bennett, C. Partridge, N. Shectman. *Packet reordering is not pathological
network behavior*. IEEE/ACM Transactions on Networking 7(6):789–798, Dec 1999 (cited in
http://conferences.sigcomm.org/imc/2002/imw2002-papers/197.pdf) — S. Jaiswal, G. Iannaccone,
C. Diot, J. Kurose, D. Towsley. *Measurement and Classification of Out-of-Sequence Packets
in a Tier-1 IP Backbone*. IEEE INFOCOM 2003. PDF:
https://infocom2003.ieee-infocom.org/papers/29_04.PDF (journal version: IEEE/ACM ToN 2007,
https://ui.adsabs.harvard.edu/abs/2007ITNet..15...54J/abstract)

**Key numbers ([Observed], Sprint tier-1 OC-48 traces):** the traces show a **relatively consistent
rate**. **~3–4% of TCP data packets arrive out of sequence**.

The split of those packets: **70.7% are retransmissions after
loss**. **20.2% are unneeded (duplicate) retransmissions**. **0.69% are network duplicates**. **5.1% are true
reorderings**. **3.35% are unknown**.

Only **13.6% of TCP connections experience any out-of-sequence
packet** (7.2–20.1% by trace). But those connections carry most of the bytes.
The central finding:
**out-of-sequence at the receiver is mostly loss in disguise**.
Reordering proper is rare in
a single-path tier-1 backbone. https://infocom2003.ieee-infocom.org/papers/29_04.PDF

**Why each exists:** Bennett et al. establish that reordering happens in real networks
(multi-path, parallel forwarding).
Reordering breaks the fast-retransmit heuristics of TCP.
This work comes before the
reordering-tolerant extensions (RFC 3708/SACK-RENEGING lineage).
Jaiswal et al. give the
classification method that turns "out of order" into a diagnostic.
**True reordering ⇒
ECMP/load-balanced fabric. Duplicate retransmits ⇒ lossy path + aggressive RTO.**
**[Inference]**

**2-h cert signal:** In the bench window, classify out-of-order TCP segments per flow.
Use sequence-gap + retrans-duplicate logic, or the reordering counters of TCP_INFO.
A rack on a
datacenter fabric with ECMP hashing can show genuine reordering.
Flag it, because
GB300-class traffic patterns (elephant flows) can hash onto one member link.
But sustained
duplicate-retransmit patterns point at loss upstream.
The Netalyzr population numbers give the
comparison point: 16–33% of access paths show *some* reordering under load.
http://conferences.sigcomm.org/imc/2010/papers/p246.pdf [Observed]

---

### 2.7 Passive TCP RTT estimation: Jiang & Dovrolis (CCR 2002), Veal et al. (PAM 2005)
**Citations:** H. Jiang, C. Dovrolis. *Passive estimation of TCP round-trip times*. ACM CCR
32(3):75–88, 2002 (cited in https://link.springer.com/chapter/10.1007/978-3-540-31966-5_10) —
B. Veal, K. Li, D. Lowenthal. *New Methods for Passive Estimation of TCP Round-Trip Times*.
PAM 2005, LNCS 3431. DOI 10.1007/978-3-540-31966-5_10.
https://link.springer.com/chapter/10.1007/978-3-540-31966-5_10 (cited by 178 per ACM;
a journal extension, *Improving passive estimation of TCP round-trip times using TCP
timestamps*, is listed at https://experts.arizona.edu/en/publications/improving-passive-estimation-of-tcp-round-trip-times-using-tcp-ti)

**Methods ([Observed] from the PAM chapter):** two passive methods recover an RTT series
for an existing flow without probes.
(1) **TCP timestamp pairing** matches data
segments to the ACKs that echo their timestamps.
This method stays robust when sequence-number matching is
ambiguous (e.g., delayed ACKs and window updates).
(2) **Segment-cluster/self-clocking
patterns** infer RTT from the periodicity of ack-clocked bursts.
Both methods track RTT *changes*
across the lifetime of a connection. So they see queueing growth as it happens.

**Why a certifier cares:** TCP timestamps pass through most NATs/middleboxes.
Modern stacks turn them on by
default (the kernel itself uses them for RTO).
So **every bench transfer
already carries a per-packet full-path RTT channel**.
The diagnostic comes free with the
throughput test.

This channel needs no separate ping stream that middleboxes can deprioritize.
The §3.4 flent tool
pairs pings with load for exactly this contrast. The §4.1 ndt7 tool harvests TCP_INFO instead.
**[Inference]**

**2-h cert signal:** Log `TCP_INFO` RTT (or ts-echo RTT from a capture) at sub-second
granularity during every object-store transfer.
That series, not a parallel idle ping, is
the ground truth for buffer delay (§1.6) and congestion signatures (§2.4.3).
Sample-size
honesty: the congestion-signatures work discards flows with <10 slow-start RTT samples.
A
60-s transfer yields thousands of samples. That is ample. [Inference]

---

### 2.8 PMTUD black holes: Luckie, Cho, Owens (IMC 2005) + Medina et al. (CCR 2005)
**Citations:** M. Luckie, K. Cho, B. Owens. *Inferring and Debugging Path MTU Discovery
Failures*. IMC '05. PDF (read in full):
http://conferences.sigcomm.org/imc/2005/papers/imc05efiles/luckie/luckie.pdf — A. Medina,
M. Allman, S. Floyd. *Measuring the evolution of transport protocols in the Internet*. ACM
CCR 35(2):37–52, 2005 (cited inside the Luckie paper).

**Key numbers ([Observed]):** Luckie et al. probe 147 jumbo-capable-network targets from two
US vantage points (Internet2/Abilene era).
Traceroute reaches 91–92.5% of them.
**30% of the
reachable targets show a forward-path PMTUD failure**.
The failures split into 7 no-ICMP-at-all
points and 22 no-PTB-message points.
16 of those sit at a 1500 B next-hop MTU (classic over-filtering
of ICMP Destination Unreachable).

There are also 2 points with an **incorrect next-hop MTU**.
There, the router suggests 4586 B when
4472 B is the truth.
The last group is 7 target-side MTU mismatches.

**Medina et al. (reverse path, TCP
handshake-probing era):** PMTUD fails for 17% of 81,776 web-server targets.
It fails for 35% of the 500
most popular websites.

The papers catalog these failure modes.
Some routers do not send PTB (the ICMP
black hole of RFC 2923).
Some middleboxes filter PTB.
Some PTB messages carry an unset/larger-than-trigger next-hop MTU.
Some MTU mismatches across switches stay invisible to IP.
Ingress filters drop the ICMP of RFC 1918-numbered interfaces. http://conferences.sigcomm.org/imc/2005/papers/imc05efiles/luckie/luckie.pdf

**Tooling:** the paper introduces the PMTUD debugging of **scamper**.
First, scamper runs traceroute with small probes
for topology.
Then scamper runs an MTU-table-guided (not blind binary) search that solicits PTBs.
Then scamper sends
**TTL-limited large probes to localize the exact hop** that silently drops oversized packets.
Their worked example converges (location + MTU) in ~14 probes. [Observed]

**2-h cert signal:** PMTUD hygiene is cheap and high-yield.
For each object-store endpoint,
verify 1500 B with DF set in both directions.
Also verify jumbo if the DC fabric uses it.
If a
failure appears, run the scamper-style next-hop-MTU + TTL search to localize it.
The failure
mode matters for triage: filter vs mismatch vs misconfigured PTB.

Do **not** trust small-ping
traceroute alone.
The punchline of the Luckie paper: default ping/traceroute sizes never
trigger PMTUD failures.
So "connectivity OK" says nothing about 1500 B payload paths.
[Observed + Inference]

The Netalyzr population numbers (§2.1) say ~8–15% of real paths fail
fragmentation or DNS-MTU even today's-era predecessors. This is not a corner case.
[Observed] Modern mitigation reference: RFC 4821 (PLPMTUD, which TCP should fall back to).
RFC 8899 is PLPMTUD for datagram transports. https://datatracker.ietf.org/doc/html/rfc4821 ;
https://datatracker.ietf.org/doc/html/rfc8899

---

## 3. The bufferbloat line: how loaded latency becomes the headline metric

### 3.1 Gettys & Nichols — the bufferbloat identification
**Citations:** J. Gettys, K. Nichols. *Bufferbloat: Dark Buffers in the Internet*. ACM Queue
9(12), Dec 2011, https://queue.acm.org/detail.cfm?id=2071893 (also IEEE Internet Computing
15(3), 2011, https://www.computer.org/csdl/magazine/ic/2011/03/mic2011030096/13rRUwcAqtV) —
*Bufferbloat: What's Wrong With the Internet?* (V. Cerf with V. Jacobson, N. Weaver, J.
Gettys), CACM 55(1), Jan 2012, https://cacm.acm.org/practice/bufferbloat-whats-wrong-with-the-internet
— the ongoing essay series: https://www.bufferbloat.net/projects/bloat/

**The claim ([Observed]):** excessively large, unmanaged buffers stay full under any bulk transfer.
These buffers sit in last-mile gear, home routers, and OSes.
They add seconds of latency.
The added latency destroys interactive traffic.
The added latency also defeats TCP's loss-based congestion avoidance.
The drops arrive
too late to be a timely congestion signal.

Netalyzr (§2.1) supplies the population evidence
(128/256 KB uplink buffers). The Gettys essays name the disease. They make **latency under
load** — not raw throughput — the user-visible definition of "bad internet." The Cerf/Jacobson
interview states the framing rack-bench should adopt: *"if you look at your own situation in
terms of time rather than capacity... you ought to be able to cut your delay by half."*
https://cacm.acm.org/practice/bufferbloat-whats-wrong-with-the-internet

**2-h cert signal:** idle latency is not a quality claim.
Pair every latency statement with its loaded counterpart (§3.4). [Inference]

---

### 3.2 CoDel (Nichols & Jacobson, ACM Queue/CACM 2012; RFC 8289) and fq_codel (RFC 8290)
**Citations:** K. Nichols, V. Jacobson. *Controlling Queue Delay*. ACM Queue 10(5), 2012 /
CACM, https://cacm.acm.org/practice/controlling-queue-delay — RFC 8289 (CoDel AQM),
https://datatracker.ietf.org/doc/html/rfc8289 — RFC 8290 (fq_codel),
https://datatracker.ietf.org/doc/html/rfc8290

**Method ([Observed]):** CoDel discards queue-length heuristics entirely.
CoDel timestamps every packet and tracks **sojourn time**.
CoDel watches the **minimum sojourn over the last interval (default
100 ms)**. If that minimum stays above the target (default 5 ms), CoDel enters controlled dropping.

CoDel has two parameters, both time-based.
CoDel needs no link-rate knowledge.
The paper's sensitivity analysis: below a 5 ms target
utilization suffers. Above 5 ms, there is little utilization gain.

**fq_codel** (RFC 8290)
adds per-flow hashing + a sparse-flow priority.
A ping coexisting with an elephant flow
does not queue behind it.
Linux makes fq_codel the default qdisc from the 3.5 era onward.
fq_codel is also the mechanism behind
"sub-5-ms jitter under load" observations on modern links.
The flent author notes that
20 Mbps uplinks with fq_codel/CAKE show strings of RRUL results.
The added latency is sub-5-ms (https://blog.cerowrt.org/post/flaws_in_flent).

**Why this matters to measurement:** CoDel changes what loaded latency **should** be. A 2010
link legitimately bloated to 1 s under load. An AQM'd link holds <10–30 ms. So rack-bench's
loaded-latency PASS bar is not a constant. State it against the AQM era (§7).
**[Inference]**

**2-h cert signal:** if the rack/DC egress shows buffer delay >~5–20 ms, that is *your* queue.
The bench's own load produces this delay.
The first-hop DC switch is the other suspect.
The DC operator should apply the RFC 8289/8290
defaults as the tuning reference. [Inference]

---

### 3.3 Høiland-Jørgensen et al. — "The Good, the Bad and the WiFi" (Computer Networks 2015)
**Citation:** T. Høiland-Jørgensen, P. Hurtig, A. Brunstrom. *The Good, the Bad and the WiFi:
Modern AQMs in a residential setting*. Computer Networks 89:90–106, Oct 2015 (citation as
listed in the author's PhD thesis, which bundles this line of work:
https://bufferbloat-and-beyond.net/static/bufferbloat-and-beyond.pdf). Venue note: this is a
Computer-Networks journal paper, **not** an IMC'15-area paper — see §9.

**Findings ([Observed] per the thesis-attached paper list):** the paper evaluates CoDel, fq_codel, PIE
and friends.
The tests run in a real residential setting (including the WiFi last hop).
The AQMs keep
latency-under-load low even when the bottleneck is the WiFi link itself.
fq_codel's flow
isolation gives the best latency/throughput trade.
This empirical validation makes fq_codel the CPE default.

The same author's *Measuring Latency Variation in the Internet*
(CoNEXT '16) is the companion measurement-methods paper.
It shows how to quantify latency variation
defensibly. This is the statistical basis for flent's plots. https://bufferbloat-and-beyond.net/static/bufferbloat-and-beyond.pdf

**2-h cert signal:** none beyond §3.2's bar-setting.
The citation serves the evidentiary chain.
AQM
efficacy is field-proven. So demanding low loaded latency from a modern DC uplink is fair.
[Inference]

---

### 3.4 flent (ValueTools 2017) + the RRUL test family: the reusable loaded-latency bench
**Citations:** T. Høiland-Jørgensen et al. *Flent: The FLExible Network Tester*. ValueTools
2017 (citation per https://bufferbloat-and-beyond.net/static/bufferbloat-and-beyond.pdf;
tool and docs: https://flent.org, test catalog: https://flent.org/tests.html) — RRUL chart
explainer: https://www.bufferbloat.net/projects/bloat/wiki/RRUL_Chart_Explanation — RRUL
origin note by D. Taht (spec originator, at https://blog.cerowrt.org/post/flaws_in_flent).

**What RRUL is ([Observed], https://flent.org/tests.html):** *Realtime Response Under Load*.
The test saturates the link with **eight TCP streams (four up, four down)**, historically one per
diffserv class.
It simultaneously measures RTT with **ICMP ping + UDP round-trip**; "this
quite reliably saturates the measured link (wherever the bottleneck might be), and thus
exposes bufferbloat when it is present."

Variants the bench can reuse: **rrul** (classed).
**rrul_be** (all best-effort — the one to use against object stores that reset DSCP).
**rrul_icmp** (ICMP-only latency under load).
**rrul_noclassification**.
The family also has tcp_ndown
single-direction variants and IPv4/v6 mixed variants (https://flent.org/tests.html and
https://www.candelatech.com/cookbook/wifire/UE_Testing_Using_flent_to_Generate_Traffic).

**Provenance worth citing in the certificate:** **Comcast** commissions the RRUL spec
("something nasty and simple and torrent-like") to find its own bufferbloat.
The flent tool puts the spec into practice.
Comcast uses the test to improve its network.
The test has an operator-grade pedigree, not just
an academic one. [Observed] https://blog.cerowrt.org/post/flaws_in_flent

**Sample-size honesty:** RRUL runs typically take 60–120 s.
flent's own reporting convention
aggregates repeated runs.
**[Calculation]** a 60-s run at 10 Hz ping sampling yields 600 RTT
samples under load.
That is enough for a stable mean and p95 of *added* latency, marginal for p99
(§2.5). Repeat 3–5×. [Inference]

**2-h cert signal:** run a `flent rrul_be`-equivalent against a bench peer for 3–5 × 60–120 s per direction.
A hand-rolled 4+4-stream load + 10 Hz
ping + TCP_INFO RTT series also works.
Report
**added latency (mean, p95, max) vs the idle baseline**, plus throughput achieved.
This is
the buffer-delay metric of RFC 6349 (§1.6), measured continuously rather than as a single
average. [Inference]

---

### 3.5 Loaded latency goes mainstream in measurement programs
The bufferbloat line ends up *inside* the regulator/industry measurement stack.
This is why
rack-bench can treat loaded latency as a first-class cert metric, not an activist one:
- The FCC MBA's 18-metric suite includes a **delay-under-load** metric.
  The retrospective
  explicitly notes it "will reflect buffering in the home access router, including any buffer
  bloat" when run idle-only. [Observed] https://vtechworks.lib.vt.edu/server/api/core/bitstreams/ba422301-2a83-439c-9ba0-0203f0d548a2/content
- Comcast deploys AQM at scale and publishes the latency analysis. [Observed]
  (Flickinger, Klatsky,
  Ledesma, Livingood, Ozer, *Improving Latency with Active Queue Management (AQM) During
  COVID-19*, arXiv:2107.13968, 2021, https://arxiv.org/abs/2107.13968)
- flent/RRUL's Comcast provenance (§3.4). [Observed]

---

## 4. Congestion control as measurement

### 4.1 BBR (Cardwell, Cheng, Gunn, Yeganeh, Jacobson — Queue 2016 / CACM 2017)
**Citation:** N. Cardwell, Y. Cheng, C. S. Gunn, S. H. Yeganeh, V. Jacobson. *BBR:
Congestion-based congestion control*. ACM Queue 14(5), Sept–Oct 2016, and Communications of
the ACM 60(2):58–66, Feb 2017 (citation as referenced in
https://conferences.sigcomm.org/imc/2017/papers/imc17-final99.pdf; full text:
https://cacm.acm.org/magazines/2017/2/212428-bbr-congestion-based-congestion-control/fulltext).

**The model ([Observed]):** BBR discards loss-as-congestion-signal.
BBR instead **explicitly
measures the two path parameters**. **BtlBw** is the bottleneck bandwidth, via a max-filter on
delivery-rate samples. **minRTT** is the minimum RTT, via a min-filter over a windowed RTT series.
BBR then
paces at BtlBw with a modeled inflight ≈ BDP.

The CACM paper's framing: loss-based control —
even best-of-breed CUBIC — is the primary cause of bufferbloat.
It is also the primary cause of throughput collapse on
shallow-buffer/high-RTT paths. The reason: "full buffer" and "packet loss" are the wrong signals.

**How the model doubles as a path diagnostic ([Inference], grounded in the ndt7 design,
https://www.measurementlab.net/blog/ndt7-introduction):**
- **BtlBw is an available-bandwidth estimator** with a decade of kernel deployment.
  Say a BBR
  flow to S3 settles at X Mbps while the committed rate is Y > X.
  The gap is *not* window-
  sizing and *not* slow-start transients. It is a real rate limit (policer, shaper §2.4.1,
  or congestion).
- **minRTT is a baseline-latency estimator** — the cleanest idle-path RTT the path offers.
  BBR harvests it *during* a bulk transfer. `ndt7` exports exactly `BBRInfo.BW` and `BBRInfo.MinRTT`
  per measurement. [Observed] https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md
- **The BBR/CUBIC throughput differential is a loss detector**: loss events govern CUBIC's
  window. BBR ignores them (up to a threshold). On a path with non-congestion random
  loss, CUBIC throughput collapses while BBR does not. Measuring both quantifies the loss
  the path imposes at full rate. [Inference] (The ndt7 design notes phrase the same logic:
  BBR's expected speed on an unloaded network is "the bitrate of the slowest hop,"
  https://www.measurementlab.net/blog/ndt7-introduction.)

**Caveat ([Observed]):** BBR confuses delay-based and signature-based diagnosis.
The IMC '17
signatures paper explicitly warns: its RTT-variation technique breaks under BBR.
The reason: BBR
controls the buffering it reads (§2.4.3). So: **use BBR flows to measure the path's limits,
use CUBIC flows to run the diagnostic signatures.** [Inference]

**2-h cert signal:** run one 60-s BBR flow + one 60-s CUBIC flow per endpoint/direction.
Log
`ss -i`/TCP_INFO (delivery rate, RTT, retrans, pacing). The pair yields (a) path capacity via
BBR, (b) loss-imposed ceiling via the CUBIC/BBR ratio, (c) minRTT baseline. [Inference]

---

### 4.2 CUBIC (Ha, Rhee, Xu — SIGOPS OSR 2008; RFC 8312/9438) + Mathis's macroscopic model (CCR 1997)
**Citations:** S. Ha, I. Rhee, L. Xu. *CUBIC: A New TCP-Friendly High-Speed TCP Variant*.
ACM SIGOPS Operating Systems Review 42(5):64–74, 2008. DOI 10.1145/1400097.1400105 (per
RFC 9438's reference list, https://www.rfc-editor.org/info/rfc9438; PDF:
https://www.cs.ucr.edu/~jiasi/teaching/cs204_spring17/papers/cubic08.pdf) — standardized as
RFC 8312 (2018), obsoleted by RFC 9438 (Aug 2023), https://www.rfc-editor.org/info/rfc9438 —
M. Mathis, J. Semke, J. Mahdavi, T. Ott. *The macroscopic behavior of the TCP congestion
avoidance algorithm*. ACM CCR 27(3):67–82, 1997 (citation per
https://www.usenix.org/system/files/nsdi24-agarwal-anup.pdf).

**Venue note (task brief asked):** CUBIC's peer-reviewed home is **SIGOPS OSR 2008**.
The researchers find no IEEE/ACM ToN journal version of CUBIC in the authors' records. Google Scholar lists
OSR'08 + the two RFCs (https://scholar.google.com/citations?user=ns_6BgMAAAAJ&hl=en). The
standards-track documents are the RFCs. See §9.

**What sustained CUBIC behavior reveals:** [Observed] for the model; **[Calculation]** for the
inversion. CUBIC grows its window as a cubic function of time-since-loss. CUBIC cuts ~30% per
loss event. The steady sawtooth therefore *encodes the loss rate the path imposes at full
rate*.

Mathis's macroscopic equation for Reno-style AIMD gives an upper bound
**BW ≤ (MSS/RTT)·C/√p** with C≈√(3/2). An observed Reno/CUBIC throughput T on a path
with MSS and RTT enables the inversion. The inversion implies an effective loss floor **p ≈ (3/2)·(MSS/(RTT·T))²**.

**[Calculation]** e.g., MSS 1448 B, RTT 30 ms, sustained 2 Gbps. p ≈ 1.5×(1448/(0.03×2×10⁹/
8))² ≈ 1.5×(1448/7.5×10⁶)² ≈ 5.6×10⁻⁸. Take throughput far below the BBR-measured
capacity with a *tiny* implied p. The limiter is then not steady-state loss but something
else (window, policer, congestion windows of a shared bottleneck). A large implied p (>1e-3)
means the path is genuinely loss-limited.

CUBIC is more loss-tolerant than Reno. So treat the
Mathis p as a **lower bound on the true loss-imposed penalty**. Cross-check against
TCP_INFO retransmit counts (RFC 6349's TCP Efficiency, §1.6). [Inference]

**2-h cert signal:** combine the CUBIC/BBR differential (§4.1) with the Mathis inversion.
This gives the
certificate a *causal* sentence, not just a number.
"egress to S3 Mumbai sustains X Gbps with
efficiency 99.9% and implied loss floor p≈…; the limiter is the committed rate / is upstream
congestion / is window configuration." [Inference]

---

## 5. Regulator-grade measurement programs

### 5.1 FCC Measuring Broadband America (SamKnows whiteboxes)
**Citations:** FCC, *Measuring Broadband America* program pages:
https://www.fcc.gov/general/measuring-broadband-america (open methodology:
https://www.fcc.gov/oet/mba/measuring-broadband-america-open-methodology); Eleventh Report
(2021, incl. COVID-19 analysis):
https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-eleventh-report;
Thirteenth Report (2024): https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-thirteenth-report;
first MBA report PDF: https://www.measurementlab.net/publications/FCC_MBA_2011.pdf; retrospective:
E. Burger, P. Krishnaswamy, H. Schulzrinne, *Measuring Broadband America: A Retrospective on
Origins, Achievements, and Challenges*, ACM CCR 53(2), 2023,
https://vtechworks.lib.vt.edu/server/api/core/bitstreams/ba422301-2a83-439c-9ba0-0203f0d548a2/content (read in full).

**Architecture (all [Observed], retrospective + reports):** SamKnows "Whitebox" hardware
runs custom OpenWrt firmware.
Each unit is an Ethernet bridge in front of the home gateway.
Test agents sense household traffic and **only measure when the line is idle**.
This removes cross-traffic as a confounder.

Off-net test servers sit at **10 major interconnects**.
The tests measure every ISP against the same, near-edge server set.
The program randomizes measurements across six 4-hour windows per day.

In 2021: **5,951 whiteboxes deployed, 2,488 used for the report dataset**.
The minimum is **45 agents per tier** for statistical validity.
The program validates the panel per service tier (4% of volunteers misidentify their ISP in the first report).

The program releases the test source code under the GPL in the early years.
The program publishes raw data quarterly.

**The metric definitions rack-bench can lift verbatim (all [Observed]):**
- **Download/upload throughput:** multi-flow TCP. Flows grow **3 → 8**. Duration shrinks
  **30 s → 10 s**. The test retains **the last five seconds of the 10-second test** — an
  explicit slow-start discard policy. https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-thirteenth-report
- **Latency and packet loss:** "approximately **2,000 packets per hour** sent at randomly
  distributed intervals; response times **less than three seconds** count toward mean
  latency; if the whitebox does not receive a response within three seconds, the packet is
  counted as lost" — the T_max conditional-loss rule straight out of RFC 2680. https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-eleventh-report
- **Peak period = weeknights 7 p.m.–11 p.m. local**; all headline findings scoped to peak.
- **The 80/80 consistency metric:** "the minimum percentage of the advertised speed
  experienced by at least 80% of subscribers for at least 80% of the time over peak periods"
  — a distributional, not mean-based, pass rule. https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-thirteenth-report
- Longitudinal measured/advertised ratios: **82% (2011) → 87% (2012) → 96–97% (2013)**
  (retrospective). [Observed]

**The Bauer/Clark/Lehr critique (2010):** S. Bauer, D. Clark, W. Lehr, *Understanding
Broadband Speed Measurements*, TPRC 2010,
https://groups.csail.mit.edu/ana/Publications/Understanding_broadband_speed_measurements_bauer_clark_lehr_TPRC_2010.pdf
(read in part).

Its core points ([Observed]): speed-test results are methodology artifacts.
Single vs parallel flows, slow-start handling, and test-server placement all shift the number.
TCP receive-window limits and **PowerBoost-style burst head-starts** shift it too.
The Ookla/Speedtest style "typically results in higher measured data rates than the other approaches".
The same access service can measure anywhere across a wide band depending on these choices.
One must state what question the measurement answers.

The MBA program demonstrably absorbs the critique.
The program adopts the Bauer-suggested subdivided throughput interval to expose PowerBoost.
The program retires it after PowerBoost's deprecation.
The program then re-bases on idle-only whiteboxes, with published technical appendices. [Observed] retrospective §3.7.

The critique's afterlife in the MBA retrospective also names its structural limits honestly.
The limits: metrics not traceable to IPPM standards, and source code no longer open.
Idle-only tests understate real user experience.
A single whitebox may represent a state.
[Observed] https://vtechworks.lib.vt.edu/server/api/core/bitstreams/ba422301-2a83-439c-9ba0-0203f0d548a2/content

**Comcast's side of that exchange:** the researchers find no stand-alone verbatim "Comcast
rebuttal" document to Bauer/Clark/Lehr in any index. See §9.

What is verifiably documented:
Comcast's engagement in the MBA Collaborative process.
Comcast commissions the RRUL spec to expose its own bufferbloat (§3.4).
Comcast publishes the AQM deployment analysis (arXiv:2107.13968).

The later WSJ investigation is *Your Internet Provider Likely Juiced
Its Official Speed Scores* (Nov 2019).
The retrospective cites it (https://www.wsj.com/articles/its-hard-to-trust-the-numbers-internet-providers-inflate-official-speed-results-11576171855).
It shows providers can influence test traffic handling on regulator platforms.
It also documents actual influence.

The retrospective documents the MBA design's countermeasure (code of conduct + control
servers not part of the program). [Observed]
Related synthesis: N. Feamster, J. Livingood, *Measuring Internet Speed: Current Challenges
and Future Recommendations*. CACM 63(12):72–80, 2020, DOI 10.1145/3372135. [Observed]

**2-h cert signal:** copy the *design* choices, not the timescale.
Use idle-detection before measuring.
Use multi-flow TCP. Discard the first half of each transfer.
Apply explicit peak-hour scoping and distributional pass rules (80/80-style).
Draw latency/loss from a Poisson-scheduled small-packet stream with a stated T_max.

Sample-size honesty: the FCC's numbers are monthly aggregates over thousands of boxes.
A 2-hour rack window certifies the window. Say so.
Prefer percentile framing (80/80) over means even with fewer samples. [Inference]

---

### 5.2 Ofcom / SamKnows UK (the model for MBA)
**Citation:** Ofcom, *UK Home Broadband Performance* (technical report; the 2023 vintage is
the seventeenth fixed-line report of this series):
https://assets.ctfassets.net/aycrbiawo3x3/3TxKFHyW0dUorSoFl0gsZ3/de714fba2fd40ac38f4d604ee98b06a0/uk-home-broadband-performance.pdf
and https://www.ofcom.org.uk/siteassets/resources/documents/research-and-data/broadband-research/broadband-speeds/home-broadband-performance-september-2023/annex-march-23-home-broadband-performance.pdf

**Method ([Observed]):** Ofcom uses the same SamKnows whitebox platform.
Ofcom precedes the FCC as SamKnows' first regulatory client.
The MBA first report notes SamKnows "had recently
completed a similar study... for Ofcom," (https://www.measurementlab.net/publications/FCC_MBA_2011.pdf).
The panel consists of UK residential volunteers.
Reporting is package-specific.

Current versions also embed
the test suite directly into ISP CPE firmware (Router SDK) with cross-traffic detection.
The methodology converges on always-on, in-router measurement.

The SamKnows regulatory deployments span the EC, Singapore IDA, Canada CRTC, and Brazil Anatel.
Source: https://www.edgeconnex.com/wp-content/uploads/2018/11/SamKnows-EdgeConneX-FINAL-20151230.pdf
The Ofcom UK series plus these deployments make this the de-facto global template.
The template is whitebox panel + per-package percentile reporting.

**2-h cert signal:** same as §5.1.
The Ofcom line adds a trend: the "whitebox" is dissolving into infrastructure.
Rack-bench makes exactly this move for the datacenter side.
[Inference]

---

### 5.3 M-Lab NDT: web100 → ndt5 (TCP_INFO/CUBIC) → ndt7 (BBR, WebSocket/TLS)
**Citations:** M-Lab NDT tool page (protocol history, read):
https://www.measurementlab.net/tests/ndt — ndt7 protocol specification (read):
https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md — ndt7 design blog:
https://www.measurementlab.net/blog/ndt7-introduction — data-transfer-cap study:
https://www.measurementlab.net/blog/short-ndt

**What NDT measures ([Observed]):** NDT is a **single-stream TCP measurement of "bulk transport
capacity"** in RFC 3148's sense.
It measures upload and download speed plus latency metrics.

The protocol
history: web100-instrumented kernels (data from 2009; archived as
`measurement-lab.ndt.web100`). Then comes **ndt5** on TCP_INFO with **CUBIC** (from 2019-07-18).
Then comes **ndt7** (from 2020-02-18).

That version uses WebSocket/TLS on standard 80/443 ports and a single TCP
connection. It uses **BBR where available** (falling back to CUBIC).
Both endpoints emit per-sub-second TCP_INFO and
BBRInfo records (`BW`, `MinRTT`). [Observed]
https://www.measurementlab.net/tests/ndt ;
https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md

**How loaded latency entered NDT ([Observed]/[Inference]):** ndt7 does not run a separate
"loaded latency" phase. Instead, the saturating single BBR stream *is* the load.
The client samples the RTT series (TCP_INFO `RTT` and BBR `MinRTT`) during the transfer.
This gives loaded-RTT evolution inside every test.

The older web100 NDT runs 10-s inbound and
outbound tests and middlebox checks.
Its well-known CLI output advises on buffers and congestion state.
See sample output: https://netbeez.net/blog/measuring-internet-speed-via-ndt
**[Inference]** This is the same trick as §2.7: the transfer carries its own RTT channel.

**Accuracy scaling honesty ([Observed]):** M-Lab's own study examines capping NDT transfers.
It finds consumer speeds >250 Mbps (≈9% of contributors) strain a 10-s single-stream design.
The platform publicly grapples with "accuracy vs download cap," i.e., how many seconds/bytes a
speed measurement needs at multi-gigabit rates.

For a rack certifying 10–100 Gbps-class
north-south, **[Inference]** a 10-s single stream is not enough.
rack-bench needs BDP-sustained multi-flow runs (§1.6).
NDT's own scaling debate is the published precedent for that claim.

**2-h cert signal:** ndt7's design is a clean blueprint for the bench's
object-store transfers.
The design uses standard ports, a single connection, and kernel TCP_INFO at
sub-second granularity. It also exports BBR BtlBw/minRTT.
The ndt-server tool is open source and deploys privately
(https://www.measurementlab.net/blog/run-a-private-ndt-server). [Observed + Inference]

---

### 5.4 RIPE Atlas: embedded probes as continuous path evidence
**Citations:** RIPE NCC, *How RIPE Atlas works*: https://www.ripe.net/analyse/internet-measurements/ripe-atlas/how-ripe-atlas-works — probe/anchor program overview (ISOC, 2016):
https://www.internetsociety.org/resources/doc/2016/ripe-atlas-probes-and-anchors — fleet
statistics and a day of usage (KOR Labs, 2026):
https://korlabs.io/blog/day-in-the-life-of-ripe-atlas — MBA retrospective's comparison of
RIPE Atlas vs MBA (scope: ISP operations/research vs consumer access):
https://vtechworks.lib.vt.edu/server/api/core/bitstreams/ba422301-2a83-439c-9ba0-0203f0d548a2/content

**What it is ([Observed]):** RIPE Atlas is a fleet of volunteer-hosted hardware probes.
The fleet has ~**13,421 connected probes**
and ~**920 anchors** as of Feb 2026 per KOR Labs. It covers ~170 countries as of 2022 per the
MBA retrospective. The probes continuously run built-in **ping, traceroute, DNS, NTP, SSL/TLS, HTTP**
measurements. **All results are open data**, queryable per measurement, per probe, per
country/ASN. The project publishes daily dumps at ftp.ripe.net.

Anyone can run ad-hoc measurements (from 100
random probes for ping / 5 for traceroute in the "instant" mode).
Runners pay with credits. Credits come from hosting probes or from public grants.
The CLI supports e.g. "an IPv6 ping from every probe in
India" in one command.

**What an operator can get for free about Chennai/India paths ([Observed] capabilities +
[Inference] application).**
(a) *third-party reachability of the rack's prefix from Indian and global probes*.
This gives Hubble-style §2.2 direction coverage, without spoofed probes.
(b) *AS-
path history* toward the object stores from Indian vantage points.
TraceMON renders path
changes over time (https://atlas.ripe.net/docs/tools-and-code/tracemon).

(c) *RTT baselines
to specific PoPs/anchors*.
The operator can compare the rack's measured latency against a crowd
prior.

Caveat: the researchers find no published count of currently-connected probes specifically
in India. The live query is the source of truth (see §9).

**2-h cert signal:** run (or reuse) RIPE Atlas ping +
traceroute measurements during and after the bench window.
Target the rack's public IPs from India-tagged and global probes.
This gives continuous inter-window evidence.
An always-on monitor then anchors the 2-hour PASS, not a stand-alone result.
[Inference]

---

## 6. Longitudinal and regional findings

### 6.1 Diurnal congestion: the evening peak is the real test window
**Evidence:**
- **FCC MBA (all reports):** "Broadband performance varies with the time of day. At peak
  hours, more people are attempting to use their broadband... Unless otherwise stated, this
  Report focuses on performance during peak usage period, which is defined as weeknights
  between 7:00 p.m. to 11:00 p.m. local time." [Observed]
  https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-eleventh-report
- **The Cogent peering dispute of 2014 (M-Lab NDT data, IMC '17 paper):** the collapse is diurnal.
  NDT throughput from
  Cogent-hosted servers to Comcast/TimeWarner/Verizon customers shows a strong diurnal
  collapse during evening peak, Jan–Feb 2014. The collapse disappears in Mar–Apr, after Cogent
  relieves congestion and Comcast-Netflix peering changes. Cox (which has direct Netflix
  peering) shows no diurnal pattern throughout. [Observed]
  https://conferences.sigcomm.org/imc/2017/papers/imc17-final99.pdf
- **Sundaresan et al. (SIGCOMM 2011), *Broadband Internet Performance: A View from the
  Gateway* (BISmark):** a gateway view. It is the first gateway-resident study (hundreds of homes, FCC/SamKnows data +
  BISmark OpenWrt routers). The study finds diurnal throughput/loss/latency structure.
  It documents per-modem
  bufferbloat (second-scale RTT inflation in a Comcast user's trace).
  It documents interleaving trade-offs
  in DSL (lower loss, higher latency). It concludes that **average throughput alone misleads**,
  so the authors propose consistency metrics (Avg/P95). [Observed]
  https://conferences.sigcomm.org/sigcomm/2011/papers/sigcomm/p134.pdf
- The IMC '17 "Challenges" paper codifies the diurnality assumption as a *precondition* for
  throughput-based congestion inference. [Observed]
  https://www.caida.org/catalog/papers/2017_challenges_inferring_internet_congestion/challenges_inferring_internet_congestion.pdf

**[Inference] for rack-bench (Chennai):** the equivalent peak for Indian residential
eyeballs is roughly **19:00–23:00 IST**.
This inference puts interconnect congestion at its worst then, if it throttles the rack's object-store paths. A 2-hour `bench internet` run at, say, 14:00
IST certifies the off-peak regime only. The certificate should state the window's IST time-
of-day. Worst-case certification should schedule loaded tests inside the evening peak.

---

### 6.2 COVID-19 stress tests of the internet
- **FCC MBA Eleventh Report (2021), COVID appendix:** the report uses March 1, 2020 as the pre-pandemic
  baseline. Download/upload speeds and packet loss hold steady through April 2020.
  **The one parameter that degrades is latency — by up to ~10% for a few ISPs**.
  Peak hours remain 7–11 p.m. [Observed]
  https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-eleventh-report
- **Feldmann et al., *The Lockdown Effect* (arXiv 2008.10959, 2020; CoNEXT version 2021):**
  one European ISP and its IXPs.
  **Traffic there rises 15–20% within ~a week** of lockdown (a change
  normally spread over months). Yet **peak-hour traffic rises by no more than ~5%**.
  The shock redistributes traffic across the day rather than breaking the peak.
  Remote-work (VPN/video) traffic explodes. Campus/education networks *lose* up to 55%. [Observed]
  https://arxiv.org/abs/2008.10959 (and "A year in lockdown," CoNEXT 2021,
  https://dl.acm.org/doi/10.1145/3465212)
- **ITU Broadband Commission chapter (2021):** total international Internet traffic: +48%.
  Peak traffic: +47%. Some local/regional networks show +60% downstream/upstream during peak.
  International capacity grows 35%. [Observed]
  https://www.itu.int/itu-d/reports/broadbandcommission/2021/09/13/chapter-two
- **Comcast's AQM/latency analysis during COVID** (arXiv:2107.13968): the traffic surge serves as a natural experiment.
  The largest US cable operator validates that AQM holds latency
  flat while volume grows. [Observed] https://arxiv.org/abs/2107.13968

**[Inference]:** the collective COVID finding supports rack-bench's metric ordering.
The finding: big volume shifts, mild aggregate
degradation, latency the first thing to move.
Latency (idle + loaded) and loss are the sensitive early indicators. Raw throughput is the
blunt one. A cert that measures only "can we pull 10 Gbps" tests the least sensitive
parameter.

---

### 6.3 India / South Asia specific
- **TRAI (the Indian regulator), *Standards of Quality of Service of Access (Wireline and
  Wireless) and Broadband (Wireline and Wireless) Service Regulations, 2024* (06 of 2024),
  effective 1 Oct 2024:** the regulation consolidates the 2006/2009/2012 QoS regulations and mandates QoS
  publication by providers.
  **Latency benchmarks align to global standards, and new parameters
  cover jitter and packet-drop rate. Measurement changes from average to
  percentile basis.** This covers downlink/uplink packet drop rate, latency, PoI congestion, and
  download/upload speed "to enable identification of pockets of degraded QoS". The regulation prescribes
  "detailed and unambiguous measurement methodology". The regulation sets graded financial disincentives for
  continued non-compliance. [Observed] PIB release:
  https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2040889 ; regulation index:
  http://www.trai.gov.in/telecom/qos
  - **[Inference]:** India's regulator independently arrives at the percentile-based,
  latency/jitter/loss-inclusive measurement philosophy this whole brief documents.
  This is useful
  framing for an India-based certifier. But TRAI's benchmarks bind consumer ISPs, not
  datacenter circuits.
- **Prasad et al. (BITS Pilani Goa), *Analysis of Impartial Quality Measurements on Indian
  Broadband Connections* (2016):** Indian broadband QoS. The study draws on M-Lab NDT data.
  The paper reports summary
  statistics (era-dependent, early-2010s data). Mean throughput ~0.5 Mbps, jitter
  ~57 ms, **latency ~427 ms**, packet loss ~4.6%. The study also shows a significant increase in throughput
  over the study period. [Observed]
  https://www.measurementlab.net/publications/2016-Prasad-et-al.pdf
  - **[Inference]:** the absolute numbers are stale, but the methodological point is not.
  M-Lab NDT data for India is public and large. rack-bench can pull India-region NDT/ndt7
  aggregates as a crowd prior for consumer-side conditions (not for the DC's carrier path).
- **RIPE Atlas in India:** the researchers locate no published India-specific probe count (§9). RIPE documents live
  capability (probe selection by country/ASN, §5.4). [Observed capability]
  https://www.ripe.net/analyse/internet-measurements/ripe-atlas/how-ripe-atlas-works
- **Academic Chennai/India datacenter-egress studies:** the researchers locate none in indexed literature —
  see §9 Gaps. IIT-authored internet-quality measurement studies at the level of the US/EU
  canon do not surface under these searches.

---

## 7. Which measurement findings change industry practice

| Finding / standard (source) | Industry change it drove |
|---|---|
| IPPM metric lattice: Type-P singletons, Poisson sampling, reported error (RFC 2330 and children, §1) | Every serious measurement platform (SamKnows/FCC, Ofcom, M-Lab) reports samples+percentiles with stated methodology. The MBA retrospective explicitly frames regulator metrics against IPPM (§5.2.2 notes the remaining gap). |
| RFC 6349's TTR / TCP-efficiency / buffer-delay triple (§1.6) | Carrier/enterprise turn-up test equipment converges on it (JDSU/VIAVI, Xena, GL, Netrounds all ship RFC 6349 modes). It is the industry-standard way to say *why* a TCP path underdelivers. |
| Y.1564's config-test + 1-hour CIR soak (§1.8) | Replaces RFC 2544 as the Ethernet-service activation standard for carriers (EtherSAM mode in every field tester). |
| Netalyzr's population pathologies: 128/256 KB access buffers, DNS-MTU/PMTUD black holes, NXDOMAIN wildcarding (§2.1) | The diagnostic-suite template for consumer tools. Its bufferbloat numbers seed the AQM crusade. The industry prioritizes DNSSEC deployment fixes after its EDNS/MTU findings. |
| Hubble: reachability failures persist for hours and don't show in BGP (§2.2) | Continuous data-plane reachability monitoring (vs BGP-only) is now standard practice. Hubble-line tooling (LIFEGUARD, Trinocular-style outage detection) puts it into practice. |
| Bufferbloat essays + Netalyzr + Dischinger-era measurements (§3.1) | "Latency under load" replaces raw throughput as the headline home-internet quality metric. Test suites (RRUL/flent) standardize it. |
| CoDel/fq_codel (Queue 2012; RFC 8289/8290) + WiFi-era validation (§3.2–3.3) | fq_codel is the Linux default qdisc. DOCSIS-era CPE carries mandated AQM, and Comcast deploys it at scale. Loaded-latency expectations collapse from seconds to milliseconds. |
| BBR's BtlBw+minRTT model (§4.1) | Congestion control *as instrumentation*: M-Lab rebuilds ndt7 around BBR. Google deploys BBR at YouTube/B4 scale. BBRInfo export is a measurement data schema. |
| Mathis macroscopic model / CUBIC (§4.2) | Loss-rate estimation from sustained throughput is textbook network triage. CUBIC is the Linux default and an Internet Standard (RFC 8312→9438). |
| The Tail at Scale (§2.5) | p99/p99.9 SLOs are the standard way latency contracts are written at scale. This is the frame a rack certifier should use for north-south latency. |
| FCC MBA / Ofcom whitebox programs (§5.1–5.2) | Open methodology + raw data + percentile (80/80) reporting is the regulator template worldwide. ISP transparency-rule compliance builds on it. Bauer/Clark/Lehr's critique institutionalizes methodology disclosure. |
| Sundaresan signatures + Luckie TSLP (§2.4.2–2.4.3) | Regulators (and the M-Lab/CAIDA ecosystem) gain cause-attributing congestion measurement. "who congested this path" is measurable from latency and flow data. |
| COVID-era longitudinal work (§6.2) | Latency/loss rises to early-warning metrics. Capacity planning shifts from peak-magnitude to peak-shape analysis. |
| TRAI 2024 QoS regulations (§6.3) | India's regime moves to percentile-based, jitter/packet-drop-inclusive, methodology-pinned reporting. This is the national backdrop an India-based certifier should align vocabulary with. |

---

## 8. Top 5 findings directly testable in a 2-hour `bench internet` certification run

The sections above back each finding. Each fits the window and yields a *causal* certificate sentence, not just
numbers. Each test states its own sample-size honesty.

1. **RFC 6349 TCP-throughput triple per object store (TTR, TCP efficiency, buffer delay), with
   BDP-sized windows.**

   Run the chain in order: MTU check, baseline RTT, BDP calculation, transfers.
   The BDP example: 1 Gbps×200 ms =
   25 MB. Run single + multi-connection 60-s transfers, both directions, ≥5 iterations.
   Apply last-half-of-run retention (MBA-style slow-start discard, §5.1).

   The three metrics triangulate
   the limiter. efficiency<100% ⇒ loss. Buffer delay high ⇒ standing queue. TTR high with
   both clean ⇒ window/rate limit. [§1.6; VIAVI worked example §1.6]
   - Budget: ~10 min per endpoint-direction; 3 object stores ≈ 60 min.
     Pass/fail: state thresholds per tier — TCP efficiency ≥99%, buffer delay ≤5–10% of baseline RTT,
     TTR ≤1.2. The certificate cites RFC 6349 as the definition source.

2. **RRUL-class loaded-latency (bufferbloat) test with idle baseline.**

   Use 4-up/4-down TCP best-effort (`rrul_be`-equivalent).
   Add 10 Hz ICMP and UDP RTT probes + TCP_INFO RTT series.
   Do 3–5 runs of 60–120 s per direction.
   Report *added* latency mean/p95/max vs idle, and
   throughput under load. flent ships it. Comcast's own deployment validates its
   real-world bite. [§3.4, §3.5, §1.6 buffer delay]
   - Budget: ~15–25 min total.
     Pass/fail: on an AQM-era path, expect single-digit-to-tens of ms
     added latency. Seconds-scale inflation = fail (the rack/DC queue is the suspect, §3.2).

3. **Sundaresan congestion signatures (NormDiff + CoV on slow-start RTT) per object-store
   path, run on CUBIC flows.**

   Discard flows with <10 slow-start RTT samples (the paper's own
   validity floor). Verdict per test: self-induced. The rack's committed rate is the bottleneck.
   This result meets the intended certification.
   The alternative is external congestion: an upstream/interconnect is full.
   This depends on the vendor or time of day. [§2.4.3]
   - Budget: ~1 min per classification; harvest from the §1.6/§4.1 transfers' packet captures.
     Honesty: 75–85% external-detection accuracy; gray zone exists.
     BBR flows must not serve this test (§2.4.3 caveat).
     A 2-hour window cannot measure the congestion *duty cycle*.
     Pair with TSLP-style continuous near/far interconnect pings (§2.4.2) during the window.
     Pair also with RIPE Atlas between windows (§5.4).

4. **Netalyzr/Lucker edge-pathology suite: PMTUD both directions + fragmentation + DNS
   forensics.**

   Send DF-set 1500 B (and 9000 B intra-fabric) probes each way with ICMP
   frag-needed accounting.
   Run scamper-style next-hop-MTU + TTL search on any failure (~14 probes
   to localize, §2.8). Test 2 KB fragmented UDP send/receive.
   DNS forensics: advertised EDNS vs actual
   resolver MTU (padded 1300/1700 B replies).
   Also check NXDOMAIN wildcarding, port randomization, and
   egress-port reachability for the bench's actual ports. [§2.1, §2.8]
   - Budget: ~10–15 min total; each verdict is categorical and cheap.
     Pass/fail: any PMTUD
     black hole or DNS-MTU < path MTU = fail (13–15% population rates mean this is not rare).
     Wildcarding by the DC's resolver = fail for a cert that claims clean DNS.

5. **BBR/CUBIC differential + Mathis inversion as the loss-imposed-ceiling estimator.**

   Run one
   60-s BBR flow and one 60-s CUBIC flow per endpoint-direction. Log delivery rate, RTT,
   retrans from TCP_INFO/BBRInfo. BBR's BtlBw gives the path's real rate limit.
   The CUBIC/BBR
   throughput gap plus the Mathis bound p ≥ (3/2)(MSS/(RTT·T))² turns sustained behavior into
   an effective-loss floor. Cross-check retrans counts = TCP efficiency. [§4.1, §4.2, §2.7]
   - Budget: ~2–4 min per endpoint-pair. Honesty: Mathis p is a bound for Reno-style AIMD.
     Under CUBIC, treat it as a lower bound on the penalty.
     Always corroborate with measured
     retransmissions. A 60-s window at 1e-5 loss rates sees <10⁴ packets.
     The *implied* loss
     estimate, not a counted rate, is what a short window can support.

**Honorable mentions (2-hour-adjacent):** TSLP interconnect near/far pings run continuously
across the window (§2.4.2). They localize any congestion found by #3 to a specific AS boundary.
An mtr path audit records the AS path per iteration and flags any change (§2.3).
Use p99/p99.9 framing for all latency reporting (§2.5). Use 80/80-style distributional pass rules (§5.1).

Schedule the loaded tests inside 19:00–23:00 IST (§6.1).
RIPE Atlas queries toward the
rack prefix from Indian probes give inter-window continuity (§5.4).

---

## 9. Gaps, corrections, and caveats

- **"Kanuparthy & Dovrolis, *Measuring Internet Congestion: A No-Man's Land Between Edge and
  Core*" (task brief) — not locatable.** No paper with this title (or the "no-man's land"
  phrase) surfaces in the researchers' searches. The search covers ACM/IEEE/USENIX indices, Google Scholar-visible listings, and the authors'
  publication records. The Kanuparthy–Dovrolis congestion/differentiation
  line that does exist: **DiffProbe** (INFOCOM 2010) and **ShaperProbe** (IMC 2011).

  The "congestion-signature
  successor" is real but belongs to others. The successors are **Luckie et al., IMC 2014 (TSLP)** and
  **Sundaresan et al., IMC 2017 (*TCP Congestion Signatures*)** (§2.4.2–2.4.3). The researchers find the acronyms
  **"LDCE/CLE" in no indexed paper**.
  The actual signature metrics are **NormDiff and CoV**.

  ShaperProbe PDF: https://conferences.sigcomm.org/imc/2011/docs/p473.pdf The brief flags a probable conflated/misremembered citation. The papers above give the evidence.
- **"SIGCOMM 2012" venue for the congestion-signature work — wrong.** The signatures paper is
  **IMC 2017** (SIGCOMM-affiliated conference, but 2017 not 2012). The neighboring
  congestion-inference papers are also IMC ('14, '17) plus a CAIDA operational paper (2018).
- **Comcast's rebuttal to Bauer/Clark/Lehr — not locatable verbatim.** The critique
  (TPRC 2010) carries full documentation (§5.1). Comcast's documented counterpart contributions follow.
  They are
  the MBA Collaborative engagement, the RRUL commission (§3.4), the AQM deployment paper
  (arXiv:2107.13968), and Feamster–Livingood CACM 2020.

  A specific Comcast rebuttal document
  to the MIT paper may exist in trade press or a blog. The searches do not surface it.
  If it
  matters, check it through the MBA Collaborative ECFS filings (referenced in the
  retrospective, https://vtechworks.lib.vt.edu/server/api/core/bitstreams/ba422301-2a83-439c-9ba0-0203f0d548a2/content).
- **Venue corrections from the task brief.** **iPlane is OSDI 2006**, not NSDI 2006 (NSDI '09
  is *iPlane Nano*; verified from the USENIX paper pages, §2.3). **flent is a ValueTools 2017
  paper**, not IMC-area (verified from the author's thesis bibliography, §3.4).

  **"The Good,
  the Bad and the WiFi" is a Computer Networks journal paper (vol 89, Oct 2015)**, not an
  IMC-area paper. The same thesis verifies it (§3.3). **CUBIC's peer-reviewed paper is
  SIGOPS OSR 42(5), 2008** — the researchers locate no IEEE/ACM ToN version. The standard-track homes
  are RFC 8312 (2018) and RFC 9438 (2023) (§4.2).

  **BBR is CACM 60(2):58–66, Feb 2017**
  (Queue 14(5) version Sept 2016). The brief's guess of CACM 2017 is right.
- **Veal et al. journal extension:** the record verifies the PAM 2005 paper (Springer LNCS 3431, DOI
  10.1007/978-3-540-31966-5_10). A university expertise index lists a journal extension ("Improving passive
  estimation of TCP round-trip times using TCP timestamps").
  Index: https://experts.arizona.edu/en/publications/improving-passive-estimation-of-tcp-round-trip-times-using-tcp-ti
  but the researchers cannot verify its venue metadata (the brief suggests ACM ToMPEBS — plausible,
  unconfirmed). Use the PAM paper as the reference here.
- **Hubble numbers are era-specific (2007–2008 PlanetLab/Internet2-era Internet).**
  The
  *rates* (85% recall at 5.5% probes, 60% >2h outages) should not serve as current
  Internet baselines. The *methods* (directional probing, partial-outage reasoning,
  BGP-uncorrelated failures) are what rack-bench reuses.

  The same caveat covers Netalyzr's 2009–2010
  population rates and Luckie's 2005 PMTUD rates. They establish that these failure modes are
  common and measurable, not today's prevalence.
- **Few peer-reviewed studies cover India-specific internet quality.** Researchers find one M-Lab-based
  study (Prasad et al., BITS Pilani, 2016, §6.3) with era-stale numbers.
  The researchers find no
  Chennai-specific or datacenter-egress-specific academic study. No IIT-authored
  equivalent of the US/EU canon surfaces under these queries.

  TRAI's 2024 QoS regulations are
  the authoritative India-side measurement standard. But they bind consumer ISPs (percentile
  reporting, jitter/packet-drop parameters) rather than datacenter circuits.

  Next steps: pull current M-Lab ndt7 India aggregates from BigQuery as a consumer-side prior.
  Query RIPE Atlas live for connected Indian probe counts and Chennai-area anchors.
  A
  dedicated search pass may find regional work outside this pass's results.
  Use Indian venues: COMSNETS, Mind, ACM India conferences.
- **RIPE Atlas India probe count:** no fetched source states it (§5.4 caveat). The live
  atlas.ripe.net network-coverage query is the source of truth.
- **Object-store-specific measurement studies (S3/R2/GCS endpoints as measurement targets)**
  stay outside this brief's scope. The hyperscaler/neocloud researchers cover them.
  This brief certifies the *method layer* that those endpoints use.
- **Adjacent standards outside this brief's coverage.** RFC 3148 is the bulk-transport-capacity framework.
  M-Lab NDT cites it as its definition (§5.3). RFC 6815 covers 2544 applicability (§1.7).
  RFC 4656 covers OWAMP (§1.5).

  ITU-T Y.1540/Y.1541 are the QoS classes — the source of the classic IPDV
  heritage (§1.4). IETF LMAP (RFC 8193) serves large-scale measurement platforms.
  Write a follow-up note if rack-bench grows multi-site.
