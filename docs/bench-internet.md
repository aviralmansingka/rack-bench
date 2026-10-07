# Spec: `rack-bench bench internet` — external network certification

Status: **proposed, awaiting captain decision** (implement vs defer).
Companion research: `research/internet-performance` branch
(`docs/internet-performance.md` — industry methodology, sources, and the
full reliability-test taxonomy this derives from).

## 1. Summary

A new `bench` category measuring the node's **north-south (external)
network performance** — egress and ingress throughput, path quality, and
latency to public object stores (S3, R2, GCS) — as a quick pass/fail
bench stage on a single host. Everything today is read-only audit or
east-west; nothing measures the internet link the offtake deal
implicitly sells.

Effort estimate: **2–4 focused sessions** (§10). No new runtime
dependencies if Option B (§7) is chosen.

## 2. Scope

This spec covers `bench internet` only. The same probes back a later
`smoke internet` (4h soak, hourly re-runs, availability %, diurnal
congestion detection, R2-only cost default) — separate spec, reuses this
module's CHECKS and S3 client unchanged.

**In (v1):**

- Single-host, single-run measurement per provider: path audit,
  sustained upload/download throughput, single-stream throughput,
  small-object latency, TCP health.
- Providers: **S3 + R2 primary**; GCS behind `--providers gcs`
  (interop endpoint) as best-effort.
- Quick (default) and certify profiles.

**Out (v1):**

- Cluster aggregate mode (all nodes saturating the shared uplink) —
  blocked on `--hosts` fan-out; lands with it.
- `smoke internet` (see above).
- Self-hosted diagnostic endpoints (§12) — deferred to keep the first
  certification scope limited.
- Failover/convergence, route-integrity monitoring, DDoS,
  burst-above-commit — runbook/monitoring concerns, documented in the
  research doc.
- Certification thresholds — `expected` stays `null` until the profile
  schema exists (locked decision #6); this stage reports measurements.

## 3. Command surface

```text
rack-bench bench internet
    [--providers s3,r2]            # default s3,r2; gcs opt-in
    [--directions up,down]         # default both
    [--profile quick|certify]      # default quick
    [--regions s3=us-east-1,...]   # default: provider default region
    [--concurrent N]               # override parallel streams (default 32)
    [--duration 60s]               # override per-test duration
    [--tool stdlib|warp]           # default stdlib; warp for certify (§7)
    [--keep-data]                  # skip bucket cleanup
    [--yes]                        # accept cost estimate for certify
```

Also the standard flags (`--json`, `--run-dir`, `--only`, `--skip`,
`--show-command`, `--quiet`) behave exactly as in audit, and
`--only/--skip` glob against check names.

## 4. Tests (v1)

Run in this order; each is one or more `Check` entries per provider.

1. **Path audit** — `mtr -zsb 100` to each provider endpoint; hop count,
   per-hop AS path, per-hop loss, RTT.
2. **DNS resolution** — resolve each endpoint hostname via the
   configured resolver; first-resolution time vs cached (repeat
   lookups); record returned address families.
3. **Small-object latency** — GET/HEAD on 100 KiB objects, sequential;
   doubles as the idle-TTFB **baseline** for the loaded-latency signal.
4. **Sustained upload (egress)** — parallel multipart PUTs of ~1 GiB
   random objects for the profile duration. Random data defeats
   provider-side compression/dedup. **Concurrent small-object TTFB
   probes** run during the window → loaded-latency signal: p95 under
   load, inflation vs test 3's baseline.
5. **Sustained download (ingress)** — parallel range GETs reading back
   the uploaded objects. Downloads read uploads; no pre-seeded data.
6. **Single-stream** — upload + download with concurrency=1.
7. **TCP health** — `ss -ti` retransmit deltas wrapped around tests
   4–5; PMTUD probe (`ping -M do`, stepped sizes) to each endpoint.

Directions run sequentially (up fully before down) so each is measured
on an otherwise idle uplink. Per-op latency samples and per-second
throughput splits are captured for every throughput test — consistency
(p50/p95 of 1s buckets) lands in `detail`, not as separate checks.
Loaded probes are upload-only in v1 (the cheap, high-signal case);
Flent RRUL remains the certify/smoke-grade follow-up.

## 5. Profiles

| Profile | Duration | Concurrency | Runs |
| --- | --- | --- | --- |
| quick | 60s/test | 32 | 1 |
| certify | 5 min/test | 1, 8, 32, 64 | 3, drop best+worst |

Cost per node at 10 Gbit/s: quick moves ~75 GB (S3 ~$7, R2 $0, GCS
~$9); certify moves ~2.2 TB (S3 ~$200, R2 $0, GCS ~$260). Certify
prints the cost estimate and requires `--yes`.

## 6. Check registry

Names are the stable public API (JSON output + `--only/--skip` globs).
`value` semantics follow audit conventions: PASS = successfully observed;
`expected` null until profile schema.

```text
internet.<p>.path.as_path            str   hop-by-hop AS list
internet.<p>.path.hops               int
internet.<p>.path.rtt_sanity         str   WARN if outside expected band
internet.<p>.upload.throughput       float MiB/s sustained
internet.<p>.upload.objs_per_sec     float
internet.<p>.download.throughput     float MiB/s sustained
internet.<p>.download.objs_per_sec   float
internet.<p>.dns.resolve             float ms first look-up (detail:
                                     cached ms, family)
internet.<p>.latency.ttfb            float ms p50 (detail: p99)
internet.<p>.latency.loaded          float ms p95 TTFB under load
                                     (detail: baseline, inflation)
internet.<p>.tcp.pmtud               int   largest passing DF payload
internet.<p>.tcp.retransmit_ratio    float % across tests 2-4
internet.<p>.summary                 dict  region, endpoint, tool, bytes
```

Throughput checks carry `detail`: single-stream MiB/s, p95 of 1s
buckets, retransmit %. `source` carries the exact commands/endpoint per
check (`--show-command` parity). Missing credentials → every check for
that provider is `SKIP` with reason "credentials not set"; missing
`mtr` → that check `SKIP`s, others proceed. `rtt_sanity` is the only
WARN-grading check in v1; the expected-band table ships in-code (from
the research doc's RTT reference) until profiles exist.

## 7. Tooling — the one real decision

**Option A — Warp binary (MinIO).** Battle-tested S3 load tool, CSV raw
data, autoterm. Costs: external Go binary fetched+checksum-pinned at
run time; violates the stdlib-only packaging policy; version pinning
and air-gapped-host handling become spec surface.

**Option B — stdlib S3 client (recommended).** A minimal S3 client in
`rack_bench/bench/s3client.py`: AWS SigV4 HMAC signing
(`hmac`/`hashlib`), multipart upload + range GET over `http.client` /
`urllib`. ~300–400 lines + tests. Works against S3, R2, and GCS interop
unchanged (all SigV4). No dependencies, no external binary, full
control of measurement instrumentation (per-op timing, per-second
buckets) — which is the whole point of a certification tool.

The certify profile can still optionally use warp (`--tool warp`) for
cross-checking against an industry-recognized tool; quick/default never
requires it.

## 8. Credentials & security

- Env only: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (S3),
  `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` + `R2_ACCOUNT_ID`
  (endpoint host), `GCS_INTEROP_ACCESS_KEY` / `GCS_INTEROP_SECRET_KEY`
  (HMAC interop keys). Never in profile/config files — the security
  scope's secrets scan would rightly fail them.
- Keys need only a scoped policy: create/delete one bench prefix +
  read/write objects in it. The doc ships the minimal IAM policy.
- Nothing runs as root; mtr in report mode, `ss`, ping are all non-root.
- Objects are random bytes; a bucket lifecycle rule deletes leftovers
  after 24h as a safety net (documented, not relied on).

## 9. Methodology (fixed; published in README when implemented)

1. Fresh prefix `rack-bench/<ts>/` in a dedicated bench bucket.
2. Path audit first (idle RTT) → DNS → small-object (idle TTFB
   baseline) → upload (loaded probes) → download → single-stream →
   TCP health last (retransmits aggregate tests 4–6).
3. Same object size upload and download; downloads read uploads.
4. Certify: 3 runs, drop best and worst, report mean.
5. Region pinned and recorded; runs are only comparable across
   identical region maps.
6. Cleanup deletes the prefix unless `--keep-data`.

## 10. Implementation plan

| Piece | Estimate |
| --- | --- |
| bench dispatch (mirrors audit runner) | 0.5 session |
| `bench/s3client.py` (SigV4, multipart, range GET) | 1 session |
| `bench/internet.py` (7 probes, CHECKS, parsing) | 1 session |
| Cost gate, README section, integration tests | 0.5 session |

Layout mirrors audit exactly: `CHECKS = {name: fn}` dict, scope module
returns data, rendering stays in `common/output.py`. ~15–20 new unit
tests (signature vectors from AWS docs). Certify profile and
`--tool warp` can be deferred past v1 without touching check names.

## 11. Open decisions for the captain

1. **Implement now vs defer** until `--hosts` fan-out lands (either way
   v1 is per-node only; no aggregation).
2. **Tooling**: Option B (stdlib, recommended) or Option A (warp)?
3. **GCS in v1** as opt-in, or S3/R2 only until interop creds exist?
4. **`rtt_sanity` WARN grading** in v1 (a pre-profile grading exception,
   like security's placeholder floors) — keep, or PASS-only until
   profiles?
5. Default region policy: nearest (lowest RTT) or explicit per-provider
   config required?

## 12. Deferred extension: self-hosted diagnostic endpoints

Not in v1. A possible later phase: a few small cloud instances (EC2 or
neutral vantage à la Backblaze) in a configurable list of regions, each
running pinned MinIO as an S3-compatible endpoint, registered as
"custom" providers (`--endpoint name=url,region=X`, creds via env;
MinIO speaks SigV4, so the stdlib client works unchanged).

Two provider classes once it lands:

- **Workload targets** (S3, R2) — the certification numbers; what the
  offtake deal actually sells.
- **Diagnostic endpoints** (self-hosted) — chosen-region path auditing
  and iperf3 colocation (raw TCP/UDP beside MinIO separates "the path
  is slow" from "the S3 frontend is slow"); explains bad numbers
  rather than certifying them.

Costs that keep it out of v1: endpoint nodes must out-bandwidth the
node under test (AWS ~5 Gbps single-flow cap applies to them too),
egress on downloads is ~$0.09/GB same as S3, and a benchmark server is
ops surface that silently rots (patching, MinIO version pinning, cred
rotation). Rough budget $150-350/mo for 4-6 always-on regions.

---

## Appendix A — Grading criteria per test

v1 grading per §6: PASS = successfully observed, SKIP = gated (no
credentials / tool), WARN = `rtt_sanity` only. This appendix defines
the **good vs bad signals** per test — what a reviewer eyeballs today,
and what becomes threshold checks the moment the certification profile
schema lands.

### A.1 Path audit

| Signal | Good | Bad |
| --- | --- | --- |
| AS path | our ASN → 1-2 transit → provider | 3+ transit ASes; no provider AS |
| Hop count | ~8-12 (Chennai→Mumbai/Singapore) | >15; unstable across runs |
| Per-hop loss | 0% | loss persisting from hop N onward |
| Final RTT | inside expected band | ≫ band (tromboning / far POP) |
| Per-hop RTT jump | smooth with distance | one hop adds >30 ms unexplained |
| StDev per hop | low | high on final hops (jittery transit) |

Interpretation traps: intermediate-hop loss with clean continuation is
router ICMP rate-limiting (ignore); non-responding hops are not gaps;
one snapshot cannot detect flapping (that is smoke's hourly loop).
This check certifies the ISP, not the node — a WARN is an offtake
conversation, not a hardware defect.

### A.2 Sustained upload (egress)

| Signal | Good | Bad |
| --- | --- | --- |
| Sustained MiB/s | stable, near link class | collapses over the window |
| p95/p50 of 1s buckets | ~1.0-1.2 | >2 (instability, policing) |
| obj/s vs throughput | consistent | retries/errors dominate |
| Per-op latency p99 | low tail | fat tail (queueing upstream) |

Bad-shape examples: throughput decaying after the first minute =
upstream buffer exhaustion or policing; sawtooth buckets = congestion
control fighting a lossy path (cross-check A.6 retransmits).

### A.3 Sustained download (ingress)

Same signals as A.2, plus one comparison:

| Signal | Good | Bad |
| --- | --- | --- |
| Up/down asymmetry | ~1:1 (DIA is symmetric) | ≪1 (shaped ingress or transit) |

Asymmetry with a clean path audit points at provider-side shaping or a
congested peering link; asymmetry with high retransmits points at loss.

### A.4 Single-stream

| Signal | Good | Bad |
| --- | --- | --- |
| Single-stream MiB/s | ≈ min(5 Gbit/s, window/RTT) | ≪ window/RTT |
| Gap to multi-stream | small at low RTT | large gap = BDP/latency limited |

The expected value is BDP math (RFC 6349): window ÷ RTT. A single-stream
number far below BDP while multi-stream scales fine = per-flow loss or
receive-window misconfiguration on the node (a node defect, unlike
A.1).

### A.5 Small-object latency

| Signal | Good | Bad |
| --- | --- | --- |
| TTFB p50 | inside regional band | ≫ band |
| p99/p50 ratio | ~2-3 | >10 (tail latency problem) |
| Error rate | 0 | any 5xx/timeouts |

TTFB p50 should track the path-audit RTT plus a few ms of TLS and
request processing; a fat p99 with clean p50 = queueing or retry
storms somewhere on the request path.

### A.6 TCP health

| Signal | Good | Bad |
| --- | --- | --- |
| Retransmit ratio | <0.5% | >1% on a clean path |
| PMTUD (DF payload) | 1472 passes (1500 MTU) | hangs at some size |

A PMTUD blackhole is the classic "SSH works, big transfers stall"
failure — worth WARN-grade attention because it silently caps every
other test's numbers (see §11 decision 4).

### A.7 Loaded latency

| Signal | Good | Bad |
| --- | --- | --- |
| p95 TTFB inflation vs idle | <=20 ms | large inflation |
| TTFB spread while loaded | stable tail | growing tail |

Idle TTFB (A.5) is the baseline; the loaded signal measures
bufferbloat — queues filling upstream during the upload. >20 ms
p95 inflation is the gate the Bangalore methodology proposes. Large
inflation with clean retransmits points at missing queue management
upstream, not loss.

### A.8 DNS resolution

| Signal | Good | Bad |
| --- | --- | --- |
| First look-up ms | regional band | slow or failing |
| Cached / first ratio | fast cache | no caching benefit |
| Answers | expected families | SERVFAIL/NXDOMAIN |

Traps: cold resolver caches make "first" look-up ambiguous on the
first cycle (record which); negative caching can mask a transient
failure. Any SERVFAIL is a real finding, not noise.
