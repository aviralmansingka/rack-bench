"""Idle IPv4 path context and configured-resolver DNS observations.

Detail is JSON inside the established string field; raw tool reports and all
regional samples therefore survive the existing run-dir artifact writer.
"""
import ipaddress
import json
import math
import os
import re
import shlex
import shutil
import socket
import struct
import subprocess
import time
from pathlib import Path
from secrets import randbelow, token_hex
from statistics import fmean

from rack_bench.common.host import _echo
from rack_bench.common.models import Check
from .stats import describe
from .targets import reason, targets

# Chennai-origin references: docs/internet-performance.md § regional RTTs.
RTT_BANDS = {"ap-south-1": (20, 35), "ap-southeast-1": (35, 55), "us-east-1": (180, 250)}


def parse_mtr(text):
    """Parse wide report rows from the right; hostnames may contain spaces/ASNs."""
    hops = []
    for line in text.splitlines():
        match = re.match(r"\s*(\d+)\.\|?--?\s*(.*)", line)
        if not match:
            match = re.match(r"\s*(\d+)\.\s+(.*)", line)
        if not match:
            continue
        number, row = match.groups()
        columns = row.rsplit(None, 7)
        if len(columns) != 8:
            continue
        host, loss, sent, last, avg, best, worst, stdev = columns
        try:
            values = [float(value.rstrip("%")) for value in (loss, last, avg, best, worst, stdev)]
            sent = int(sent)
        except ValueError:
            continue
        if not 0 <= values[0] <= 100 or sent <= 0 or any(not math.isfinite(value) or value < 0 for value in values):
            continue
        asns = re.findall(r"\bAS(?:\d+|\?+)\b", host)
        host = re.sub(r"\bAS(?:\d+|\?+)(?:\s+|$)", "", host).strip()
        lost = values[0] == 100
        hops.append({"hop": int(number), "host": host, "asns": [a for a in asns if a[2:].isdigit()],
                     "loss_percent": values[0], "sent": sent,
                     **{key: None if lost else value for key, value in zip(
                         ("last_ms", "avg_ms", "best_ms", "worst_ms", "stdev_ms"), values[1:])}})
    return hops


def parse_traceroute(text):
    """Keep unanswered hops; traceroute RTTs are not an mtr loss estimate."""
    hops = []
    for line in text.splitlines():
        match = re.match(r"\s*(\d+)\s+(.+)", line)
        if not match:
            continue
        number, row = match.groups()
        samples = [float(value) for value in re.findall(r"(\d+(?:\.\d+)?)\s*ms\b", row)]
        if not samples and "*" not in row:
            continue
        hops.append({"hop": int(number), "host": row, "asns": re.findall(r"\bAS\d+\b", row),
                     "loss_percent": None, "timeouts": row.count("*"), "rtt_samples_ms": samples,
                     "avg_ms": fmean(samples) if samples else None, "stdev_ms": None})
    return hops


def _path_reports(provider, options, run, which, resolve):
    records, sources = [], []
    for target in targets(provider, options):
        record = dict(target, reports=[])
        records.append(record)
        if target["reason"]:
            continue
        tool = which("mtr") or which("traceroute")
        if not tool:
            record["reason"] = "missing tools: mtr and traceroute"
            continue
        try:
            record["addresses"] = sorted({row[4][0] for row in resolve(
                target["host"], 443, socket.AF_INET, socket.SOCK_STREAM)})
        except OSError:
            record["addresses"] = []  # Tool may still resolve; do not invent destination RTT.
        # Pin the resolved IPv4 address so DNS rotation cannot invalidate the
        # destination match between our lookup and the tool's own lookup.
        destination = record["addresses"][0] if record["addresses"] else target["host"]
        mtr = Path(tool).name == "mtr"
        command = ([tool, "-4", "-r", "-w", "-z", "-b", "-s", "100", "-c", "10", destination]
                   if mtr else [tool, "-4", "-A", "-q", "3", "-w", "1", "-m", "30", destination])
        sources.append(shlex.join(command))
        for _ in range(target["runs"]):
            try:
                _echo(shlex.join(command))
                result = run(command, capture_output=True, text=True, timeout=120, check=False,
                             env={**os.environ, "LC_ALL": "C"})
                report = {"tool": "mtr" if mtr else "traceroute", "stdout": result.stdout,
                          "stderr": result.stderr, "returncode": result.returncode,
                          "hops": (parse_mtr if mtr else parse_traceroute)(result.stdout)}
                if result.returncode or not report["hops"]:
                    report["reason"] = "path tool failed or returned no parseable hops"
            except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
                report = {"hops": [], "reason": f"path tool unavailable: {type(exc).__name__}"}
            record["reports"].append(report)
    return records, sources


def path_probe(provider, metric, options, *, run=subprocess.run, which=shutil.which,
               resolve=socket.getaddrinfo):
    name = f"internet.{provider}.path.{metric}"
    # Three registry entries share one idle audit, scoped to this collection's Options.
    cache = options.__dict__.setdefault("_path_reports", {})
    try:
        if provider not in cache:
            cache[provider] = _path_reports(provider, options, run, which, resolve)
        records, sources = cache[provider]
    except ValueError as exc:
        return Check(name, "skip", detail=reason(exc))
    primary = records[0]
    reports = primary["reports"]
    detail = {"regions": records, "interpretation": "Context only; intermediate loss with clean continuation is ICMP rate limiting. "
              "Unanswered hops still count; a single snapshot cannot establish route flapping.",
              "rtt_reference": "Chennai-origin bands, not location-independent certification thresholds"}
    status, value = "pass", None
    failure = primary["reason"] or next((r.get("reason") for r in reports if r.get("reason")), None)
    if not failure:
        hops = reports[0]["hops"]
        if metric == "hops":
            value = max(h["hop"] for h in hops)
        elif metric == "as_path":
            if not any(h["asns"] for h in hops):
                failure = "ASN annotations unavailable from path tool"
            else:
                value = " -> ".join(
                    f'{h["hop"]}:{",".join(h["asns"]) or "?"}' for h in hops)
        else:
            findings, primary_findings = [], []
            for region in records:
                band = RTT_BANDS.get(region["region"]) if provider == "s3" else None
                for report in region["reports"]:
                    if report.get("reason") or not report["hops"]:
                        continue
                    final = report["hops"][-1]
                    # Never grade the last answering transit router as the destination.
                    addresses = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", final["host"])
                    reached = bool(set(addresses) & set(region.get("addresses", [])))
                    report["destination_confirmed"] = reached
                    if not reached:
                        report["rtt_reason"] = "destination address not confirmed by tool"
                    if band and reached and final["avg_ms"] is not None:
                        rtt = final["avg_ms"]
                        finding = f'{region["region"]}: {rtt:g} ms (reference {band[0]}-{band[1]} ms)'
                        findings.append(finding)
                        if region is primary:
                            primary_findings.append(finding)
                        if not band[0] <= rtt <= band[1]:
                            status = "warn"
            detail["rtt_findings"] = findings
            value = "; ".join(primary_findings) or None
            if value is None:
                failure = "RTT ungradable: no confirmed destination RTT with a supported regional band"
    if failure:
        status, value = "skip", None
        detail["reason"] = failure
    return Check(name, status, value=value, detail=json.dumps(detail), source=sources)


def _dns_name_end(packet, offset):
    """Skip an encoded DNS name without following compression pointers."""
    while True:
        length = packet[offset]
        offset += 1
        if length == 0:
            return offset
        if length & 0xC0 == 0xC0:
            if offset >= len(packet):
                raise ValueError("truncated DNS pointer")
            return offset + 1
        if length > 63:
            raise ValueError("invalid DNS label")
        offset += length


def _dns_answers(packet, ident, question):
    if len(packet) < 12:
        raise ValueError("truncated DNS header")
    response_id, flags, questions, answers, _, _ = struct.unpack("!6H", packet[:12])
    if response_id != ident or not flags & 0x8000 or flags & 0x7800 or questions != 1:
        raise ValueError("invalid DNS response header")
    offset = _dns_name_end(packet, 12) + 4
    if packet[12:offset].lower() != question.lower():
        raise ValueError("DNS question mismatch")
    records = []
    for _ in range(answers):
        offset = _dns_name_end(packet, offset)
        kind, cls, ttl, size = struct.unpack_from("!HHIH", packet, offset)
        offset += 10
        data = packet[offset:offset + size]
        if len(data) != size:
            raise ValueError("truncated DNS record")
        if cls == 1 and kind in (1, 28):
            family = socket.AF_INET if kind == 1 else socket.AF_INET6
            if size != (4 if kind == 1 else 16):
                raise ValueError("invalid DNS address size")
            records.append({"address": socket.inet_ntop(family, data),
                            "family": "IPv4" if kind == 1 else "IPv6", "ttl": ttl})
        offset += size
    return {"rcode": flags & 15, "answers": records, "truncated": bool(flags & 0x200)}


def resolve_dns(host, kind="A"):
    """Query the first configured IPv4 nameserver, preserving NXDOMAIN vs SERVFAIL.

    No public-resolver fallback, search suffix, cache flush, or synthetic answers.
    A local stub (e.g. systemd-resolved) remains the configured resolver.
    UDP truncation retries over TCP to that same IPv4 resolver.
    """
    servers = []
    for line in Path("/etc/resolv.conf").read_text().splitlines():
        words = line.split()
        if len(words) >= 2 and words[0] == "nameserver":
            try:
                if ipaddress.ip_address(words[1]).version == 4:
                    servers.append(words[1])
            except ValueError:
                continue
    if not servers:
        raise OSError("no configured IPv4 DNS resolver in /etc/resolv.conf")
    ident = randbelow(65536)
    labels = host.rstrip(".").encode("ascii").split(b".")
    if any(not 0 < len(label) <= 63 for label in labels):
        raise ValueError("invalid DNS hostname")
    question = b"".join(bytes([len(label)]) + label for label in labels) + b"\0"
    question += struct.pack("!HH", {"A": 1, "AAAA": 28}[kind], 1)
    packet = struct.pack("!6H", ident, 0x100, 1, 0, 0, 0) + question
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(3)
        sock.connect((servers[0], 53))
        sock.send(packet)
        response = sock.recv(65535)
    try:
        # TC responses may truncate mid-record: inspect the header before parsing.
        if len(response) >= 12 and struct.unpack_from("!H", response, 2)[0] & 0x200:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                sock.connect((servers[0], 53))
                sock.sendall(struct.pack("!H", len(packet)) + packet)

                def read_exact(size):
                    data = bytearray()
                    while len(data) < size:
                        block = sock.recv(size - len(data))
                        if not block:
                            raise ValueError("truncated DNS TCP response")
                        data.extend(block)
                    return bytes(data)

                response = read_exact(struct.unpack("!H", read_exact(2))[0])
        result = _dns_answers(response, ident, question)
    except (IndexError, struct.error) as exc:
        raise ValueError("malformed DNS response") from exc
    if result.pop("truncated"):
        raise ValueError("truncated DNS TCP response")
    return dict(result, resolver=servers[0])


def dns_probe(provider, options, *, resolver=resolve_dns, clock=time.perf_counter, repeats=5):
    name = f"internet.{provider}.dns.resolve"
    try:
        selected = targets(provider, options)
    except ValueError as exc:
        return Check(name, "skip", detail=reason(exc))
    records, sources, interception = [], [], False

    def lookup(host, kind):
        _echo(f"configured resolver: {kind} {host}")
        start = clock()
        try:
            answer = resolver(host, kind)
            return dict(answer, ms=(clock() - start) * 1000)
        except (OSError, ValueError) as exc:
            return {"error": f"{type(exc).__name__}: {exc}", "ms": (clock() - start) * 1000}

    for target in selected:
        record = dict(target, runs_detail=[])
        records.append(record)
        if target["reason"]:
            continue
        sources.append(f'configured resolver: A {target["host"]} (IPv4-only endpoint selection)')
        for _ in range(target["runs"]):
            samples = [lookup(target["host"], "A") for _ in range(repeats + 1)]
            trap = f"rack-bench-{token_hex(8)}.invalid"
            traps = {kind: lookup(trap, kind) for kind in ("A", "AAAA")}
            sources.append(f"configured resolver: A/AAAA {trap}")
            interception |= any(t.get("answers") for t in traps.values())
            valid = all(s.get("rcode") == 0 and any(a.get("family") == "IPv4" for a in s.get("answers", []))
                        for s in samples)
            valid &= all(t.get("rcode") == 3 and not t.get("answers") for t in traps.values())
            record["runs_detail"].append({"samples": samples, "first_ms": samples[0]["ms"],
                                          "cached_ms": describe([s["ms"] for s in samples[1:]]),
                                          "trap": trap, "trap_answers": traps, "valid": valid})
    primary = records[0]
    valid = bool(primary["runs_detail"]) and all(r["valid"] for r in primary["runs_detail"])
    detail = {"regions": records, "interception": bool(interception),
              "cache_state": "first observed lookup; upstream cache state unknown, repeated queries do not prove a cache hit",
              "families": sorted({a["family"] for r in records for run in r["runs_detail"]
                                  for sample in run["samples"] for a in sample.get("answers", [])}), "ipv6": "AAAA queried only for .invalid interception, never socket selection"}
    if not valid or interception:
        detail["reason"] = ("DNS interception: .invalid returned invented addresses" if interception else
                            primary["reason"] or "DNS ungradable: endpoint failure or .invalid did not return NXDOMAIN")
    return Check(name, "pass" if valid and not interception else "skip",
                 value=primary["runs_detail"][0]["first_ms"] if valid and not interception else None,
                 detail=json.dumps(detail), source=sources)
