"""Endpoint-scoped TCP observations around transfer windows, and idle DF probes."""
from contextvars import copy_context
from collections import Counter
import json
import os
import re
import socket
import subprocess
import threading
from statistics import median

from rack_bench.common.host import Unavailable, _echo, run_command
from rack_bench.common.models import Check
from .targets import reason, targets

LIMIT_FIELDS = ("busy", "rwnd_limited", "cwnd_limited", "sndbuf_limited")
_DURATION_UNITS = {"us": .001, "µs": .001, "usec": .001, "ms": 1.0, "sec": 1000.0, "s": 1000.0}
_RATE_UNITS = {"k": 1e3, "m": 1e6, "g": 1e9, "t": 1e12}
_LIMIT_TOKEN = r"(\d+(?:\.\d+)?)(usec|µs|ms|sec|us|s|%)?(?:\((\d+(?:\.\d+)?)%\))?"


def _duration_ms(token):
    """Milliseconds from one ss duration token (123ms, 456us, 7.5sec); None if malformed."""
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(us|µs|usec|ms|sec|s)", token)
    return float(match[1]) * _DURATION_UNITS[match[2]] if match else None


def socket_limits(line):
    """Per-socket limit shares (percent) plus delivery_rate_bps and cwnd.

    ss -ti prints busy/rwnd_limited/cwnd_limited/sndbuf_limited (Linux 4.10+
    tcp_info time shares) only when nonzero, as durations with the share of
    busy time in parentheses; some iproute2 releases print percent tokens
    instead. An absent flag is zero, never an invented measurement. busy is a
    duration, not a share: a nonzero busy time marks a fully busy socket (the
    kernel exports no socket-lifetime share). A duration without a printed
    share and without a usable busy denominator stays 0. Unparseable tokens
    stay zero/None: parsing is defensive across iproute2 releases, never fatal.
    delivery_rate carries an optional k/M/G/T scale (plain under ss -n).
    """
    def field(name):
        return re.search(rf"\b{name}:{_LIMIT_TOKEN}", line)

    busy = field("busy")
    if not busy:
        busy_pct, busy_ms = 0.0, None
    elif busy[2] == "%":
        busy_pct, busy_ms = float(busy[1]), None
    else:
        busy_ms = _duration_ms(busy[1] + (busy[2] or "ms"))
        busy_pct = 100.0 if busy_ms else 0.0

    def share(match):
        if match is None:
            return 0.0
        if match[3] is not None:
            return float(match[3])
        if match[2] == "%":
            return float(match[1])
        span = _duration_ms(match[1] + (match[2] or "ms"))
        return 100.0 * span / busy_ms if span is not None and busy_ms else 0.0

    rate = re.search(r"\bdelivery_rate\s+(\d+(?:\.\d+)?)([kKmMgGtT])?(?:bps|b/s)", line)
    cwnd = re.search(r"\bcwnd:(\d+)", line)
    return {"busy_pct": busy_pct,
            "rwnd_limited_pct": share(field("rwnd_limited")),
            "cwnd_limited_pct": share(field("cwnd_limited")),
            "sndbuf_limited_pct": share(field("sndbuf_limited")),
            "delivery_rate_bps": float(rate[1]) * _RATE_UNITS.get((rate[2] or "").lower(), 1.0) if rate else None,
            "cwnd": int(cwnd[1]) if cwnd else None}


def parse_ss(text, pid=None):
    """Keep socket identity and cumulative *data* segments, not ACK segments.

    ss omits retrans when zero; data_segs_out is mandatory. snd_wnd is the
    peer's advertised window; rcv_space is NOT an advertised receive window.
    pid scopes ownership: an int, any iterable of ints (e.g. the benchmark
    process plus worker-process pids), or None for no pid filter.
    """
    result, identity, owned = {}, None, False
    wanted = None if pid is None else ({pid} if isinstance(pid, int) else {int(value) for value in pid})
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] in {"ESTAB", "CLOSE-WAIT", "FIN-WAIT-1", "FIN-WAIT-2"}:
            identity = " ".join(fields[3:5]) if len(fields) >= 5 else None
            owned = wanted is None or any(f"pid={candidate}," in line for candidate in wanted)
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
                                "receive_window_bytes": int(receive_window[1]) if receive_window else None,
                                **socket_limits(line)}
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


def dominant_limit(entry):
    """The largest socket limiter, or busy/clean when no limiter is reported."""
    shares = [(entry.get(f"{name}_pct") or 0.0, name)
              for name in ("rwnd_limited", "cwnd_limited", "sndbuf_limited")]
    top = max(shares)
    if top[0] > 0:
        return top[1]
    return "busy" if entry.get("busy_pct") else "clean"


def limit_ticks(snapshots):
    """One row per sample tick that observed owned sockets: medians of the
    per-socket limit shares (percent), median delivery rate and cwnd, and the
    socket count per dominant limit state. Ticks with no owned socket stay
    absent; no share is ever invented for an unseen socket."""
    rows = []
    for snapshot in snapshots:
        entries = list(snapshot.values())
        if not entries:
            continue
        row = {"sockets": len(entries),
               **{f"{name}_pct": median([entry.get(f"{name}_pct") or 0.0 for entry in entries])
                  for name in LIMIT_FIELDS},
               "dominant_states": dict(Counter(dominant_limit(entry) for entry in entries))}
        rates = [entry["delivery_rate_bps"] for entry in entries if entry.get("delivery_rate_bps") is not None]
        windows = [entry["cwnd"] for entry in entries if entry.get("cwnd") is not None]
        if rates:
            row["delivery_rate_bps"] = median(rates)
        if windows:
            row["cwnd"] = median(windows)
        rows.append(row)
    return rows


def limit_stats(ticks):
    """Window aggregate over ticks: the median of each per-tick median plus
    socket-tick counts per dominant state. Shares are percent of socket busy
    time (kernel lifetime counters on pooled connections); delivery_rate_bps
    and cwnd are the kernel's own estimates, not derived rates."""
    if not ticks:
        return {"ticks": 0,
                "reason": "no sample tick observed an owned socket; limit shares unavailable",
                "semantics": "shares of socket busy time in percent; busy_pct is 100 when ss reports any busy time"}
    states = Counter()
    for tick in ticks:
        states.update(tick["dominant_states"])
    result = {"ticks": len(ticks),
              **{f"{name}_pct_median": median([tick[f"{name}_pct"] for tick in ticks])
                 for name in LIMIT_FIELDS},
              "sockets_per_dominant_state": dict(states),
              "dominant_state": max(states, key=states.get),
              "semantics": "shares of socket busy time in percent; busy_pct is 100 when ss reports any busy time"}
    for field in ("delivery_rate_bps", "cwnd"):
        values = [tick[field] for tick in ticks if field in tick]
        if values:
            result[f"{field}_median"] = median(values)
    return result


class TCPWindow:
    """Poll live sockets: the client closes connections after every request.

    Only deltas between two sightings of an owned socket count. Short-lived
    sockets may escape polling; this is an observed subset, never host counters.
    pids is an optional callable returning the pids whose sockets are owned
    (the benchmark process plus any worker processes); by default only this
    process's sockets are owned.
    """
    def __init__(self, host, *, command=run_command, interval=0.2, pids=None):
        self.host, self.command, self.interval = host, command, interval
        self._pids = pids or (lambda: {os.getpid()})
        self.stop = threading.Event()
        self.snapshots, self.sources, self.errors = [], [], []
        self.thread = None

    def sample(self):
        try:
            text = self.command(self.args, timeout=2)
            self.snapshots.append(parse_ss(text, self._pids()))
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
        self.detail.update(limits=limit_stats(limit_ticks(self.snapshots)),
                            sources=self.sources, errors=self.errors,
                            snapshot_count=len(self.snapshots), owned_pids=sorted(self._pids()),
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
