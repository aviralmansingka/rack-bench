# Academic literature: disk/filesystem reliability and benchmarking

Peer-reviewed field studies and benchmarking-methodology papers, mined for (a) the failure
mode or methodology finding, (b) the scale of evidence (N drives, years), and (c) the
measurable signal a **2-hour certification run** could use. Primary PDFs (USENIX, ACM,
author sites) were fetched and read; vendor/internal tech notes are flagged as such.
Companion notes: `clustermax.md` (cluster economics), `parallel-fs.md` (parallel file
systems).

---

## 1. Disk reliability field studies

### 1.1 Pinheiro, Weber, Barroso (Google) — "Failure Trends in a Large Disk Drive Population" — USENIX FAST'07
**Citation:** Eduardo Pinheiro, Wolf-Dietrich Weber, Luiz André Barroso. *Failure Trends in
a Large Disk Drive Population*. 5th USENIX Conference on File and Storage Technologies
(FAST '07), San Jose, CA, Feb 2007. PDF: https://research.google.com/archive/disk_failures.pdf

**Scale of evidence:** >100,000 consumer-grade ATA drives (80–400 GB, 5,400–7,200 rpm, ≥9
models, several vendors), Google production fleet; 9-month SMART/environmental observation
window (Dec 2005–Aug 2006) plus ~5 years of repair records.

**Findings:**
- Annualized failure rate (AFR) 1.7% for first-year drives rising to >8.6% for the 3-year-old
  cohort — far above the <2% vendors quote.
- Temperature and utilization show *much less* correlation with failure than prior
  (vendor/accelerated-test) literature claimed; in the mid temperature range failure rate is
  flat, and 3-year-old low-utilization drives failed *more* than high-utilization ones.
- Strong SMART signals: after the **first scan error, drives are 39× more likely to fail
  within 60 days**; first reallocation → >14× (AFR 3–6× higher); first offline reallocation →
  21×; first probational count → 16×. Critical threshold for all four is **one**.
- **56% of failed drives had zero counts on all four strong SMART signals; 36% had zero on
  every SMART variable** — so SMART alone cannot predict individual drive failures; it is a
  fleet-aggregate signal.
- CRC errors (~2% of drives) point at cables/connectors more than drives.

**2-h cert signal:** Snapshot SMART 5 (Reallocated_Sector_Ct), 197
(Current_Pending_Sector), 198 (Offline_Uncorrectable) + scan-error attributes before and
after a full-surface read; **any nonzero reallocation/pending/scan count on a candidate
drive is a fail** (39×/14×/21× elevated 60-day risk). Do not fail drives on temperature or
utilization alone — the field data says those barely matter in a managed datacenter.

---

### 1.2 Schroeder & Gibson (CMU/PDL) — "Disk Failures in the Real World: What Does an MTTF of 1,000,000 Hours Mean to You?" — USENIX FAST'07
**Citation:** Bianca Schroeder, Garth A. Gibson. *Disk Failures in the Real World: What Does
an MTTF of 1,000,000 Hours Mean to You?* FAST '07, Feb 2007 (Best Paper).
PDF: https://www.cs.toronto.edu/~bianca/papers/fast07.pdf (earlier tech report:
https://www.pdl.cmu.edu/PDL-FTP/Failure/CMU-PDL-06-111.pdf)

**Scale of evidence:** 7 datasets (HPC + internet services), ~100,000 drives (SCSI, FC, SATA,
≥4 vendors), durations from 1 month to 5 years.

**Findings:**
- Datasheet MTTF 1.0–1.5M hours ⇒ nominal AFR 0.58–0.88%. Observed annual replacement rates
  (ARR): 0.5–13.5%, **commonly ~3%, weighted average 3.01% — 3.4× the datasheet number**;
  for 5–8-year-old systems, up to 30×.
- **No bathtub "bottom":** replacement rates nearly double from year 1→2 and 2→3; early
  wear-out dominates, infant mortality barely visible to the customer.
- **SATA drives were not worse than SCSI/FC** — operating conditions dominate component class.
- Failures are **not a Poisson process**: weekly autocorrelation 0.72, monthly 0.79; long-range
  dependence (Hurst 0.6–0.8); a week's replacement count predicts the next week's by up to 9×.
- **The probability of a second drive failing within 1 hour is 4× the exponential-model
  estimate** (2× within 10 hours) — RAID rebuild-window risk is systematically underestimated.
- One documented bad batch: 11,000 SATA drives decommissioned (lubricant breakdown → high
  flying heights → media errors), a firmware/materials failure mode invisible in datasheets.
- Disks were the single most-replaced component (30.6% of replacements in HPC1; 49.1% in COM2).

**2-h cert signal:** Treat any drive failure as evidence about its *batch*, not just itself
(autocorrelation); record vintage/model and don't accept datasheet AFR as a pass/fail
criterion. If certifying a RAID-ish group, budget rebuild windows with the 4×-higher
correlated-failure probability, not AFR/8760.

---

### 1.3 Bairavasundaram, Goodson, Pasupathy, Schindler (UW–Madison/NetApp) — "An Analysis of Latent Sector Errors in Disk Drives" — ACM SIGMETRICS'07
**Citation:** Lakshmi N. Bairavasundaram, Garth R. Goodson, Shankar Pasupathy, Jiri
Schindler. *An Analysis of Latent Sector Errors in Disk Drives*. ACM SIGMETRICS '07, San
Diego, CA, June 2007. PDF: https://research.cs.wisc.edu/adsl/Publications/latent-sigmetrics07.pdf
(Note: often mis-remembered as SIGMETRICS'08; venue is 2007.)

**Scale of evidence:** 1.53 million drives (nearline + enterprise, 14 families / 30 models)
in >50,000 NetApp filers at customer sites, **32 months** of error logs — an order of
magnitude larger than any prior published study.

**Findings:**
- **3.45% of all disks developed ≥1 latent sector error (LSE)** over 32 months: 8.5% of
  nearline vs 1.9% of enterprise. Worst nearline model: ~20% of drives hit within 24 months.
- LSE incidence **increases with drive capacity**; nearline growth is super-linear in age.
- Once a disk has one LSE, it is far more likely to get more:
  **P(≥1 more error in 6 months | had one) = 0.671 vs 0.018 baseline (~37×)**. Errors are not
  independent.
- Spatial locality: ≥0.5 probability of another LSE within a **10 MB radius** of an existing
  error. Temporal locality: 40–80% of errors arrive within **1 minute** of the previous one.
- **Disk scrubbing found >60% of all LSEs** (verify ops: 86.6% of nearline, 61.5% of
  enterprise discoveries) — the background media scrub is the detection mechanism that works.
- Correlations: enterprise drives with a *recovered error* are 13× more likely to develop an
  LSE; nearline drives with *not-ready-condition* errors show LSE probability 0.38 vs 0.085.
- Design lesson: accelerate RAID reconstruction when surviving disks are >1 year old or have
  a recent error.

**2-h cert signal:** A **full-surface read/verify scrub** is the single highest-yield test —
it is how the largest study found most errors. One LSE ≠ remap-and-pass: conditional
probability says more are coming (0.671/6mo) — fail or flag the drive. Also capture
recovered-error and not-ready-condition counts (smartctl -a / SCSI sense counters): they are
leading indicators.

---

### 1.4 Bairavasundaram, Goodson, Schroeder, Arpaci-Dusseau, Arpaci-Dusseau (UW/NetApp/Toronto) — "An Analysis of Data Corruption in the Storage Stack" — USENIX FAST'08
**Citation:** Lakshmi N. Bairavasundaram, Garth R. Goodson, Bianca Schroeder, Andrea C.
Arpaci-Dusseau, Remzi H. Arpaci-Dusseau. *An Analysis of Data Corruption in the Storage
Stack*. 6th USENIX Conference on File and Storage Technologies (FAST '08), Feb 2008.
PDF: https://research.cs.wisc.edu/adsl/Publications/corruption-fast08.pdf

**Scale of evidence:** Same 1.53M-drive NetApp fleet, **41 months**, tens of thousands of
production systems; first large-scale study of *silent* corruption (detected only by
system-level checksums/identity/parity checks, not by the drive).

**Findings:**
- **>400,000 checksum mismatches** observed; 0.86% of nearline and 0.065% of enterprise disks
  affected (nearline an order of magnitude worse; worst model ~3.5% of drives within 17
  months).
- **8% of corruptions were discovered during RAID reconstruction** — i.e., exactly when a
  second failure means data loss. For some models >20%.
- Corruption is *not* randomly distributed: heavy tail (**top 1% of corrupt disks produce >50%
  of all mismatches**; mean 104 vs median 3 mismatches per corrupt disk); extreme spatial
  locality — corruption hits **consecutive 4 KB blocks** (average run 3.4 blocks; 3% of disks
  with ≥2 mismatches have runs of ≥100 consecutive bad blocks); temporal autocorrelation up
  to 10 months.
- Corruption correlates with **system resets (3.7×)** and weakly with latent sector errors.
- Root causes documented anecdotally: a drive firmware bug that **acked cache flushes without
  committing data** (lost writes), misdirected writes, torn writes, SATA/FC **adapter-caused**
  corruption, and corruption concentrated at *specific LBA ranges* on one model.
- Lessons for integrity design: end-to-end per-block checksums **plus block-identity
  validation** (catches lost/misdirected writes that checksums miss), double parity, staggered
  stripes, aggressive/smart scrubbing, spread redundant structures in space *and* time.

**2-h cert signal:** Write-then-read-back with **per-4KB-block checksums** (not per-file:
consecutive-block runs are the observed pattern), verify a *sample across the whole LBA
range* (block-specific firmware bugs), and count mismatches — **one corruption event = fail**.
Testing a full path (host RAM → HBA → drive → read-back) catches the adapter/firmware causes
that disk-only tests miss.

---

### 1.5 Schwarz et al. (Internet Archive / HP Labs / Santa Clara / MSR) — "Disk Failure Investigations at the Internet Archive" — IEEE MSST'06
**Citation:** Thomas Schwarz, Mary Baker, Steven Bassi, Bruce Baumgart, Wayne Flagg,
Catherine van Ingen, Kobus Joste, Mark Manasse, Mehul Shah. *Disk Failure Investigations at
the Internet Archive*. NASA/IEEE Conf. on Mass Storage Systems and Technologies (MSST '06),
work-in-progress session, May 2006.
Slides: https://msstconference.org/MSST-history/2006/Presentations/39rWFlagg.pdf

**Scale of evidence:** ~2,489 desktop-class ATA drives at the Internet Archive, 2005–2006,
plus a **2 PB bit-rot experiment** (periodic full MD5 re-reads of the archive).

**Findings:**
- Replacement rate 2.00% in 2005 (historically as high as 6%); combined node failure
  (mobo/CPU/memory) 2.54% — no observed infant mortality.
- Bit-rot experiment: **no genuine permanent corruption incident** in 2 PB, but **"many MD5
  misreadings"** — transient checksum mismatches that vanish on re-read; of 10 disks with a
  *permanent* MD5 change, 2 were later confirmed drive failures. Distinguishing
  transient-vs-persistent requires a **re-read**.
- SMART "oscillation" analysis: 136 oscillating signal chains, 94 spurious, 42 genuine (27 of
  4,978 disks) — **in all genuine cases SMART gave ample warning before failure**.

**2-h cert signal:** On checksum mismatch, **re-read before condemning** (transients are
common); but a mismatch that persists across two reads = real. SMART trajectory (oscillating
values are often spurious; sustained monotonic degradation is genuine).

*(Note: no paper titled "Disk Failures in the Petabyte Era" is locatable in ACM/IEEE/USENIX
archives; the PB-scale bit-rot evidence the name evokes is this MSST'06 study plus the
NetApp/CERN work below. See §8 Gaps.)*

---

### 1.6 Gunawi et al. — "Fail-Slow at Scale: Evidence of Hardware Performance Faults in Large Production Systems" — USENIX FAST'18 / ACM TOS 14(3) 2018
**Citation:** Haryadi S. Gunawi, Riza O. Suminto, Russell Sears, et al. *Fail-Slow at Scale:
Evidence of Hardware Performance Faults in Large Production Systems*. FAST '18, Feb 2018
(101 incident reports from 12 institutions); extended in ACM Trans. on Storage 14(3), Oct
2018. PDF: https://www.usenix.org/system/files/conference/fast18/fast18-gunawi.pdf

**Findings:** All hardware types — disk, SSD, CPU, memory, network — exhibit **performance
faults** (stalls, slowdowns, decay) rather than clean fail-stop; faults **convert from one
form to another**; root-cause chains are long; fail-slow is systematically confused with
software performance bugs. The authors argue fail-slow must be treated as a distinct
failure class.

**2-h cert signal:** Log latency, not just throughput: per-interval min/median/p99 across the
2 hours. A drive that *slows down* over the run (throughput decay, growing tail) is failing
in a way a single average-throughput number hides.

---

## 2. Silent data corruption (storage path and compute path)

### 2.1 Panzer-Steindel (CERN/IT) — "Data Integrity" internal study, 2007 (the "CERN experiences with silent data corruption" data)
**Citation:** Bernd Panzer-Steindel. *Data Integrity* (Draft 1.3), CERN/IT, April 2007 —
systematic analysis of data corruption in the CERN computer center, Jan–Feb 2007 (internal
technical note; not peer-reviewed, but the canonical SDC measurement).
PDF: https://indico.cern.ch/event/13797/contributions/1362288/attachments/115080/163419/Data_integrity_v3.pdf

**Scale of evidence:** A write/read-back/compare probe (~2 GB pattern file) run **every 2
hours on >3,000 nodes for ~5 weeks**; RAID-5 verify across 492 systems (~1.5 PB) over 4
weeks; checksum audit of 33,700 CASTOR files (~8.7 TB).

**Findings:**
- The probe caught **500 corruption events on 100 nodes in 5 weeks**. Taxonomy: 10%
  single-bit, 10% sector/page-sized, **80% in 64 KB regions** (correlated with a
  3ware/Western Digital disk-dropout firmware bug — firmware, not media, dominates big
  corruptions).
- Measured **byte error rate ~3×10⁻⁷** (22 mismatches in 33,700 files ≈ 1 bad file per
  ~1,500) vs the vendor 10⁻¹⁴/bit claim — orders of magnitude higher in practice, with
  "complicated patterns".
- RAID controllers do **not** check parity on normal reads; weekly verify fixed ~300 bad
  blocks and read ~3× more bits than physics applications did.
- **99.8% of compressed files with a single bit error become entirely unreadable** —
  corruption hurts compressed/checksummed formats far more than raw counts suggest.
- Countermeasures adopted: disk probe every 2 h, memory probe (1 GB/4 h), weekly RAID
  consistency checks, weekly file-checksum verification, application-level checksums — at
  the cost of roughly **doubling required I/O performance** on disk servers.
- ECC memory errors were observed at ~4 orders of magnitude below vendor BER expectations
  (or under-reported through IPMI), while double-bit errors still occurred.

**2-h cert signal:** This study *is* the template: **write a known-pattern ~2 GB file, sync,
read back, compare — per node, per 2-hour window**; classify mismatches by size
(bit/sector/64 KB) to localize firmware vs media. A node that fails once is a node with a
problem, not a statistical fluke at fleet scale.

### 2.2 File-system-side integrity: IRON File Systems (SOSP'05) and ZFS
**Citations:**
- Vijayan Prabhakaran, Lakshmi N. Bairavasundaram, Nitin Agrawal, Haryadi S. Gunawi,
  Andrea C. Arpaci-Dusseau, Remzi H. Arpaci-Dusseau. *IRON File Systems*. ACM SOSP '05,
  Brighton, Oct 2005. (Fault-injection showed mainstream file systems of the era detected
  and recovered from few disk-corruption/misdirected-write cases; metadata policies are
  the weak point.) Referenced in FAST'08 corruption paper §7.
- Jeff Bonwick, Bill Moore. *ZFS: The Last Word in File Systems*. Sun Microsystems tech
  note, 2003–2006. https://web.archive.org/web/20060427092041/http://www.sun.com/2004-0914/feature/
  (Vendor design doc, not peer-reviewed: 64-bit end-to-end checksums stored with every block
  pointer, block identity, self-healing copy/parity repair, periodic scrub — the design the
  FAST'08 field data later validated.)

**Relevance:** The FAST'08 study (§1.4) is the field evidence behind the ZFS-class design:
checksums alone miss lost/misdirected writes; you need **identity + checksum + double parity
+ scrub**. Today ZFS, Btrfs, Ceph, WAFL, and GFS-descendants all ship this stack.

**2-h cert signal:** Verify both dimensions: data checksum *and* placement/identity (that the
block you read is the block you wrote where you wrote it). Scrub-on-cert catches
corruption-at-rest that write/read tests miss.

### 2.3 Compute-side silent corruption (CPU/GPU) — "Cores that don't count" and successors
**Citations:**
- Peter H. Hochschild, Paul Turner, Jeffrey C. Mogul, Rama Govindaraju, Parthasarathy
  Ranganathan, David E. Culler, Amin Vahdat (Google). *Cores that don't count*. 18th
  Workshop on Hot Topics in Operating Systems (HotOS '21), Ann Arbor, May 2021, pp. 9–16,
  DOI 10.1145/3458336.3465297. PDF:
  https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s01-hochschild.pdf
- Harish Dattatraya Dixit, Sneha Pendharkar, Matt Beadon, Chris Mason, Tejasvi Chakravarthy,
  Bharath Muthiah, Sriram Sankar (Meta). *Silent Data Corruptions at Scale*. arXiv:2102.11245,
  2021. https://arxiv.org/abs/2102.11245
- Devesh Tiwari, Saurabh Gupta, James Rogers, et al. *Understanding GPU errors on large-scale
  HPC systems and the implications for system design and operation*. IEEE HPCA '15.
  (GPU field errors on Titan-class systems — flagged as the later GPU-training relevance.)

**Findings (HotOS'21):** Google observes **ephemeral silent corrupt execution errors (CEEs)
on the order of a few "mercurial" cores per several thousand machines** — manufacturing
defects that escaped test, workload- and (frequency, voltage, temperature)-dependent,
afflicting one core of a chip, sometimes appearing years into service. Documented
manifestations: a self-inverting AES miscomputation, garbage-collector corruption losing
live data, DB index corruption varying by which core serves the query, lock-semantics
violations, repeated bit flips at a fixed bit position. Detection at Google: fleet-wide
recurring screening tests (crypto/compression/hash/copy libraries, sanitizers), machine-check
analysis, **core-specific recidivism**, and an RPC service where applications "report a
suspect core"; roughly half of human-flagged suspect cores prove mercurial. Mitigations:
quarantine cores, replicate/vote critical computations, self-checking libraries; Colossus
uses end-to-end checksums on the write path and Spanner multi-layer checksums. Meta's
companion study (Dixit et al.) found **hundreds of faulty CPUs across hundreds of thousands
of machines** after >18 months of fleet screening — a systemic, cross-generation issue.
SIGARCH's 2022 analysis puts fleet SDC at ~one faulty device per thousand.

**2-h cert signal (storage relevance):** the certifying node's CPU/RAM sits in your data
path — it computes the checksums. Pin a **self-checking kernel (SHA/AES/compress) per core**,
run repeatedly during the 2 h, compare results across cores and over time; a core that
disagrees = mercurial = fail the *node*, not the disk. Cross-check: corrupted checksums
computed on a bad core will "verify" data that is actually wrong.

### 2.4 DRAM errors — the page-cache link
**Citations:**
- Bianca Schroeder, Eduardo Pinheiro, Wolf-Dietrich Weber (Google). *DRAM Errors in the Wild:
  A Large-Scale Field Study*. ACM SIGMETRICS '09, Seattle, June 2009, pp. 193–204.
  https://research.google/pubs/dram-errors-in-the-wild-a-large-scale-field-study/
- Justin Meza, Qiang Wu, Sanjeev Kumar, Onur Mutlu (CMU/Facebook). *Revisiting Memory Errors
  in Large-Scale Production Data Centers: Analysis and Modeling of New Trends from the
  Field*. 45th IEEE/IFIP DSN, Rio de Janeiro, June 2015, pp. 415–426.
  PDF: https://people.inf.ethz.ch/omutlu/pub/memory-errors-at-facebook_dsn15.pdf
- Leonardo Bautista-Gomez, Ferad Zyulkyarov, Osman Unsal, Simon McIntosh-Smith.
  *Unprotected Computing: A Large-Scale Study of DRAM Raw Error Rate on a Supercomputer*.
  SC '16 (International Conf. for HPC, Networking, Storage and Analysis), Salt Lake City,
  Nov 2016, 55:1–55:11.
  https://research-information.bris.ac.uk/en/publications/unprotected-computing-a-large-scale-study-of-dram-raw-error-rate-

**Scale & findings:**
- *Schroeder SIGMETRICS'09:* all Google servers, 2.5 years, many millions of DIMM-days.
  Error rates **orders of magnitude above assumptions**: 25,000–70,000 errors per billion
  device-hours per Mbit; **>8% of DIMMs affected per year**; dominated by *hard* faults, not
  cosmic-ray soft errors. (Per Meza DSN'15: their UCE rate was 25× smaller than CE rate.)
- *Meza DSN'15:* Facebook's **entire fleet, 14 months, billions of device-days**. ~2.08% of
  servers/month log correctable errors (~9.6%/yr); uncorrectable ~0.03%/month. Error counts
  per server follow a **Pareto/power law — mean is 55× the median** (a few machines bombard).
  Socket/channel (non-DIMM) failures cause the majority of error *events* and MCE storms that
  make servers unresponsive ("denial of service"). Newer fabrication (4 Gb chips) is 1.8×
  worse than 2 Gb. Workload type moves failure rate up to 6.5×. **Page offlining cut error
  rate 67%** in a 12,276-server production deployment (6% of offline attempts failed on
  locked/prefetching pages).
- *Bautista-Gomez SC'16:* a ~1,000-node supercomputer block **with ECC disabled**, scanned
  continuously for over a year (Feb 2015–Feb 2016): thousands of raw DRAM errors, many
  multi-bit; most multi-bit errors corrupt **non-adjacent** bits; most flips are **1→0**;
  thousands of simultaneous multi-region single-bit events; correlated with temperature and
  even the sun's position (solar/neutron effects).

**Page-cache claim:** a DRAM fault in a dirty page gets written to disk; in a clean page it
gets served to your process. ECC corrects most (Schroeder's hard-fault dominance says
scrubbing matters), but SEC-DED leaves double-bit events, and unprotected nodes see raw
errors at measurable rates.

**2-h cert signal:** Count EDAC/mcelog corrected/uncorrected errors during the window (a burst
during a 2-h run is a Pareto-tail machine — repair it); on ECC-less nodes run a memory
scan (the SC'16 methodology) to get the actual raw bit-error rate of the box that will hold
your page cache.

---

## 3. Benchmarking methodology

### 3.1 Traeger, Zadok, Joukov, Wright — "A Nine-Year Study of File System and Storage Benchmarking" — ACM TOS 4(2), 2008
**Citation:** Avishay Traeger, Erez Zadok, Nikolai Joukov, Charles P. Wright. *A Nine Year
Study of File System and Storage Benchmarking*. ACM Transactions on Storage 4(2), Article 5,
May 2008, DOI 10.1145/1367829.1367831 (presented at FAST '08).
PDF: https://www.fsl.cs.stonybrook.edu/docs/fsbench/fsbench-tr.pdf

**Scale of evidence:** Survey of **415 benchmarks drawn from 106 papers** at SOSP/OSDI/
FAST/USENIX ATC, 1999–2007, plus original experiments (the "Slowfs" ext2 variant).

**Findings (the canonical critique):**
- **"Most popular benchmarks are flawed and many research papers do not provide a clear
  indication of true performance."**
- Reporting hygiene: the majority of papers did not state the number of runs (median ~1–3);
  only 21.5% of benchmarks reported per-result statistical dispersion.
- **Runtime: 58.3% of benchmarks ran <5 minutes; 70.9% <10 minutes** — too short to reach
  steady state.
- Specific demolitions: PostMark's default configuration runs in **<0.1 s** and "barely
  performs any I/O"; Andrew Benchmark's dataset fits in the buffer cache so post-copy reads
  never touch disk; compile benchmarks are CPU-bound — **slowing ext2 reads by 32× changed
  wall-clock time only 2–5%**; five hand-rolled variants of the "same" Sprite LFS small-file
  benchmark differed by 13× in runtime.
- Guidelines that became the checklist: report every parameter and version; justify the
  benchmark; control cache state (reboot beats remount); make the **working set exceed RAM**;
  disclose partition placement (ZCAV); age the file system; run to steady state; report
  confidence intervals; publish benchmark source.

**2-h cert signal:** The cert itself must survive this critique: dataset ≫ RAM, explicit
cache-clearing between phases, ≥5-minute steady-state phases, N repeated runs with reported
variance. A cert built on a compile benchmark or default-config PostMark certifies nothing.

### 3.2 The era critiques (pre-Traeger)
**Citations:**
- John Ousterhout. *Why aren't operating systems getting faster as fast as hardware?*
  USENIX Summer Technical Conf., Anaheim, June 1990, pp. 247–256.
- Dawson Tang, Margo Seltzer. *Lies, Damned Lies, and File System Benchmarks*. Harvard
  TR-34-94, Dec 1994 (in *VINO: The 1994 Fall Harvest*).
- Christopher Small, Aamer Ghosh, Hasnain Saleeb, Margo Seltzer, Keith Smith. *Does Systems
  Research Measure Up?* Harvard TR-16-97, Nov 1997. (Surveyed ten conference proceedings:
  **>90% of file-system benchmarks were ad-hoc; two-thirds of experiments reported a single
  number with no statistics.**)
- Margo Seltzer, Aamer Ghosh, Keith Smith, Junxing Zhang. *The Case for Application-Specific
  Benchmarking*. IEEE HotOS VIII, 1999.
- Don Capps, William Norcott. *Iozone File System Benchmark*. 1998. (The Norcott connection:
  William Norcott is IOzone's co-author — see §8 Gaps on "Norcutt".)

**Finding:** The critique lineage is 30 years old: benchmarks mismeasure caches as disks,
single numbers hide variance, and "standard" benchmarks outlive the workloads they modeled.

### 3.3 Tarasov et al. — "Benchmarking File System Benchmarking: It *IS* Rocket Science" — USENIX HotOS'11
**Citation:** Vasily Tarasov, Erez Zadok, et al. *Benchmarking File System Benchmarking:
It IS Rocket Science*. 13th Workshop on Hot Topics in Operating Systems (HotOS '11), Napa,
May 2011. PDF: https://www.usenix.org/event/hotos11/tech/final_files/Tarasov.pdf

**Findings:** Even the trivial question "how good is random-read performance of Linux file
systems?" produces answers spanning **orders of magnitude** with innocuous configuration
changes (benchmark fragility). On-disk metadata benchmarks silently become **in-memory/cache
benchmarks** when the file system groups metadata or the benchmark sweeps small file sizes
or reports warm-cache results. File systems are multi-dimensional and must be evaluated as
such.

**2-h cert signal:** Run each operation in at least two cache configurations (page-cache warm
vs O_DIRECT/cleared); if a metadata or read number doesn't change when you bypass caches, you
measured RAM, not storage.

### 3.4 Smith & Seltzer — "File System Aging — Increasing the Relevance of File System Benchmarks" — ACM SIGMETRICS'97
**Citation:** Keith A. Smith, Margo I. Seltzer. *File System Aging — Increasing the Relevance
of File System Benchmarks*. ACM SIGMETRICS '97, Seattle, June 1997.
PDF: https://www.seltzer.com/assets/publications/File-System-Aging.pdf

**Findings:** Benchmarks on freshly-formatted, empty file systems mislead: fragmentation and
allocation state dominate real performance (an empty FS vs a 75%-full 7-month-old duplicate
of the same FS differ measurably); aging a 1 GB file system by 7 months required writing
87.3 GB of data.

**2-h cert signal:** Certify against a **pre-filled, aged state** (or at least 70%+ full with
fragmented free space), never a fresh mkfs — a fresh-FS result is an upper bound the
customer will never see.

### 3.5 IO500 — the institutionalized methodology
**Citations:**
- Julian M. Kunkel, John Bent, Jay Lofstead, George S. Markomanolis. *Establishing the
  IO-500 Benchmark*. PDSW-DISCS '17 (12th Parallel Data Storage Workshop), Atlanta, Nov
  2017 (work-in-progress). Slides:
  https://pdsw.org/pdsw-discs17/wips/slides/kunkel-wipslides-pdsw-discs17.pdf
- IO500 Steering/BoF abstracts: SC '18 (https://sc18.supercomputing.org/proceedings/bof/bof_pages/bof134.html)
  and SC '25 (https://sc25.supercomputing.org/proceedings/bof/bof_pages/bof135.html) —
  "the de facto benchmarking standard for HPC storage", biannual lists since 2017, 300+
  entries, execution scripts collected "for providing means of result verification".
- Hongzhe Shan, John Shalf. *Using IOR to analyze the I/O performance for HPC platforms*.
  LBNL Tech Report LBNL-62647, 2007. https://www.osti.gov/biblio/923356 (IOR methodology);
  mdtest: LLNL, https://github.com/LLNL/mdtest
- Radita Liem, Dmytro Povaliaiev, Jay Lofstead, Julian Kunkel, Christian Terboven.
  *User-Centric System Fault Identification Using IO500 Benchmark*. IEEE/ACM 6th
  Parallel Data Systems Workshop (PDSW '21), pp. 35–40, DOI 10.1109/PDSW54622.2021.00011.
- Aasish Kumar Sharma, Anila Ghazanfar, Sepehr Mahmoodianhamedani, Sascha Safenreider,
  Julian Kunkel (GWDG). *Repository-Scale Performance Characterization of the IO500
  Benchmark*. arXiv:2610.07035, 2025. https://arxiv.org/html/2610.07035v1

**Methodology (IO500):** IOR (easy/hard) + mdtest (easy/hard) + parallel find — **12 phases,
9 scored**; write/create phases use a **300-second stonewall** with wear-down; the bandwidth
score is the geometric mean of 4 IOR results, metadata score combines mdtest phases + find,
and the **overall score = sqrt(bandwidth × metadata)** (verified on every submission record
to 0.1% in the 2025 study). Design goals per Kunkel's slides: "easy for optimized patterns,
hard for naive patterns" (the hard phases punish naive stacks), lightweight to run (5-minute
phases), and **trustworthy: anti-cheat via published execution scripts and mandatory
disclosure of all tunings**.

**Repository-scale findings (2025):** 294 post-reset submissions, 116 sites, 2019–2025.
Overall scores span 0.58–210,255 (CV 7.40); **metadata-phase CVs (7.0–11.3, find = 11.3)
dwarf IOR CVs (2.5–4.6)** — metadata is the volatile dimension. Bandwidth↔metadata
correlations are only 0.49–0.82: similar overall scores can hide opposite profiles
(GekkoFS: 24.8 GiB/s + 934 kIOPS vs IME: 341 GiB/s + 63 kIOPS, near-identical overall).
**49 read/stat/find phases finished in <10 s — consistent with cache or client-side data
retention effects** (cache leakage even inside IO500). Stonewall-to-final throughput ratios:
median ~1.03–1.05 but p95 up to 1.77 and max 2.56 — straggler losses hidden by the composite
score. Liem et al. (PDSW '21) show the phase-level results can be used as **fault
fingerprints** for user/system-level I/O fault identification.

**2-h cert signal:** Adopt the IO500 pattern at node/cluster scale: report **bandwidth and
metadata as separate scores** (never one composite); include an easy *and* hard phase
(large sequential vs small random/strided); use a stonewall timer so slow starts can't hide;
check phase wall-times — a read phase that finishes in seconds means you measured cache.

---

## 4. HPC checkpoint I/O at scale

### 4.1 Luu et al. — "A Multiplatform Study of I/O Behavior on Petascale Supercomputers" — ACM HPDC'15
**Citation:** Huong Luu, Marianne Winslett, William Gropp (UIUC); Robert Ross, Philip Carns,
Kevin Harms (ANL); Prabhat, Surendra Byna, Yushu Yao (LBNL). *A Multiplatform Study of I/O
Behavior on Petascale Supercomputers*. ACM HPDC '15, Portland, June 2015, DOI
10.1145/2749246.2749269. PDF: https://sdm.lbl.gov/~sbyna/research/papers/201506-HPDC-iologs.pdf

**Scale of evidence:** Darshan logs of **~1M production jobs** across three leadership
platforms: Intrepid (IBM Blue Gene/P, 4 years, 239K jobs), Mira (Blue Gene/Q, 18 months, 137K
jobs), Edison (Cray XC30, 9 months, 703K jobs).

**Findings ("in the wild" reality check):**
- **~⅓ of jobs never exceed the aggregate throughput of a single USB thumb drive (~256
  MB/s); ¾ of apps never exceed four thumb drives** — against platform peaks of 88–240 GB/s.
- **Over ⅓ of jobs spend more time in metadata functions than in data transfer.**
- **90% of platform I/O time comes from <10% of jobs** (Edison) / under 4–6% of apps — the
  checkpoint/heavy writers dominate storage load.
- ~95% of Edison jobs (80% Intrepid, 50% Mira) use **POSIX-only I/O**, never MPI-IO.
- Case studies of burst behavior: "Earth1" spent 56% of runtime in I/O, dominated by metadata
  on global files (small, unaligned POSIX writes); "PDE1" wrote global **text** files with
  fprintf from up to 512K processes — one 7-hour, 3.5M-core-hour job; after an MPI-IO rewrite
  the same output took **11 seconds**. Text-file I/O is a widespread, hidden anti-pattern.

**2-h cert signal:** Measure **metadata separately** (create/stat/delete rates) and simulate
a **checkpoint burst** (all writers simultaneously, large sequential) plus a **restart read**
— the two patterns that dominate leadership I/O time. Flag small/unaligned writes and
text-format output; they are the documented bottleneck.

### 4.2 Continuous characterization (Darshan lineage)
**Citations:**
- Philip Carns, Robert Latham, Robert Ross, Kamil Iskra, Samuel Lang, Kevin Riley. *24/7
  Characterization of Petascale I/O Workloads*. IEEE CLUSTER '09, New Orleans, Aug–Sep 2009.
- Philip Carns, Kevin Harms, Bill Allcock, Charles Bacon, Samuel Lang, Robert Latham, Robert
  Ross. *Understanding and Improving Computational Science Storage Access through Continuous
  Characterization*. ACM Trans. on Storage 7(3), Article 8, 2011.
- Shane Snyder, Philip Carns, Kevin Harms, Robert Ross, Glenn K. Lockwood, Nicholas J.
  Wright. *Modular HPC I/O Characterization with Darshan*. ESPT '16, pp. 9–17.

**Finding:** Lightweight in-situ instrumentation (1–2% overhead), deployed by default on
every job, outperforms one-off benchmarks for understanding storage behavior — the
methodological counterpoint to benchmark-of-the-week.

### 4.3 Variability of parallel I/O
**Citation:** Jay Lofstead, Fang Zheng, Qian Liu, Scott Klasky, Ron Oldfield, Todd
Kordenbrock, Karsten Schwan, Matthew Wolf. *Managing Variability in the IO Performance of
Petascale Storage Systems*. SC '10, New Orleans, Nov 2010, DOI 10.1109/SC.2010.32.

**Finding:** Concurrent parallel I/O at petascale shows high run-to-run and node-to-node
variability; managing (not just maximizing) bandwidth is a first-class design goal. The IO500
repository study (§3.5) confirms: per-phase CV of 2.5–11.3 across supposedly comparable
systems.

**2-h cert signal:** Report variance, not a single pass: N repeats of the same phase;
CV per phase; flag p99 stalls.

### 4.4 Checkpoint modeling
**Citations:**
- Ron Oldfield, Todd Kordenbrock, et al. *Modeling the Impact of Checkpoints on
  Next-Generation Systems*. Cray User Group (CUG) 2008.
  PDF: https://cug.org/5-publications/proceedings_attendee_lists/2008CD/S08_Proceedings/pages/Authors/16-19Thursday/Oldfield-Thursday17A/Oldfield-Thursday17A-paper.pdf
  (Applies Daly's optimal-interval model to four massive-scale systems; checkpoint latency
  drives overhead at scale.)
- Adam Moody, Greg Bronevetsky, Kathryn Mohror, B.R. de Supinski. *Design, Modeling, and
  Evaluation of a Scalable Multi-Level Checkpointing System*. SC '10.
- (Classic analytic basis: John Daly. *A higher order estimate of the optimal checkpoint
  interval and restart latency*. ICCS 2004.)

**Finding:** Checkpoint volume × interval vs system MTBF sets the achievable utilization;
multi-level checkpointing (RAM/local-SSD/PFS) is the scalable answer.

### 4.5 Burst buffers
**Citations:**
- Kento Sato, Kathryn Mohror, Adam Moody, Todd Gamblin, Bronis R. de Supinski, Naoya
  Maruyama, Satoshi Matsuoka. *A User-Level InfiniBand-Based File System and Checkpoint
  Strategy for Burst Buffers*. IEEE/ACM CCGrid '14.
  PDF: https://kento.github.io/files/2014-01-28-CCGrid2014-conf-paper.pdf
- Teng Wang, Sarp Oral, Yandong Wang, Brad Settlemyer, Scott Atchley, Weikuan Yu.
  *BurstMem: A High-Performance Burst Buffer System for Scientific Applications*. IEEE Big
  Data 2014.
- Teng Wang, Sarp Oral, Michael Pritchard, Bin Wang, Weikuan Yu. *TRIO: Burst Buffer Based
  I/O Orchestration*. IEEE CLUSTER '15, DOI 10.1109/CLUSTER.2015.38.
  https://www.osti.gov/biblio/1567391
- Teng Wang, Kathryn Mohror, Adam Moody, Kento Sato, Weikuan Yu. *An Ephemeral Burst-Buffer
  File System for Scientific Applications* (BurstFS). SC '16, pp. 807–818.
  https://ieeexplore.ieee.org/document/7877147
- Kwang-Jong Sung et al. (LBNL/IBM). *BBOS: Efficient HPC Storage Management via Burst
  Buffer Over-subscription*. CCGrid '20. PDF: https://sdm.lbl.gov/oapapers/ccgrid20-sung.pdf

**Findings:** Checkpoint traffic is **bursty by nature** (all nodes write at once); burst
buffers (node-local or shared SSD/NVM layers) absorb the burst and drain asynchronously to
the PFS. TRIO intercepts and **reshapes bursty writes into sequential streams** and
coordinates flush order across buffers — cutting average job I/O time **37%** in typical
checkpointing scenarios. BurstFS aggregates node-local buffer bandwidth with scalable
metadata indexing; BBOS shows buffer *over-subscription* with transparent staging can beat
1:1 provisioning. Sato et al. show burst buffers also improve C/R *resiliency* (fast
checkpoints → shorter exposure windows).

**2-h cert signal:** A storage system cert for checkpoint duty must test the **burst
profile specifically** — simultaneous-onset, sustained, large sequential writes (and the
matching restart read) — because average-latency/async-scheduled tests understate the
thundering-herd worst case that dominates production I/O time (HPDC'15: <10% of jobs = 90%
of I/O time).

---

## 5. SMR: host-managed vs drive-managed shingled drives

### 5.1 He & Du — "SMaRT: An Approach to Shingled Magnetic Recording Translation" — USENIX FAST'17
**Citation:** Weiping He, David H.C. Du (University of Minnesota). *SMaRT: An Approach to
Shingled Magnetic Recording Translation*. 15th USENIX Conference on File and Storage
Technologies (FAST '17), Santa Clara, Feb 2017.
Page: https://www.usenix.org/conference/fast17/technical-sessions/presentation/he

**Findings:** Drive-managed SMR (DM-SMR) hides the shingled-zone constraint behind a
**shingled translation layer** in firmware that emulates an ordinary block device — at the
cost of **metadata overhead and garbage-collection overhead**. SMaRT (a hybrid
in-place/out-of-place update scheme with background and on-demand GC) is presented as an
efficient translation layer; experiments vs. a **simulated Seagate DM-SMR drive** show the
commercial-style DM-SMR approach performs *worse* than SMaRT, and that DM-SMR provides
performance **"comparable to regular HDDs only when drive space usage is below a certain
threshold"** — i.e., random-write performance collapses as utilization grows and GC work
mounts.

### 5.2 Standards and the host-managed ecosystem
**Citations:**
- ZBC (T10 SCSI, INCITS) / ZAC (T13 ATA) zoned-block-device standards — the normative basis
  for host-managed/host-aware SMR (referenced throughout below).
- Matias Bjørling (Western Digital). *Zone Append: A New Way of Writing to Zoned Storage*.
  USENIX Vault '20. Slides:
  https://www.usenix.org/system/files/vault20_slides_bjorling.pdf — host-managed zone
  model (zone states, write pointers), Linux zoned stack: dm-zoned, f2fs/btrfs/zonefs,
  libzbd, fio zbd support, and its extension to NVMe ZNS.
- Linux kernel ZoneFS documentation: https://docs.kernel.org/filesystems/zonefs.html
  (exposes each zone as a file; append-only sequential zones).
- Btrfs zoned-mode documentation:
  https://btrfs.readthedocs.io/en/latest/Zoned-mode.html — explicitly: **"there are devices
  that appear as non-zoned but actually are; this is drive-managed and using zoned mode
  won't help"**.
- Western Digital. *Shingled Magnetic Recording (SMR) HDD Technology* white paper.
  https://documents.westerndigital.com/content/dam/doc-library/en_us/assets/public/western-digital/collateral/white-paper/white-paper-shingled-magnetic-recording-hdd-technology.pdf
  — vendor-primary confirmation that DM-SMR "emulates a traditional block storage device
  ... however performance may be unpredictable in certain workloads" (random writes).

### 5.3 The "SMR drives lie about being CMR" failure mode
**Mechanism:** SMR overlaps tracks like roof shingles; writing a track invalidates its
neighbors, so zones must be rewritten sequentially. DM-SMR firmware accepts random writes by
staging them in a small persistent media cache and performing band rewrites/GC on its own
schedule — while **reporting itself as an ordinary non-zoned block device** (sysfs
`/sys/block/*/queue/zoned` reports `none`, same as CMR; no standardized SMART attribute
distinguishes them; only host-aware/host-managed drives answer ZBC/ZAC queries). The
customer sees a CMR-shaped device whose random-write throughput and latency are
workload- and fill-level dependent.

**Documented consequences:** consumer/NAS deployments sold DM-SMR-as-CMR (2020
WD Red/Seagate controversy — class actions and vendor disclosure lists followed; industry
response, not academic literature); the FAST'17 SMaRT results quantify the mechanism
(translation-layer GC, performance only CMR-comparable below a utilization threshold).

**2-h cert signal (the detection recipe):**
1. **Behavioral probe:** sustained **random 4K writes at ≥70% fill**, long enough to exhaust
   the media cache (typically tens of seconds to minutes) — DM-SMR shows a **throughput
   collapse (often >10×) and multi-second latency stalls** when band GC kicks in; random
   *reads* stay CMR-fast. A CMR drive stays flat. Sequential writes stay fast on both.
2. **Identity probe:** `sg_zbc`/`zbc-report` (or `lsblk -o ZONED` / `cat
   /sys/block/*/queue/zoned`): `hostmanaged`/`hostaware` = honest zoned device; `none`
   proves nothing on its own (DM-SMR hides there) — so fall back to the model-number/firmware
   database or the behavioral probe.
3. For archival (mostly-sequential) duty the failure mode is acceptable — certify the *use
   case*, not the drive label.

---

## 6. Which academic findings changed industry practice

| Finding (paper) | Industry change it drove |
|---|---|
| Field AFR ≫ datasheet MTTF; no bathtub bottom; SATA ≈ SCSI/FC (Schroeder & Gibson FAST'07; Pinheiro et al. FAST'07) | Death of datasheet-MTTF as an ops planning number; AFR/ARR from field data became the standard reliability metric; legitimized commodity (SATA) drives in hyperscale datacenters; reliability modeling moved to Weibull/field-derived distributions and correlated-failure-aware RAID design. |
| SMART: strong but incomplete signals; 56% of failures give no SMART warning (Pinheiro et al. FAST'07) | SMART-based fleet health monitoring became universal (e.g., Backblaze's public SMART stats program, hyperscaler proactive replacement), but vendors/operators treat SMART as a *fleet* signal, not a per-drive oracle; motivated RUL/ML approaches (e.g., "Making Disk Failure Predictions SMARTer!", FAST'20). |
| Latent sector errors at 3.45%/32mo; scrubbing finds >60%; LSEs cluster (Bairavasundaram et al. SIGMETRICS'07) | Background **disk scrubbing** became standard in enterprise arrays/RAID; RAID-rebuild acceleration policies; RAID-6/double-parity defaults for large arrays; pending-sector SMART attributes became standard triage. |
| Silent corruption is real: 400K checksum mismatches, 8% found during RAID rebuild; checksums alone miss lost/misdirected writes (Bairavasundaram et al. FAST'08; IRONFS SOSP'05) | Mainstreamed **end-to-end data-integrity stacks** — checksum + block-identity + double parity + scrub — in ZFS, Btrfs, Ceph, WAFL and hyperscale file systems; validation of ZFS's 2003 design; DIF/DIX (T10 PI) extensions for the storage fabric. |
| Measured SDC byte-error rate ~3×10⁻⁷ vs vendor 10⁻¹⁴; 80% of corruptions are 64 KB-region firmware bugs (Panzer-Steindel, CERN 2007) | CERN/WLCG deployed checksums-everywhere (per-file + periodic re-verification, probes, weekly RAID verifies); data-integrity budget became an explicit line item ("doubling of required I/O performance"); HPC centers adopted similar probe/scrub regimes. |
| Benchmark reporting is statistically bankrupt: <5-min runs, hidden params, cache-measured-as-disk (Traeger et al. TOS'08; Tang & Seltzer '94; Small et al. '97; Tarasov HotOS'11) | Modern venue norms (report configs, cache state, variance); and directly shaped **IO500** (published scripts, disclosed tunings, stonewalling, 300-s steady-state phases, bandwidth+metadata as separate scored dimensions) — now the de facto HPC storage procurement benchmark with 300+ submissions. |
| Production I/O is dominated by <10% of jobs; metadata ≥ data time for ⅓ of jobs; text-IO anti-pattern (Luu et al. HPDC'15; Carns et al. TOS'11) | Darshan-style continuous characterization deployed by default at ALCF/NERSC; I/O "boot camps" at leadership facilities; storage procurement sized for checkpoint bursts, not averages. |
| Checkpoint bursts need an intermediate tier (Sato CCGrid'14; TRIO Cluster'15; BurstFS SC'16) | Burst buffers became standard on leadership systems (Cori/Theta/Summit-class: node-local SSD tiers, scheduler-integrated staging); burst-aware job scheduling (I/O-aware backfill, HPDC'16 Flux work). |
| Mercurial cores / CPU SDC: a few per few thousand machines (Hochschild et al. HotOS'21; Dixit et al., Meta 2021) | Fleet-wide SDC screening became standard practice at hyperscalers; OCP industry working groups and white papers on SDC (2025); end-to-end checksum + replication validation extended to the compute path; GPU vendors acknowledged analogous GPU SDC (relevant later for training clusters). |
| DM-SMR performance is fill- and workload-dependent while presenting as CMR (He & Du FAST'17; ZBC/ZAC; btrfs/ZoneFS docs) | ZBC/ZAC zoned standards + Linux zoned stack (dm-zoned, f2fs, btrfs, zonefs, libzbd, fio) and NVMe ZNS; after the 2020 NAS-SMR controversy, vendors published CMR/SMR disclosure lists and moved NAS lines back to CMR; "check the drive, not the label" became procurement practice. |

---

## 7. Top 5 findings testable in a 2-hour certification run

Each is directly measurable in a 2-hour window and backed by field evidence above.

1. **CERN-style silent-corruption probe: write → sync → read-back → compare, per-node, on a
   ~2 GB pattern file (or scaled to fill the window).** Classify mismatches by extent
   (single-bit / sector / 64 KB region) — 80% of real events were 64 KB firmware-clustered
   corruptions. Count per node·window; a node with one persistent mismatch fails. Re-read on
   mismatch to separate transients (Internet Archive MSST'06) from persistent errors
   (FAST'08). *[Panzer-Steindel 2007; Bairavasundaram et al. FAST'08; Schwarz et al. MSST'06]*
   - Pass/fail: zero persistent mismatches; any persistent corruption = fail; log the extent
     class for vendor triage.

2. **Full-surface read scrub + SMART 5/197/198 delta.** The largest LSE study found >60% of
   latent errors via background verify; a nonzero reallocation/pending/scan count predicts
   14–39× higher 60-day failure risk. Fail on *first* nonzero pending/reallocated/scan-error
   count; pass requires the whole surface readable with zero new SMART error counts.
   *[Bairavasundaram et al. SIGMETRICS'07; Pinheiro et al. FAST'07]*
   - Include the whole LBA range (FAST'08 found model-specific block-number corruption),
     and count recovered/not-ready errors as leading indicators (13× and 4.5× conditional
     risk multipliers).

3. **Anti-cache-trick benchmark: working set ≫ RAM, explicit cache clearing, ≥5-minute
   steady-state phases, repeated runs with reported variance, and metadata measured
   separately from bandwidth.** 58% of published storage benchmarks ran <5 min; a 32× I/O
   slowdown was invisible in a CPU-bound compile benchmark; ⅓ of production HPC jobs are
   metadata-dominated; IO500 metadata-phase variance is 2–3× bandwidth variance; read phases
   finishing in seconds = cache measurement. *[Traeger et al. TOS'08; Tarasov HotOS'11;
   Luu et al. HPDC'15; Sharma et al. 2025 (IO500 repository)]*
   - Pass/fail: cert only counts numbers measured in steady state, working set > RAM, with
     both an "easy" (sequential) and "hard" (random/strided, small) phase — the IO500
     easy/hard design — and a run-to-run CV threshold (metadata CV is expected to be high;
     that's a property of the system, not noise).

4. **DM-SMR-as-CMR behavioral detector: sustained random 4K writes at ≥70% fill until the
   drive's media cache is exhausted, with per-interval latency tracking.** DM-SMR shows a
   >10× random-write throughput collapse with multi-second GC stalls while random reads stay
   fast; performance is only CMR-comparable below a utilization threshold. Check
   `queue/zoned` (hostmanaged/hostaware = honest; `none` requires the behavioral probe or
   model database). *[He & Du FAST'17; WD SMR white paper; btrfs zoned-mode docs]*
   - Pass/fail: random-write throughput must stay within a stated factor of the drive's spec
     across the whole window at high fill; latency p99 must stay bounded; SMR-classified
     drives are certified only for sequential/archival duty.

5. **Node-integrity co-cert: per-core self-checking compute loop + EDAC/mcelog error count
   during the window.** A few mercurial cores per few thousand machines silently corrupt
   results (including the checksums that "verify" your storage); ~2% of servers/month log
   correctable DRAM errors (Pareto-distributed — bursts matter); unprotected nodes show raw
   DRAM errors at measurable rates — and your page cache lives there. Pin a hash/AES/compress
   self-check kernel to each core for the full window and diff results across cores and time;
   record corrected/uncorrectable ECC events. *[Hochschild et al. HotOS'21; Dixit et al.
   2021; Meza et al. DSN'15; Schroeder et al. SIGMETRICS'09; Bautista-Gomez et al. SC'16]*
   - Pass/fail: zero core disagreements, zero uncorrectable ECC, and any correctable-ECC
     burst above a threshold flags the node for DIMM repair even if I/O passes.

**Honorable mentions (2-hour-adjacent):** checkpoint-burst profile (simultaneous-onset large
sequential writes + restart read — HPDC'15/TRIO/SC'16); fail-slow detection via
latency-vs-time trend across the window (FAST'18); aged/75%-full baseline instead of fresh
mkfs (SIGMETRICS'97); SMART trajectory oscillation analysis (MSST'06).

---

## 8. Gaps, corrections, and caveats

- **"Disk Failures in the Petabyte Era" (Schwarz et al., FAST'09/HotDep)** — no paper with
  this title is locatable in USENIX/ACM/IEEE archives or Google Scholar-visible indices. The
  PB-scale bit-rot evidence under that name maps to: Schwarz et al., *Disk Failure
  Investigations at the Internet Archive* (MSST '06, §1.5) plus the NetApp FAST'08 corruption
  study (§1.4) and CERN's 1.5 PB RAID-verify campaign (§2.1). If a "petabyte era" paper
  exists under another venue/name, it is obscure enough that the above three carry the same
  evidentiary weight.
- **"Norcutt, 'The UNIX file system: only benchmarked?'"** — not locatable. William Norcott
  is the co-author (with Don Capps) of **IOzone** (1998, §3.2). The era critiques that do
  exist and carry this argument are Ousterhout (USENIX '90), Tang & Seltzer (TR-34-94,
  *Lies, Damned Lies, and File System Benchmarks*), and Small et al. (TR-16-97, *Does Systems
  Research Measure Up?*) — all cited in §3.2.
- **Marin & Van Hensbergen (metadata-benchmarking critique)** — could not locate any such
  paper; Eric Van Hensbergen's publication record (IBM; 9p2000/Plan 9, FS work) contains no
  benchmarking-methodology paper surfaced by searches. The methodological critiques of
  metadata benchmarking that do exist: Tarasov et al. HotOS '11 (§3.3) and the mdtest
  treatment inside IO500 (§3.5). Flagged as a probable mis-remembered citation.
- **Meza et al. (Facebook/CMU)** — there is no standalone peer-reviewed *HDD* field study
  from Meza; the Facebook/CMU large-scale program is: flash SSDs (SIGMETRICS '15, §2.4-era
  data), DRAM (DSN '15), and network reliability (IMC '18), bundled in Meza's CMU PhD thesis
  *Large Scale Studies of Memory, Storage, and Network Failures in a Modern Data Center*
  (2018). Flash venue corrected here: SIGMETRICS '15 (PER 43(1):177–190), often miscited as
  FAST'15.
- **Venue corrections:** Bairavasundaram LSE study is SIGMETRICS **2007** (task brief said
  '08); the *Data Corruption in the Storage Stack* paper is the FAST'08 one.
- **ZFS** — there is no peer-reviewed ZFS paper; the canonical source is the Sun tech note
  (Bonwick & Moore, 2003). The peer-reviewed evidence validating its design is IRONFS
  (SOSP '05) + the FAST'08 field study. Cited accordingly.
- **CERN study** — an internal CERN/IT technical note (Panzer-Steindel, 2007), not
  peer-reviewed; included because it is the canonical measured SDC-rate source and the
  template for the 2-hour probe. The 500-errors/100-nodes number is probe-condition-specific
  (early 2007 hardware, 3ware/WD firmware issue era).
- **Non-academic sources deliberately kept, clearly labeled:** WD SMR white paper and Linux
  kernel/btrfs documentation (§5.2) — normative/primary for the DM-SMR detection recipe;
  Rossmann/practitioner NAS-SMR pages were read but excluded from claims.
- **Silent-corruption rates are era- and stack-specific:** CERN's ~3×10⁻⁷ byte error rate
  (2007) and NetApp's 0.86%/41mo drive-corruption fraction (2004–2007 drives) predate modern
  DIF/T10-PI fabrics; treat them as upper bounds for modern stacks, and as motivation for
  checksum-everywhere rather than as expected rates.
