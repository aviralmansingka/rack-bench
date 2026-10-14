"""Shared transfer instrument: guards, window engine, reduction, grading and cleanup.
Both direction policies use this engine and its options-local run state; owned
keys survive until the collection finalizer, independently of check filtering.

Worker model: bulk windows (concurrency > 1) run one worker per process via a
ProcessPoolExecutor so the per-byte data path (chunk regeneration, digest
pre-pass, socket send/receive, verification) escapes the GIL; each worker
process builds its own S3Client and keeps its own pooled TLS connection. All
single-stream windows (concurrency 1, including bulk-sweep concurrency 1) keep
the in-process thread executor: they are the unchanged control group, their
code path is identical to earlier fixes, and the parent-pid ss filter still
applies to them. Both modes run the same picklable top-level worker, which
validates every part/range and RETURNS results for the parent to merge.
"""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from contextvars import copy_context
import json
import math
import multiprocessing
import os
import sys
import threading
import time

from rack_bench.common.host import _echo, operation_echo
from rack_bench.common.models import Check
from .latency import timing_sample
from .s3client import S3Client, S3Error, ProtocolError, SeededPayload, set_chunk_cache_limit
from .stats import describe, windows
from .targets import bucket_names, reason, run_prefix, targets
from .tcp import TCPWindow

MIB = 1024 ** 2
OBJECT_SIZE = 1024 * MIB
# Larger parts amortize per-request S3 server processing (TTFB ~110 ms is paid
# once per part/range, not per byte). 64 MiB keeps a single part comfortably
# inside the 30 s client socket timeout even at ~5 MiB/s single-stream rates;
# do not raise the default past 128 MiB without re-checking that interaction.
PART_SIZE = 64 * MIB
LIGHT_SIZE = 32 * MIB
ERRORS = (S3Error, ValueError, OSError)


class _WindowEnded(S3Error):
    """Normal part-boundary stop; multipart_upload aborts the known upload ID."""


def object_url(client, key):
    endpoint = client.endpoint
    if endpoint.path_style:
        return f"https://{endpoint.host}/{client.bucket}/{key}"
    return f"https://{client.bucket}.{endpoint.host}/{key}"


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


def _mp_context():
    # Fork on Linux (the lab host): cheap, and children inherit warm module
    # state. Everywhere else (e.g. macOS dev hosts, where forking a threaded
    # interpreter is unsafe) use spawn; both carry the pool initargs through
    # Process construction, so synchronization primitives stay shareable.
    return multiprocessing.get_context("fork" if sys.platform.startswith("linux") else "spawn")


def _process_pool_factory(concurrency, *, initializer=None, initargs=()):
    """Bulk-window default: one worker process per stream (own GIL, own client)."""
    return ProcessPoolExecutor(max_workers=concurrency, mp_context=_mp_context(),
                               initializer=initializer, initargs=initargs)


def _thread_pool_factory(concurrency, *, initializer=None, initargs=()):
    """Single-stream default: in-process worker threads (unchanged control group)."""
    return ThreadPoolExecutor(max_workers=concurrency, initializer=initializer, initargs=initargs)


_POOL_STATE = {}
"""Worker-process state (client, stop event) set by _pool_initialiser.

Only worker processes populate this; the parent and in-process worker threads
receive the client and stop event through the task spec instead, so stale
parent-side state can never leak into a threaded window.
"""


def _pool_initialiser(client_config, stop, pid_slots, chunk_limit, echo):
    """Worker-process setup: own S3Client, shared stop event, pid registration.

    S3Client is not picklable (its connection pool is threading.local), so each
    child constructs its own from plain config and thereby keeps its own warm
    pooled TLS connection across objects. The stop event and pid slots arrive
    through the pool initargs, which travel via Process construction rather
    than the task queue, so synchronization primitives remain shareable.
    chunk_limit re-caps this process's chunk cache: bulk workers each cache the
    same run-shared payload bytes, so N processes must not each hold the
    parent-side cap; one part's worth of chunks keeps the current part hot.
    The operation-echo contextvar does not cross process boundaries; the
    parent's callback is passed in and re-installed explicitly.
    """
    bucket, endpoint, timeout, control_retries, backoff = client_config
    _POOL_STATE["client"] = S3Client(bucket, endpoint.region, endpoint=endpoint,
                                     timeout=timeout, control_retries=control_retries,
                                     backoff=backoff)
    _POOL_STATE["stop"] = stop
    set_chunk_cache_limit(chunk_limit)
    operation_echo.set(echo)
    with pid_slots.get_lock():
        for slot in range(len(pid_slots)):
            if pid_slots[slot] == 0:
                pid_slots[slot] = os.getpid()
                break


def _transfer_worker(spec):
    """One scheduled transfer stream; validates each part/range, returns results.

    Runs as an in-process worker thread (single-stream windows) or inside a
    worker process (bulk windows). Per-part validation -- timing shape,
    monotonic progress, byte accounting -- happens here, before anything is
    accepted. Nothing is shared with the scheduler: the worker returns
    (samples, points, completed, errors, owned_keys, incomplete_objects,
    attempted_bytes) and the parent merges. owned_keys are collected before
    each upload attempt so ambiguous PUTs stay cleanable even when the worker
    reports them only at completion. A failing worker sets the shared stop
    event so sibling workers exit at their next check.
    """
    client = spec["client"] if spec["client"] is not None else _POOL_STATE["client"]
    stop = spec["stop"] if spec["stop"] is not None else _POOL_STATE["stop"]
    clock, deadline, start, active = spec["clock"], spec["deadline"], spec["start"], spec["active"]
    samples, points, completed, errors, owned_keys = [], [], [], [], []
    attempted_bytes = incomplete_objects = 0
    index, iteration = spec["index"], 0
    while not stop.is_set() and (iteration == 0 or clock() < deadline):
        direction = spec["direction"]
        key = f'{spec["prefix"]}{index}-{iteration}.bin' if direction == "up" else spec["objects"][index % len(spec["objects"])]["key"]
        payload = SeededPayload(spec["seed"] if spec["seed"] is not None else key, spec["size"]) if direction == "up" else SeededPayload(**spec["objects"][index % len(spec["objects"])]["payload"])
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
            attempted_bytes += delta
            if delta and active is not None:
                active.set()

        def accept(response, count):
            nonlocal last, part_number, cpu_start
            sample = sample_timing(response.timing, count, direction)
            if sum(pending.values()) != count:
                raise ProtocolError("progress bytes differ from measured transfer", timing=response.timing)
            sample.update(bytes=count, key=key, part=part_number, cpu_ms=(time.thread_time() - cpu_start) * 1000)
            samples.append(sample)
            points.extend(pending.items())
            pending.clear()
            last = 0
            part_number += 1
            cpu_start = time.thread_time()

        try:
            if direction == "up":
                owned_keys.append(key)
                _echo(f"multipart PUT {object_url(client, key)} ({payload.size} bytes)")
                def on_part(response):
                    accept(response, min(spec["part_size"], payload.size - part_number * spec["part_size"]))
                    if part_number * spec["part_size"] < payload.size and (stop.is_set() or not spec["one_object"] and clock() >= deadline):
                        raise _WindowEnded("profile window ended; abort incomplete multipart")
                client.multipart_upload(key, payload, part_size=spec["part_size"], on_part=on_part, on_progress=progress)
                completed.append({"key": key, "payload": {"seed": payload.seed, "size": payload.size, "chunk_size": payload.chunk_size}})
            else:
                # One stream reads one uploaded object in bounded, verified ranges.
                for offset in range(0, payload.size, spec["part_size"]):
                    count = min(spec["part_size"], payload.size - offset)
                    _echo(f"GET {object_url(client, key)} Range: bytes={offset}-{offset + count - 1}")
                    def consume(data, _offset):
                        progress(last + len(data), 0)
                    response = client.get_object(key, byte_range=(offset, offset + count - 1), payload=payload, consume=consume)
                    accept(response, count)
                    if offset + count < payload.size and (stop.is_set() or not spec["one_object"] and clock() >= deadline):
                        raise _WindowEnded("profile window ended at range boundary")
                completed.append({"key": key})
        except _WindowEnded as exc:
            incomplete_objects += 1
            if exc.cleanup_error:
                errors.append({"type": "AbortError", "reason": str(exc.cleanup_error)})
            break
        except ERRORS as exc:
            errors.append({"type": type(exc).__name__, "reason": reason(exc),
                           "cleanup_error": str(getattr(exc, "cleanup_error", None) or "")})
            stop.set()
            break
        iteration += 1
        if spec["one_object"]:
            break
    return samples, points, completed, errors, owned_keys, incomplete_objects, attempted_bytes


def transfer_window(client, *, direction, prefix, concurrency, duration, objects,
                    owned, size=OBJECT_SIZE, one_object=False, loaded=None,
                    clock=time.monotonic, tcp_factory=TCPWindow, host="", loaded_interval=1.0,
                    part_size=None, seed=None, pool_factory=None):
    """Schedule until deadline, drain the current part/range; report actual wall time.

    No object-sized buffers. Validate each measured part/range before accepting
    its progress. Any invalid operation makes this window ungradable, while byte
    lower bounds and completed object manifests remain available for diagnosis.
    part_size=None means the module PART_SIZE; policies plumb the CLI value in.
    seed is the run-shared payload seed (targets.run_seed): every upload object
    in the run derives identical bytes per offset, so the bounded chunk/digest
    caches in s3client turn the signed-digest pre-pass and chunk regeneration
    into hits. seed=None falls back to the object key, matching stored records.

    Execution scoping: concurrency > 1 windows schedule one worker per process
    (pool_factory=None picks _process_pool_factory) so the data path escapes the
    GIL; concurrency 1 windows keep in-process threads (_thread_pool_factory).
    pool_factory is the test seam, mirroring tcp_factory: thread-based factories
    run the same picklable worker in-process, where mock clients and fake clocks
    work unchanged. The loaded-latency probe always stays in this (parent)
    process as a thread with fresh_connection=True semantics.
    """
    if part_size is None:
        part_size = PART_SIZE  # resolved per call so tests can patch the default
    out_of_process = concurrency > 1 and pool_factory in (None, _process_pool_factory)
    factory = pool_factory or (_process_pool_factory if out_of_process else _thread_pool_factory)
    stop, pid_slots, initializer, initargs = threading.Event(), None, None, ()
    if out_of_process:
        context = _mp_context()
        stop = context.Event()
        # Worker pids register here; TCPWindow polls this array so child sockets
        # stay inside the window diagnostics instead of vanishing from the
        # parent-pid ss filter. The array and event travel via pool initargs.
        pid_slots = context.Array("i", concurrency)
        initializer = _pool_initialiser
        initargs = ((client.bucket, client.endpoint, client.timeout, client.control_retries, client.backoff),
                    stop, pid_slots, part_size, operation_echo.get())

    def pids():
        # Parent plus registered worker processes; read under the array lock.
        with pid_slots.get_lock():
            workers = {int(value) for value in pid_slots if value}
        return {os.getpid()} | workers

    samples, points, completed, errors, loaded_samples, loaded_errors = [], [], [], [], [], []
    attempted_bytes = 0
    loaded_bytes = 0
    incomplete_objects = 0
    active = threading.Event()
    start = clock()
    deadline = start + duration

    def task(index):
        return {"direction": direction, "prefix": prefix, "index": index, "objects": objects,
                "size": size, "one_object": one_object, "deadline": deadline, "start": start,
                "part_size": part_size, "seed": seed, "clock": clock,
                "client": None if out_of_process else client,
                "stop": None if out_of_process else stop,
                "active": None if out_of_process else active}

    def latency_worker():
        nonlocal loaded_bytes
        active.wait()
        while not stop.is_set():
            began = clock()
            cpu_start = time.thread_time()
            try:
                _echo(f'GET {object_url(client, loaded["key"])} (loaded latency)')
                # One-shot socket: every loaded sample keeps TCP+TLS inside its
                # TTFB, matching cold-client semantics; bulk pooling is separate.
                response = client.get_object(loaded["key"], payload=loaded["payload"],
                                             fresh_connection=True)
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

    with tcp_factory(host, pids=pids if out_of_process else None) as tcp:
        # Window includes TCP snapshots/setup overhead, but never a hidden retry.
        thread = None
        try:
            with factory(concurrency, initializer=initializer, initargs=initargs) as pool:
                futures = [pool.submit(_transfer_worker, task(index)) if out_of_process else
                           pool.submit(copy_context().run, _transfer_worker, task(index))
                           for index in range(concurrency)]
                # Worker processes spawn on first submit: the loaded-latency
                # thread starts only now, so every fork happens before it exists
                # and its one-shot connections are always made post-spawn. Child
                # processes cannot set a parent-side threading event, so the
                # parent approximates first-transfer activity at submit time.
                if out_of_process:
                    active.set()
                if loaded:
                    thread = threading.Thread(target=copy_context().run, args=(latency_worker,), daemon=True)
                    thread.start()
                for future in futures:
                    try:
                        result = future.result()
                    except (ERRORS, BrokenProcessPool) as exc:
                        # Unpicklable task/return or a dead worker: explicit skip.
                        errors.append({"type": type(exc).__name__, "reason": reason(exc)})
                        stop.set()
                        continue
                    worker_samples, worker_points, worker_completed, worker_errors, worker_owned, worker_incomplete, worker_attempted = result
                    samples.extend(worker_samples)
                    points.extend(worker_points)
                    completed.extend(worker_completed)
                    owned.extend(worker_owned)
                    errors.extend(worker_errors)
                    incomplete_objects += worker_incomplete
                    attempted_bytes += worker_attempted
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
    if not bucket_names(provider, options):
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
            # Generic grading over shared run state; no direction-policy callbacks.
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
                 detail=json.dumps(detail), source=[f'{"multipart PUT" if direction == "up" else "verified range GET"} {r["endpoint"]} buckets={",".join(bucket_names(provider, options))} prefix={run_prefix(options)}' for r in records])


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
                _echo(f"DELETE {object_url(client, key)}")
                client.delete_object(key)
            except ERRORS as exc:
                errors.append({"key": key, "reason": reason(exc)})
        record["cleanup"] = "failed" if errors else "deleted exact owned keys"
        record["cleanup_errors"] = errors
        client.close()  # pooled socket teardown after the final owned-key DELETE
