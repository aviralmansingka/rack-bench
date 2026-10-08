# Cloud lab: practice rack-bench on cloud machines

Status: practice guide. This document tells you how to run the audit and the
`bench internet` category on cloud machines, before you have a rack in a
datacenter. The lab exists to build operator skill: run the tool, read the
output, fix what it finds, and learn networking from real paths that differ by
cloud.

## 1. Purpose

You have no rack today. Use small cloud machines first. You have three goals:

1. Run rack-bench without help.
2. Read every check result and fix the problems you find.
3. Learn networking by comparison. Each cloud gives you a different path to the
   same storage endpoints.

## 2. Rules

1. The audit is read-only. It sends about four external queries per address
   family. It changes nothing on the machine.
2. Use R2 for all repeat tests. Storage of deleted objects and egress on R2 cost
   nothing. This is the default provider for the lab.
3. Do not use `--profile certify` in the lab. Certify moves about 2.2 TB per
   provider and requires `--yes`. Use the default quick profile.
4. Stop each machine after the session. Small machines cost cents per hour. A
   stopped machine costs almost nothing.

## 3. The machines

Make four machines. Use the smallest useful size: 2 vCPU and 2-4 GB of memory.
The audit and the context probes need almost no compute. The transfer probes
need one CPU core per stream, so expect a small machine to limit the measured
throughput. That limit is itself a lesson: the tool reports what the machine can
do, not only what the path can do.

| Machine      | Region                | Lesson                                                  |
| ------------ | --------------------- | ------------------------------------------------------- |
| AWS EC2      | Mumbai (ap-south-1)   | Same-region S3. Very low RTT. AWS ASNs.                 |
| Google Cloud | Mumbai or us-central1 | Google transit. A different path to the same endpoints. |
| DigitalOcean | Bangalore             | A small cloud. Real transit. NIXI in the path.          |
| Hetzner      | Germany or US         | A lean network. Long-RTT paths.                         |

Point each machine at a near endpoint and a far endpoint. Example: the Hetzner
machine tests S3 in ap-south-1 (far) and its own region (near). The `--regions`
flag sets this per provider.

## 4. Prepare once

Do this on your own computer:

```text
cd ~/rack-bench
uv build
```

The wheel is one file. It needs no other packages. Copy it to each machine:

```text
scp dist/rack_bench-0.1.0*.whl <machine>:
```

Make two buckets:

1. One R2 bucket.
2. One S3 bucket in ap-south-1.

Make one credential per cloud. Give each credential access to one bucket only.
For S3, the policy allows `PutObject`, `GetObject`, `DeleteObject`, and
`ListBucket` on that bucket. For R2, scope the token to the bucket.

## 5. Set up one machine

Do this on each machine. Install uv first:

```text
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install the tool. uv installs Python 3.14 when the machine does not have it. The
tool needs no other packages.

```text
uv tool install ./rack_bench-0.1.0*.whl
```

Install the path tools. The audit tells you when a tool is missing, so you can
also run the audit first and install after.

```text
sudo apt-get install -y mtr-tiny traceroute
```

Set the credentials in each shell. The tool reads nothing else: no config files,
no cloud metadata.

```text
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export R2_ACCOUNT_ID=...
```

## 6. The work loop

Do this on each machine:

1. Run the audit.
2. Read each finding and each SKIP.
3. Fix one problem.
4. Run the audit again. Confirm the fix.
5. Run the bench.
6. Write down the results.

Do not skip step 3. The skill you build in this lab is the fix step.

## 7. Run the audit

```text
rack-bench audit --json audit.json
```

Read the connectivity scope first. It answers these questions:

| Check                  | Question                                                  |
| ---------------------- | --------------------------------------------------------- |
| connectivity.routes    | Which default route and which source address, per family? |
| connectivity.resolver  | Which DNS resolver is configured?                         |
| connectivity.ipv6      | Does IPv6 exist on this machine?                          |
| connectivity.proxies   | Is a proxy declared in the environment?                   |
| connectivity.egress_ip | Which public address do we exit from?                     |
| connectivity.asn       | Which network announces our prefix?                       |
| connectivity.roa       | Is that announcement signed (RPKI)?                       |
| connectivity.ris       | Do routing collectors see the announcement?               |

Then read the software scope. It names every missing tool.

## 8. Read and fix

Typical findings on a fresh cloud machine:

| Finding                         | Meaning                                                            | Fix                                        |
| ------------------------------- | ------------------------------------------------------------------ | ------------------------------------------ |
| `software.mtr` SKIP             | mtr is not installed.                                              | `sudo apt-get install -y mtr-tiny`         |
| DNS trap returns an address     | DNS interception. The resolver answers a name that must not exist. | Change the resolver. Test again.           |
| Proxy variables set             | Some images export `http_proxy`. This changes every measurement.   | Remove the variables from the environment. |
| egress ASN is not the cloud ASN | Something else is in the path.                                     | Record it. Ask the cloud provider.         |
| ROA not found                   | The prefix is unsigned. Common. Not a fault.                       | None. Record it.                           |

## 9. Run the bench

Start with R2 only:

```text
rack-bench bench internet --providers r2 --buckets r2=NAME \
  --json bench.json
```

Add S3 when you are ready:

```text
rack-bench bench internet --providers s3,r2 --buckets s3=NAME,r2=NAME
```

You get 13 checks per provider:

| Group    | Checks                                         |
| -------- | ---------------------------------------------- |
| path     | `path.as_path`, `path.hops`, `path.rtt_sanity` |
| dns      | `dns.resolve`                                  |
| latency  | `latency.ttfb`, `latency.loaded`               |
| upload   | `upload.throughput`, `upload.objs`             |
| download | `download.throughput`, `download.objs`         |
| tcp      | `tcp.pmtud`, `tcp.retransmit_ratio`            |
| summary  | `summary`                                      |

Every run writes `rack-bench-runs/<timestamp>/` in the current directory. Keep
these directories. They are your record.

## 10. The experiments

Each experiment teaches one networking idea. Run each one on at least two
machines and compare.

1. **PMTUD.** Read `tcp.pmtud` on each machine. Cloud networks often carry extra
   headers, so the real MTU can be 1450 or less. A stall above a passing size is
   a PMTUD blackhole: small packets pass, big transfers stall.
2. **DNS.** Compare `dns.resolve` across clouds. Compare the first query with
   repeated queries. Watch the `.invalid` trap on every machine. Some networks
   answer names that must not exist.
3. **AS chain.** Read `path.as_path` from each machine to the same endpoint.
   Compare the chains. Count the transit networks. A long detour through a far
   country is a real finding.
4. **TCP tuning.** On the far machine, set BBR and a larger `tcp_wmem` maximum,
   then run the bench again. Watch the single-stream rate move. This experiment
   is the window/RTT lesson: one stream can send only window/RTT bytes per
   second.
5. **Loaded latency.** Read `latency.loaded` on a small machine. The upload
   fills the uplink. The queue grows. Latency grows. This is bufferbloat,
   measured on your own machine.

## 11. Read a SKIP correctly

A SKIP can mean three different things. Learn to tell them apart:

1. The thing does not exist here. Example: GPU scopes on a cloud machine. This
   is normal. No action.
2. The check could not observe. The reason is in the detail field. Read it. Fix
   the cause when you can.
3. A prerequisite is missing. Example: no bucket, or no successful upload. The
   detail names what the check needed.

## 12. Record the results

For each machine, keep one line in a table:

| Column            | Example                 |
| ----------------- | ----------------------- |
| machine           | do-blr-1                |
| cloud / region    | DigitalOcean, Bangalore |
| egress ASN        | AS14065                 |
| path to S3 Mumbai | hop count, AS chain     |
| RTT to S3 Mumbai  | 20 ms                   |
| TTFB p50 / p95    | 8 / 12 ms               |
| loaded inflation  | 4 ms                    |
| single-stream     | 180 MiB/s               |
| PMTUD             | 1472 clean              |
| findings          | DNS trap answered once  |

## 13. Limits of this lab

1. The RTT reference bands in the tool are Chennai-origin numbers. A cloud
   machine in another region gives different RTT. This is expected. The bands
   are a reference, not a threshold.
2. The retransmit ratio counts outbound data segments only. It shows the
   upload-side loss. The provider-side counters during a download are not
   reachable.
3. A small machine limits throughput. The tool measures the machine and the path
   together. Do not report a small-machine number as a path number.
4. The lab never produces certification evidence. It builds operator skill.
   Certification runs on real nodes, with the quick or certify profile, on
   hardware that matches the deal.
