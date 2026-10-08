# Spec: `rack-bench bench internet` — external network certification

Status: **v1 probes implemented** (Session 3 Parts 1–2): context, baseline,
bulk/loaded, single-stream, TCP and summary. Live cloud transfer
interoperability has not been certified. Remaining limitations are listed in
§11. Session 2 contracts are frozen (§11). Companion research:
`research/internet-performance` branch (`docs/internet-performance.md` —
industry methodology, sources, and the full reliability-test taxonomy this
derives from).

## 1. Summary

A new `bench` category measuring the node's **north-south (external) network
performance** — egress and ingress throughput, path quality, and latency to
public object stores (S3, R2, GCS) — as a quick pass/fail bench stage on a
single host. Everything today is read-only audit or east-west; nothing measures
the internet link the offtake deal implicitly sells.

Effort estimate: **2–4 focused sessions** (§10). No new runtime dependencies if
Option B (§7) is chosen.

## 2. Scope

This spec covers `bench internet` only. The same probes back a later
`smoke internet` (4h soak, hourly re-runs, availability %, diurnal congestion
detection, R2-only cost default) — separate spec, reuses this module's CHECKS
and S3 client unchanged.

**In (v1):**

- Single-host, single-run measurement per provider: path audit, sustained
  upload/download throughput, single-stream throughput, small-object latency,
  TCP health.
- Providers: **S3 + R2 primary**; GCS behind `--providers gcs` (interop
  endpoint) as best-effort.
- Quick (default) and certify profiles.

**Out (v1):**

- Cluster aggregate mode (all nodes saturating the shared uplink) — blocked on
  `--hosts` fan-out; lands with it.
- `smoke internet` (see above).
- Self-hosted diagnostic endpoints (§12) — deferred to keep the first
  certification scope limited.
- Failover/convergence, route-integrity monitoring, DDoS, burst-above-commit —
  runbook/monitoring concerns, documented in the research doc.
- Certification thresholds — `expected` stays `null` until the profile schema
  exists (locked decision #6); this stage reports measurements.

## 3. Command surface

```text
rack-bench bench internet
    [--providers s3,r2]            # default s3,r2; gcs opt-in
    [--directions up,down]         # default both
    [--profile quick|certify]      # default quick
    [--regions s3=us-east-1,...]    # override the tiered region matrix (§11)
    [--buckets s3=<name>,r2=<name>] # existing buckets for object probes (§8)
    [--concurrent N]               # override parallel streams (default 32)
    [--duration 60s]               # override per-test duration
    [--tool stdlib|warp]           # default stdlib; warp for certify (§7)
    [--keep-data]                  # skip bucket cleanup
    [--yes]                        # accept cost estimate for certify
```

Also the standard flags (`--json`, `--run-dir`, `--only`, `--skip`,
`--show-command`, `--quiet`) behave exactly as in audit, and `--only/--skip`
glob against check names.

## 4. Tests (v1)

Run in this order; each is one or more `Check` entries per provider.

1. **Path audit** — `mtr -4 -r -w -z -b -s 100 -c 10 <endpoint>`; observed hop
   count (including unanswered hops), per-hop AS path, loss, RTT and StDev. The
   former `-zsb 100` shorthand incorrectly grouped `-s`'s argument; spell out
   the flags. Fall back to `traceroute -4 -A -q 3 -w 1 -m 30 <endpoint>` when
   mtr is absent. Traceroute records individual RTTs/timeouts, not invented mtr
   loss percentages or StDev. No ASN annotations means the AS check SKIPs.
   Destination RTT grading requires a final-hop address matching the endpoint's
   IPv4 resolution; an answering transit router is not a destination sample.
2. **DNS resolution** — query each endpoint hostname through the first IPv4
   nameserver in `/etc/resolv.conf` (including a configured local resolver
   stub), preserving DNS response codes; UDP with same-resolver TCP truncation
   fallback. One first query plus five repeats records first-resolution vs
   repeated-query latency and returned families. Endpoint queries are A-only in
   v1; no search suffixes, public-resolver fallback, or cache flushing. “First”
   is first observed in this run, not a claim of a cold upstream cache; repeats
   do not prove hits. Each idle pass also queries A and AAAA for a fresh random
   name under RFC 2606 `.invalid`. It must return NXDOMAIN for both: any address
   is an interception finding (NXDOMAIN hijacking). SERVFAIL, NODATA, timeouts
   and malformed replies are distinct ungradable findings, not successful
   NXDOMAIN tests. Wrong trap answers invalidate the baseline and SKIP with a
   reason, not a new WARN/FAIL exception. AAAA trap queries never enable IPv6
   endpoint connections. **Deferred extension:** DNSSEC tamper comparison
   (known-good resolver vs configured resolver, answer-divergence grading) is
   future work; unsigned-zone expectations are unspecified and are not tested in
   v1.
3. **Small-object latency** — create one 100 KiB seeded object using a
   checksummed PUT, then 20 sequential verified GETs per idle run; delete the
   owned key at teardown unless `--keep-data`. Setup PUT is not a latency
   sample. This is the idle-TTFB **baseline** for the loaded-latency signal.
   Detail records p50/p95/p99, min/max/mean and raw samples for `connect_ms`
   (TCP+TLS duration), `response_first_byte_ms` (first status-line byte
   available to the buffered HTTP reader), `headers_ms`, `body_first_byte_ms`,
   and `total_ms`. The last four are cumulative from request start, not additive
   phases. Check value is response TTFB p50; `baseline_ms.p95` uses that same
   response-byte clock for Part 2's loaded comparison. Per-operation process CPU
   includes payload generation or verification, not just network time.
   Failed/invalid samples never become zero latency. Certify's nearest band
   retains three runs and drops best/worst ranked by response-TTFB p50; each
   light band has only one 20-GET run.
4. **Sustained upload (egress)** — parallel multipart PUTs of ~1 GiB random
   objects for the profile duration. Random data defeats provider-side
   compression/dedup. **Concurrent small-object TTFB probes** run during the
   window → loaded-latency signal: p95 under load, inflation vs test 3's
   baseline.
5. **Sustained download (ingress)** — parallel range GETs reading back the
   uploaded objects. Downloads read uploads; no pre-seeded data.
6. **Single-stream** — upload + download with concurrency=1.
7. **TCP health** — `ss -ti` retransmit deltas wrapped around tests 4–5; PMTUD
   probe (`ping -M do`, stepped sizes) to each endpoint.

Directions run sequentially (up fully before down) so each is measured on an
otherwise idle uplink. Per-op latency samples and per-second throughput splits
are captured for every throughput test — consistency (p50/p95 of 1s buckets)
lands in `detail`, not as separate checks. Loaded probes are upload-only in v1
(the cheap, high-signal case); Flent RRUL remains the certify/smoke-grade
follow-up.

## 5. Profiles

| Profile | Duration   | Concurrency  | Runs               |
| ------- | ---------- | ------------ | ------------------ |
| quick   | 60s/test   | 32           | 1                  |
| certify | 5 min/test | 1, 8, 32, 64 | 3, drop best+worst |

Cost per node at 10 Gbit/s: quick moves ~75 GB (S3 ~$7, R2 $0, GCS
~$9); certify moves ~2.2 TB (S3 ~$200, R2 $0, GCS ~$260). Certify prints the
cost estimate and requires `--yes`. These are full-volume reference figures for
the nearest band, not three full-volume regional runs. Certify's far-band
physics probes add only the bounded light traffic in §11; custom `--regions`,
durations, and directions must be reflected by the future cost gate rather than
multiplying this reference by three.

## 6. Check registry

Names are the stable public API (JSON output + `--only/--skip` globs). `value`
semantics follow audit conventions: PASS = successfully observed; `expected`
null until profile schema.

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

Throughput checks carry `detail`: single-stream MiB/s, p95 of 1s buckets,
retransmit %. For multi-band probes, the scalar value represents the
nearest/overridden band; JSON-encoded `detail` retains the effective region
matrix, individual runs, unsupported-band reasons, raw path reports and timing
samples. These survive in `bench.values.json` without a separate artifact
writer. RTT sanity can WARN on any measured band's reference excursion; its
value still describes the nearest band. R2 has no guaranteed regional RTT band,
so RTT sanity SKIPs with a reason. `source` carries the exact commands/endpoint
per check (`--show-command` parity). Missing credentials → every check for that
provider is `SKIP` with reason "credentials not set"; missing `mtr` → that check
`SKIP`s, others proceed. `rtt_sanity` is the only WARN-grading check in v1; the
expected-band table ships in-code (from the research doc's RTT reference) until
profiles exist.

## 7. Tooling — the one real decision

**Option A — Warp binary (MinIO).** Battle-tested S3 load tool, CSV raw data,
autoterm. Costs: external Go binary fetched+checksum-pinned at run time;
violates the stdlib-only packaging policy; version pinning and air-gapped-host
handling become spec surface.

**Option B — stdlib S3 client (recommended).** A minimal S3 client in
`rack_bench/bench/internet/s3client.py`: AWS SigV4 HMAC signing
(`hmac`/`hashlib`), multipart upload + range GET over `http.client` (not
`urllib`). Targets S3 and R2; GCS interoperability remains follow-up work. No
dependencies or external binary; per-request timing and streaming hooks support
later probe instrumentation without SDK retries hiding bad samples.

The certify profile can still optionally use warp (`--tool warp`) for
cross-checking against an industry-recognized tool; quick/default never requires
it.

## 8. Credentials & security

- The S3 client reads only `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` and
  optional `AWS_SESSION_TOKEN`; R2 also requires `R2_ACCOUNT_ID` for its
  endpoint host. Set the AWS-named variables to the selected provider's
  credentials. No config files, IMDS, or implicit credential discovery. Provider
  orchestration and GCS interop remain later probe work.
- Keys need only a scoped policy: create/delete one bench prefix + read/write
  objects in it. The doc ships the minimal IAM policy.
- **Bucket configuration:** `--buckets s3=<name>,r2=<name>` is a provider-keyed
  map of existing bucket names, following `--regions`: known, unique providers
  only. Names must be DNS-compatible; S3 virtual-hosted TLS bucket names cannot
  contain dots. Flags are run configuration; environment variables remain
  credentials-only. Path and DNS ignore this map. Object probes without a bucket
  SKIP with a reason naming `--buckets <provider>=<name>`. No buckets are
  created. A bucket must be accessible at the selected endpoint/region: regional
  S3 redirects/errors are ungradable, never silently followed into another band.
- **Prefix ownership:** each collection owns a fresh `rack-bench/<run-id>/...`
  prefix. Create objects only beneath it; cleanup may list/delete only under
  that prefix, never any other key or the bucket root. Buckets may contain real
  user data. The baseline deletes its exact owned key, including after a failed
  PUT with an ambiguous response; `--keep-data` retains it and records the
  key/seed. Cleanup failures remain explicit in detail.
- Nothing runs as root; mtr in report mode, `ss`, ping are all non-root.
- Objects are deterministic seeded pseudorandom bytes (§11). Normal cleanup
  deletes the scoped prefix and aborts known failed multipart uploads. A
  lifecycle rule aborts incomplete uploads and deletes leftovers after 24h as a
  crash safety net. Initiation is not idempotent: a lost response followed by a
  control retry can leave an unknown upload ID that only this safety net can
  reclaim. Never claim prefix listing finds incomplete multipart uploads.

## 9. Methodology (fixed; published in README when implemented)

1. Fresh prefix `rack-bench/<ts>/` in a dedicated bench bucket.
2. Path audit first (idle RTT) → DNS → small-object (idle TTFB baseline) →
   upload (loaded probes) → download → single-stream → TCP health last
   (retransmits aggregate tests 4–6).
3. Same object size upload and download; downloads read uploads.
4. Certify: 3 runs, drop best and worst, report mean.
5. Region pinned and recorded; runs are only comparable across identical region
   maps.
6. Cleanup deletes the prefix unless `--keep-data`.

## 10. Implementation plan

| Piece                                                      | Estimate    |
| ---------------------------------------------------------- | ----------- |
| bench dispatch (mirrors audit runner)                      | 0.5 session |
| `bench/internet/s3client.py` (SigV4, multipart, range GET) | 1 session   |
| `bench/internet/` (7 probes, CHECKS, parsing)              | 1 session   |
| Cost gate, README section, integration tests               | 0.5 session |

Layout mirrors audit exactly: `CHECKS = {name: fn}` dict, scope module returns
data, rendering stays in `common/output.py`. Client tests include four literal
AWS signing vectors plus loopback-only transport and streaming checks. Certify
profile and `--tool warp` can be deferred past v1 without touching check names.

## 11. Frozen decisions and remaining residue

The following four contracts are frozen for Session 2 and later probes:

1. **Ungradable means SKIP with a reason**, not a new status. Missing
   credentials/tools, invalid transfer samples, checksum failures, transport
   failures, and unsupported measurements must remain distinguishable in detail.
   Never turn an unavailable measurement into a zero or a PASS. Probe code owns
   per-check grading; the client surfaces typed errors and request timing.
   Successful observations remain PASS with `expected: null`; the existing
   `rtt_sanity` WARN exception is unchanged.
2. **IPv4-only v1**, including DNS-to-socket selection. Do not use dual-stack
   endpoints or process-wide socket defaults. IPv6 is a future additive `.v6`
   check-name suffix; existing names keep their IPv4 meaning.
3. **Deterministic seeded payloads and checksums in both directions.** Chunk
   content is a reproducible function of seed, chunk index, and size, with a
   pseudorandom hash stream to defeat compression. The client owns generation,
   bounded streaming, per-body/per-part Content-MD5 and CRC32 headers, and
   download regeneration/comparison hooks. CRC32 means `zlib.crc32`, not CRC32c.
   Upload hashes are prepared before timed I/O; generation and download
   verification CPU costs still need observation by probes. Never silently retry
   measured PUTs or GETs. Control operations may retry connection errors and 5xx
   with bounded backoff; their timings are not throughput samples.
4. **Tiered regions, not three full-volume certifications.** Quick uses nearest
   S3 `ap-south-1` (Mumbai) and R2 `apac`. Certify keeps Mumbai full-volume and
   adds Singapore (`ap-southeast-1`) and N. Virginia (`us-east-1`) as light
   physics probes. `--regions` overrides this policy; record the effective
   matrix and volumes in artifacts and cost estimates.

The region matrix is probe policy, not S3-client policy. S3 resolves to
`https://s3.<region>.amazonaws.com` with virtual-hosted bucket requests
(`https://<bucket>.s3.<region>.amazonaws.com/<key>`). R2 uses path-style
`https://<account-id>.r2.cloudflarestorage.com/<bucket>/<key>`, with
`R2_ACCOUNT_ID` from the environment and signing region `auto`. R2 `apac` is a
placement hint, _not_ a SigV4 region or a guarantee of a particular ingress POP.
Do not claim Mumbai/Singapore/Virginia R2 paths without evidence; unsupported
pinned-band measurements SKIP with a reason.

### Probe × band × volume budget

Full-volume rows use §5's profile durations, sweeps, and repetitions. Light rows
do not repeat that sweep. Limits below are per provider and far band; R2
far-band rows apply only if that path can actually be established.

| Probe                      | Quick: nearest only                | Certify: Mumbai / nearest          | Certify: Singapore + N. Virginia, each                   |
| -------------------------- | ---------------------------------- | ---------------------------------- | -------------------------------------------------------- |
| Path, DNS, PMTUD           | One idle pass                      | One idle pass per run              | One idle pass; no bulk payload                           |
| Idle small-object GET/HEAD | 100 KiB objects                    | 100 KiB objects                    | At most 20 × 100 KiB GETs; HEAD adds no body             |
| Sustained PUT + range GET  | Full 60s, concurrency 32           | Full 5 min, 1/8/32/64, 3 runs      | Omitted; not a sustained-throughput certification        |
| Single-stream PUT + GET    | Full profile window, concurrency 1 | Full profile window, concurrency 1 | One object, at most 32 MiB each direction, concurrency 1 |
| Loaded latency             | During full upload                 | During full upload                 | Omitted; no full-volume load window                      |
| TCP retransmit deltas      | Around bulk transfers              | Around bulk transfers              | Around the bounded single-stream transfer only           |

Thus the two far bands add at most 64 MiB uploaded and about 68 MiB downloaded
per provider, plus protocol/control traffic, not another two ~2.2 TB runs. At
the S3 reference egress rate this is under $0.01 of extra payload egress;
request fees and custom overrides still belong in the eventual cost gate. The
current estimate is a full-transfer reference, not a quote for the probes
implemented so far.

Remaining implementation residue: GCS interoperability, certification
thresholds/profile schema, optional Warp execution, and effective matrix-aware
cost estimates. All v1 probes are implemented; cloud transfer interoperability
still requires a paid live exercise. Reference cost output is not a quote for
custom runs. Missing credentials still SKIP every provider check, including
context and summary. See README for orchestration, TCP sampling limitations,
part-boundary duration overruns, and filtered-prerequisite behavior.

## 12. Deferred extension: self-hosted diagnostic endpoints

Not in v1. A possible later phase: a few small cloud instances (EC2 or neutral
vantage à la Backblaze) in a configurable list of regions, each running pinned
MinIO as an S3-compatible endpoint, registered as "custom" providers
(`--endpoint name=url,region=X`, creds via env; MinIO speaks SigV4, so the
stdlib client works unchanged).

Two provider classes once it lands:

- **Workload targets** (S3, R2) — the certification numbers; what the offtake
  deal actually sells.
- **Diagnostic endpoints** (self-hosted) — chosen-region path auditing and
  iperf3 colocation (raw TCP/UDP beside MinIO separates "the path is slow" from
  "the S3 frontend is slow"); explains bad numbers rather than certifying them.

Costs that keep it out of v1: endpoint nodes must out-bandwidth the node under
test (AWS ~5 Gbps single-flow cap applies to them too), egress on downloads is
~$0.09/GB same as S3, and a benchmark server is
ops surface that silently rots (patching, MinIO version pinning, cred
rotation). Rough budget $150-350/mo
for 4-6 always-on regions.

---

## Appendix A — Grading criteria per test

v1 grading per §6 and §11: PASS = successfully observed, SKIP = ungradable with
a reason (including missing credentials/tools or invalid measurements), WARN =
`rtt_sanity` only. This appendix defines the **good vs bad signals** per test —
what a reviewer eyeballs today, and what becomes threshold checks the moment the
certification profile schema lands.

### A.1 Path audit

| Signal           | Good                             | Bad                                  |
| ---------------- | -------------------------------- | ------------------------------------ |
| AS path          | our ASN → 1-2 transit → provider | 3+ transit ASes; no provider AS      |
| Hop count        | ~8-12 (Chennai→Mumbai/Singapore) | >15; unstable across runs            |
| Per-hop loss     | 0%                               | loss persisting from hop N onward    |
| Final RTT        | inside expected band             | ≫ band (tromboning / far POP)        |
| Per-hop RTT jump | smooth with distance             | one hop adds >30 ms unexplained      |
| StDev per hop    | low                              | high on final hops (jittery transit) |

Interpretation traps: intermediate-hop loss with clean continuation is router
ICMP rate-limiting (ignore); non-responding hops are not gaps; one snapshot
cannot detect flapping (that is smoke's hourly loop). This check certifies the
ISP, not the node — a WARN is an offtake conversation, not a hardware defect.

### A.2 Sustained upload (egress)

| Signal                | Good                    | Bad                          |
| --------------------- | ----------------------- | ---------------------------- |
| Sustained MiB/s       | stable, near link class | collapses over the window    |
| p95/p50 of 1s buckets | ~1.0-1.2                | >2 (instability, policing)   |
| obj/s vs throughput   | consistent              | retries/errors dominate      |
| Per-op latency p99    | low tail                | fat tail (queueing upstream) |

Bad-shape examples: throughput decaying after the first minute = upstream buffer
exhaustion or policing; sawtooth buckets = congestion control fighting a lossy
path (cross-check A.6 retransmits).

### A.3 Sustained download (ingress)

Same signals as A.2, plus one comparison:

| Signal            | Good                    | Bad                            |
| ----------------- | ----------------------- | ------------------------------ |
| Up/down asymmetry | ~1:1 (DIA is symmetric) | ≪1 (shaped ingress or transit) |

Asymmetry with a clean path audit points at provider-side shaping or a congested
peering link; asymmetry with high retransmits points at loss.

### A.4 Single-stream

| Signal              | Good                        | Bad                             |
| ------------------- | --------------------------- | ------------------------------- |
| Single-stream MiB/s | ≈ min(5 Gbit/s, window/RTT) | ≪ window/RTT                    |
| Gap to multi-stream | small at low RTT            | large gap = BDP/latency limited |

The expected value is BDP math (RFC 6349): window ÷ RTT. A single-stream number
far below BDP while multi-stream scales fine = per-flow loss or receive-window
misconfiguration on the node (a node defect, unlike A.1).

### A.5 Small-object latency

| Signal        | Good                 | Bad                        |
| ------------- | -------------------- | -------------------------- |
| TTFB p50      | inside regional band | ≫ band                     |
| p99/p50 ratio | ~2-3                 | >10 (tail latency problem) |
| Error rate    | 0                    | any 5xx/timeouts           |

TTFB p50 should track the path-audit RTT plus a few ms of TLS and request
processing; a fat p99 with clean p50 = queueing or retry storms somewhere on the
request path.

### A.6 TCP health

| Signal             | Good                   | Bad                 |
| ------------------ | ---------------------- | ------------------- |
| Retransmit ratio   | <0.5%                  | >1% on a clean path |
| PMTUD (DF payload) | 1472 passes (1500 MTU) | hangs at some size  |

A PMTUD blackhole is the classic "SSH works, big transfers stall" failure —
worth operator attention because it silently caps every other test's numbers. v1
does not add a PMTUD WARN-grading exception.

### A.7 Loaded latency

| Signal                     | Good        | Bad             |
| -------------------------- | ----------- | --------------- |
| p95 TTFB inflation vs idle | <=20 ms     | large inflation |
| TTFB spread while loaded   | stable tail | growing tail    |

Idle TTFB (A.5) is the baseline; the loaded signal measures bufferbloat — queues
filling upstream during the upload. >20 ms p95 inflation is the gate the
Bangalore methodology proposes. Large inflation with clean retransmits points at
missing queue management upstream, not loss.

### A.8 DNS resolution

| Signal               | Good              | Bad                |
| -------------------- | ----------------- | ------------------ |
| First look-up ms     | regional band     | slow or failing    |
| Cached / first ratio | fast cache        | no caching benefit |
| Answers              | expected families | SERVFAIL/NXDOMAIN  |

Traps: cold resolver caches make "first" look-up ambiguous on the first cycle
(record which); negative caching can mask a transient failure. Any SERVFAIL is a
real finding, not noise.
