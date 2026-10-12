# Kubernetes Programming with Go — Philippe Martin

Research date: 2026-10-11.

1. **Access and metadata.** [observed] This research fetches the requested O’Reilly URL first. It returns an access-denied page. The page does not expose book contents. [O’Reilly record](https://learning.oreilly.com/library/view/-/9781484290262/?orm_source=mcp).

   [observed] The Springer/Apress publisher record identifies the book. The title is *Kubernetes Programming with Go: Programming Kubernetes Clients and Operators Using Go and the Kubernetes API*.

   It lists Philippe Martin, first edition, Apress, and 316 numbered pages (XX + 316). It lists eBook ISBN 978-1-4842-9026-2 (published 24 Dec 2022) and print ISBN 978-1-4842-9025-5 (25 Dec 2022).

   Its copyright line says 2023. The publication dates are in 2022. Therefore metadata resolves 2022 publication, not 2023 copyright, and one author. [Springer/Apress book record](https://link.springer.com/book/10.1007/978-1-4842-9026-2).

   [observed] The supplied “326pp” does not match the publisher-listed 316 numbered pages. Page-count conventions may differ. This research finds no basis for 326. [Springer/Apress book record](https://link.springer.com/book/10.1007/978-1-4842-9026-2).

2. **Primary TOC and chapter locations.** [observed] Springer/Apress lists 13 chapters. Lifecycle-relevant verified chapters: Ch. 2 “Kubernetes API Operations,” pp. 17–55. Ch. 6 “The Client-go Library,” pp. 109–168.

   Ch. 7 “Testing Applications Using Client-go,” pp. 169–191.

   Ch. 10 “Writing Operators with the Controller-Runtime Library,” pp. 231–265. Ch. 11 “Writing the Reconcile Loop,” pp. 267–275. Ch. 12 “Testing the Reconcile Loop,” pp. 277–290.

   [TOC: Ch. 2](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_2); [Ch. 6](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_6); [Ch. 7](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_7); [Ch. 10](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_10); [Ch. 11](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_11); [Ch. 12](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_12). Confidence: high for title/edition/year/author/page count and chapter titles/locations (publisher record and chapter pages).

   Confidence stays limited for full chapter-body detail because most content is subscription-only.

3. **Verified lifecycle coverage; body-access boundary.** [observed] Publisher descriptions say Ch. 2 treats API operations. Ch. 6 presents client-go clients. Ch. 7 is testing client-go applications.

   Ch. 10 covers controller-runtime operators. Ch. 11 covers implementation of the Reconcile function. Ch. 12 tests a reconcile loop.

   The Ch. 11 abstract explicitly says the prior chapter bootstraps an operator. It says this chapter focuses on the Reconcile function.

   [Ch. 2](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_2); [Ch. 6](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_6); [Ch. 7](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_7); [Ch. 10](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_10); [Ch. 11](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_11); [Ch. 12](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_12). [observed] Springer chapter pages expose abstracts/metadata but not full body without purchase/login in this research. This note claims no chapter-level section details beyond the visible evidence.

   [Ch. 11 access page](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_11).

4. **Coverage assessment.** [observed] Clients, API operations, operator implementation, reconciliation, and test tooling are directly in the verified coverage. [Springer/Apress book record](https://link.springer.com/book/10.1007/978-1-4842-9026-2); [TOC](https://link.springer.com/book/10.1007/978-1-4842-9026-2#toc).

   [inference] Accessible chapter titles/abstracts do not verify status publication, finalizer/resource-cleanup specifics, version migration practices, or operator runbook procedures. Do not attribute these topics to the book without full text. [Springer/Apress TOC](https://link.springer.com/book/10.1007/978-1-4842-9026-2#toc). The publisher overview does say clients can create, delete, update, and monitor resources.

   That does not establish reliable lifecycle semantics or safe cleanup. [observed] [Springer/Apress book record](https://link.springer.com/book/10.1007/978-1-4842-9026-2).

## Portable techniques and measured bench checks

These are proposed controller-engineering checks. The book does not prescribe rack operations in verified evidence. Use only a disposable Kubernetes tenant and isolated test target. Do not run live/destructive tests, production eviction, shared-cluster changes, firmware/OS changes, or repeated internet/storage performance tests. [inference] [Book coverage basis](https://link.springer.com/book/10.1007/978-1-4842-9026-2); [Kubernetes API concepts](https://kubernetes.io/docs/concepts/overview/working-with-objects/).

1. **Treat API operations as observed state transitions.** [inference] Build a disposable-resource probe around create/read/update/delete. Record request result, observed object state, resource version, and elapsed time.

   In a measured bench, use synthetic objects. Pass only when the intended transition is observed and evidence is retained. Do not pass merely because the API call returns success.

   The book’s client-go/API-operation scope supports implementation relevance, not any threshold.

   [observed] scope: [Ch. 2](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_2), [Ch. 6](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_6); [inference] proposed check.

2. **Make reconciliation repeatable and idempotent.** [inference] A controller should converge actual state toward declared intent on repeated reconcile. It should handle retries without creating duplicate unmanaged resources.

   Bench a disposable custom resource: submit desired state. Observe convergence. Trigger a harmless second reconcile. Compare owned-resource inventory and status.

   Record completion latency and errors. Do not promote a short check to availability or performance guarantee.

   Reconcile implementation is directly verified as Ch. 11’s focus. Idempotence/check design here is an engineering application.

   [observed] [Ch. 11](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_11); [inference] proposed technique/check.

3. **Test controller behavior at the client boundary and reconcile boundary.** [inference] Use the book’s explicitly verified testing coverage to motivate isolated unit/fake-client tests. Also use it to motivate a disposable API-backed integration check. Distinguish mocked logic from real API behavior.

   Measure assertion outcomes and elapsed time. Retain cluster/API version and test output. A fake-client pass alone is not proof of behavior against the target cluster.

   [observed] Ch. 7 and Ch. 12 titles: [Ch. 7](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_7), [Ch. 12](https://link.springer.com/chapter/10.1007/978-1-4842-9026-2_12); [inference] proposed bench interpretation.

4. **Make cleanup completion explicit; do not infer wipe from deletion.** [inference] For a disposable tenant resource, observe deletion request, object disappearance, dependent-resource disposition, and any asynchronous cleanup completion separately. Report stalled deletion rather than force-removing metadata.

   Do not claim finalizer coverage by this book based on available evidence. Do not treat Kubernetes deletion as data sanitization. For operational behavior use current cluster-version Kubernetes documentation and approved provider/media sanitization procedures.

   [observed] book overview includes create/delete/monitor, but not verified finalizer chapter detail: [Springer/Apress record](https://link.springer.com/book/10.1007/978-1-4842-9026-2); current deletion/finalizer authority: [Kubernetes finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/); [NIST SP 800-88 Rev. 2](https://csrc.nist.gov/pubs/sp/800/88/r2/final).

5. **Pin version context and check compatibility deliberately.** [inference] Record Kubernetes server version, client-go module version, and tested API versions for every measured outcome. Compare against supported skew policy before implementation or rollout. Do not treat this 2022 book as authority for current APIs or the specific cluster.

   Bench uses read-only version discovery and a disposable API test. The bench performs no upgrade or migration.

   [observed] book dates: [Springer/Apress record](https://link.springer.com/book/10.1007/978-1-4842-9026-2); current authority: [Kubernetes version-skew policy](https://kubernetes.io/releases/version-skew-policy/), [client-go compatibility matrix](https://github.com/kubernetes/client-go#compatibility-matrix).

## Canon relation

[inference] This is an optional adapter/controller-engineering appendix, not part of the rack-bench lifecycle canon spine. Use it only if Kubernetes is the actual tenant interface. It teaches client and operator programming. The reviewed publisher descriptions do not establish rack acceptance or offboarding procedures. [observed] scope described by [Springer/Apress book record](https://link.springer.com/book/10.1007/978-1-4842-9026-2); [inference] fit to rack-bench scope in [books.md](../books.md).

Separate the layers: book material is coding implementation guidance. Current Kubernetes documentation, the deployed cluster’s version-specific docs, NVIDIA/operator guidance, and approved site runbooks control operational semantics. Measured rack-bench PASS requires observed evidence, not publisher claims, API object presence, or a controller’s reported status alone. [inference] [Kubernetes documentation](https://kubernetes.io/docs/); [NVIDIA GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/).

## Gaps

- [observed] The O’Reilly platform denies access in this research, and publisher pages restrict chapter-body access. Primary evidence is Springer/Apress catalog data, TOC, chapter metadata and abstracts. [O’Reilly URL](https://learning.oreilly.com/library/view/-/9781484290262/?orm_source=mcp); [publisher book](https://link.springer.com/book/10.1007/978-1-4842-9026-2).
- [inference] Verify full text for exact status handling, finalizers, cleanup, resource ownership, and version-change coverage. Do this before attributing those specific mechanics to the book. [Publisher TOC](https://link.springer.com/book/10.1007/978-1-4842-9026-2#toc).
- [inference] The book and available public metadata cannot establish current Kubernetes API behavior, cluster-specific compatibility, or NVIDIA GPU operator/device-plugin behavior. They cannot establish rack acceptance thresholds. Confirm against version-matched official docs and local approved procedures before any operational action. [Kubernetes version policy](https://kubernetes.io/releases/version-skew-policy/); [NVIDIA GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/).
- [inference] Proposed disposable tests check interface behavior only. They do not establish production safety or media sanitization. [Publisher scope](https://link.springer.com/book/10.1007/978-1-4842-9026-2); [NIST Rev. 2](https://csrc.nist.gov/pubs/sp/800/88/r2/final).
