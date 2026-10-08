"""Endpoint-scoped TCP observations around transfer windows, and idle DF probes."""
from contextvars import copy_context
import json
import os
import re
import socket
import subprocess
import threading

from rack_bench.common.host import Unavailable, _echo, run_command
from rack_bench.common.models import Check
from .targets import reason, targets


def parse_ss(text, pid=None):
    """Keep socket identity and cumulative *data* segments, not ACK segments.

    ss omits retrans when zero; data_segs_out is mandatory. snd_wnd is the
    peer's advertised window; rcv_space is NOT an advertised receive window.
    """
    result, identity, owned = {}, None, False
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] in {"ESTAB", "CLOSE-WAIT", "FIN-WAIT-1", "FIN-WAIT-2"}:
            identity = " ".join(fields[3:5]) if len(fields) >= 5 else None
            owned = pid is None or f"pid={pid}," in line
        elif identity and owned:
            segments = re.search(r"\bdata_segs_out:(\d+)", line)
            if not segments:
                continue
            retrans = re.search(r"\bretrans:\d+/(\d+)", line)
            rtt = re.search(r"\brtt:([\d.]+)/", line)
            window = re.search(r"\bsnd_wnd:(\d+)", line)
            receive_window = re.search(r"\brcv_wnd:(\d+)", line)
            result[identity] = {"segments": int(segments[1]),
                                "retransmits": int(retrans[1]) if retrans else 0,
                                "rtt_ms": float(rtt[1]) if rtt else None,
                                "window_bytes": int(window[1]) if window else None,
                                "receive_window_bytes": int(receive_window[1]) if receive_window else None}
    return result


def tcp_deltas(snapshots):
    previous, segments, retransmits, observations = {}, 0, 0, []
    for snapshot in snapshots:
        for identity, current in snapshot.items():
            old = previous.get(identity)
            # Never assume the first observed counters started at zero.
            if old is not None:
                ds = current["segments"] - old["segments"]
                dr = current["retransmits"] - old["retransmits"]
                if ds >= 0 and dr >= 0:
                    segments += ds
                    retransmits += dr
            observations.append(current)
        previous = snapshot
    return {"segments": segments, "retransmits": retransmits,
            "ratio_pct": 100 * retransmits / segments if segments else None,
            "observations": observations}


class TCPWindow:
    """Poll live sockets: the client closes connections after every request.

    Only deltas between two sightings of an owned socket count. Short-lived
    sockets may escape polling; this is an observed subset, never host counters.
    """
    def __init__(self, host, *, command=run_command, interval=0.2):
        self.host, self.command, self.interval = host, command, interval
        self.stop = threading.Event()
        self.snapshots, self.sources, self.errors = [], [], []
        self.thread = None

    def sample(self):
        try:
            text = self.command(self.args, timeout=2)
            self.snapshots.append(parse_ss(text, os.getpid()))
        except Unavailable as exc:
            self.errors.append(exc.detail)
            self.stop.set()

    def __enter__(self):
        try:
            addresses = sorted({item[4][0] for item in socket.getaddrinfo(
                self.host, 443, socket.AF_INET, socket.SOCK_STREAM)})
            expression = "( " + " or ".join(f"dst {ip}" for ip in addresses) + " )"
            self.args = ["ss", "-4tinpH", expression]
            self.sources.append(" ".join(self.args))
            self.sample()
            def poll():
                while not self.stop.wait(self.interval):
                    self.sample()
            self.thread = threading.Thread(target=copy_context().run, args=(poll,), daemon=True)
            self.thread.start()
        except OSError as exc:
            self.errors.append(reason(exc))
        return self

    def __exit__(self, *args):
        self.stop.set()
        if self.thread:
            self.thread.join()
            self.sample()
        self.detail = tcp_deltas(self.snapshots)
        self.detail.update(sources=self.sources, errors=self.errors,
                           snapshot_count=len(self.snapshots),
                           coverage="deltas only for owned IPv4 endpoint sockets seen twice; short-lived sockets may be missed")


def parse_ping(text):
    if re.search(r"\b[1-9]\d* (?:packets )?received", text):
        return "pass"
    if re.search(r"[Ff]rag needed|[Mm]essage too long|mtu[= ]", text):
        return "too_large"
    if re.search(r"\b0 (?:packets )?received|100% packet loss", text):
        return "timeout"
    return "unavailable"


def ping_command(args, *, timeout, ok_codes):
    # ping reports local EMSGSIZE/MTU errors on stderr; preserve those findings.
    source = " ".join(args)
    _echo(source)
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=timeout, env={**os.environ, "LC_ALL": "C"})
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unavailable(source, str(exc)) from exc
    if result.returncode not in (*ok_codes, 2):
        raise Unavailable(source, f"ping exited {result.returncode}: {result.stdout.strip()}")
    return result.stdout.strip()


def pmtud_probe(provider, options, *, command=ping_command):
    name = f"internet.{provider}.tcp.pmtud"
    try:
        selected = targets(provider, options)
    except ValueError as exc:
        return Check(name, "skip", detail=reason(exc))
    records, sources = [], []
    for target in selected:
        record = dict(target, runs_detail=[])
        records.append(record)
        if target["reason"]:
            continue
        for _ in range(target["runs"]):
            samples = []
            for size in (1200, 1400, 1472):
                args = ["ping", "-4", "-n", "-M", "do", "-c", "2", "-W", "1", "-s", str(size), target["host"]]
                sources.append(" ".join(args))
                try:
                    text = command(args, timeout=5, ok_codes=(0, 1))
                    samples.append({"payload": size, "result": parse_ping(text), "raw": text})
                except Unavailable as exc:
                    samples.append({"payload": size, "result": "unavailable", "reason": exc.detail})
            passing = [s["payload"] for s in samples if s["result"] == "pass"]
            largest = max(passing) if passing else None
            stalled = any(s["result"] == "timeout" and largest is not None and s["payload"] > largest for s in samples)
            record["runs_detail"].append({"samples": samples, "largest_payload": largest,
                                          "finding": "1500 MTU clean" if largest == 1472 else
                                          "possible PMTUD blackhole (larger DF probes stall)" if stalled else
                                          "explicit MTU limit" if any(s["result"] == "too_large" for s in samples) else
                                          "ICMP unavailable; cannot infer a blackhole"})
    values = [r["largest_payload"] for r in records[0]["runs_detail"] if r["largest_payload"] is not None]
    detail = {"regions": records}
    if not values:
        detail["reason"] = records[0]["reason"] or "no passing DF probe; ICMP may be filtered"
    return Check(name, "pass" if values else "skip", min(values) if values else None,
                 detail=json.dumps(detail), source=sources)


def retransmit_probe(provider, options):
    name = f"internet.{provider}.tcp.retransmit_ratio"
    try:
        targets(provider, options)
    except ValueError as exc:
        return Check(name, "skip", detail=reason(exc))
    state = getattr(options, "_transfer_reports", {}).get(provider, {})
    regions = [{"direction": direction, "region": region["region"], "band": region["band"],
                "windows": [run["tcp"] for run in region.get("runs_detail", []) if "tcp" in run]}
               for direction in ("up", "down") for region in state.get(direction, [])]
    windows = [window for region in regions if region["band"] == "nearest" for window in region["windows"]]
    segments = sum(w["segments"] for w in windows)
    retransmits = sum(w["retransmits"] for w in windows)
    ratio = 100 * retransmits / segments if segments else None
    detail = {"regions": regions, "segments": segments, "retransmits": retransmits,
              "selection": "nearest/overridden band; light-band counters retained separately",
              "finding": "good (<0.5%)" if ratio is not None and ratio < .5 else
                         "high (>1%); bad on a clean path" if ratio is not None and ratio > 1 else "intermediate",
              "scope": "outbound data retransmits observed during upload/download/single-stream; remote download sender counters unavailable"}
    if ratio is None:
        detail["reason"] = "needs upload/download transfer windows with observable ss data-segment deltas"
    return Check(name, "pass" if ratio is not None else "skip", ratio, detail=json.dumps(detail),
                 source=list(dict.fromkeys(s for r in regions for w in r["windows"] for s in w["sources"])))
