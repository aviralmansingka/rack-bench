# Site Reliability Engineering on AWS — source node N15

Research date: 2026-10-11.

## 1. Access and verification

1. **Requested O’Reilly URL:** https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp . In this research, a direct `web_fetch` returns HTTP 403. This verifies an access restriction for this research session, not the content behind the login. [observed] [O’Reilly catalog URL](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp)
2. **Primary publisher source located:** Packt’s product page identifies the title and ISBN-13 9781800205970. Its chapter/section pages expose module names. The Packt pages also return HTTP 403 to direct fetch in this research. Search-indexed snippets supply limited catalog evidence. [observed] [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium); [Packt chapter page: module 3](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3)
3. **Scope boundary:** Metadata and module/section titles below are catalog/index evidence only. No authenticated video, complete transcript, or complete course TOC is available or watched in this research. Do not treat the title list as proof of detailed instructional content. [observed] [O’Reilly catalog URL](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp); [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)

## 2. Metadata

- **Exact title:** *Site Reliability Engineering on AWS*. [observed] [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)
- **Format:** Video course / streaming video, not a book edition. Packt product record and O’Reilly video record identify it as a video. [observed] [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium); [O’Reilly video listing](https://www.oreilly.com/videos/site-reliability-engineering/9781800205970/9781800205970-video1_5)
- **Release year:** 2020, as specified by the O’Reilly video record supplied for this node. This research could not independently inspect the inaccessible page’s date field. Packt search snippets establish ISBN/title but not a visible release date. [observed] [O’Reilly catalog URL](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp)
- **Instructor:** Malcolm Orr. Packt search-indexed product excerpt identifies Malcolm Orr and says he is a Principal Architect in AWS Professional Services. [observed] [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)
- **Duration:** O’Reilly source-node catalog reports 281 minutes. Packt’s publisher search-indexed product snippets report 4 hrs 41 mins, equal to 281 minutes. O’Reilly’s separate public listing describes it approximately as a 4-hour course. [observed] [O’Reilly catalog URL](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp); [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium); [O’Reilly video listing](https://www.oreilly.com/videos/site-reliability-engineering/9781800205970/9781800205970-video1_5). [calculated] 4 hours 41 minutes = 281 minutes.

## 3. Verified module / chapter-title evidence

Catalog/search evidence surfaces these module titles. It does not establish a complete table of contents or the content of unlisted modules. [observed] [Packt module 1 page](https://subscription.packtpub.com/video/cloud-and-networking/9781800205970/p1/video1_5/sre-is-a-mindset); [Udemy course listing](https://www.udemy.com/course/site-reliability-engineering-on-aws); [Packt module 3 page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3)

1. **P1 — The Basics of Site Reliability Engineering.** A Packt section page confirms course part P1 and section “SRE Is a Mindset”. The course listing reports this module and 5 lectures. [observed] [Packt P1 section](https://subscription.packtpub.com/video/cloud-and-networking/9781800205970/p1/video1_5/sre-is-a-mindset); [course listing](https://www.udemy.com/course/site-reliability-engineering-on-aws)
2. **P2 — Gaining Resilience and Reliability On AWS.** Module title appears in the course listing, which reports 6 lectures and 52 minutes. [observed] [course listing](https://www.udemy.com/course/site-reliability-engineering-on-aws)
3. **P3 — Accepting Failure in Multi-Tier Applications.** Packt chapter URL establishes this part title; an exposed section is “Managing State.” [observed] [Packt P3 section](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3)
4. **P7 — Surviving Failure of a Global Scale.** Packt search result exposes this chapter title and a named section. The section is “Review AWS Global Architecture and What We Have Just Built.” [observed] [Packt P7 section](https://www.packtpub.com/en-in/product/site-reliability-engineering-on-aws-video-9781800205970/chapter/surviving-failure-of-a-global-scale-p7/section/review-aws-global-architecture-and-what-we-have-just-built-video7_1)

The course-listing source reports 7 sections, 37 lectures, 4h 40m. Packt reports 4h 41m. Duration variance of one minute may reflect rounding or catalog differences and is unresolved. [observed] [Udemy course listing](https://www.udemy.com/course/site-reliability-engineering-on-aws); [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)

## 4. Lifecycle coverage and portable mechanisms

The course is explicitly AWS-focused. The observed catalog topics include reliability mindset, resilience/reliability on AWS, multi-tier failure, state management, and global-scale failure. The techniques below are operational abstractions from those titles. They do not claim that the inaccessible video prescribes these checks. They are not GB300/NVL72-specific capability claims. [observed] [Packt P1](https://subscription.packtpub.com/video/cloud-and-networking/9781800205970/p1/video1_5/sre-is-a-mindset); [course listing](https://www.udemy.com/course/site-reliability-engineering-on-aws); [Packt P3](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3); [Packt P7](https://www.packtpub.com/en-in/product/site-reliability-engineering-on-aws-video-9781800205970/chapter/surviving-failure-of-a-global-scale-p7/section/review-aws-global-architecture-and-what-we-have-just-built-video7_1)

1. **Make readiness and recovery observable.** Inference from the reliability/resilience focus: define readiness as observed serviceable capacity plus a successful bounded workload. Readiness is not a provisioning-complete flag.

   Rack-bench check: timestamp provisioned, image-ready, scheduler-visible, and successful representative GPU work. Record each interval and errors.

   [inference] Basis: [P1 section](https://subscription.packtpub.com/video/cloud-and-networking/9781800205970/p1/video1_5/sre-is-a-mindset); [P2 listing](https://www.udemy.com/course/site-reliability-engineering-on-aws)
2. **Bound failure and validate recovery.** Inference from the failure/resilience module titles: rehearse only a controlled, isolated and reversible failure mode. Verify detection, containment, recovery, and return to intended state.

   Check with a disposable service or synthetic job, never production eviction or a destructive rack-level failure.

   [inference] Basis: [P2 listing](https://www.udemy.com/course/site-reliability-engineering-on-aws); [P3 section](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3)
3. **Track state through transitions.** Inference from P3’s “Managing State” section: record authoritative desired state and observed state across deployment, recovery, resize/migration, and cleanup.

   Check one approved, non-destructive configuration transition on an isolated target. Compare before/after inventory, job outcome, and drift. Then restore.

   [inference] Basis: [P3 section](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3)
4. **Design for more than one failure domain, without assuming portability of cloud topology.** Inference from the AWS global-scale module: make dependencies and failure boundaries explicit. Then measure whether the target service can recover within its declared bounds.

   The rack-bench analogue is a tabletop or isolated service-level exercise. Do not claim AWS Regions/AZ patterns map directly to an NVL72 rack.

   [inference] Basis: [P7 section](https://www.packtpub.com/en-in/product/site-reliability-engineering-on-aws-video-9781800205970/chapter/surviving-failure-of-a-global-scale-p7/section/review-aws-global-architecture-and-what-we-have-just-built-video7_1)
5. **Use explicit exit and cleanup evidence as a local extension, not course-attributed coverage.** The catalog evidence that search surfaces does not verify tenant offboarding, secure wipe, or physical media disposition instruction.

   For the rack-bench, measure a disposable-tenant exit. Deny new work. Revoke test credentials. Reconcile test-data handling. Confirm capacity release. Do not equate deletion or a clean status flag with sanitization.

   [inference] Basis/coverage boundary: [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium); [P3 section](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3)

Keep checks short, non-destructive, and measured during a two-hour category run. Reserve the final 20 minutes for cleanup/evidence. A pass means only that the named bounded probe met its declared local criteria. It does not prove long-term reliability, production eviction safety, image integrity across a fleet, sanitization, or GB300 acceptance. [inference] Basis: [Packt course catalog](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium); rack-bench constraints from project scope.

## 5. Canon relation

Optional video supplement, not a spine book. Its AWS-specific example architecture and catalog-level evidence do not justify elevating it above the existing general lifecycle texts. They do not justify treating cloud patterns as GB300/NVL72 capabilities. [inference] [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium); [O’Reilly catalog URL](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp)

## Gaps

- O’Reilly and Packt pages are not directly readable in this session (403). The release year follows the requested O’Reilly catalog record. It needs authenticated publisher-page confirmation. [observed] [O’Reilly catalog URL](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp); [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)
- Catalog/search evidence surfaces only P1, P2, P3, and P7 titles. Exact titles and module locations for P4–P6, all lecture titles, and a complete module sequence remain unverified. [observed] [Packt P1](https://subscription.packtpub.com/video/cloud-and-networking/9781800205970/p1/video1_5/sre-is-a-mindset); [Packt P3](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970/chapter/accepting-failure-in-multi-tier-applications-p3/section/managing-state-video3_3); [Packt P7](https://www.packtpub.com/en-in/product/site-reliability-engineering-on-aws-video-9781800205970/chapter/surviving-failure-of-a-global-scale-p7/section/review-aws-global-architecture-and-what-we-have-just-built-video7_1)
- This review watched no transcript and read no full module text. This review cannot establish detailed technique attribution, deployment/image recovery procedure, scaling practice, configuration controls, or tenant-exit/wipe coverage. [observed] [O’Reilly catalog URL](https://learning.oreilly.com/videos/-/9781800205970/?orm_source=mcp); [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)
- No source verifies GB300/NVL72 hardware procedure, firmware/OS changes, production preemption/eviction, repeated internet/storage performance testing, or rack-specific acceptance thresholds. Do not perform these as part of this source review. [inference] [Packt product page](https://www.packtpub.com/en-us/product/site-reliability-engineering-on-aws-9781800205970?type=premium)
