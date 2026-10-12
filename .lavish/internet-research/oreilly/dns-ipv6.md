# N06 — DNS and BIND on IPv6

Research date: 2026-10-11. Researcher: oreilly-dns-ipv6-N06.

## Identity and evidence correction

Supplied central catalog metadata: Cricket Liu, O'Reilly, 2011, 52 pages, ISBN 9781449308025.
The first researcher reply presents May 2011 catalog metadata as observed.
The follow-up limits independently checked public evidence to indexed title and chapter descriptions.
Direct public O'Reilly fetches return permission denial.
Keep the central catalog metadata. Do not call it independently verified through a successful public fetch.
A secondary PDF search record gives print ISBN 9781449305192. Format-specific confirmation remains limited.

## Five chapters — public indexed contents

1. DNS and IPv6: IPv6 addresses, AAAA, ip6.arpa, and forward/reverse mapping.
2. BIND on IPv6: listeners, clients, protocol selection, ACLs, delegation, and control.
3. Resolver Configuration: host resolver setup, DHCPv6, and router advertisements.
4. DNS64: synthesis, DNSSEC interaction, and reverse mapping.
5. Troubleshooting: nslookup and dig.

The public indexed cover and Chapter 1 pages show all five titles.
The researcher does not read the full book through the catalog.

## Terms and modern primary evidence

AAAA data, DNS transport over IPv6, and application traffic over IPv6 are different concepts.
An AAAA answer does not prove an IPv6 DNS transport or application connection.
RFC 10001 defines IPv6-reachable name servers separately from DNS data.
It replaces RFC 3901 and gives mixed-family operational guidance.
RFC 9715 gives informational fragmentation-avoidance guidance. It does not give a universal certification gate.
Its recommended maximum DNS/UDP payload is 1400 bytes. Smaller limits can apply.

## Proposed bench techniques — inferences

1. Compare A and AAAA outcomes for the same artifact host. Keep NODATA separate from NXDOMAIN and SERVFAIL.
2. Compare identical queries through each available resolver transport family.
   Example: `dig -4 @<resolver-v4> host A` and `dig -6 @<resolver-v6> host A`.
3. Test application connections separately by address family when both addresses exist.
   Happy Eyeballs can hide an IPv6 failure through successful IPv4 fallback.
4. Compare controlled large-response UDP behavior with TCP behavior over each family.
   Record truncation, retries, timeouts, and completion. Correct TCP fallback is not a failure.
5. Check DNS64 only when IPv6-only/NAT64 represents the production environment.
   A synthesized AAAA answer does not prove native destination IPv6.

These checks do not require reverse DNS on all endpoints.
A large DNS response test does not prove PMTUD behavior for the bulk-transfer path.
Keep resolver, query type, transport family, timestamp, response code, answer, and timing for every sample.

## Canon verdict

Add a new optional IPv6-DNS supplement. Keep the spine unchanged.
Read chapters 1 and 5. Read chapter 4 only when DNS64 applies.
Use current RFCs, not 2011 BIND recipes, for present transport policy.

## Gaps

Direct public metadata and full-text access remain unverified.
The book does not establish encrypted-DNS, present TLS/QUIC, or statistical resolver-certification procedures.
The two-hour run establishes observed DNS behavior, not long-term resolver reliability.

## Sources

- [Central Learning record](https://learning.oreilly.com/library/view/-/9781449308025/?orm_source=mcp).
- [Public indexed cover](https://www.oreilly.com/library/view/dns-and-bind/9781449308025/cover.html).
- [Public indexed Chapter 1](https://www.oreilly.com/library/view/dns-and-bind/9781449308025/ch01.html).
- [Public indexed preface](https://www.oreilly.com/library/view/dns-and-bind/9781449308025/pr02.html).
- [RFC 10001](https://www.rfc-editor.org/rfc/rfc10001).
- [RFC 9715](https://www.rfc-editor.org/rfc/rfc9715).
- [RFC 8305](https://www.rfc-editor.org/rfc/rfc8305).
- [RFC 6147](https://www.rfc-editor.org/rfc/rfc6147).

The orchestrator fetches RFCs 10001 and 9715. It checks the decisive transport and fragmentation passages.
