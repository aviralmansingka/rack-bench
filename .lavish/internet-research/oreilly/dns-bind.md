# N04 — DNS and BIND editions

Research date: 2026-10-11. Researcher: oreilly-dns-bind-N04.

## Edition and access

Cricket Liu and Paul Albitz, fifth edition, O'Reilly, May 2006, 640 pages.
ISBN 0596100574 / 9780596100575.
The overview names BIND 9.3.2 and BIND 8.4.7.
The researcher checks the Learning catalog and reports visible metadata and contents.
The orchestrator's Learning fetch redirects to a permission-denied page.
Keep this access difference visible. Do not claim universal public catalog access or full-text entitlement.
The researcher finds no authoritative sixth-edition listing. This is a bounded search result.

## Complete fifth-edition chapter titles — researcher catalog check

1. Background
2. How Does DNS Work?
3. Where Do I Start?
4. Setting Up BIND
5. DNS and Electronic Mail
6. Configuring Hosts
7. Maintaining BIND
8. Growing Your Domain
9. Parenting
10. Advanced Features
11. Security
12. nslookup and dig
13. Reading BIND Debugging Output
14. Troubleshooting DNS and BIND
15. Programming with the Resolver and Nameserver Library Routines
16. Architecture
17. Miscellaneous

Appendices: A. DNS Message Format and Resource Records; B. BIND Compatibility Matrix;
C. Compiling and Installing BIND on Linux; D. Top-Level Domains;
E. BIND Nameserver and Resolver Configuration.

Read Chapters 2, 6, and 12–14 first. Use Chapters 10–11 for EDNS and security context.
Resolver caching, delegation, and query tools help explain object-store setup failures.
Do not copy 2006 BIND configuration into current production systems without current documentation.

## Proposed bench techniques — inferences

1. Record the resolver address, query name, record type, response code, and query duration.
2. Keep NXDOMAIN, NODATA, SERVFAIL, and timeouts separate.
3. Compare controlled warm and cold names. Client cache flushing does not prove recursive-cache coldness.
4. Compare UDP and TCP queries. Keep EDNS settings and response sizes with results.
5. Check authoritative and recursive answers when delegation or validation symptoms appear.

Example: a warm recursive answer can hide a slow authoritative path.
Use a controlled name to test that path. Record cache assumptions.
DNS success does not prove IPv6 application reachability or sustained object-transfer rate.

## Verdict and gaps

Add an optional DNS SKIM. Keep the four-book spine unchanged.
Chapters 12–14 have the closest diagnostic fit.
The old BIND versions require current operational and security documentation.
The orchestrator cannot reproduce the researcher's direct catalog access.

## Sources

- [Learning catalog](https://learning.oreilly.com/library/view/dns-and-bind/0596100574).
- [Supplied Learning URL](https://learning.oreilly.com/library/view/-/0596100574/?orm_source=mcp).
- [O'Reilly catalog](https://www.oreilly.com/library/view/dns-and-bind/0596100574/).
