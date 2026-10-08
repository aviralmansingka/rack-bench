# Internet performance: definition and bench design

Research branch `research/internet-performance`. Goal: a precise,
testable definition of "internet performance" for rack-bench nodes, and
a bench command that measures it against S3, R2, and GCS as the load
generators.

---

## 1. Definition: what "internet performance" actually is

The industry (IETF, MEF, ITU-T, cloud providers) never certifies
"speed". They certify **separate dimensions**, each with its own
measurement method:

| Dimension | Definition | Unit |
| --- | --- | --- |
| Egress throughput | Sustained bytes/sec pushed OUT | Gbit/s |
| Ingress throughput | Sustained bytes/sec pulled IN | Gbit/s |
| Idle latency | RTT with no traffic on the path | ms |
| Loaded latency | RTT while the pipe is full (bufferbloat) | ms |
| Jitter | Variation of consecutive RTTs | ms |
| Packet loss | % of packets dropped on the path | % |
| Consistency | p50/p95/p99 of 1s throughput buckets | ratio |
| Transfer efficiency | Bytes delivered vs retransmitted | % |

Three distinctions the standards draw that matter for our bench:

1. **Capacity vs throughput.** Capacity is what the link can carry (line
   rate). Throughput (goodput) is what a real TCP session actually
   sustains. Datacenters certify *sustained* throughput, never bursts.
2. **Single-flow vs multi-flow.** A single TCP 5-tuple can't fill a
   modern pipe: AWS documents single-flow traffic capped at ~5 Gbps
   regardless of instance size — parallel streams (AWS's own methodology
   is iperf3 with 8 parallel streams) are needed to certify aggregate
   bandwidth. Both numbers are meaningful: single-stream reflects what
   one user's download gets; multi-stream reflects the provisioned pipe.
3. **Latency caps throughput.** Max single-stream throughput ≈
   window / RTT (BDP math, RFC 6349). A 25 ms RTT path halves
   single-stream speed vs 12 ms, at any capacity. That is why idle AND
   loaded latency are separate certification dimensions, and why region
   choice (which S3/GCS region we test against) must be pinned.

### The standards we anchor to

- **RFC 6349** (Framework for TCP Throughput Testing, 2011) — the IETF
  methodology: (1) verify path MTU, (2) measure baseline RTT + bottleneck
  bandwidth, (3) sustained TCP transfer tests at sized windows. Defines
  Transfer Time Ratio, TCP Efficiency (retransmits), and Buffer Delay
  (% latency added under load). Pass/fail verdicts against the CIR.
- **RFC 2544 / ITU-T Y.1564** — Layer-2/3 service turn-up: throughput,
  latency, frame loss, jitter per traffic class at the committed rate.
  These are what carriers actually run on a circuit before accepting it.
- **MEF / business-internet SLA norms** — availability ≥ 99.9%,
  regional RTT < 50–100 ms, jitter < 30 ms, loss < 1%, committed vs
  burst throughput.
- **Cloudflare AIM** (internet-quality scoring) — same five metrics
  (down/up throughput, idle/loaded latency, jitter, loss) scored in
  bands for consumer connections; confirms loaded latency as the "real
  experience" metric.

---

## 2. How datacenters and providers actually certify

Five patterns found in practice, all directly reusable:

1. **Carrier turn-up test** (RFC 2544 / Y.1564 / RFC 6349): run a
   scripted suite at the committed rate, emit a pass/fail per metric.
   The suite is fixed and published — reproducibility is the
   certification.
2. **AWS EC2 networking**: publishes per-instance "network bandwidth"
   (inbound and outbound independently, simultaneously); methodology is
   iperf3, 8 parallel streams, instances in a placement group; ENA
   Express / MPTCP called out for single-flow limits. They certify the
   *method*, not one number.
3. **Google Cloud `gsutil perfdiag`**: Google ships a **known
   measurement suite** ("run perfdiag when troubleshooting") — 1 MiB
   read/write throughput tests + operation-latency tests for
   0b/1KiB/100KiB objects, JSON report out. The precedent for a
   built-in diagnostic subcommand.
4. **Backblaze Performance Stats** (the closest template for us):
   neutral Vultr VM (not their own network), **Warp** as the load tool,
   fixed profiles — 5-minute single-threaded and multi-threaded upload
   AND download at 256 KiB → 100 MiB object sizes, plus month-long
   average response times. Full methodology published so third parties
   can replicate. Result: cross-provider comparable numbers.
5. **MLPerf Storage** (MLCommons): certification-grade storage
   benchmark for AI training — metric is samples/sec *subject to
   minimum accelerator utilization*, plus checkpoint write/read
   bandwidth for LLM workloads. The lesson: certify against the
   workload you sell (GPU cluster ⇒ object storage in/out), and gate on
   utilization, not raw Gbps alone.

### Takeaways for rack-bench

- Certify **egress and ingress separately**, each as sustained
  throughput over a fixed window (5 min for certify, shorter for quick
  bench).
- Report **single-stream AND multi-stream** numbers both.
- Pin the **region** of every target; report RTT alongside throughput.
- Use **one identical tool and profile across all providers** (the
  Backblaze model) so numbers are comparable.
- Discard-and-average (run N, drop best/worst, report mean) to control
  run-to-run variance.
- Keep raw per-operation samples (warp writes CSV) so p50/p95/p99 are
  computed, not guessed.

---

## 3. Object stores as the bench substrate

Why S3 / R2 / GCS specifically: they are (a) the actual workloads a GPU
node's internet link exists for — datasets down, checkpoints and
artifacts up; (b) effectively infinitely provisioned endpoints
(per-object streams of ~200+ MiB/s on GCS, similar on S3), so the node's
uplink and TCP stack are the bottleneck, which is exactly what we want
to measure; (c) they have well-known regions to pin RTT.

Upload test (PUT/multipart) exercises **egress**; download test (GET)
exercises **ingress**.

### Provider matrix

| Provider | Native API | Bench access |
| --- | --- | --- |
| AWS S3 | S3 | warp or stdlib client → `s3.amazonaws.com` |
| Cloudflare R2 | S3-compatible | `https://<account>.r2.cloudflarestorage.com` |
| GCS | JSON/XML | S3-interop endpoint + HMAC keys, or `gcloud perfdiag` |

Notes:

- R2: **zero egress fee** ⇒ download tests cost nothing; upload ingress
  is free.
- S3: GET tests incur S3 egress + request costs.
- GCS interop = XML API + HMAC-SHA256, supports multipart upload; some
  S3 semantics differ (V4 signing details, no chunked
  transfer-encoding).

### Tool recommendation: Warp (MinIO), single binary, for all three

- One Go binary, zero deps, S3-API — works against S3, R2 natively, and
  GCS via interop mode. Identical methodology across providers (the
  Backblaze precedent).
- Measures per-operation throughput (MiB/s + obj/s) and latency, with
  per-1s splits (fastest / p50 / slowest) — the consistency dimension
  for free.
- `--autoterm` stops when variance stabilizes (steady-state detection).
- Writes full per-op CSV (`.csv.zst`) — reproducible raw data for the
  certification envelope.
- GCS-native cross-check (`gcloud storage perf-diag`) as an optional
  second check, not the primary path — keeps the primary matrix
  uniform.

(For the v1 implementation, the bench-internet spec recommends a
stdlib S3 client instead of an external binary — see
`docs/bench-internet.md` §7 in the main repo.)

### Cost guardrails (important)

A 10 Gbit/s × 5 min download from S3 ≈ 375 GB ≈ ~$34 of S3 egress per
run, per node. R2 is free. Rules for the bench:

- Default **quick profile** is short (autoterm, 60s cap) and
  byte-capped (`--max-objects`, `--obj.size`).
- **Certify profile** (5 min, full matrix) must be explicit
  (`--profile certify`) and prints an estimated byte/cost summary
  before running, gated by `--yes`.
- Prefer R2 for repeated download-heavy regression testing; S3/GCS for
  the authoritative quarterly certification.
- Cleanup: delete bench bucket/prefix after run (warp `cleanup`).

---

## 4. The bench command

Fits the existing stage model: `bench` = quick pass/fail. The full
review-ready spec lives in the main repo at
`docs/bench-internet.md`; summary here for completeness.

```text
rack-bench bench internet
    [--providers s3,r2]        # default all three
    [--directions up,down]     # default both
    [--profile quick|certify]  # quick=60s/8-32 concurrent
    [--regions <map>]          # e.g. s3=us-east-1,gcs=us-east1,r2=auto
    [--concurrent N]
    [--obj-size 1GiB]
    [--single-stream]
    [--keep-data]
    [--bucket <prefix>]
```

### Test order per node

Path audit (idle RTT) → upload pass (egress) → download pass (ingress)
→ single-stream → small-object (1 KiB–100 KiB) → latency probe last
(GETs reuse PUT data; probes stay idle-latency).

### Checks emitted

Uniform `Check` envelope; `expected: null` until a certification
profile schema exists (locked decision #6). Per provider:

```text
internet.<p>.path.as_path / hops / rtt_sanity
internet.<p>.upload.throughput / objs_per_sec
internet.<p>.download.throughput / objs_per_sec
internet.<p>.latency.ttfb
internet.<p>.tcp.pmtud / retransmit_ratio
internet.<p>.summary
```

Each throughput check's `detail` carries single-stream Gbit/s,
multi-stream Gbit/s, p95 of 1s throughput buckets, retransmit count,
region, RTT, and the raw-sample file (archived next to the envelope
like audit runs). `source` = the exact command (honors
`--show-command`).

### Methodology rules (fixed, published — this IS the certification)

1. Path audit first (idle RTT, before any load); then fresh
   bucket/prefix per run; PUT pass (egress), GET pass (ingress),
   latency probe last.
2. Same object size for upload and download; GETs read what PUTs wrote.
3. autoterm on for quick; hard 5-min floor for certify.
4. Certify = 3 runs, drop best and worst, report mean.
5. Region pinned and recorded; a run is only comparable to runs with
   the same region map.
6. Cleanup deletes objects unless `--keep-data`.
7. Credentials via env — never on the command line, never in the
   envelope.

### Path audit (runs first, before any load)

Routing is asymmetric — upload and download can take different paths —
and the ISP's transit choices directly determine the numbers every
other test produces. Path auditing (traceroute/BGP analysis) is
standard NOC practice; carriers publish looking glasses so customers
can verify it.

1. `mtr -zsb 100` to each provider endpoint for 100 cycles — per-hop
   loss, latency, and the AS number of every hop. Sane path: our ASN →
   1-2 transit ASes → AS16509 (AWS) / AS13335 (Cloudflare), latency
   accumulating smoothly with distance.
2. RTT sanity vs the reference table
   (`~/.agents/s3_region_rtt.md`, distance-derived expected bands):
   Singapore ~35-55 ms, Mumbai ~20-35 ms, N. Virginia ~180-250 ms.
   Measured ≫ expected = tromboning / distant POP entry.
3. Reverse path via looking glasses (bgp.tools, lg.he.net, carrier
   LGs) — how the provider sees our prefix back. Record if
   forward/reverse differ materially.
4. Peering check on PeeringDB: direct peering vs paid transit chain to
   the provider. Direct = fewer failure domains.
5. Red flags → WARN on `rtt_sanity`: 3+ transit ASes, monotonic
   per-hop loss, US-continent RTT for an APAC endpoint, wildly
   divergent up/down paths.

**Provider scope (decided): S3 + R2 are the primary bench targets** —
R2 because it is natively S3-compatible, has a Cloudflare Chennai POP
(sub-10 ms edge RTT), and zero egress fees make regression testing
free; S3 as the authoritative provider. GCS stays in this doc as a
documented extension (S3-interop endpoint or `gcloud perfdiag`) but is
not in the first implementation.

---

## 5. Reliability test categories (beyond bandwidth and path audit)

| Category | What it tests |
| --- | --- |
| Availability / continuity | uptime %, flap detection via continuous probes |
| Failover & convergence | reconvergence after a link/BGP session dies |
| Route integrity | hijack/leak monitoring of our prefixes; RPKI ROV |
| Transit diversity | independence of our 2+ ISPs (no shared fate) |
| DNS health | resolver latency + failure rate from nodes |
| DDoS resilience | volumetric absorption / scrubbing capacity upstream |
| Burst behavior | can we burst above commit (CIR/EIR), and for how long |
| Soak / stability | 24h+ repeated probes; diurnal congestion, route churn |
| TCP-level health | retransmits, SYN timeouts, PMTUD blackholes |

Stage mapping: **bench** = path audit, bandwidth, burst probe, TCP
health, DNS latency. **smoke** = soak, failover (needs ISP
coordination), continuous availability probe. **report / external
monitoring** = route-integrity alerts and availability (a NOC function;
rack-bench certifies, does not monitor).

The critical ones for ISP quality: **failover & convergence** and
**transit diversity** — they distinguish a good carrier from a cheap
one, and cannot be inferred from bandwidth numbers.

---

## 6. Feasibility: the internet suite as a smoke network module

Read against the merged audit-stage code (108 checks, 7 scopes) and
the README spec for `bench`/`smoke`.

### What fits cleanly

- **Envelope**: every test maps to the `Check` dataclass
  (name/status/value/expected/detail/source). Warp throughput, mtr
  path audit, TCP health, DNS timing — all `collect_check`-shaped.
- **Timing model**: smoke is long-duration periodic sampling; the
  internet suite is exactly that — hourly quick profiles, continuous
  availability probes, per-cycle TCP-health + path audit. Diurnal
  congestion detection only exists at smoke timescales.
- **No retrofit cost**: smoke is unimplemented, so the module is
  greenfield.

### Design decision: separate category, not `smoke network`

`smoke network` is internal east-west mesh (sustained RDMA/TCP across
NICs and intra-rack pairs). The internet suite is north-south (single
host ↔ external providers): different targets, tools, credentials, and
cost model. Recommend `smoke internet` as its own category; `smoke
full` runs both.

### Real constraints (the honest part)

1. **Stdlib-only policy**: pyproject has `dependencies = []`; audit is
   pure stdlib. Warp is a Go binary → either (a) fetch+checksum-pin
   the warp binary on demand, or (b) implement a minimal S3 client in
   stdlib (HMAC signing is fully doable) for the quick profile, warp
   only for certify. Recommend (b) for smoke soak, (a) for certify.
2. **Cost at smoke duration**: 4h sustained 10 Gbit/s download from S3
   ≈ 18 TB × $0.09/GB ≈ $1.6k/node. Smoke soak must default to
   **R2 only** (zero egress); S3/GCS are certify-profile targets.
3. **Credentials**: S3/R2 keys via env only — the security scope's
   secrets scan would (correctly) flag keys in a profile/config.
   Missing creds → `SKIP` with reason, like other permission-gated
   probes; certification gating applies.
4. **Root/privs**: none needed — mtr in report mode, ss, dig, all
   non-root. Good fit with the non-root cluster-user design.
5. **Aggregate mode** (N nodes saturating the shared uplink) needs
   `--hosts` fan-out — unimplemented; ship single-host smoke first.

### What we'd still be missing if this shipped

- **Failover & convergence** — needs ISP coordination to reset
  sessions; runbook + maintenance-window test, not smoke.
- **Route integrity monitoring** (hijack/leak alerts) — continuous NOC
  monitoring (bgp.tools/RIPE), not a burn-in stage.
- **DDoS resilience** — vendor engagement, never self-tested.
- **Burst-above-commit** — short, expensive; a one-shot bench certify
  check, not a smoke loop.

---

## 7. ClusterMAX comparison — network performance

ClusterMAX (SemiAnalysis) network performance suite vs our spec:

| ClusterMAX tests | rack-bench status |
| --- | --- |
| NCCL/RCCL sweep: 8 B → 16 GB, dual launcher | partial; spec adds it |
| Goodput as % of line rate headline metric | added to spec |
| Monotonicity check on busbw curve | added to spec |
| Multi-node scale-out collectives (to 13 nodes) | partial; N-node added |
| RDMA perftest point-to-point | added (explicit naming) |
| 8h GPU+network simultaneous burn-in | covered (`smoke gpu-network`) |
| Fabric fault injection (link flap, node kill) | missing — roadmap |
| Observability validation (metrics emitting) | partial — roadmap |
| Multi-tenant network isolation (RoCE VPC) | missing — roadmap |
| Internet egress/ingress to public clouds | not tested by ClusterMAX at all |

The ClusterMAX-parity additions are now in the main repo README
(`bench network` spec + "ClusterMAX coverage" section). Internet
egress/ingress is a differentiator for an offtake deal, not table
stakes — ClusterMAX does not test it.

---

## Sources

- RFC 6349, Framework for TCP Throughput Testing —
  <https://www.rfc-editor.org/info/rfc6349>
- AWS EC2 instance network bandwidth (single-flow vs multi-flow) —
  <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-network-bandwidth.html>
- AWS network throughput benchmark methodology (iperf3, placement
  groups) — <https://repost.aws/knowledge-center/network-throughput-benchmark-linux-ec2>
- MinIO Warp (S3 benchmark tool, CSV, autoterm) —
  <https://github.com/minio/warp>
- Backblaze Performance Stats (neutral-origin warp methodology) —
  <https://www.backblaze.com/cloud-storage-performance-stats>
- Google Cloud Storage interoperability (S3-compatible XML API, HMAC) —
  <https://docs.cloud.google.com/storage/docs/interoperability>
- GCS performance guidance (per-stream ~200 MiB/s, parallelism) —
  <https://www.beginswithdata.com/2024/02/01/google-cloud-storage-max-throughput>
  and the Cloud Storage Performance Atlas post on the Google Cloud blog
- MLPerf Storage (certification-style AI storage benchmark) —
  <https://mlcommons.org/benchmarks/storage>
- Cloudflare speed test methodology (loaded latency, jitter, loss) —
  <https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work>
  and <https://github.com/cloudflare/speedtest/blob/main/README.md>
- Business internet SLA norms (latency/jitter/loss thresholds) —
  <https://wwt.net/blog/service-level-agreement-for-business-internet>
