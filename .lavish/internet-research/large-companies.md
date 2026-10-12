# Large Internet Companies — How Netflix, Cloudflare, Akamai, Google, Meta, Spotify, and Microsoft Diagnose Internet Quality at Scale

**Scope:** This brief shows public methods from large consumer-internet companies.
The companies use client-side speed tests, server-side streaming telemetry, CDN/POP health systems, edge/WAN monitoring, and routing-integrity detection.
The brief keeps source thresholds, tool names, and commands.
It shows which methods a third-party bench can reuse, including rack-bench's `bench internet` category.

**Legend:** The brief puts source URLs with quoted facts.
It uses **[calculation]** for derived numbers.
It uses **Inference:** for conclusions beyond one source.

Research date: 2026-10-11. All claims below carry a source URL.

---

## 1. Netflix — fast.com, the ISP Speed Index, and Open Connect health monitoring

### 1.1 fast.com methodology (what it measures, and why Netflix runs it)
- **What it measures:** "To calculate your Internet speed, FAST.com performs a series of downloads from and uploads to Netflix servers and calculates the maximum speed your Internet connection can provide" ([fast.com FAQ](https://fast.com)). The test runs globally on devices with browsers. Netflix computes results "from a series of downloads".
  The downloads use Netflix's Open Connect CDN servers, not a neutral third party ([fast.com](https://fast.com)).
- **Unloaded vs loaded latency:** "FAST.com provides two different latency measurements for your Internet connection: 'unloaded' and 'loaded' with traffic. The difference between these two measurements is also called 'bufferbloat'" ([fast.com FAQ](https://fast.com)). The 2018 Netflix blog shows latency and upload measurement: "Latency … will be measured on both unloaded and loaded connections. Unloaded latency measures the round-trip time of a request when there is no other traffic present on a user's network, while loaded latency measures the round-trip time when data-heavy applications are being used on the network" ([Netflix blog: FAST.com Now Measures Latency and Upload Speed](https://about.netflix.com/news/fast-com-now-measures-latency-and-upload-speed)). Netflix shows a gaming example. A user alone on the network gets response time ≈ unloaded latency.
  A user with a parallel stream gets response time ≈ loaded latency (same source).
- **Configurable test parameters:** The settings panel shows the number of parallel connections (min/max).
  It shows test duration in seconds (min/max).
  It also shows per-connection data-volume choices (0 MB and larger). A user can use these settings for a heavier test ([fast.com settings UI](https://fast.com); described in [gHacks review](https://www.ghacks.net/2018/07/18/netflixs-fast-com-internet-speed-test-gets-better)).
- **Why Netflix runs a speed test:** Netflix uses the test for consumer trust and ISP transparency.
  Users can check Netflix's connection with an ad-free, minimal test. The test has no upsell or ads ([about.netflix.com](https://about.netflix.com/news/fast-com-now-measures-latency-and-upload-speed), [gHacks](https://www.ghacks.net/2018/07/18/netflixs-fast-com-internet-speed-test-gets-better)). **Inference:** fast.com also supports Netflix's ISP-performance narrative. It measures Netflix's own CDN path. rack-bench uses the same approach to certify a datacenter node's egress to object stores/CDNs.
- **Industry context for loaded latency:** "A large gap between unloaded and loaded latency results (for example, 10ms unloaded but 180ms under load) is a reliable indicator of bufferbloat" ([Preseem](https://preseem.com/2023/06/how-to-reduce-latency-for-isps-and-subscribers)); Bufferbloat-era measurements show loaded latency of seconds: "a good router will minimize the additional latency, but many routers will add a lot — between two and five seconds (2000 to 5000 msec)" ([Hacker News discussion of fast.com](https://news.ycombinator.com/item?id=17557242)).

### 1.2 The Netflix ISP Speed Index — computed from actual streams
The index is "a measure of prime time Netflix performance on particular ISPs (internet service providers) around the globe … determined by calculating the average primetime bitrate for Netflix content streamed by Netflix subscribers in a particular month" ([GVTC summary](https://blog.gvtc.com/gvtc-ranks-1-nationwide-on-netflix-isp-speed-index); official: [ispspeedindex.netflix.net](https://ispspeedindex.netflix.net)). Netflix shows the exact computation ([How We Calculate Rankings](https://ispspeedindex.netflix.net/about)):
1. **Step 1 — per-bucket time-weighted bitrate:** Each streamed session has a known maximum achievable bitrate.
   The requested resolution (SD/HD/4K), streaming device, and encode recipe set this maximum.
   Netflix puts prime-time sessions in **0.5 Mbps buckets** by maximum possible bitrate.
   It computes the **time-weighted bitrate achieved** for all sessions in each bucket.
   For example, sessions capped at 5.0–5.5 Mbps achieve 5.2 Mbps time-weighted.
2. **Step 2 — global normalization:** Netflix computes the global hours-distribution over the same 0.5 Mbps buckets.
   It normalizes every ISP to that distribution.
   If 10% of global hours occur in the 0.5–1 Mbps bucket, the ISP's 0.9 Mbps gets 10% weight.
   Netflix shows the weighted sum as the **Speed Index metric in Mbps**.
3. **Prime time** = "the top 3 hours of Netflix viewing each day for each ISP" (so the hours themselves are data-driven, per-ISP, per-day).
4. **Coverage rules:** Netflix uses home broadband networks only.
   It removes cellular streams by IP CIDR ranges or device-reported cellular connections. It uses ISPs only if they "consistently have >1% of Netflix view hours in the country"; **no sampling — Netflix uses all prime-time sessions**.
   Netflix puts results on the site on the 2nd Monday of the following month.
   It uses ISP type labels Fiber/Cable/DSL/Wireless/Satellite ([same methodology page](https://ispspeedindex.netflix.net/about)).
5. **Recent numbers:** The September 2025 index shows twenty-four countries/regions in the top tier at **3.2 Mbps** average ([About Netflix: September 2025 index](https://about.netflix.com/news/netflix-isp-speed-index-for-september-2025)). The 2025 index shows top four providers: Telus Fiber Canada, LG U+ Korea, Virgin UK, and Optimum Fiber US.
   Each shows **3.37 Mbps** monthly averages. Netflix now uses quarterly reporting ([The Pickool summary of the annual index](https://www.thepickool.com/2025-netflix-isp-speed-index-top-global-providers)).
6. **What this measures:** "Higher Netflix performance generally means better picture quality, quicker start times, and fewer interruptions" — i.e., Netflix uses *server-side, all-session, application-layer* measurements for the index, not synthetic probes ([About Netflix](https://about.netflix.com/news/netflix-isp-speed-index-for-september-2025)). Users can get historical 2012–2020 data as a CSV from Netflix. This data uses the older methodology ([ispspeedindex.netflix.net/about](https://ispspeedindex.netflix.net/about)).
7. **[calculation]** Encode recipes make the index's 3.2–3.4 Mbps ceiling.
   Top 4K ladders cap session bitrates well below raw link speed.
   The index shows the *fraction of achievable bitrate realized* for each ISP, not raw capacity.
   It saturates in well-peered markets.

   **Inference:** Use this metric as a model for GPU-rack uplink certification.
   Compare achieved application bitrate with the maximum possible. Do not copy its threshold.

### 1.3 Open Connect appliance health-checking and ISP-link monitoring
- **Continuous health monitoring by Netflix's NOC:** "OCAs report health values and get their configuration from the Open Connect supporting services … Netflix will monitor the health and performance of each OCA as soon as it is reachable from our Network Operations Center (NOC) … Health and system load information feedback is automatically incorporated into Netflix content routing decisions" ([Open Connect Appliances page](https://openconnect.netflix.com/en/appliances)).
- **Turn-up gating ("OCA Live checks"):** "The appliance will not start serving client traffic until all checks pass and acceptable offload can be achieved. When the system is ready, the Netflix Open Connect Operations team will automatically enable the system to serve clients and will continue to monitor its performance. At this point, we will start monitoring and flagging a similar set of Live checks" ([Open Connect Deployment Guide PDF](https://openconnect.netflix.com/deploymentguide.pdf)). An ISP can check basic OCA health through the Netflix Partner Portal at `https://my.oc.netflix.net` (same source).
- **Program mechanics:** ISP partners "configure BGP sessions with the OCAs to steer traffic," and provide "a small amount of data center rack space, power, and connectivity"; Netflix sends the configured, pre-filled appliance (~1 week shipping).
  It uses "ongoing health monitoring and maintenance," and sends "replacement power supplies or optics in case of failure at no cost to the ISP" ([Open Connect overview](https://openconnect.netflix.com/en), [appliances page](https://openconnect.netflix.com/en/appliances)).
- **Software stack** (third-party documentation): FreeBSD OS, NGINX web server, BIRD routing daemon, IPv4+IPv6, plus "other software [that] handle[s] content management and transmits information regarding the system's health and other statistics to the Open Connect supporting services at Netflix" ([Open Connect Wikipedia](https://en.wikipedia.org/wiki/Open_Connect)).

---

## 2. Cloudflare — speed test, AIM, Radar, 1.1.1.1, Argo

### 2.1 The speed-test methodology (loaded latency, jitter, loss, throughput bands)
From Cloudflare's own methodology deep-dive ([How does Cloudflare's Speed Test really work?](https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work)):
- The engine runs on Cloudflare's Network Quality API on Workers. It uses anycast, so "your browser begins sending data requests … right away," Cloudflare sends these requests to the nearest data center automatically.
- **It deliberately does not saturate the connection:** it "sends a series of data payloads of predefined sizes — what we call data blocks" a fixed number of times.
  The test shows box-and-whisker plots (ranges/percentiles) per block size. Download/upload numbers are "the rate at which you can reliably expect to send various sizes of data," not peak capacity.
- **Latency model:** The test records idle latency first, on page load. Then "as throughput measurements run, the test also sends empty requests at regular intervals to measure loaded latency: the round-trip time (RTT) … while your connection is busy." Jitter = "the average variation between consecutive RTT measurements."
- **Packet loss:** "the percentage of packets that fail to reach the destination when relayed through a WebRTC TURN server over a period of time" — The test measures loss as an application sees it, not with ICMP.
- **Diagnostic heuristics published by Cloudflare:** "differences approaching 100 milliseconds or more over a wired connection" between idle and loaded latency mean "your ISP is likely at fault".
  Transfers smaller than **10 MB** are latency-limited and "can't utilize the full bandwidth" of a fast connection (same source).
- **Known limitation (Cloudflare's own words):** results include browser + Wi-Fi + local network, "don't solely reflect the performance of your ISP," and "no speed test — including Cloudflare's — is a definitive measure of ISP service."
- **Data volume:** a run "can consume up to 200MB of data" ([Radar speed-test page](https://radar.cloudflare.com/speedtest)).

### 2.2 The AIM (Aggregated Internet Measurement) internet-quality score — exact thresholds
AIM gives points for each metric. It computes scenario scores for **Streaming, Gaming, and WebChat/RTC**.
The scores use **Bad / Poor / Average / Good / Great** labels ([AIM docs](https://developers.cloudflare.com/speed/aim/)). The full rubric ([AIM announcement blog](https://blog.cloudflare.com/aim-database-for-internet-quality/)):

| Metric | 0 pts | 5 pts | 10 pts | 20 pts | 30 pts |
| --- | --- | --- | --- | --- | --- |
| Loss rate | > 5% | < 5% | < 1% | | |
| Jitter | > 20 ms | < 20 ms | < 10 ms | | |
| Unloaded latency | > 100 ms | < 50 ms | < 20 ms | < 10 ms | |
| Download throughput | < 1 Mbps | < 10 Mbps | < 50 Mbps | < 100 Mbps | < 1000 Mbps |
| Upload throughput | < 1 Mbps | < 10 Mbps | < 50 Mbps | < 100 Mbps | < 1000 Mbps |
| Loaded − unloaded latency difference | > 50 ms | < 50 ms | < 20 ms | < 10 ms | |

Scenario composition (same source):
**Streaming** = download + unloaded latency + packet loss + (loaded−unloaded diff), max 70 pts.
**Gaming** = packet loss + unloaded latency + (loaded−unloaded diff), max 40 pts.
**RTC/video** = packet loss + jitter + unloaded latency + (loaded−unloaded diff), max 50 pts.

The blog shows a connection with scores: 25/70 (Average) streaming, 15/40 (Poor) gaming, and 15/50 (Average) RTC.
After the Wi-Fi AP move, the scores show 45/70 (Good), 35/40 (Great), and 35/50 (Great).

Field data uses a Tokyo sample from the first week of October.
The sample shows **5,814 speed tests**: 50.7% with good streaming quality, 48.2% with average streaming quality.
The sample shows 39% with a poor gaming experience.

City average scores (streaming/gaming/RTC): Tokyo 31/13/16, New York 33/13/17, Mumbai 25/13/16, Dublin 32/14/18 ([same blog](https://blog.cloudflare.com/aim-database-for-internet-quality/)). A community review shows the scoring intent.
A ~150 Mbps up/down connection with >100 ms latency can be "Great" for streaming.
The same connection can be "Poor" for gaming or video chat ([NetBeez review](https://netbeez.net/blog/measuring-internet-speed-with-cloudflares-speedtest)).

### 2.3 Cloudflare Radar — Internet Quality Index and Connection Quality by country/ASN
From the Radar Internet Quality launch post ([Introducing the Cloudflare Radar Internet Quality Page](https://blog.cloudflare.com/introducing-radar-internet-quality-page/)):
- **Two distinct data products:** The **Internet Quality Index (IQI)** estimates average quality from end-user measurements against "a set of Cloudflare & third-party targets" . Cloudflare uses the same method to benchmark its own edge, per its [benchmarking post](https://blog.cloudflare.com/benchmarking-edge-network-performance/).
  **Connection Quality** shows peak/best-case characteristics from `speed.cloudflare.com` results. It uses results from the previous **90 days**.
- **IQI math:** Cloudflare computes each metric for each ASN at **15-minute intervals**.
  It uses the **25th percentile, median, and 75th percentile**.
  At country level, it combines these numbers with weights from **estimated user population of each ASN** (from [APNIC's stats](https://stats.labs.apnic.net/aspop)) "biasing the numbers away from networks that source a lot of automated traffic but have few end users."
- **Connection Quality math:** Cloudflare combines p25/median/p75 for each ASN through the **trimean**.
  It uses 90-day aggregation for variability. Users have different test motives. Cloudflare records no PII.
- **By design, IQI punishes international-link dependence:** "IQI will show worse results for regions and Internet providers that rely on international (rather than peering) links for most content," IQI shows web-browsing load rather than bulk transfer (same source). **Inference:** A Chennai datacenter may depend heavily on international capacity (Mumbai/Chennai submarine cables + NIXI peering).
  IQI-style multi-target measurement gives a more honest result than one nearest-CDN speed test. `bench internet` should test "public object stores and CDNs".
- **IQI data shows published outage/quality case studies** (same post).
  Virgin Media UK (AS5089) data shows median bandwidth **~35 → ~23 Mbps** several days *before* the April 2023 outages.
  This gives an early-warning signal.

  PLDT (AS9299) data shows a June 2023 submarine-cable fault.
  Median bandwidth halves **17 → 8 Mbps**. Median latency shows **+75% (37 → 65 ms)**.
  p75 latency nearly triples **63 → 180 ms**.

  Pakistan May 2023 mobile-shutdown data shows country median latency down ~25%.
  Users move from mobile to fixed broadband.
- **Year-in-review aggregates:** The 2025 data shows European countries with the highest median download speeds, all above **200 Mbps**.
  Spain consistently has the highest value.
  Governments direct almost half of **174 major Internet outages** globally.
  Indian clients **use IPv6 for over two-thirds of dual-stack requests** ([2025 Radar Year in Review](https://blog.cloudflare.com/radar-2025-year-in-review)).

  The 2023 reference gives Iceland the best overall rank.
  Its average speeds: **282.5 Mbps down / 179.9 Mbps up**.
  Its average latency: **9.6 ms idle / 77.1 ms loaded latency** ([2023 Year in Review](https://blog.cloudflare.com/radar-2023-year-in-review)).
- **Radar API / Radar UI** show the same data programmatically: IQI percentiles and quality by country/ASN.
  See the [Radar quality pages](https://radar.cloudflare.com/quality) and the [speed-test data announcement](https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work).
  Cloudflare also puts all Radar results in Measurement Lab's public BigQuery dataset ([AIM/M-Lab partnership](https://blog.cloudflare.com/aim-database-for-internet-quality)).

### 2.4 Radar outage and traffic-anomaly detection
- **Detection method:** Cloudflare builds a **forecast from historical traffic and compares observed traffic against it**; "if what we are observing is significantly different from what we expect, we call it an anomaly" (drops only). The anomaly threshold uses α.
  A detection keeps the same reference until traffic is normal.
  Cloudflare uses **lower thresholds and a four-hour no-anomaly window** before it closes a detection.
  This prevents flap-counting ([Gone offline: how Cloudflare Radar detects Internet outages](https://blog.cloudflare.com/detecting-internet-outages)).
- **Publication:** Cloudflare puts detected country/ASN anomalies in the **Radar Outage Center**.
  Each entry shows type, entity, start time, duration, and verification status, with subscription notifications.
  Cloudflare first uses an internal alert workflow. It then puts entries in the public center ([Traffic anomalies and notifications with Cloudflare Radar](https://blog.cloudflare.com/traffic-anomalies-notifications-radar)).
- **Ongoing reporting:** Quarterly disruption summaries show event causes: weather, earthquakes, power outages, government shutdowns, and cable cuts.
  Other causes include cloud-infrastructure damage and DNSSEC misconfiguration ([Q2 2026 disruption summary](https://blog.cloudflare.com/q2-2026-internet-disruption-summary)).

### 2.5 Route-leak and hijack detection, RPKI/ASPA tracking
- **BGP origin-hijack detection:** Cloudflare Radar scores each BGP event before publication.
  The check sequence uses **RPKI, IRR, bogon prefixes/ASNs, AS relationships, and AS path** ([Cloudflare Radar's new BGP origin hijack detection system](https://blog.cloudflare.com/bgp-hijack-detection)).
- **Route-leak detection:** the module "works at the level of individual BGP announcements … estimates how likely a given BGP message is a result of a route leak event"; Cloudflare groups leaks into route-leak events. It shows them through web UI, API, and alerts ([How we detect route leaks](https://blog.cloudflare.com/route-leak-detection-with-cloudflare-radar)).
- **Routing visibility:** Radar shows real-time route visibility.
  Example: a prefix has validity from **94 of 121 peers → visibility 0.777**, with `rpki_validation` per origin.
  Radar lists aggregated looking-glass alternatives: bgp.tools, bgp.he.net, RouteViews, NLNOG RING ([Bringing connections into view](https://blog.cloudflare.com/bringing-connections-into-view-real-time-bgp-route-visibility-on-cloudflare)).
- **RPKI adoption tracking:** Radar's Routing section shows RPKI validation status, **ASPA deployment trends**, and per-ASN provider details.
  It also shows an **ASPA validation tool**.
  Put a BGP `AS_PATH` in the tool. The tool gives `Valid` / `Invalid` / `Unknown`.
  Invalid means "no chain of provider authorizations covers the whole path … the signature of a route leak" ([Radar changelog](https://developers.cloudflare.com/changelog/product/radar)).

  API endpoints include `/bgp/ips/top/ases` and `/bgp/rpki/roas/timeseries` (same source). Cloudflare shows external network capacity above **500 Tbps** ([Cloudflare blog tag: RPKI](https://blog.cloudflare.com/tag/rpki)).
- **This concrete India-adjacent event directly matters for Chennai routing.**

  Analysis of Cloudflare's 2025-11 resolver incident shows "a pre-existing BGP hijack by AS4755 (Tata Communications India)" of **1.1.1.0/24**.
  The hijacked route has **RPKI-invalid** status. The analysis shows "networks that properly implemented RPKI-based origin validation did reject it, and their users remained unaffected,".
  Other networks (e.g., Lumen, AT&T) show no routes. This suggests that they use RPKI filtering. Catchpoint's Internet Sonar shows the issue at **21:50 UTC**.

  Cloudflare's internal incident declaration shows **22:01 UTC**, minutes later ([Catchpoint analysis](https://www.catchpoint.com/blog/cloudflares-resolver-outage-more-than-just-dns)). Cloudflare's post-mortem shows a November 18, 2025 outage — "our worst outage since 2019".
  It shows an auto-generated threat-traffic configuration file as the cause. The file "grew beyond an expected size of entries and triggered a crash" ([Cloudflare post-mortem](https://blog.cloudflare.com/18-november-2025-outage)).

### 2.6 1.1.1.1 performance monitoring
- Cloudflare shows the **April 1, 2018** launch of 1.1.1.1 as "the Internet's fastest, privacy-first public DNS resolver,".
  Cloudflare commits to no querying IPs on disk with DNS queries.
  An independent privacy examination validates this commitment ([privacy examination results](https://blog.cloudflare.com/announcing-the-results-of-the-1-1-1-1-public-dns-resolver-privacy-examination)).
- Independent latency benchmarks (2024–2025 global averages): **1.1.1.1 ~11 ms global / ~8 ms US, jitter ~3 ms**.
  Google 8.8.8.8 shows ~14 ms global / ~10 ms US, jitter ~5 ms ([DNS Benchmark comparison](https://dnsbenchmark.app/blog/cloudflare-vs-google-dns)).
- Third parties monitor resolver health in practice.
  The July 14, 2025 1.1.1.1 outage shows an internal DLS misconfiguration.
  That misconfiguration removes the 1.1.1.1 **BGP prefixes** — "the DNS servers themselves weren't malfunctioning … without valid routes, DNS queries couldn't reach Cloudflare's resolvers"). External Internet-performance monitoring shows the outage.
  This shows that **resolver reachability is a BGP/routing property, not a service property** ([Catchpoint](https://www.catchpoint.com/blog/cloudflares-resolver-outage-more-than-just-dns)).

  **Inference:** A bench DNS-health check needs resolution latency.
  Users check this with `dig @1.1.1.1 example.com` timing ([Cloudflare community examples](https://community.cloudflare.com/t/high-dns-filtering-latency-with-cloudflare-gateway/501423)).
  The check also needs path integrity: BGP visibility of the resolver prefix.

### 2.7 Argo Smart Routing — measurement-driven path selection
- **Product claim:** "detect[s] and rout[es] traffic around real-time network congestion … on average, it can make web applications **30% faster**,".
  Argo uses timing data from the **~115 million HTTP requests/second** average on Cloudflare's network ([Argo product page](https://www.cloudflare.com/application-services/products/argo-smart-routing)).
- **How it decides:** Argo uses "existing timing data from traffic that's already being sent over our edge to optimize routes" — passive measurement, not synthetic probes ([Argo 2.0 blog](https://blog.cloudflare.com/argo-v2)). Third-party testing supports this: Argo "monitors Cloudflare's network in real time and collects latency and packet loss data from each request … uses this information to find the fastest and most optimal paths" ([SpeedVitals review](https://speedvitals.com/blog/cloudflare-argo-review)); A hosting provider's dashboard shows "70% of our traffic gets a 43% latency improvement" ([Servebolt](https://servebolt.com/help/feature/cloudflare-support/argo-smart-routing)).
- **Argo 2.0 (for Packets) numbers:** "**10% average latency improvement worldwide** in our internal testing," with last-mile optimizations that "can save **up to 40% on last mile round trip time (RTT)**" ([Argo v2 blog](https://blog.cloudflare.com/argo-v2)). Community operators use **~6–8 hours of global traffic** with Argo enabled for a good baseline.
  Users can query per-datacenter Argo metrics through the Cloudflare API for custom reports ([Cloudflare community](https://community.cloudflare.com/t/need-help-understanding-argo-traffic-routing-patterns/596574)).

### 2.8 What Cloudflare exposes that a third-party bench can reuse
1. **The open-source speed-test engine:** `github.com/cloudflare/speedtest` — The embeddable JavaScript engine uses the same measurements. Its API methods include `getUnloadedLatency()`, `getUnloadedJitter()`, `getDownLoadedJitter()`, `getDownLoadedLatencyPoints()`, `getSummary()`, and `getScores()` ("the computed AIM scores that categorize the quality of the network connection according to use cases such as streaming, gaming or real-time communications").
   The repository also shows AIM score calculation code ([repo README](https://github.com/cloudflare/speedtest); [AIM blog](https://blog.cloudflare.com/aim-database-for-internet-quality)). **[calculation]** This artifact gives the most direct reuse among the surveyed companies.
   It shows measurement method + scoring rubric + open data.
2. **The public dataset:** Cloudflare puts all speed-test results in Measurement Lab's public BigQuery repository and the Radar API.
   Cloudflare removes identifying data from these results ([speed-test deep-dive](https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work)).
3. **The Network Quality API** now scales for third-party integration.
   UNICEF's Giga project uses Cloudflare's Speed Test to measure school connectivity with "up to **10 million availability tests per month** … on Internet speed, latency, and affordability" ([Giga partnership](https://finance.yahoo.com/news/cloudflare-partners-giga-unicef-itu-201717810.html)). Orb uses it for continuous end-user monitoring ([speed-test deep-dive](https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work)).
4. **Radar API** for country/ASN quality, outages, routing anomalies, RPKI coverage — free tier available for research ([Radar](https://radar.cloudflare.com/quality), [API announcement](https://blog.cloudflare.com/traffic-anomalies-notifications-radar)).
5. **Planned capability (2026):** Cloudflare plans higher-throughput measurements for "enterprise or shared-office environments where multiple users share the same connection".
   Cloudflare shows that its current non-saturating design undershoots enterprise bandwidth validation ([deep-dive](https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work)). **Inference:** A rack bench must NOT copy Cloudflare's data-block approach alone.
   It must also saturate the link with bulk transfer to certify contracted uplink capacity.

---

## 3. Akamai — mPulse RUM, the old State of the Internet reports, and edge health

### 3.1 mPulse real-user monitoring
- **What it collects:** "200+ business and performance metrics are collected during real-world user sessions and returned via an mPulse beacon" — Pages use a JavaScript beacon (Boomerang-based).
  The beacon sends real-time data to dashboards. Users can select user/device segments and use alerts ([mPulse product page](https://www.akamai.com/products/mpulse-real-user-monitoring)).
- **Performance timers:** mPulse uses **metrics** for non-performance data, such as conversion/bounce rate.
  It uses **timers** for performance data: "DNS lookup time, SSL connection time, front-end time, back-end time, and page load time,".
  It also uses custom timers. Element-level per-page-load waterfalls show "exactly when every HTML, image, style sheet, and JavaScript asset is requested and how long they take to load," with component timings like DNS lookup, TCP connect time ([Use metrics and timers](https://techdocs.akamai.com/mpulse/docs/use-metrics)).
- **Percentiles, not means:** The standard integration shows **p50 and p95 page load times** (`akamai.mpulse.pageload.p50` / `.p95`).
  It also shows first-byte timing and time-between-first-and-last-byte durations ([Datadog integration doc](https://www.datadoghq.com/blog/integrate-akamai-mpulse-real-user-monitoring-with-datadog)).
- **RUM vs synthetic framing:** Akamai's glossary shows RUM with "data on a wide range of performance metrics and dimensions from actual user sessions,".
  RUM complements synthetic monitoring that "simulates user interactions" ([Akamai RUM glossary](https://www.akamai.com/glossary/what-is-real-user-monitoring)). **Inference:** mPulse measures *application-layer* experience (page load, availability, TTFB), not link throughput.
  Analysts infer ISP quality from RUM distributions by geography/ASN.
  Netflix uses the same inference with the ISP Speed Index.
- **Akamai's own research links QoE to engagement.**
  The research shows this effect: **1 second of additional startup delay causes a 5.8% increase in user abandonments** (Krishnan & Sitaraman, Akamai/Umass — cited in [INFOCOM 2018 real-time QoE monitoring paper](https://hammadmazhar1.github.io/files/real-time-infocom18.pdf)).

### 3.2 State of the Internet (connectivity) — methodology
- **Data basis:** "Akamai's quarterly State of the Internet report is based on data collected from the globally-distributed Akamai Internet Platform, carrying as much as **30 percent of global Web traffic** on any given day, and with servers located in **650 cities, 72 countries** and deployed within approximately **1,000 of the Internet's most important networks**" ([PR Newswire, 4th-year anniversary release](https://www.prnewswire.com/news-releases/akamais-state-of-the-internet-report-enters-fourth-year-of-analyzing-global-connectivity-attack-traffic-and-broadband-consumption-126145798.html)).
- **Metrics published:** Akamai publishes average connection speed and average **peak** connection speed.
  Adoption tiers include high broadband (≥10 Mbps), broadband (≥4 Mbps), and narrowband (<256 kbps).
  Later tiers include 15/25 Mbps adoption.
  A companion visualization tool shows trend graphs by geography ([same release](https://www.prnewswire.com/news-releases/akamais-state-of-the-internet-report-enters-fourth-year-of-analyzing-global-connectivity-attack-traffic-and-broadband-consumption-126145798.html)).
- **Definition subtlety:** Akamai uses HTTP session data at its edges for "average connection speed" (unique IPs, Akamai-served traffic).
  This gives lower values than synthetic tests of the same era.
  Examples: global average **5.0 Mbps**, Q1 2015; South Korea **23.6 Mbps**; Singapore peak **98.5 Mbps** ([Q1 2015 report PDF](https://www.akamai.com/site/en/documents/state-of-the-internet/2021/akamai-state-of-the-internet-report-q1-2015.pdf)). The Q1 2017 report shows global average **7.2 Mbps** and South Korea **28.6 Mbps**.
  It also shows IPv6 traffic share per country ([Q1 2017 executive summary](https://www.akamai.com/site/en/documents/state-of-the-internet/2021/q1-2017-state-of-the-internet-connectivity-executive-summary.pdf)). A separate SOTI Security report shows security/attack-traffic content from that period (same source).

  Akamai no longer uses the connectivity series. Current SOTI output shows security research ([Akamai SOTI page](https://www.akamai.com/security-research/the-state-of-the-internet)).

### 3.3 How a CDN decides a POP/path is unhealthy
- **Observed:** Akamai's public materials show these health-signal sources.
  (a) Edge-side session data across the platform uses the SOTI data basis above.
  (b) mPulse uses RUM beacons per session ([mPulse](https://www.akamai.com/products/mpulse-real-user-monitoring)), (c) Element-level waterfalls show diagnostic data ([use-metrics](https://techdocs.akamai.com/mpulse/docs/use-metrics)).
- **Gap (explicit):** Researchers find no public Akamai documentation for its internal edge-probing/POP-health decision system.
  The gap covers thresholds, probe cadence, and withdrawal logic. See §9. **Inference:** Peer systems give a comparison: Netflix's OCA live checks with offload gating, §1.3; Meta's Edge Fabric, §5.1.
  These systems suggest continuous passive session-quality telemetry and automated withdrawal/steering for POP health decisions.
  This is almost certainly the mechanism, but Akamai's mechanism remains an inference, not a sourced fact.

---

## 4. Google — YouTube QoE, BBR, Google Global Cache, interconnection

### 4.1 YouTube QoE — measuring "good internet" from the server side
- **The Video Quality Report (2014–):** Google's launch introduces a "Video Quality Report".
  It "sheds light on exactly what kind of performance your Internet Service Provider delivers" for YouTube.
  The report ranks ISPs by how often they send streams in HD ("HD hours" per ISP).
  It shows the network path from Google's edge ([Google Canada blog](https://canada.googleblog.com/2014/01/youtube-launches-new-video-quality.html); [StreamingMediaBlog coverage](https://www.streamingmediablog.com/2014/01/google-launches-video-quality-report-rates-isps-delivery-youtube-content.html)). This directly precedes Netflix's ISP Speed Index. It measures each ISP from sessions.
- **QoE metric families** give the industry-standard taxonomy that Google-era services use.
  The families include rebuffer ratio, join/startup time, playback failures, and average bitrate/resolution.
  Startup delay and rebuffering reduce engagement.
  Akamai's 5.8%-per-second-of-startup-delay figure above shows this effect ([INFOCOM 2018](https://hammadmazhar1.github.io/files/real-time-infocom18.pdf)). 

  Operators widely use these benchmarks.
  Video startup: **<1 s excellent / 1–2 s acceptable / >3 s needs attention**.
  Rebuffer ratio: **<0.5% excellent / 0.5–1% acceptable / >3% needs attention**.
  VSF: <0.3%/<0.5%/>1%. Exit-before-video-start: <1%/<3%/>5% ([Qualabs QoE metrics guide](https://www.qualabs.com/blog/video-qoe-metrics-ott)). Netflix's own consumer guidance: **5 Mbps for HD, 15 Mbps for 4K** ([Business Insider troubleshooting guide](https://www.businessinsider.com/reference/netflix-not-working)).
- **Encrypted-traffic monitoring literature** shows how the industry does server-side QoE now.
  Researchers continuously infer QoE metrics from encrypted streams with machine learning in **10-second windows**.
  These metrics include startup delay and rebuffering ([Real-time QoE monitoring, INFOCOM'18](https://hammadmazhar1.github.io/files/real-time-infocom18.pdf)). **Inference:** Google does not publish its internal YouTube QoE dashboards.
  The Video Quality Report shows a public, sourced artifact of that measurement system.

### 4.2 BBR — Google's measurement finding, and fleet deployment
- **The measurement insight:** loss-based congestion control (CUBIC) cannot use high-BDP paths with loss: "for CUBIC, sustaining **10 Gbps over 100 ms RTT** needs a packet loss rate below **0.000003%** (more than 40 seconds between packet losses) … over a 100 ms RTT path a more feasible loss rate like **1%** can only sustain at most **3 Mbps**" ([IETF BBR draft](https://www.ietf.org/archive/id/draft-cardwell-iccrg-bbr-congestion-control-01.html), citing RFC 8312). The CACM paper's canonical worked example uses an **8 MB / 200 ms intercontinental RTT** link.
  BBR sends at full bandwidth on that link. Loss-based CC collapses ([BBR: Congestion-Based Congestion Control, CACM Queue](https://queue.acm.org/doi/fullHtml/10.1145/3012426.3022184)).
- **How BBR measures:** BBR continuously estimates two path parameters.
  These are **bottleneck bandwidth (max recent delivery rate)** and **round-trip propagation time (minimum RTT)**.
  BBR paces packets at their product.
  It probes at **125% of estimated bandwidth** and drains at 75%.
  ProbeRTT's design sacrifices "no more than roughly **2%** of a flow's available bandwidth" and keeps ProbeBW active for "at least roughly 96%" of time in ProbeBW ([IETF draft](https://www.ietf.org/archive/id/draft-cardwell-iccrg-bbr-congestion-control-01.html); [morning paper summary](https://blog.acolyer.org/2017/03/31/bbr-congestion-based-congestion-control)).
- **Deployment result:** Google's deployment results show "**2–25x throughput improvement** over the previous loss-based congestion control CUBIC" on its paths.
  Initially, deployed TCP receive buffer sizes limit BBR. Google removes this limit with larger buffers.
  Google deploys BBR across its serving fleet, including YouTube ([morning paper](https://blog.acolyer.org/2017/03/31/bbr-congestion-based-congestion-control)). Google Cloud's later deployment uses BBR for GCP external TCP traffic: "because of this ability to curb bufferbloat, one might say that BBR could also stand for BufferBloat Resilience" ([GCP blog](https://cloud.google.com/blog/products/networking/tcp-bbr-congestion-control-comes-to-gcp-your-internet-just-got-faster)).
- **Bench-relevant command:** BBR ships in mainstream Linux.
  For example, RHEL 8+ kernels support `tcp_bbr`.
  Enable it with sysctl `net.ipv4.tcp_congestion_control=bbr` ([RHEL BBR configuration guide](https://oneuptime.com/blog/post/2026-03-04-configure-tcp-bbr-congestion-control-algorithm-rhel/view)).

  **Inference:** A default-CUBIC certification run on a long, lossy path can under-report provisioned capacity by orders of magnitude.
  Chennai → US object stores is an example.
  Run rack-bench bulk transfers under both CUBIC and BBR. Alternatively, explicitly pin and report the CC algorithm.

### 4.3 Google Global Cache — what an ISP must provide
- **Program shape:** GGC is "a voluntary program … that allows ISPs to host caches that serve Google traffic within their own network … These caches temporarily store static content that is popular with the ISP's subscribers,".
  This lets ISPs avoid carrying that traffic from a Google POP ([Google Cloud blog: network infrastructure investments](https://cloud.google.com/blog/products/infrastructure/google-network-infrastructure-investments)). "Google provides the box and fills it. The ISP provides rack space, power and internal transport. The ISP saves transit; Google saves peering egress and shortens the path" ([BlazingCDN's technical analysis of YouTube's CDN](https://blog.blazingcdn.com/en-us/how-youtube-cdn-works)).
- **Routing/fill mechanics (documented requirement):** "To enable peer-to-peer traffic, the IP prefix of the GGC servers must be advertised to all GGC nodes that you want to be candidates to be cache-fill sources" . The host network must run BGP toward the GGC nodes for cache-fill ([Google Interconnect Help: Cache-Fill](https://support.google.com/interconnect/answer/7658593?hl=en)).
- **Peering requirements (public):** Google's peering portal requires presence at major interconnection locations and adequate port capacity.
  A CDN-industry practitioner gives this summary: "go look up peering.google.com and you'll see what's required to peer with Google — be present in one of the big locations where all the exchanges take place and have 10-gig ports and ASNs" — with "technical requirements only … and no cost involved" ([Cloud Native Media podcast, EP4](https://www.youtube.com/watch?v=8zOSDpIfTT4)). Google also states an **open peering policy** for Media CDN, connecting "to as many networks as possible, which reduces latency and improves the capacity for large traffic spikes" ([Media CDN cache locations](https://docs.cloud.google.com/media-cdn/docs/locations)).

### 4.4 Google's interconnection measurement stance
- Google's public stance is interconnection-transparency-by-construction.
  Google publishes per-ISP measured YouTube delivery quality (the Video Quality Report, §4.1).
  It publishes its peering/GGC requirements (§4.3).
  Google puts money into POPs "to bring content closer to ISPs and end users" ([network infrastructure blog](https://cloud.google.com/blog/products/infrastructure/google-network-infrastructure-investments)). **Inference:** unlike FCC-style regulator measurement, Google's stance is "we measure you with our real traffic and publish it" 
  rack-bench uses the same measured-never-claimed philosophy for a datacenter's uplink.

---

## 4.5 Cross-company QoE→engagement evidence (used by all streaming companies)
The industry cites causal QoE literature: **+1 s startup delay → +5.8% abandonments** (Krishnan & Sitaraman).
Rebuffer-event rate negatively correlates with engagement (Dobrian et al.).
The real-time QoE monitoring paper cites both findings ([INFOCOM'18](https://hammadmazhar1.github.io/files/real-time-infocom18.pdf)).

---

## 5. Meta — edge/WAN monitoring at scale

### 5.1 Edge Fabric — measurement-augmented BGP at the edge
- "Edge Fabric is able to **augment BGP with measurement and control mechanisms** to overcome BGP's lack of congestion awareness and performance awareness," Edge Fabric steers egress user traffic from PoPs worldwide.
  Meta's production record spans years.
  The edge stack includes **fbflow** for host-based "end-to-end flow monitoring".
  It includes **Robotron** for cross-domain network lifecycle automation.
  The backbone runs Express Backbone + Open/R as an SD-WAN with centralized traffic engineering ([Engineering at Meta: Steering oceans of content to the world](https://engineering.fb.com/2017/08/21/networking-traffic/steering-oceans-of-content-to-the-world)).
- Edge Fabric solves a practical problem. PoPs connect to "tens or hundreds of networks" with heterogeneous connectivity options.
  Meta describes the problem: "traditional routing protocols could not address our needs" given application-level performance requirements (same source). **Inference:** Meta continuously measures and steers link/path health. fbflow closes the loop that BGP leaves open. Check that the bench node can run a "path/routing audit" (mtr, AS-path checks), even without traffic steering.

### 5.2 Host-side telemetry: fbflow, Millisampler, FBOSS
- **Millisampler** (2023): "a **BPF-based, lightweight traffic measurement tool that operates at [millisecond] granularity** … built and deployed **in every server in the entire fleet** at Meta for continual monitoring," because "managing data center networks with low loss requires understanding traffic patterns, especially burstiness of the traffic, at fine time granularity. Yet, monitoring traffic with millisecond granularity fleet wide is challenging" ([Millisampler post](https://engineering.fb.com/2023/04/17/networking-traffic/millisampler-network-traffic-analysis); talk recap in [optimizing large-scale networks](https://engineering.fb.com/2023/01/27/networking-traffic/optimizing-large-scale-networks-meta-engineers)).
- **FBOSS switch software** with built-in monitoring service: canary-based staged code deployment (`fbossdeploy`), Meta warns: "monitoring only before and after a push is not enough. Some failures don't show up immediately".
  Warm Boot keeps forwarding during agent restarts.
  Early monitoring shows "brief error spikes" during weekly updates ([Open networking advances with Wedge and FBOSS](https://engineering.fb.com/2015/11/19/data-center-engineering/open-networking-advances-with-wedge-and-fboss)).
- **Transport-layer monitoring at scale** (2022): Meta's backbone uses QUIC with **cached congestion-control state** across transfers.
  Meta explains the reason: "transfers in high-BDP links incur a startup delay for congestion control to probe the bandwidth … small transfers may repeatedly spend all their transfer time probing" ([QUIC and TCP innovations talk](https://engineering.fb.com/2022/07/06/networking-traffic/watch-metas-engineers-discuss-quic-and-tcp-innovations-for-our-network)).
- **AI-fabric era (2025):** Meta's network monitoring now covers AI clusters: "**packet losses can cause ML training jobs to time out or expire prematurely**".
  Measured link-loss and utilization-skew data drive fabric changes.
  These changes include DPR static routing → adaptive routing and shallow-buffer switches with ~**160 MB** buffers ([Evolution of Ethernet fabrics talk](https://www.youtube.com/watch?v=ELtoxc4g9JI)). The Disaggregated Scheduled Fabric (DSF) uses packet spraying and credit-based congestion control.
  Meta reports "a large skew in the bandwidth utilization of fabric links,".
  Meta says this "impacts how much we should overprovision the fabric" ([DSF post, Oct 2025](https://engineering.fb.com/2025/10/20/data-center-engineering/disaggregated-scheduled-fabric-scaling-metas-ai-journey); [SDxCentral on NSF/Prometheus](https://www.sdxcentral.com/news/meta-unveils-non-scheduled-fabric-architecture-for-gigawatt-scale-ai-clusters)).

### 5.3 Internet Performance from Facebook's Edge (the published measurement study)
- "We execute a large-scale, **10-day measurement study** of metrics at the **TCP and HTTP layers for production user traffic at all of Facebook's PoPs worldwide**, collecting performance measurements for **hundreds of trillions of sampled HTTP sessions** … including a novel approach to characterizing user **achievable goodput from the server side**" ([IMC'19 paper](https://www.iab.org/wp-content/IAB-uploads/2021/09/Internet-Performance-from-Facebooks-Edge.pdf); ACM DL: [dl.acm.org/doi/10.1145/3355369.3355567](https://dl.acm.org/doi/10.1145/3355369.3355567)). This study shows how Meta measures users' *public internet quality*. Meta infers per-session goodput at servers across all PoPs. This is the server-side counterpart of a speed test.
- Meta's networking team catalogs the published systems behind this measurement stack.
  These include Fbflow (SIGCOMM 2015), Robotron (2016), Edge Fabric (2017), FBOSS (2018), and the edge-performance studies ([Meta Research: Networking](https://research.facebook.com/teams/networking)).

### 5.4 Reliability data and monitoring-of-monitoring
- "A Large Scale Study of Data Center Network Reliability" shows **seven years of intra-DC operation data across thousands of network incidents**.
  It also shows **eighteen months of WAN backbone repair tickets**.
  This longitudinal dataset supports Meta's threshold-setting for network health ([Meta Research publication page](https://research.facebook.com/publications/a-large-scale-study-of-data-center-network-reliability)).
- The **Oct 4, 2021 outage** changes Meta's monitoring requirements.
  The incident record shows a backbone drain during maintenance → 6+ hour global outage.
  Responders cannot reach monitoring during that incident.

  Monitoring systems now run **scripted graceful drains roughly every 30 days**. Automation selects the drains.
  On-call staff expect "no degradations in service quality,".
  Meta expects monitoring systems "to be among the most resilient systems at Meta".
  During the 2021 event, some monitoring systems face large loads.
  These loads reach **4–10× larger than typical daily peaks** ([Building Resilient Monitoring at Meta, @Scale](https://atscaleconference.com/building-resilient-monitoring-at-meta)).

### 5.5 What signals Meta collects (summary, from the above sources)
Meta collects session-level HTTP/TCP metrics and server-side goodput at every PoP (IMC'19).
Meta collects ms-granularity per-server traffic burstiness (Millisampler).
Meta collects per-switch state and canary error rates (FBOSS).
Meta collects per-flow host telemetry (fbflow).
Meta uses PoP egress congestion signals for steering decisions (Edge Fabric).
Meta uses fabric link loss and traffic skew for overprovisioning decisions (DSF posts).

 **Note:** Meta does not publish specific *action thresholds* (e.g., "loss > X% triggers drain"). See Gaps.

---

## 6. Spotify, LinkedIn, Microsoft — client-side connectivity telemetry

### 6.1 Spotify
- Spotify's public engineering writing covers **service-side** monitoring.
  The history shows Zabbix + homegrown "sitemon" → the "Hero" monitoring team.
  An in-memory sitemon replacement holds only "roughly one month worth of metrics" at then-current load ([Monitoring at Spotify: The Story So Far](https://engineering.atspotify.com/2015/11/16/monitoring-at-spotify-the-story-so-far)).
- Client telemetry exists as an **event-delivery pipeline**, not a connectivity diagnostic.
  Spotify describes the pipeline: "Whenever a user performs an action in the Spotify client … a small piece of information, an event, is sent to our servers,".
  Spotify logs events through syslog at gateways.
  Spotify uses syslog timestamps "to be able to give latency and completeness guarantees for the event delivery" ([Spotify's Event Delivery](https://engineering.atspotify.com/2016/02/spotifys-event-delivery-the-road-to-the-cloud-part-i)).
- **Observed:** Researchers find no Spotify publication that uses client telemetry to diagnose *ISP* quality.
  Researchers find no Spotify equivalent of the ISP Speed Index or Video Quality Report. See Gaps.

### 6.2 Microsoft — the richest published enterprise-side practice
- **Microsoft 365 network connectivity principles** (the closest enterprise analogue to internet-quality diagnosis): the primary design goal is "to **minimize latency** by reducing the round-trip time (RTT) from your network into the Microsoft Global Network". Core principles: **egress locally**.
  Microsoft explains: "local DNS and internet egress is of critical importance for reducing connection latency".
  **Avoid network hairpins**.
  Check "whether the ISP that is used to provide internet egress … has a **direct peering relationship with the Microsoft Global Network** in close proximity".

  Avoid TLS-decryption/proxying of M365 endpoints. Route to the nearest "Distributed Service Front Door" ([Microsoft 365 network connectivity principles](https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-network-connectivity-principles?view=o365-worldwide)).
- **The Microsoft 365 Network Connectivity Test** (`https://connectivity.office.com`) is Microsoft's public client-side diagnostic.
  The tool runs a signed-in or anonymous test from the user's location.
  It measures connectivity to M365 service front doors. It finds blocked connections.
  The tool saves results and telemetry for review ([connectivity.office.com](https://connectivity.office.com); [M365 connectivity test docs](https://learn.microsoft.com/en-us/microsoft-365/enterprise/office-365-network-mac-perf-onboarding-tool?view=o365-worldwide)).

  The documented test scope checks whether required M365 domains are reachable.
  The tool measures the network path characteristics that the principles above define ([docs](https://learn.microsoft.com/en-us/microsoft-365/enterprise/office-365-network-mac-perf-onboarding-tool?view=o365-worldwide)).
- **Windows client diagnostics (commands):** `netsh wlan show wlanreport` makes a wireless network report.
  The report shows session duration, disconnect reasons, and color-coded event history to diagnose connectivity ([Microsoft Support](https://support.microsoft.com/en-us/windows/experience/connectivity-networking/analyze-the-wireless-network-report)). The **TSS** troubleshooting toolkit runs scenario-scoped traces.
  Examples: `.\TSS.ps1 -Scenario NET_General` (general connectivity); `.\TSS.ps1 -Scenario NET_802Dot1x` / `NET_WLAN` (auth/wireless); `.\TSS.ps1 -Scenario NET_SMBCli` (file transfer).
  The toolkit records full client-side traces, including DHCP DORA sequences ([TSS docs](https://learn.microsoft.com/en-us/troubleshoot/windows-client/windows-tss/collect-data-analyze-troubleshoot-windows-networking-scenarios)). Microsoft documents simultaneous source+destination packet traces as the method to find loss location ("on the source side, you can see the retransmitted packets … on the destination side, these packets won't be present … a network device between source and destination is dropping the packets") ([TCP/IP connectivity troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/windows-client/networking/tcp-ip-connectivity-issues-troubleshooting)).
- **Microsoft's own WAN:** Inside Track describes Microsoft Digital's move to **gNMI push-based streaming telemetry**.
  The telemetry uses **intervals as short as one minute**.
  This lets network engineers "access near real-time data for any onboarded devices so they can find and fix outages in minutes—not hours" ([Microsoft Inside Track](https://www.microsoft.com/insidetrack/blog/boosting-network-performance-at-microsoft-with-real-time-telemetry-and-performance-visualization)). On the consumer/client side, Microsoft's integration puts **Ericsson Enterprise 5G Connect** into Windows 11.
  The announcement describes "an AI- and cloud-analytics-powered platform that **continuously monitors network quality and automatically adjusts connectivity** for best performance".
  The MWC 2026 announcement covers enterprise 5G PCs ([Microsoft/Ericsson announcement](https://finance.yahoo.com/news/microsoft-ericsson-bring-enterprise-grade-165000298.html)).
- **Inference:** Only Microsoft publishes an *enterprise user-side* connectivity diagnosis stack in this set.
  The stack includes a connectivity test tool + principles + per-client commands + telemetry.
  Its measurements target *Microsoft's* service front doors.
  This gives a direct bench template: certify a datacenter node's path to specific SaaS/object-store endpoints.
  Do not certify "the internet" in the abstract.

### 6.3 LinkedIn
- This research pass finds no published LinkedIn practice on client-side connectivity telemetry that diagnoses ISP quality.
  LinkedIn Engineering's public blog covers other domains. See Gaps.

---

## 7. The consumer-internet quality scorecard — what "good" means, and what maps to a datacenter uplink

### 7.1 Cloudflare AIM bands (the de-facto modern consumer score)
§2.2 gives exact thresholds.
Loss **<1%** gives full points; **>5%** gives zero.
Jitter **<10 ms** gives full points; **>20 ms** gives zero.
Unloaded latency **<10 ms** gives the best band; **>100 ms** gives zero.
Loaded−unloaded latency difference **<10 ms** gives the best band; **>50 ms** gives zero.

The rubric uses throughput bands at **1 / 10 / 50 / 100 / 1000 Mbps** ([AIM rubric](https://blog.cloudflare.com/aim-database-for-internet-quality)). Consumer tools use these rule-of-thumb equivalents.
Excellent = **0% loss, latency ≤30 ms, jitter ≤5 ms**.
Good = **loss ≤0.5%, latency ≤50 ms, jitter ≤10 ms** ([check-internet-stability.com](https://check-internet-stability.com)).

### 7.2 FCC Measuring Broadband America + CAF-II thresholds (regulatory)
- **The 80/80 metric:** "the percentage of the advertised speed that at least 80% of subscribers experience at least 80% of the time over peak periods".
  The 11th report shows 7 of 12 ISP/technology configurations at ≥95% of advertised speed by this measure.
  Cincinnati Bell DSL's 80/80 shows the worst case: **46%** of advertised speed ([MBA Eleventh Report](https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-eleventh-report)). The 13th report shows 6 of 12 at or above advertised speed on 80/80.
  A second consistency view shows consumer fractions with medians >95%, 80–95%, <80% of advertised speed ([MBA Thirteenth Report](https://www.fcc.gov/reports-research/reports/measuring-broadband-america/measuring-fixed-broadband-thirteenth-report)).
- **Measurement platform:** SamKnows puts Whiteboxes (off-the-shelf routers with embedded tests) in volunteers' homes.
  The original panel includes 12,000 selected participants.
  Early-year records show ~5,500 whiteboxes covering ISPs that support 85% of US consumers ([FCC open methodology](https://www.fcc.gov/oet/mba/measuring-broadband-america-open-methodology); [CAIDA workshop slides](https://www.caida.org/workshops/wie/1512/slides/wie1512_wjohnston.pdf)). SamKnows gives software source code for non-commercial academic review ([open methodology](https://www.fcc.gov/oet/mba/measuring-broadband-america-open-methodology)).
- **Hard regulatory thresholds (CAF high-cost program):** carriers must show "**at least 80 percent of network speed measurements to be at 80 percent of required speeds** and **95 percent of latency measurements to be at or below 100 milliseconds round-trip time**" . The program treats failure as failure to deploy.
  The program keeps support payments until the carrier shows a full compliant quarter ([USAC performance measures testing](https://www.usac.org/high-cost/annual-requirements/performance-measures-testing)). **[calculation]** This is the only *binary pass/fail* latency+throughput pair in the industry scorecard.
  Thus, it gives the closest regulatory analogue to a certification gate.

### 7.3 SamKnows whitebox test suite (what a regulator-grade agent measures)
From SamKnows' published methodology ([SamKnows Testing Methodology, Sept 2018](https://www.comcom.govt.nz/__data/assets/pdf_file/0038/97859/SamKnows-testing-methodology-September-2018.PDF)):
- **Latency, jitter, packet loss (UDP):** "a fixed-rate stream of UDP traffic … A bi-directional **64 kbps** stream is used with the same characteristics and properties (i.e. packet sizes, delays, bitrate) as the G.711 codec" — The tester measures loss/jitter with VoIP-shaped traffic, not ICMP.
- **Disconnection detection:** When connectivity to all servers fails simultaneously, the UDP latency/loss client increases sampling to **~2,000 packets per hour**, "providing a resolution of **2–4 seconds** for disconnection events."
- **Video streaming test** outputs: "the bitrate reliably streamed; the startup delay (**the time taken to download two seconds of video**); the TCP connection time; the number of stalls and their duration."
- **VoIP emulation:** "The standard configuration uses **500 packets upstream and 500 packets downstream** … the client records the number of packets it sent and received (thus providing a loss rate), and the jitter observed."
- **Other tests:** The suite checks web browsing (time to fetch HTML + referenced resources of a popular page).
  It checks DNS resolution, downstream/upstream throughput, and availability.
  The EU study adds latency/loss **under load**, FTP, and email relaying.
  It uses on-network and off-network dedicated **bare-metal test nodes** as endpoints ([Quality of Broadband Services in the EU](https://www.dimt.it/wp-content/uploads/2015/10/localhost_dimt_wp-content_uploads_2015_10_QualityofBroadbandServicesintheEU.pdf)). Modern Broadband Forum work (TR-471) moves speed testing to **UDP-based** measurement of "jitter, packet loss, latency under load, and packet reordering … using a UDP-based approach that reflects how modern traffic actually moves" ([QA Cafe on TR-471](https://finance.yahoo.com/sectors/technology/articles/qa-cafe-targets-next-generation-120000645.html)).

### 7.4 ITU-T P.1203 — the standards-body QoE model
- P.1203 is "the first standardized model of end-to-end adaptive-streaming QoE — the quality of a whole session, not one clip," The model combines a short-term video module (P.1203.1), audio module (P.1203.2), and integration module (P.1203.3).
  The integration module uses "**loading delay, rebuffering stalls, and bitrate switching**,".
  The model makes a session-level MOS.
  ITU-T SG12's approval dates to December 2016.
  The model supports H.264 up to HD with extension to 4K/HEVC/VP9.

  Input modes 0–3 depend on encryption level.
  Inputs range from pure metadata up to full bitstream ([ITU recommendation page](https://www.itu.int/ITU-T/recommendations/rec.aspx?rec=13399); [NTT press release](https://group.ntt/en/newsrelease/2017/03/06/170306a.html); [Streaming Learning Center](https://streaminglearningcenter.com/blogs/itu-t-p1203-p1204.html)).
- An open-source implementation exists: `github.com/itu-p1203/itu-p1203`.
  Give it JSON with stall events (`[start timestamp, duration]` per stall), segment/representation metadata, and device/display info.
  The tool gives per-second audio/video/audiovisual scores and the overall session score.
  The sample shows stalling quality O23 5.0 and overall O46 4.92 ([ITU P.1203 implementation](https://github.com/itu-p1203/itu-p1203)).

### 7.5 Which of these map to a datacenter node's uplink certification
1. **Directly transferable thresholds:** Use loss <1% (AIM full-points band) and jitter <10 ms.
   Use loaded−unloaded latency difference <10–20 ms and latency p95 ≤100 ms RTT (CAF).
   Use 80/80 sustained-capacity consistency (FCC).
   **[calculation]** A possible rack-bench gate specifies sustained egress ≥80% of contracted port rate for ≥80% of the 2-hour window.
   Other gate values: loss <1%; jitter <10 ms; loaded-latency inflation <20 ms during the saturation run.
2. **Transferable methods:** Use Cloudflare's loaded-latency measurement: empty requests during bulk transfer.
   The bench can possibly use a parallel ping/mtr stream during the bulk egress test.
   Use SamKnows' VoIP-shaped UDP loss probe (64 kbps G.711-like stream) and its 2-second-resolution disconnection detector.
   Use Netflix's "achieved vs maximum bitrate" framing.
   Measure achieved application throughput against the known maximum of the target store.
3. **Not transferable (access-network artifacts):** Most AIM/ consumer scores encode Wi-Fi/last-mile issues.
   A datacenter node uses wires. Thus, the loaded-latency delta measures upstream congestion/oversubscription.
   The bench must isolate this (cf. Cloudflare's own wired-connection heuristic: ≥100 ms delta over wired ⇒ upstream at fault, [speed-test deep-dive](https://blog.cloudflare.com/how-does-cloudflares-speed-test-really-work)).
4. **Saturation vs quality trade-off:** Cloudflare deliberately avoids saturation for consumer quality scoring.
   Cloudflare's 2026 plan adds enterprise high-throughput measurement (§2.8.5).
   A certification must do both. Saturate for capacity.
   Measure quality *during* saturation to check bufferbloat/queue management.
5. **RPKI/routing integrity as a first-class score dimension** (§8) has no consumer-scorecard equivalent.
   The surveyed companies use it as standard practice.
   Examples include Cloudflare Radar anomaly tracking and RPKI invalid rejection during the Tata AS4755 event, §2.5.

---

## 8. Route/BGP integrity as an internet-quality dimension — free monitoring for a small operator

### 8.1 RPKI ROV — the baseline control
- RPKI/ROV is "the internet's best defense against accidental BGP hijacks … ROV rejects RPKI-invalid routes"; ROAs now cover a majority of routes, including a super majority of traffic.
  Kentik tells operators to "reject RPKI-invalid BGP routes on EBGP sessions" ([Kentik: RPKI ROV Deployment Reaches Major Milestone](https://kentik.com/blog/rpki-rov-deployment-reaches-major-milestone)).
- Free public ROA/ROV data tools: **NIST's RPKI Monitor** and **RIPE RIPEstat** ([Kentik: Measuring RPKI ROV adoption with NetFlow](https://www.kentik.com/blog/measuring-rpki-rov-adoption-with-netflow)). **Inference:** A bench's routing audit can use free tools for both checks.
  (a) Check that the datacenter's own prefixes have ROAs and are RPKI-valid from major vantage points.
  (b) Check that transit providers in the node's AS path reject invalids.
- Live evidence that ROV works: during the 2025 Tata (AS4755) hijack of 1.1.1.0/24, "networks that properly implemented RPKI-based origin validation did reject it, and their users remained unaffected" ([Catchpoint](https://www.catchpoint.com/blog/cloudflares-resolver-outage-more-than-just-dns)).

### 8.2 bgp.tools — free per-ASN/prefix monitoring
- Free tier: "Near Realtime BGP Data, User Friendly interfaces, Frequently updated external data".
  The tier gives per-ASN and per-prefix pages (e.g., 8.8.8.0/24).
  The upstreams tab shows RPKI ROA and **ASPA** data.
  The tier gives a hosted looking glass.
  Its **Global Looking Glass** queries "all public BGP sessions connected to bgp.tools" ([bgp.tools](https://bgp.tools); [super-lg](https://bgp.tools/super-lg); [April 2023 changelog](https://bgp.tools/kb/april-2023-changelog)).
- bgp.tools' IXP view does "real time lookups against a feed of the route collector" Thus, bgp.tools observes route-server peering status instead of using PeeringDB self-declarations (same changelog).
  The paid tier adds BGP network monitoring and IRR/RPKI monitoring ([bgp.tools](https://bgp.tools)). Also free: RIPE Atlas traceroute integration, and an in-network agent option for fast traceroute/ping looking glass (same changelog).

### 8.3 Outage/anomaly detection — public feeds a bench can consume
- **Cloudflare Radar** gives free web + API access.
  Radar shows traffic-anomaly/outage detection by country/ASN (§2.4).
  Radar shows BGP hijack/leak/MOAS anomalies (§2.5).
  Radar gives RPKI/ASPA coverage time series and notifications ([Radar changelog](https://developers.cloudflare.com/changelog/product/radar); [traffic anomalies post](https://blog.cloudflare.com/traffic-anomalies-notifications-radar)).
- **Kentik's public analysis** (blog, free to read): Kentik shows route-leak taxonomy and detection case studies.
  One case shows a leak where "60.7% of our BGP sources saw the leaker (AS266970) as the origin," 
  Kentik reports that, of leaked routes, "17,173 were RPKI-unknown and 12,588 were RPKI-valid,".
  This shows: **ROV cannot catch path leaks (only origin hijacks)**. **ASPA checks path leaks** ([A Tale of Two BGP Leaks](https://www.kentik.com/blog/a-tale-of-two-bgp-leaks)).

  Kentik continues work on "ephemeral leaks".
  These are brief, low-impact artifacts of normal BGP convergence that automated detectors flag ([Kentik BGP monitoring blog](https://www.kentik.com/blog/category/bgp-monitoring)). Route-leak definition per RFC 7908: "propagation of routing announcement(s) beyond their intended scope" (same source).
- **Cisco ThousandEyes** publishes free outage analyses with per-incident path and BGP visibility timelines.
  Examples include Cloudflare Nov/Dec 2025, Meta June 2026, and Azure Front Door Oct 2025, etc. ([ThousandEyes outage blog](https://www.thousandeyes.com/blog/meta-outage-analysis-june-12-2026)).
- Regional studies use **CAIDA BGPStream**, the underlying public BGP-event feed, for outage/leak tracking.
  LACNIC's FORT routing-security report gives an example: it counts 2017 outages and leak propagations by country ([FORT diagnostic report](https://fortproject.net/en/diagnostic-report.pdf)). **Routeviews** and the **NLNOG RING** looking glass give classic free vantage-point sources ([Cloudflare route-visibility post](https://blog.cloudflare.com/bringing-connections-into-view-real-time-bgp-route-visibility-on-cloudflare)).
- **Free small-operator stack [calculation]:** Use bgp.tools for ASN/prefix watch + LG.
  Use Cloudflare Radar API for anomalies, quality, and RPKI time series.
  Use RIPEstat/NIST RPKI Monitor for ROA validity. Use BGPStream for the event stream.
  All these tools have zero cost.
  The large companies above use all these tools in some form.

---

## 9. Gaps — what public sources do not answer

1. **Netflix Open Connect "Live checks" specifics:** Netflix confirms pre-serving checks, offload gating, and NOC monitoring ([deployment guide](https://openconnect.netflix.com/deploymentguide.pdf), [appliances page](https://openconnect.netflix.com/en/appliances)).
   Netflix does not publish the check list, thresholds, or probe cadence. No public Open Connect SLA document exists. Next step: partner-portal access (requires being an ISP partner) or an interview.
2. **Netflix ISP Speed Index India specifics:** The index covers India, which appears in country listings.
   This research pass lacks Chennai/India per-ISP numbers and a Netflix-India peering profile (GGC/OC presence in Chennai datacenters). Next step: pull [ispspeedindex.netflix.net/country/india](https://ispspeedindex.netflix.net/country/india) and PeeringDB entries for Chennai IXPs (NIXI Chennai, DE-CIX Chennai?).
3. **Akamai POP/path-health internals:** No public document describes Akamai's edge-probing system, thresholds, or POP withdrawal logic.
   §3.3's mechanism is inference from the data basis (SOTI platform description) plus mPulse.
   Akamai's path-optimization product documentation (e.g., Sure Route / Premier routing) can possibly give partial coverage.
   This research pass lacks that documentation. Next step: Akamai technical docs behind product pages.
4. **Google/YouTube internal QoE dashboards:** Google publishes the Video Quality Report and research.
   Google does not publish current internal join-time/rebuffer-ratio thresholds or ISP-level YouTube QoE data post-2016.
   Google does not publish BBR fleet-deployment percentages (share of Google traffic on BBRv1/v2/v3).
5. **Meta's "nearby monitoring":** This research pass finds no Meta publication with that exact term.
   The closest published artifacts are Edge Fabric, fbflow, Millisampler, and the IMC'19 edge-performance study (§5).
   Researchers find no published Meta *action thresholds* (the loss/latency value that starts a drain or re-route).
   
   A 2024–2025 Meta post specifically on network-monitoring architecture possibly exists.
   This excludes the cited @Scale monitoring-resilience talk and DSF/NSF posts. These searches do not show such a post.
6. **Spotify and LinkedIn ISP-quality telemetry:** This research pass confirms no Spotify practice in public engineering blogs.
   This research pass finds no LinkedIn practice. If either uses playback/connectivity telemetry to characterize ISP quality, it is unpublished.
7. **Microsoft Windows consumer connectivity analytics:** Microsoft documents Windows' consumer-side connectivity telemetry only as troubleshooting guidance.
   This includes Network Connectivity Status Indicator / connected- experiences data.
   Microsoft does not document it as a published ISP-quality measurement program.
   The M365 connectivity test and Ericsson 5G integration serve enterprises.

   This research pass lacks the exact metrics that connectivity.office.com measures.
   These include the front doors for latency measurements and per-service thresholds.
   The historical "80 ms to Exchange front door" guidance gives an example.
   Fetch the connectivity-test docs page separately.
8. **ITU P.1203 threshold mapping to raw link metrics:** P.1203 uses application-level events: stalls, startup delay, and bitrates.
   Thus, a non-video bench cannot use the model directly.
   Only AIM maps raw loss/jitter/throughput to a single "internet quality" score among these standards.
   A bench can possibly use P.1203 against a test video stream as an application-layer proxy.
   This is a design option, not a sourced fact.
9. **Ofcom/SamKnows UK specifics:** The methodology PDF and EU study cover SamKnows' methodology.
   Regulators including the FCC, EC, UK, Brazil, and Singapore use this methodology.
   This research pass lacks Ofcom's own current UK thresholds.
   Examples include "decent broadband" 10 Mbps down / 1 Mbps up and the 2024–25 USO performance lines.
   Next step: check Ofcom's "Home Broadband Performance" technical annexes.
10. **Cloudflare speed-test engine reuse in a non-browser bench:** The open-source engine uses JavaScript.
   A datacenter-node CLI bench needs to port the measurement pattern or run the engine headless.
   The pattern uses data blocks, empty-request loaded latency, and TURN-based loss. No documented CLI port exists in the sources found.

