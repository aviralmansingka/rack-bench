# Neocloud (GPU cloud) storage offerings & validation claims

Research date: 2026-10-11. Purpose: input to `rack-bench bench storage` certification
design — what storage neoclouds actually sell, what they claim, what they measure,
what customers complain about, and which claims a certification suite could falsify.
Every claim carries its source URL. Quotes are verbatim from the cited page.

---

## 1. Provider-by-provider storage inventory

### Matrix (what you can buy today)

| Provider | Local NVMe | Shared FS | Object | Publishes storage perf numbers? |
|---|---|---|---|---|
| CoreWeave | Yes (NVMe RAID, XFS, `/mnt/local`) | DFS (VAST-based POSIX) + Dedicated VAST | CAIOS (S3) + LOTA cache | **Yes** — one fio blog + public test repo (no fsync) |
| Lambda | Yes (root SSD; 1CC nodes 24 TB NVMe) | Filesystem (NFS-style, `/lambda/nfs/...`) | S3-compatible | **No** (GPU benchmarks only) |
| Crusoe | Ephemeral disks (local NVMe, AES-XTS) | Shared Disks (VAST, NFS) | S3, $0.06/GiB/mo | **Partial** — one scaling claim + relative Lightbits numbers |
| Voltage Park | Local NVMe (customer-managed LVM) | VAST-backed shared volumes | None published self-service | **No** |
| Nebius | Local SSD (ephemeral) | Shared Filesystem (SSD, EC) | S3 (Standard/Enhanced) | **Yes** — "tested" bandwidth tables (no methodology) |
| TensorWave | Node-local NVMe | `/home` on WEKA (parallel FS) | S3 endpoint | **No** |
| Fluidstack | Marketplace per-host | Private-cloud only (VAST/WEKA/DDN per deal) | Private-cloud only | **No** |
| Prime Intellect | Marketplace per-host | Persistent disks + ephemeral cluster FS | Via providers | **No** |
| SiliconFlow | (GPU hosting via serverless/reserved tiers) | Not documented publicly | Not documented publicly | **No** (isolation claims only) |

Cross-vendor context, incl. RunPod, Hyperstack, SF Compute, Vultr, Vast.ai, Hot Aisle, GMI:
[Saturn Cloud GPU Cloud Comparison Report](https://saturncloud.io/reports/gpu-cloud-comparison-report) —
key finding: *"VAST/WEKA partnerships are mostly an offtake story, not a self-service one."*

### CoreWeave — deepest public docs, one real benchmark

**Tiers.** Five products: CoreWeave AI Object Storage (CAIOS, S3-compatible), Distributed
File Storage (POSIX shared FS), Dedicated VAST (single-tenant), Local Storage (node-local
NVMe), CoreWeave Database.
([docs: About CoreWeave Storage](https://docs.coreweave.com/products/storage))
Note: the current lineup contains **no managed-Lustre and no lakeFS-style product** —
despite "LakeFS/managed Lustre" being commonly attributed to CoreWeave, neither exists on
their live storage pages as of 2026-10-11 ([same](https://docs.coreweave.com/products/storage)).

**Local NVMe.** Node NVMe drives assembled into software RAID, XFS, mounted `/mnt/local`.
2–3 drives → RAID1: *"Writes are about the speed of a single drive, because data is
mirrored rather than striped."* 4+ drives → RAID10: *"High parallel read and write
throughput that scales with the number of drives and the concurrency of the workload."*
Most GPU nodes are 8-drive RAID10. Encrypted at rest with an in-memory key: *"The key is
discarded when the Node reboots, which crypto-shreds the data."*
([docs: About local storage](https://docs.coreweave.com/products/storage/local-storage))

**Unusual methodology honesty in docs.** Same page warns about two benchmarking mistakes:
(1) *"In a SUNK Enroot or Pyxis container, `/tmp` is `tmpfs` (RAM), which inflates results
and does not represent NVMe"*; (2) *"A single-stream tool such as `dd`, or `fio` with
`numjobs=1`, is latency-bound and understates a striped RAID10 array."* They recommend fio
with 12 concurrent jobs and publish a reference script
([local-storage docs](https://docs.coreweave.com/products/storage/local-storage);
[runtests.sh](https://cw-storage.cwobject.com/perf/runtests.sh)).

**The published benchmark (Distributed File Storage).** fio on a 24-CNode/16-DNode VAST
cluster, H200 nodes, storage via BlueField-3 DPU at 100 Gbit/s (12.5 GiB/s theoretical per
node). Results: single-node mixed read ~11 GiB/s ("88% of theoretical"); 8 nodes: 7.96
GiB/s per node; 64 nodes: **~500 GiB/s aggregate, 7.94 GiB/s per node** ("remarkably close
to our target of 8 GiB/s per node (1 GiB/s/GPU)"); ~2M IOPS at small block sizes.
Methodology, verbatim: read tests are *"an average of the sequential and random IO
performance"*; write tests are *"Focusing on sequential writes to replicate checkpoint
operations."*
([blog: Storage Benchmarking — Distributed File Storage](https://www.coreweave.com/blog/storage-benchmarking-distributed-file-storage))

**Public test repo — and the fsync answer.** The scripts behind those numbers are public:
[coreweave/ioperftest](https://github.com/coreweave/ioperftest). The actual fio
invocation ([fio-tests.slurm](https://raw.githubusercontent.com/coreweave/ioperftest/master/fio-tests.slurm)):

```
fio --name=test --direct=1 --rw=$OP --size=20G --bs=$BS --ioengine=sync \
    --refill_buffers --randrepeat=0 --runtime=120 --numjobs=8
```

for `OP` in `read`, `randread`, `write`. So: `--direct=1` (page cache bypassed — good) but
**no `-fsync`/`--sync=1`/`-end_fsync`**: published writes are direct but *not*
fsync-durable. Their [runtests.sh](https://cw-storage.cwobject.com/perf/runtests.sh)
local-volume script is the same shape (`-direct=1 -ioengine=sync -numjobs=12 -time_based`,
4k IOPS + 4M BW, read+write) plus a timed `git clone` metadata test — again no fsync.
**No fsync'd write number is published anywhere in CoreWeave's public material.**

**Marketing claims.** "Up to 60TB ephemeral" local storage; shared FS *"up to 1 GB/s per
GPU. Our benchmarks show strong results for up to 64-node NVIDIA H200 GPU clusters"*
([product page](https://www.coreweave.com/products/storage)). LOTA object cache: *"a
caching proxy on every GPU and CPU node... holding objects on local NVMe and serving
cached reads at up to 7 GB/s per GPU"* — a cache-hit number by definition; no cold-read,
write, or methodology numbers
([blog: cross-region writes and archive](https://www.coreweave.com/blog/new-in-coreweave-ai-object-storage-cross-region-writes-and-archive-storage);
[blog: AI storage expansions](https://www.coreweave.com/blog/ai-storage-without-limits-exploring-the-latest-coreweave-ai-object-storage-expansions)).
Older object-storage marketing: *"NVMe accelerated option, supporting multiple terabits
per second of throughput"* with no measurement
([blog: Performant, Flexible Object Storage](https://www.coreweave.com/blog/performant-flexible-object-storage)).
Multi-tenant sharing is real: default quotas are 20 TiB CAIOS per AZ and 10 TiB DFS per
CKS cluster ([docs changelog](https://docs.coreweave.com/release-notes/changelog)).
CAIOS durability architecture (erasure coding, fragment rebuilds) is documented but has
no availability/perf SLO
([docs: About AI Object Storage](https://docs.coreweave.com/products/storage/object-storage/about)).

### Lambda — 24 TB of local NVMe, zero published storage numbers

**Tiers.** On-demand instances ship a root SSD sized per instance (e.g., 1× H100 SXM:
2.75 TiB; 8×: 22 TiB)
([on-demand docs](https://docs.lambda.ai/public-cloud/on-demand);
[pricing](https://lambda.ai/pricing)). 1-Click Clusters: *"Each compute node includes
24TB of usable local ephemeral NVMe storage"* (management nodes: 208 GB); all ephemeral
data *"will be deleted and unrecoverable once your reservation ends"*
([1CC docs](https://docs.lambda.ai/public-cloud/1-click-clusters)). Persistent storage is
"Lambda Filesystems" — networked filesystems mounted at `/lambda/nfs/<name>`, billed for
used storage ([filesystems docs](https://docs.lambda.ai/public-cloud/filesystems)).
The docs themselves imply the shared FS is slower than local NVMe: *"For higher
performance, you can also use rsync to copy data from your Lambda filesystem to your
nodes' local ephemeral storage"* ([1CC docs](https://docs.lambda.ai/public-cloud/1-click-clusters)).

**Published benchmarks.** Lambda publishes GPU benchmarks only
([lambda.ai/gpu-benchmarks](https://lambda.ai/gpu-benchmarks)); the persistent-storage
launch blog claims *"a high speed filesystem"* with no numbers, and nothing has been added
since ([blog: persistent storage beta](https://lambda.ai/blog/persistent-storage-beta)).
VAST/WEKA are backend infrastructure, not customer-facing products
([Saturn report](https://saturncloud.io/reports/gpu-cloud-comparison-report)).

**The only public numbers are third-party.** Mark Nelson's independent fio study on
Lambda 8×V100 (2022): local NVMe *"surprisingly good"*; persistent network storage
*"a little over 1GB/s for large reads"*, and *"16K IOPS was somewhat slower in both
cases"*; conclusion: persistent storage *"may not be able to fully saturate 8 V100 GPUs"*
([markhpc.github.io](https://markhpc.github.io/2022/11/28/Lambda.html)).

### Crusoe — one concrete scaling claim, otherwise relative/vendor numbers

**Tiers.** Ephemeral Disks (local NVMe, *"AES-XTS encrypted"*, erased on stop/restart);
Persistent Disks (Lightbits NVMe/TCP block); Shared Disks (VAST-backed NFS, *"Data
preserved until explicitly deleted"*); Object Storage (S3-compatible, $0.06/GiB/mo,
regional, co-located)
([solutions: data preparation](https://www.crusoe.ai/cloud/solutions/data-preparation);
[docs: object storage](https://docs.crusoecloud.com/storage/object-storage/overview)).

**Block storage claims (relative only).** After "extensive performance testing" vs "the
leading OSS option" (Ceph), Lightbits shows *"up to 4x performance advantage in terms of
bandwidth"* and *"consistently maintains latencies under 500 microseconds"* while the
competitor *"exceed[s] 2.5ms under random access"*. No absolute IOPS/GB/s for Crusoe's
service; self-run comparison; no fio jobs published
([blog: How we built block storage with Lightbits](https://www.crusoe.ai/resources/blog/how-we-built-it-block-storage-for-ai-ml-workloads-powered-by-lightbits)).

**Shared Disks claim (concrete but unverified).** Launch announcement: *"reads up to
200 MBps per TiB per node with hundreds of GBps in aggregate read and write bandwidth per
cluster"* — a capacity-proportional scaling claim with no methodology or reproduction
steps ([newsroom: Crusoe & VAST](https://www.crusoe.ai/resources/newsroom/crusoe-vast-data-to-deliver-high-performance-data)).
Data-prep marketing repeats *"hundreds of GB/s in aggregate bandwidth"*
([solutions page](https://www.crusoe.ai/cloud/solutions/data-preparation)).

### Voltage Park — VAST everywhere, numbers nowhere

**Tiers.** On-demand storage volumes backed by *"VAST Data's Universal Storage
architecture... all-flash performance and exabyte-scale capacity"*; attach to bare-metal
GPU instances ([help: Deploy Storage](https://support.voltagepark.com/article/deploy-storage)).
Local NVMe is customer-managed — docs walk through configuring an LVM volume yourself on
bare-metal local disks
([docs: LVM on local storage](https://docs.voltagepark.com/support/troubleshooting/local-storage-configuring-an-lvm-volume-on-voltage-park-on-demand-bare-metal-servers));
shared storage is mounted via documented VAST NFS options
([docs: mounting VAST NFS shares](https://docs.voltagepark.com/support/troubleshooting/options-for-mounting-vast-nfs-shares));
managed Kubernetes ships a VAST CSI driver
([managed Kubernetes](https://www.voltagepark.com/managed-kubernetes)).

**Claims without measurement.** Storage product page: *"Consistent high throughput.
Across training, inference and evaluation"* — no numbers
([product: storage](https://www.voltagepark.com/product/storage)). VAST strategy blog:
EBox *"outperformed benchmarks"* (which benchmarks? unpublished); a customer *"told us
the AI storage performance with VAST on our system was better than any major cloud
provider"* (anecdote); *"One customer scaled from 64 GPUs to 2,000 GPUs in under six
months"*
([blog: VAST improvements](https://www.voltagepark.com/blog/vast-improvements-our-high-performance-ai-storage-strategy)).
VAST's own customer page: *"instant volume attachment, rapid checkpointing... scalability
to exabyte scale"* ([VAST Data: Voltage Park](https://www.vastdata.com/customers/voltage-park)).

**Cluster validation.** No public cluster-validation page exists; the closest public
"validation" content is an InfiniBand troubleshooting runbook with NCCL `all_reduce_perf`
commands ([docs: InfiniBand basic setup](https://docs.voltagepark.com/support/troubleshooting/infiniband-basic-setup)).
Marketing states *"performance validated at the cluster level"* as a Reference Platform
NVIDIA Cloud Partner — with no published test list or numbers
([blog: NVIDIA fleet expansion](https://www.voltagepark.com/blog/nvidia-fleet-expansion-as-voltage-park-becomes-reference-platform-nvidia-cloud-partner)).
No storage acceptance tests appear anywhere in their docs. Their comparison page claims
Nebius offers a *"Shared 20 GB/s file system"* ([compare/nebius](https://www.voltagepark.com/compare/nebius)).

### Nebius — the most concrete "tested" numbers, with no methodology

**Tiers.** Network SSD / Network SSD Non-Replicated / Network SSD IO M3 block disks;
Local SSD (ephemeral, host-attached, *"not encrypted"*, *"Treat them as ephemeral"*);
Shared Filesystem (SSD-backed, erasure-coded, tolerates two concurrent failures,
$0.08/GiB/mo); Object Storage (S3); filesystem buckets (S3 view of a filesystem)
([docs: storage types](https://docs.nebius.com/compute/storage/types)).

**Published numbers.** Shared filesystem specs, verbatim: *"Tested read bandwidth per
client: up to 15 GiB/s; Tested write bandwidth per client: up to 10 GiB/s; Tested
aggregate read bandwidth: up to 1.9 TiB/s; Tested aggregate write bandwidth: up to 1.5
TiB/s"* (aggregate measured on a 20 PiB filesystem); capacity-proportional scaling of
*"+3.70 GiB/s read / +1.89 GiB/s write per 4 TiB"*. Disk tables: network SSD max 450
MiB/s & 20k IOPS; NRD max 2 GiB/s & 75k IOPS; local SSD values are *"peak numbers
achieved per disk under synthetic workload."*
([docs: storage types](https://docs.nebius.com/compute/storage/types)).
No tool, block size, queue depth, direct-IO, or fsync semantics are published —
these cannot be distinguished from cache-friendly sequential numbers.
Marketing adds *"over 500 GB/s aggregate read performance"* for the high-performance
class ([nebius.com/storage](https://nebius.com/storage)).

**Self-acknowledged storage noisy-neighbor.** Their own checkpointing blog: *"If a
storage has a fixed bandwidth, it will be shared by all readers. Thus, each host will get
only a fraction of the bandwidth and read multiple times slower, for example, 32 times
slower"* ([blog: checkpointing tips](https://nebius.com/blog/posts/model-pre-training/large-ml-model-checkpointing-tips)).

**Network acceptance methodology exists, storage doesn't.** Soperator ships prebuilt
NCCL test jobs for cluster validation
([docs: NCCL all-reduce in Soperator](https://docs.nebius.com/slurm-soperator/jobs/examples/nccl-all-reduce));
no equivalent storage validation job is documented.

### TensorWave — WEKA home directories, tmpfs honesty, no numbers

**Tiers.** `/home` is a *"shared, persistent filesystem backed by a high-performance
distributed storage system"* (WEKA — quotas administered via the `weka` CLI, linking
WekaFS docs); worker `/tmp` is memory-backed tmpfs, with the warning *"writing large
amounts of data here can lead up pages being swapped to disk, leading to reduced
performance"*; `/run/tmp` and `/dev/shm` are tmpfs
([docs: Slurm storage](https://docs.tensorwave.com/slurm/storage)). Product tier: a
software-defined parallel FS with NFS-style mount, S3-compatible access, K8s PV mounts,
plus node-local NVMe for *"Dataset Caching & Staging"*
([product: high-speed network storage](https://tensorwave.com/products/storage/high-speed-network-storage)).
Claims are purely qualitative: *"Consistent bandwidth and low latency for training,
inference, and checkpointing at scale"* — no numbers anywhere. WEKA is
enterprise/bespoke-priced only ([Saturn report](https://saturncloud.io/reports/gpu-cloud-comparison-report)).

### Fluidstack — private-cloud VAST/WEKA/DDN, nothing public

Two models: private cloud (single-tenant clusters for Anthropic, Meta, Mistral, etc.,
~62% of revenue) where *"Storage integrates customer-preferred solutions (VAST, WEKA,
DDN)"*, and a marketplace (38%, variable per-host storage). No published self-service
pricing; storage products are contract-only
([Saturn report — Fluidstack profile](https://saturncloud.io/reports/gpu-cloud-comparison-report);
[fluidstack.io](https://www.fluidstack.io/);
[docs.fluidstack.io](https://docs.fluidstack.io/kubernetes/overview)).
No storage performance claims or numbers are public.

### Prime Intellect — marketplace disks, no perf claims at all

Storage = persistent disks (pre-created, per-datacenter, multinode-capable, discovered
via `prime availability disks`) plus ephemeral shared storage auto-created per cluster
([docs: cluster storage](https://docs.primeintellect.ai/tutorials-storage/cluster-storage);
[docs: managing disks](https://docs.primeintellect.ai/cli-reference/managing-disks)).
Homepage markets SLURM/K8s, InfiniBand, Grafana dashboards — no storage performance
claims ([primeintellect.ai](https://www.primeintellect.ai)).

### SiliconFlow & Asian neoclouds — thin storage documentation

- **SiliconFlow** is an inference-first platform (serverless API, reserved/elastic GPUs,
  fine-tuning). No public storage tier documentation; marketing asserts
  计算/网络/存储隔离 ("compute/network/storage isolation") with no numbers
  ([siliconflow.cn](https://www.siliconflow.cn),
  [siliconflow.com](https://www.siliconflow.com/zh)). Their GPU-instance article claims
  *"2.3x the inference speed and 32% lower latency vs leading AI cloud platforms"* —
  methodology unpublished
  ([article](https://www.siliconflow.com/zh/articles/the-best-on-demand-gpu-instances-service)).
- **AutoDL / 智星云 / 恒源云** (budget Chinese GPU rental): pay-per-GB data-disk model,
  no performance numbers in docs ([autodl.com/docs](https://www.autodl.com/docs/gpu));
  third-party course notes put consumer-netdisk mount transfer at ~30–50 MB/s
  ([source](https://front-end.toimc.com/notes/llm_notes/8-4%20GPU%E7%AE%97%E5%8A%9B%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%A7%9F%E7%94%A8%E6%96%B9%E6%A1%88%EF%BC%88AutoDL%E5%92%8C%E6%99%BA%E6%98%9F%E4%BA%91%E5%92%8C%E6%81%92%E6%BA%90%E4%BA%91%EF%BC%89.md)
  — third-party, treat as anecdote).
- A Chinese AI lab's public user story describes the classic NFS-on-GPU-cluster failure:
  *"severe training task delays or complete stalls during peak hours, performance
  degradation under multi-user concurrency"* before moving off NFS
  ([JuiceFS blog](https://juicefs.com/en/blog/user-stories/ai-storage-platform-large-language-model-training-inference)).

---

## 2. Published benchmarks & acceptance methodology — the fsync question

**Who publishes what:**

| Source | What's measured | fsync? | Reproducible? |
|---|---|---|---|
| CoreWeave DFS blog ([link](https://www.coreweave.com/blog/storage-benchmarking-distributed-file-storage)) | mixed/random reads + **sequential** writes, 1–64 nodes, fio `--direct=1` | **No** | Yes — [ioperftest repo](https://github.com/coreweave/ioperftest) |
| CoreWeave runtests.sh ([link](https://cw-storage.cwobject.com/perf/runtests.sh)) | 4k IOPS + 4M BW (R+W), `--direct=1`, plus timed git-clone | **No** | Yes — public script |
| Nebius docs ([link](https://docs.nebius.com/compute/storage/types)) | per-client & aggregate FS bandwidth, disk IOPS/BW caps | Unknown — methodology unpublished | No |
| Crusoe/VAST PR ([link](https://www.crusoe.ai/resources/newsroom/crusoe-vast-data-to-deliver-high-performance-data)) | 200 MB/s per TiB per node reads; hundreds of GB/s aggregate | No mention | No |
| Together AI acceptance guide ([link](https://www.together.ai/blog/a-practitioners-guide-to-testing-and-running-large-gpu-clusters-for-training-generative-ai-models)) | fio random/sustained R+W at various block sizes (example output: 21.8 GiB/s sequential read, 22.3k IOPS) | **No** (no fsync in published jobs) | Partially — fio job files not published |
| MLCommons MLPerf Storage v3.0 ([link](https://mlcommons.org/benchmarks/storage/)) | Training (Unet3D/RetinaNet), **Checkpointing (fsync-enforced)**, Vector DB, KV cache | **Yes — required** | Yes — open rules, but submitters are storage vendors, not neoclouds |

**The fsync verdict.** As of 2026-10-11, **no neocloud publishes an fsync'd write number
for any storage product it sells.** The pattern across the industry:

1. Writes, when measured at all, are sequential and direct-IO but not durable —
   CoreWeave's own repo proves it (`--direct=1`, no fsync flag)
   ([fio-tests.slurm](https://raw.githubusercontent.com/coreweave/ioperftest/master/fio-tests.slurm)).
2. Marketing skews read-side and cache-warm: LOTA's 7 GB/s/GPU is explicitly a *cached*
   read ([blog](https://www.coreweave.com/blog/new-in-coreweave-ai-object-storage-cross-region-writes-and-archive-storage));
   Nebius's tested read (15 GiB/s) exceeds its tested write (10 GiB/s) with methodology
   absent ([docs](https://docs.nebius.com/compute/storage/types)).
3. The only public methodology that forces write durability is **MLPerf Storage
   checkpointing**: *"with an fsync forcing every file to durable media before it counts
   as done... The fsync requirement means write-back caches cannot hide slow media: the
   clock stops only when data is durable"* — and MLCommons notes *"sustained
   fsync-bounded write bandwidth is harder to scale than read bandwidth."* It also
   defeats caching by sizing datasets at ≥5× aggregate client DRAM
   ([mlcommons.org](https://mlcommons.org/benchmarks/storage/)). No neocloud has
   submitted its own managed storage to it.
4. Even the best public cluster-acceptance guide (Together AI) includes a storage phase
   — fio for *"random reads, random writes, sustained reads, or sustained writes"* — but
   publishes no fsync/durability job and no write example
   ([Together AI guide](https://www.together.ai/blog/a-practitioners-guide-to-testing-and-running-large-gpu-clusters-for-training-generative-ai-models)).
   Its hard published thresholds are for the *network* (NCCL `all_reduce_perf` at ~92% of
   fabric theoretical, ~370 GB/s on 400 Gbit/s) — storage has no equivalent bar.
5. Two providers at least document the tmpfs trap: CoreWeave warns `/tmp` is RAM in
   Slurm containers and "inflates results"
   ([docs](https://docs.coreweave.com/products/storage/local-storage)); TensorWave
   documents worker `/tmp` as memory-backed
   ([docs](https://docs.tensorwave.com/slurm/storage)). Most others never say what backs
   `/tmp` — a common way "fast local storage" specs go unmeasured.

---

## 3. Customer complaints about neocloud storage

1. **Vast.ai "verified" hosts delivering ~1% of advertised speed.** Trustpilot review:
   rented a *"verified"* 4× RTX PRO 6000 machine *"listed at 2010 Mbps download. In
   practice it downloaded at about 1 MB/s (roughly 1% of the listing)"* — a 203 GB model
   download reached only 8 GB in an hour; the host was quietly un-verified afterwards
   (*"which makes me question how hosts are checked in the first place"*). Another:
   a verified RTX 4090 advertised >600 Mbps, but *"outbound transfers were extremely slow
   and unstable. Throughput sometimes dropped to 10–20 KB/s, and connections repeatedly
   terminated"* while retrieving a checkpoint.
   ([Trustpilot: vast.ai](https://www.trustpilot.com/review/vast.ai))
2. **Advertised bandwidth vs. reality, systematically.** *"Some users report advertised
   bandwidth of 1,500 Mbps but actual throughput closer to 100 Mbps on unverified hosts —
   while still paying the listed rate"*; storage also keeps billing while instances are
   stopped. ([GPUnex: Vast.ai Review 2026](https://www.gpunex.com/blog/vast-ai-review-2026))
   Vast.ai's own verification bar is only 500 Mbps down/up plus continuous DLPerf checks
   ([docs: verification stages](https://docs.vast.ai/host/verification-stages)) — the
   lying-spec problem is structural to marketplace neoclouds.
3. **Lambda's shared filesystem measured at ~1 GB/s.** The only independent fio numbers:
   persistent network storage *"a little over 1GB/s for large reads"*, slower at 16K
   IOPS, potentially unable to saturate 8 GPUs
   ([markhpc.github.io](https://markhpc.github.io/2022/11/28/Lambda.html)). Lambda's own
   docs route performance-sensitive users to local NVMe via rsync
   ([1CC docs](https://docs.lambda.ai/public-cloud/1-click-clusters)).
4. **Nebius itself documents storage noisy-neighbor math** — a fixed-bandwidth shared
   filesystem can leave each reader *"32 times slower"* under load
   ([Nebius blog](https://nebius.com/blog/posts/model-pre-training/large-ml-model-checkpointing-tips)).
5. **NFS bottleneck pattern in GPU clusters generally.** *"Severe training task delays or
   complete stalls during peak hours, performance degradation under multi-user
   concurrency"* — why one lab abandoned NFS for a parallel FS
   ([JuiceFS user story](https://juicefs.com/en/blog/user-stories/ai-storage-platform-large-language-model-training-inference)).
6. **General cloud-storage disillusionment (HN).** "SSDs have become fast, except in the
   cloud" — long thread on rented storage underdelivering vs. local NVMe
   ([news.ycombinator.com](https://news.ycombinator.com/item?id=39443679)). Modal's GPU
   reliability writeup: renting hyperscaler/neocloud cards is *"dangerous"* — anonymized
   providers A–D, recurring hardware failures
   ([HN thread](https://news.ycombinator.com/item?id=46669001)).
7. **Marketplace data-loss risk.** Community comparison: Vast.ai *"Storage is local to
   the machine — if it goes down, your data may too (always use external backups);
   Multi-node training is essentially unsupported"*
   ([EVAL #005 GPU cloud showdown](https://buttondown.com/ultradune/archive/eval-005-gpu-cloud-showdown-lambda-labs-vs)).
8. **X/Twitter:** not captured — see Gaps.

---

## 4. Marketing gaps — claims made with no measurement

Ranked by offensiveness (worst first):

1. **Voltage Park** — *"performance validated at the cluster level"* (NVIDIA NCP
   Reference Platform) with zero published tests
   ([blog](https://www.voltagepark.com/blog/nvidia-fleet-expansion-as-voltage-park-becomes-reference-platform-nvidia-cloud-partner));
   storage *"Consistent high throughput"* with no numbers
   ([product page](https://www.voltagepark.com/product/storage)); EBox *"outperformed
   benchmarks"* (benchmarks unnamed) and a single-customer anecdote *"better than any
   major cloud provider"*
   ([VAST blog](https://www.voltagepark.com/blog/vast-improvements-our-high-performance-ai-storage-strategy)).
   An entire storage stack sold on adjectives.
2. **TensorWave** — *"Consistent bandwidth and low latency,"* "scales cleanly," "built-in
   redundancy," zero quantitative claims
   ([product page](https://tensorwave.com/products/storage/high-speed-network-storage)).
3. **CoreWeave LOTA "up to 7 GB/s per GPU"** — true-by-definition cache-hit reads; no
   cold-read, write, hit-rate, or eviction numbers; no methodology
   ([blog](https://www.coreweave.com/blog/new-in-coreweave-ai-object-storage-cross-region-writes-and-archive-storage),
   [blog](https://www.coreweave.com/blog/ai-storage-without-limits-exploring-the-latest-coreweave-ai-object-storage-expansions)).
   Their DFS blog benchmark is genuinely reproducible but is single-tenant, unloaded,
   and never fsyncs writes
   ([blog](https://www.coreweave.com/blog/storage-benchmarking-distributed-file-storage),
   [repo](https://github.com/coreweave/ioperftest)).
4. **Nebius "tested" bandwidths** — concrete tables, but the methodology is a black box
   (tool, block size, direct/fsync, concurrency all unpublished), and local-SSD rows are
   explicitly "synthetic workload" peaks
   ([docs](https://docs.nebius.com/compute/storage/types)).
5. **Crusoe** — *"hundreds of GB/s"* aggregate and *"200 MBps per TiB per node"* reads,
   unexplained ([newsroom](https://www.crusoe.ai/resources/newsroom/crusoe-vast-data-to-deliver-high-performance-data));
   Lightbits claims are relative ("4× vs leading OSS"), self-run, no absolute service
   numbers ([blog](https://www.crusoe.ai/resources/blog/how-we-built-it-block-storage-for-ai-ml-workloads-powered-by-lightbits)).
6. **Lambda "high speed filesystem"** — four years from beta blog to today with no
   published storage number at all
   ([blog](https://lambda.ai/blog/persistent-storage-beta)).
7. **Fluidstack VAST/WEKA/DDN** — partnership marketing for private-cloud deals, no
   public performance data ([Saturn report](https://saturncloud.io/reports/gpu-cloud-comparison-report)).
8. **SiliconFlow** — "storage isolation" and "2.3× inference speed" claims with no
   published methodology ([siliconflow.cn](https://www.siliconflow.cn)).
9. **Structural gap (everyone):** nobody publishes (a) fsync'd write bandwidth or fsync
   latency, (b) shared-FS throughput under concurrent multi-tenant load, (c) metadata /
   small-file performance thresholds (CoreWeave's git-clone timing is the only gesture,
   with no pass/fail bar — [runtests.sh](https://cw-storage.cwobject.com/perf/runtests.sh)),
   or (d) storage availability SLOs distinct from compute uptime. Uptime claims like
   Voltage Park's 99.982% ([homepage](https://www.voltagepark.com)) say nothing about
   storage.

---

## 5. Storage claims a certification suite could falsify

Each row: the claim (with source) → the falsifying test. Maps to `rack-bench bench
storage` categories (sequential/random read+write IOPS & bandwidth, fsync latency).

| # | Claim under test | Falsifying test |
|---|---|---|
| 1 | Local storage is "N-drive NVMe RAID10/RAID1" (CoreWeave [docs](https://docs.coreweave.com/products/storage/local-storage)) | Audit: `nvme list`, `/proc/mdstat`, `lsblk` — drive count, model, RAID level vs spec |
| 2 | RAID1 nodes deliver "writes about the speed of a single drive" (same) | fio direct=1 sequential write, numjobs=8, bs=4M: expect ≈ single-drive BW, not N× |
| 3 | "24TB usable local ephemeral NVMe" per 1CC node (Lambda [docs](https://docs.lambda.ai/public-cloud/1-click-clusters)) | `df` on the NVMe mount + sustained write fill test |
| 4 | `/tmp` is fast local NVMe (implicit in most SKUs) | `findmnt /tmp` — tmpfs detection (CoreWeave [warns](https://docs.coreweave.com/products/storage/local-storage) it's RAM in containers; TensorWave [documents](https://docs.tensorwave.com/slurm/storage) it) |
| 5 | Shared FS sustains "1 GB/s per GPU" / ~8 GiB/s per node (CoreWeave [blog](https://www.coreweave.com/blog/storage-benchmarking-distributed-file-storage)) | Reproduce their own suite: 8 concurrent fio jobs/node, mixed seq+rand reads, ≥N nodes concurrently (repo: [ioperftest](https://github.com/coreweave/ioperftest)) |
| 6 | Shared FS aggregate ~500 GiB/s at 64 nodes (same blog) | 64-node fan-out fio; per-node BW must not degrade >1% vs 8-node run |
| 7 | **Fsync'd checkpoint writes** — no vendor publishes this; MLPerf Storage requires it ([MLCommons](https://mlcommons.org/benchmarks/storage/)) | fio `-sync=1` (or `-end_fsync=1`) sequential write at 4–32M: durable-write GiB/s per node; expect well below the marketed write number |
| 8 | **fsync latency** — unpublished anywhere | `fio -rw=randwrite -bs=4k -sync=1 -iodepth=1`: p50/p99 fsync latency on local NVMe and shared FS |
| 9 | ~2M IOPS small-block on shared FS (CoreWeave [blog](https://www.coreweave.com/blog/storage-benchmarking-distributed-file-storage)) | fio direct=1 randread bs=4k, aggregate across nodes |
| 10 | Metadata performance (git-clone speed — CoreWeave's own proxy, [runtests.sh](https://cw-storage.cwobject.com/perf/runtests.sh)) | Timed `git clone` of a fixed large repo to shared FS; set the pass bar they never set |
| 11 | "Tested 15 GiB/s read / 10 GiB/s write per client" (Nebius [docs](https://docs.nebius.com/compute/storage/types)) | Single-client fio direct=1, large bs, sustained ≥60s; write side with fsync variant |
| 12 | "200 MB/s per TiB per node" reads (Crusoe [newsroom](https://www.crusoe.ai/resources/newsroom/crusoe-vast-data-to-deliver-high-performance-data)) | Provisioned-TiB-proportional read test at several sizes |
| 13 | Noisy-neighbor isolation on shared FS (Nebius's own "32× slower" scenario, [blog](https://nebius.com/blog/posts/model-pre-training/large-ml-model-checkpointing-tips)) | Client A holds target BW while K background clients saturate the same FS; measure A's degradation |
| 14 | LOTA "cached reads up to 7 GB/s per GPU" (CoreWeave [blog](https://www.coreweave.com/blog/new-in-coreweave-ai-object-storage-cross-region-writes-and-archive-storage)) | S3 GET: cold (first) read vs warm (repeat) read per GPU — the delta is the cache; hit rate under working-set churn |
| 15 | Object storage cross-region writes acknowledged "at local latency" (same blog) | Timed S3 PUT from a remote-region client; compare ack latency to in-region |
| 16 | Local storage "does not survive a reboot" / crypto-shredded (CoreWeave [docs](https://docs.coreweave.com/products/storage/local-storage)) | Write marker file, reboot node, verify absence (and verify persistent tiers *do* survive) |
| 17 | Advertised host/network/storage throughput on marketplaces (Vast.ai hosts: 2010 Mbps → ~1 MB/s, [Trustpilot](https://www.trustpilot.com/review/vast.ai)) | iperf3 + storage BW probe at provisioning time, compared against the listing |
| 18 | "Consistent high throughput" (Voltage Park [product](https://www.voltagepark.com/product/storage)), "consistent bandwidth" (TensorWave [product](https://tensorwave.com/products/storage/high-speed-network-storage)) | Any of tests 5–13, run repeatedly over hours — consistency is exactly what a smoke test measures |

The deeper point for the certification suite: rows 5, 6, 9 and 11 are the *only* numbers
the industry ever publishes — sequential/mixed reads and non-durable writes on an
unloaded cluster. Rows 7, 8, 10, 13 and 16 are the measurements **no neocloud has ever
published**, and they are exactly the ones that separate durable, multi-tenant storage
from a cache benchmark.

---

## 10-line summary

1. Every major neocloud now sells three storage tiers — local NVMe scratch, shared
   POSIX FS (mostly VAST or WEKA), S3 object — but only CoreWeave and Nebius publish any
   performance numbers for theirs.
2. CoreWeave is the gold standard for transparency: a reproducible fio benchmark, public
   scripts, RAID-layout tables, and tmpfs warnings — yet even CoreWeave never fsyncs a
   write in public.
3. Nebius publishes the most concrete table ("tested 15 GiB/s read / 10 GiB/s write per
   client; 1.9 TiB/s aggregate") but with zero methodology, so cache vs durable is
   unverifiable.
4. Voltage Park and TensorWave sell entire storage stacks on adjectives — "consistent
   high throughput," "validated at the cluster level" — with no numbers at all; these are
   the two worst marketing offenders.
5. Lambda publishes no storage numbers whatsoever; the only public measurement of its
   shared filesystem (~1 GB/s reads) is a third-party blog from 2022.
6. The universal pattern: read-side, cache-warm, single-tenant, unloaded numbers
   (LOTA's "7 GB/s per GPU" is a cache hit by definition); write-side numbers are
   smaller, sequential, and never durable.
7. MLPerf Storage v3.0 is the only public methodology enforcing fsync'd writes and
   cache-defeating dataset sizing — and no neocloud submits its own service to it.
8. Customer complaints concentrate on marketplaces (Vast.ai verified hosts delivering
   ~1% of advertised throughput), slow shared NFS (~1 GB/s on Lambda), and noisy-neighbor
   storage contention — which Nebius's own blog quantifies as up to "32× slower."
9. Two tmpfs honesty points exist (CoreWeave, TensorWave document `/tmp` = RAM); most
   providers never disclose what backs `/tmp`, letting "fast local storage" go untested.
10. A falsifiable certification suite should target exactly the unpublished claims:
    fsync'd write bandwidth, fsync latency, metadata ops, loaded multi-tenant throughput,
    cache-vs-cold object reads, and reboot durability — the 18-row table in §5.
