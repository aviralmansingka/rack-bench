"""Shared transfer windows and sustained/single-stream upload policy.

The options-local report is also the download manifest. No dependent check
starts a hidden upload. All owned keys survive until the collection finalizer.
"""
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
import json
import math
import threading
import time

from rack_bench.common.host import _echo
from rack_bench.common.models import Check
from .latency import OBJECT_SIZE as LATENCY_SIZE, timing_sample
from .s3client import S3Client, S3Error, ProtocolError, SeededPayload
from .stats import describe, windows
from .targets import reason, run_prefix, targets
from .tcp import TCPWindow

MIB = 1024 ** 2
OBJECT_SIZE = 1024 * MIB
PART_SIZE = 8 * MIB
LIGHT_SIZE = 32 * MIB
ERRORS = (S3Error, ValueError, OSError)


class _WindowEnded(S3Error):
    """Normal part-boundary stop; multipart_upload aborts the known upload ID."""


def sample_timing(timing, size, direction):
    fields = {"connect_ms": timing.connect_seconds,
              "response_first_byte_ms": timing.response_first_byte_seconds,
              "headers_ms": timing.headers_seconds, "total_ms": timing.elapsed_seconds}
    values = list(fields.values())
    if (any(v is None or not math.isfinite(v) or v < 0 for v in values) or
            values != sorted(values) or values[-1] <= 0 or timing.attempts != 1):
        raise ProtocolError("invalid transfer timing/order or retried measurement", timing=timing)
    if timing.first_byte_seconds is not None:
        if not values[2] <= timing.first_byte_seconds <= values[-1]:
            raise ProtocolError("invalid body-first-byte timing", timing=timing)
        fields["body_first_byte_ms"] = timing.first_byte_seconds
    elif direction == "down":
        raise ProtocolError("missing GET body timing", timing=timing)
    count = timing.bytes_sent if direction == "up" else timing.bytes_received
    if count != size:
        raise ProtocolError("transfer byte count differs from requested size", timing=timing)
    return {key: value * 1000 for key, value in fields.items()}


def reduce_runs(runs):
    """§5: discard best/worst, leaving the middle of exactly three runs."""
    if len(runs) not in (1, 3) or any(r["status"] != "pass" for r in runs):
        return None
    return sorted(runs, key=lambda r: r["mib_per_sec"])[len(runs) // 2]


def bdp(single, multi, window_bytes, rtt_ms):
    if not window_bytes or not rtt_ms or rtt_ms <= 0:
        return {"expected_mib_per_sec": None, "reason": "needs measured advertised TCP window and RTT (RFC 6349)"}
    expected = min(5e9 / 8, window_bytes / (rtt_ms / 1000)) / MIB
    return {"window_bytes": window_bytes, "rtt_ms": rtt_ms, "expected_mib_per_sec": expected,
            "single_to_expected": single / expected, "single_to_multi": single / multi if multi else None,
            "finding": "possible node-side window/loss defect" if single < expected / 2 and multi and multi >= expected else
                       "compare measured single stream with window/RTT; 5 Gbit/s cap",
            "reference": "RFC 6349; diagnostic ratios, not certification thresholds"}


def throughput_buckets(points, elapsed):
    # Progress events count bytes in their observed second, not at object completion.
    # Explicit zero-byte observations preserve idle seconds within the measured span.
    points = list(points) + [(float(i), 0) for i in range(math.ceil(elapsed))]
    return [{"start_seconds": start, "duration_seconds": min(1.0, elapsed - start),
             "bytes": sum(counts), "mib_per_sec": sum(counts) / MIB / min(1.0, elapsed - start)}
            for start, counts in windows(points, duration=1.0) if 0 <= start < elapsed]


def transfer_window(client, *, direction, prefix, concurrency, duration, objects,
                    owned, size=OBJECT_SIZE, one_object=False, loaded=None,
                    clock=time.monotonic, tcp_factory=TCPWindow, host="", loaded_interval=1.0):
    """Schedule until deadline, drain the current part/range; report actual wall time.

    No object-sized buffers. Validate each measured part/range before accepting
    its progress. Any invalid operation makes this window ungradable, while byte
    lower bounds and completed object manifests remain available for diagnosis.
    """
    lock, stop, active = threading.Lock(), threading.Event(), threading.Event()
    samples, points, completed, errors, loaded_samples, loaded_errors = [], [], [], [], [], []
    attempted_bytes = 0
    loaded_bytes = 0
    incomplete_objects = 0
    start = clock()
    deadline = start + duration

    def worker(index):
        nonlocal attempted_bytes, incomplete_objects
        iteration = 0
        while not stop.is_set() and (iteration == 0 or clock() < deadline):
            key = f"{prefix}{index}-{iteration}.bin" if direction == "up" else objects[index % len(objects)]["key"]
            payload = SeededPayload(key, size) if direction == "up" else SeededPayload(**objects[index % len(objects)]["payload"])
            pending, last, part_number = {}, 0, 0
            cpu_start = time.thread_time()

            def progress(count, _seconds):
                nonlocal last, attempted_bytes
                delta = count - last
                if delta < 0:
                    raise ProtocolError("non-monotonic transfer progress")
                last = count
                timestamp = clock() - start
                bucket = math.floor(timestamp)
                pending[bucket] = pending.get(bucket, 0) + delta
                with lock:
                    attempted_bytes += delta
                if delta:
                    active.set()

            def accept(response, count):
                nonlocal last, part_number, cpu_start
                sample = sample_timing(response.timing, count, direction)
                if sum(pending.values()) != count:
                    raise ProtocolError("progress bytes differ from measured transfer", timing=response.timing)
                sample.update(bytes=count, key=key, part=part_number, cpu_ms=(time.thread_time() - cpu_start) * 1000)
                with lock:
                    samples.append(sample)
                    points.extend(pending.items())
                pending.clear()
                last = 0
                part_number += 1
                cpu_start = time.thread_time()

            try:
                if direction == "up":
                    with lock:
                        owned.append(key)
                    _echo(f"multipart PUT {client.endpoint.host}/{key} ({payload.size} bytes)")
                    def on_part(response):
                        accept(response, min(PART_SIZE, payload.size - part_number * PART_SIZE))
                        if part_number * PART_SIZE < payload.size and (stop.is_set() or not one_object and clock() >= deadline):
                            raise _WindowEnded("profile window ended; abort incomplete multipart")
                    client.multipart_upload(key, payload, part_size=PART_SIZE, on_part=on_part, on_progress=progress)
                    obj = {"key": key, "payload": {"seed": payload.seed, "size": payload.size, "chunk_size": payload.chunk_size}}
                    with lock:
                        completed.append(obj)
                else:
                    # One stream reads one uploaded object in bounded, verified ranges.
                    for offset in range(0, payload.size, PART_SIZE):
                        count = min(PART_SIZE, payload.size - offset)
                        _echo(f"GET {client.endpoint.host}/{key} Range: bytes={offset}-{offset + count - 1}")
                        def consume(data, _offset):
                            progress(last + len(data), 0)
                        response = client.get_object(key, byte_range=(offset, offset + count - 1), payload=payload, consume=consume)
                        accept(response, count)
                        if offset + count < payload.size and (stop.is_set() or not one_object and clock() >= deadline):
                            raise _WindowEnded("profile window ended at range boundary")
                    with lock:
                        completed.append({"key": key})
            except _WindowEnded as exc:
                with lock:
                    incomplete_objects += 1
                    if exc.cleanup_error:
                        errors.append({"type": "AbortError", "reason": str(exc.cleanup_error)})
                break
            except ERRORS as exc:
                with lock:
                    errors.append({"type": type(exc).__name__, "reason": reason(exc),
                                   "cleanup_error": str(getattr(exc, "cleanup_error", None) or "")})
                stop.set()
                break
            iteration += 1
            if one_object:
                break

    def latency_worker():
        nonlocal loaded_bytes
        active.wait()
        while not stop.is_set():
            began = clock()
            cpu_start = time.thread_time()
            try:
                response = client.get_object(loaded["key"], payload=loaded["payload"])
                loaded_bytes += response.timing.bytes_received
                sample = timing_sample(response.timing)
                sample["cpu_ms"] = (time.thread_time() - cpu_start) * 1000
                sample["at_seconds"] = began - start
                # Only completed probes wholly inside the transfer window qualify.
                if not stop.is_set():
                    loaded_samples.append(sample)
            except ERRORS as exc:
                loaded_errors.append({"type": type(exc).__name__, "reason": reason(exc)})
            if stop.wait(loaded_interval):
                break

    with tcp_factory(host) as tcp:
        # Window includes TCP snapshots/setup overhead, but never a hidden retry.
        thread = threading.Thread(target=copy_context().run, args=(latency_worker,), daemon=True) if loaded else None
        if thread:
            thread.start()
        try:
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                futures = [pool.submit(copy_context().run, worker, index) for index in range(concurrency)]
                for future in futures:
                    future.result()
        finally:
            end = clock()
            stop.set()
            active.set()
            if thread:
                thread.join()
    elapsed = end - start
    buckets = throughput_buckets(points, elapsed) if elapsed > 0 else []
    stats = describe([b["mib_per_sec"] for b in buckets])
    valid_bytes = sum(s["bytes"] for s in samples)
    valid = not errors and elapsed > 0 and valid_bytes > 0
    result = {"status": "pass" if valid else "skip", "concurrency": concurrency,
              "requested_seconds": duration, "elapsed_seconds": elapsed, "drain_seconds": max(0, elapsed - duration),
              "bytes": valid_bytes, "progress_bytes_lower_bound": attempted_bytes, "objects": len(completed),
              "incomplete_objects": incomplete_objects,
              "mib_per_sec": valid_bytes / MIB / elapsed if valid else None,
              "objs_per_sec": len(completed) / elapsed if valid else None,
              "samples": samples, "latency_ms": describe([s["total_ms"] for s in samples]),
              "buckets": buckets, "bucket_stats": stats,
              "p95_p50_ratio": stats["p95"] / stats["p50"] if stats["p50"] else None,
              "errors": errors, "loaded_samples": loaded_samples, "loaded_errors": loaded_errors,
              "loaded_bytes": loaded_bytes, "tcp": tcp.detail}
    if not valid:
        result["reason"] = "invalid/failed transfer samples" if errors else "no complete verified transfer in window"
    return result, completed


def prerequisites(provider, options, direction):
    selected = targets(provider, options)
    if direction not in options.directions:
        raise ValueError(f"direction {direction} disabled by --directions")
    if not options.buckets.get(provider):
        raise ValueError(f"missing bucket configuration: --buckets {provider}=<name>")
    if options.tool != "stdlib":
        raise ValueError("Warp execution not implemented; use --tool stdlib")
    return selected


def baseline(provider, options):
    check = getattr(options, "_internet_checks", {}).get(f"internet.{provider}.latency.ttfb")
    if check and check.status == "pass":
        return json.loads(check.detail).get("baseline_ms", {}).get("p95")
    return None


def plan(target, options):
    if target["band"] == "light":
        return [(1, "single", 1)]
    sweep = ([options.concurrent] if getattr(options, "_concurrent_override", False) else [1, 8, 32, 64]) if options.profile == "certify" else [options.concurrent]
    result = [(c, "bulk", target["runs"]) for c in sweep]
    # A dedicated single stream has no concurrent loaded GETs, even when the
    # sustained sweep itself includes concurrency 1.
    result.append((1, "single", target["runs"]))
    return result


def upload_reports(provider, options, *, client_factory=S3Client, window=transfer_window):
    selected = prerequisites(provider, options, "up")
    state = options.__dict__.setdefault("_transfer_reports", {}).setdefault(provider, {})
    if "up" in state:
        return state["up"]
    records = state["up"] = []
    for target in selected:
        record = dict(target, runs_detail=[], objects=[], owned=[], cleanup="pending collection finalizer")
        records.append(record)
        if target["reason"]:
            continue
        prefix = f'{run_prefix(options)}{provider}/{target["region"]}/transfer/'
        try:
            client = client_factory(options.buckets[provider], target["region"], provider=provider)
        except ERRORS as exc:
            record["reason"] = f"{type(exc).__name__}: {reason(exc)}"
            record["cleanup"] = "no client or objects created"
            continue
        options.__dict__.setdefault("_transfer_owners", []).append((client, record, prefix))
        loaded = None
        if target["band"] == "nearest" and baseline(provider, options) is not None:
            key = prefix + "loaded.bin"
            record["owned"].append(key)
            payload = SeededPayload(key, LATENCY_SIZE)
            try:
                response = client.put_object(key, payload)
                sample_timing(response.timing, LATENCY_SIZE, "up")
                record["loaded_setup_bytes"] = response.timing.bytes_sent
                loaded = {"key": key, "payload": payload}
            except ERRORS as exc:
                record["loaded_reason"] = f"loaded-object setup failed: {reason(exc)}"
        else:
            record["loaded_reason"] = "needs successful internet.%s.latency.ttfb baseline_ms.p95" % provider
        for concurrency, kind, runs in plan(target, options):
            for index in range(runs):
                run, objects = window(client, direction="up", prefix=f"{prefix}{kind}-{concurrency}-{index}/",
                                      concurrency=concurrency, duration=options.duration, objects=[], owned=record["owned"],
                                      size=LIGHT_SIZE if target["band"] == "light" else OBJECT_SIZE,
                                      one_object=target["band"] == "light", loaded=loaded if kind == "bulk" else None,
                                      host=target["host"] if provider == "r2" else f'{options.buckets[provider]}.{target["host"]}')
                run.update(kind=kind, run=index)
                record["runs_detail"].append(run)
                record["objects"].extend(objects)
    return records


def transfer_check(provider, direction, metric, options, records):
    suffix = "upload" if direction == "up" else "download"
    primary = records[0]
    groups = {}
    for run in primary["runs_detail"]:
        groups.setdefault((run["kind"], run["concurrency"]), []).append(run)
    selected = [reduce_runs(runs) for (kind, _), runs in groups.items() if kind == "bulk"]
    # Report the largest measured concurrency, not the best result (no cherry-pick).
    chosen = max(selected, key=lambda r: r["concurrency"]) if selected and all(selected) else None
    if primary.get("cleanup_errors"):
        chosen = None
    singles = next((reduce_runs(runs) for (kind, _), runs in groups.items() if kind == "single"), None)
    detail = {"regions": records, "selection": "nearest; median of 3 by MiB/s per concurrency, scalar is largest concurrency; all runs retained",
              "single_stream_mib_per_sec": singles["mib_per_sec"] if singles else None,
              "timing_semantics": "schedule for duration, drain current part/range; abort incomplete multipart; actual elapsed denominator includes hashing/verification/control; per-op CPU is thread CPU",
              "single_stream": {}}
    for region in records:
        single = reduce_runs([r for r in region["runs_detail"] if r["kind"] == "single"])
        if not single:
            region["single_stream"] = {"mib_per_sec": None, "reason": "needs valid dedicated single-stream window(s)"}
            continue
        field = "window_bytes" if direction == "up" else "receive_window_bytes"
        measured = sorted([o for o in single["tcp"]["observations"] if o.get(field) and o["rtt_ms"]],
                          key=lambda o: o[field] / o["rtt_ms"])
        framing = measured[len(measured) // 2] if measured else {}
        signal = bdp(single["mib_per_sec"], chosen["mib_per_sec"] if chosen and region is primary else None,
                     framing.get(field), framing.get("rtt_ms"))
        signal["mib_per_sec"] = single["mib_per_sec"]
        if direction == "down" and not measured:
            signal["reason"] = "ss rcv_space is not an advertised receive window; rcv_wnd unavailable"
        region["single_stream"] = signal
    detail["single_stream"] = primary.get("single_stream", {})
    if chosen:
        detail.update(bucket_stats=chosen["bucket_stats"], p95_p50_ratio=chosen["p95_p50_ratio"],
                      retransmit_pct=chosen["tcp"]["ratio_pct"])
        if direction == "down":
            uploads = getattr(options, "_transfer_reports", {}).get(provider, {}).get("up", [])
            up = transfer_check(provider, "up", "throughput", options, uploads) if uploads else None
            detail["download_to_upload_ratio"] = chosen["mib_per_sec"] / up.value if up and up.status == "pass" and up.value else None
            if detail["download_to_upload_ratio"] is None:
                detail["asymmetry_reason"] = "needs successful upload.throughput measurement"
    else:
        detail["reason"] = ("owned-key cleanup failed" if primary.get("cleanup_errors") else primary["reason"] or
                            "needs valid sustained transfer runs (all 3 for certify reduction)")
    return Check(f"internet.{provider}.{suffix}.{metric}", "pass" if chosen else "skip",
                 chosen["mib_per_sec" if metric == "throughput" else "objs_per_sec"] if chosen else None,
                 detail=json.dumps(detail), source=[f'{"multipart PUT" if direction == "up" else "verified range GET"} {r["endpoint"]} bucket={options.buckets[provider]} prefix={run_prefix(options)}' for r in records])


def upload_probe(provider, metric, options):
    try:
        records = upload_reports(provider, options)
        return transfer_check(provider, "up", metric, options, records)
    except ERRORS as exc:
        return Check(f"internet.{provider}.upload.{metric}", "skip", detail=reason(exc))


def loaded_probe(provider, options):
    name = f"internet.{provider}.latency.loaded"
    try:
        prerequisites(provider, options, "up")
    except ERRORS as exc:
        return Check(name, "skip", detail=reason(exc))
    idle = baseline(provider, options)
    records = getattr(options, "_transfer_reports", {}).get(provider, {}).get("up", [])
    if idle is None:
        return Check(name, "skip", detail=f"needs successful internet.{provider}.latency.ttfb baseline_ms.p95")
    if not records:
        return Check(name, "skip", detail=f"needs internet.{provider}.upload transfer window")
    runs = [r for r in records[0]["runs_detail"] if r["kind"] == "bulk"]
    groups = {}
    for run in runs:
        groups.setdefault(run["concurrency"], []).append(run)
    reduced = {}
    for concurrency, group in groups.items():
        if len(group) in (1, 3) and all(r["loaded_samples"] for r in group):
            reduced[concurrency] = sorted(group, key=lambda r: describe(
                [s["response_first_byte_ms"] for s in r["loaded_samples"]])["p95"])[len(group) // 2]
    chosen = reduced.get(max(groups)) if groups else None
    samples = [s["response_first_byte_ms"] for s in chosen["loaded_samples"]] if chosen else []
    errors = [e for r in runs for e in r["loaded_errors"]]
    stats = describe(samples)
    valid = bool(samples) and len(reduced) == len(groups) and not errors and all(r["status"] == "pass" for r in runs)
    inflation = stats["p95"] - idle if valid else None
    detail = {"baseline_ms": {"p95": idle}, "loaded_ms": stats, "inflation_ms": inflation,
              "gate_ms": 20, "gate_exceeded": inflation > 20 if valid else None,
              "selection": "median loaded p95 of 3 runs per concurrency; scalar is largest concurrency",
              "retained_run_by_concurrency": {c: r["run"] for c, r in reduced.items()},
              "finding": "bufferbloat signal (>20 ms)" if valid and inflation > 20 else "within 20 ms" if valid else None,
              "runs": [{"concurrency": r["concurrency"], "run": r["run"], "samples": r["loaded_samples"]} for r in runs], "errors": errors}
    if not valid:
        detail["reason"] = records[0].get("loaded_reason", "needs valid concurrent TTFB samples inside successful upload windows")
    return Check(name, "pass" if valid else "skip", stats["p95"] if valid else None,
                 detail=json.dumps(detail), source=[f'concurrent verified GET {records[0]["endpoint"]}; upload windows only'])


def cleanup(options):
    """No listings: delete exact owned keys, even after ambiguous PUT responses."""
    for client, record, prefix in getattr(options, "_transfer_owners", []):
        if options.keep_data:
            record["cleanup"] = "retained (--keep-data)"
            continue
        errors = []
        for key in record["owned"]:
            try:
                if not key.startswith(prefix) or not prefix.startswith(run_prefix(options)):
                    raise ValueError("refusing cleanup outside owned prefix")
                _echo(f"DELETE {client.endpoint.host}/{key}")
                client.delete_object(key)
            except ERRORS as exc:
                errors.append({"key": key, "reason": reason(exc)})
        record["cleanup"] = "failed" if errors else "deleted exact owned keys"
        record["cleanup_errors"] = errors
