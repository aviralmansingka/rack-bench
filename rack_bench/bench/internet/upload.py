"""Upload policy: owned-object setup, upload windows and upload-only loaded latency.
The shared transfer instrument supplies measurement and grading; this module
registers owned keys and publishes the options-local manifest for download.
"""
import json

from rack_bench.common.host import _echo
from rack_bench.common.models import Check
from .latency import OBJECT_SIZE as LATENCY_SIZE
from .s3client import S3Client, SeededPayload
from .stats import describe
from .targets import reason, run_prefix
from .transfer import (ERRORS, LIGHT_SIZE, OBJECT_SIZE, baseline, object_url, plan,
                       prerequisites, sample_timing, transfer_check, transfer_window)


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
            record["loaded_key"] = key
            payload = SeededPayload(key, LATENCY_SIZE)
            try:
                _echo(f"PUT {object_url(client, key)} (loaded setup)")
                response = client.put_object(key, payload)
                sample_timing(response.timing, LATENCY_SIZE, "up")
                record["loaded_setup_bytes"] = response.timing.bytes_sent
                loaded = {"key": key, "payload": payload}
            except ERRORS as exc:
                record["loaded_reason"] = f"loaded-object setup failed: {reason(exc)}"
        else:
            record["loaded_reason"] = ("omitted by light-band budget; no sustained upload window" if target["band"] == "light" else
                                       f"needs successful internet.{provider}.latency.ttfb baseline_ms.p95")
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
              "regions": [{"region": r["region"], "endpoint": r["endpoint"], "band": r["band"],
                           "reason": r["reason"] or r.get("loaded_reason")} for r in records],
              "gate_ms": 20, "gate_exceeded": inflation > 20 if valid else None,
              "selection": "median loaded p95 of 3 runs per concurrency; scalar is largest concurrency",
              "retained_run_by_concurrency": {c: r["run"] for c, r in reduced.items()},
              "finding": "bufferbloat signal (>20 ms)" if valid and inflation > 20 else "within 20 ms" if valid else None,
              "runs": [{"concurrency": r["concurrency"], "run": r["run"], "samples": r["loaded_samples"]} for r in runs], "errors": errors}
    if not valid:
        detail["reason"] = records[0].get("loaded_reason", "needs valid concurrent TTFB samples inside successful upload windows")
    return Check(name, "pass" if valid else "skip", stats["p95"] if valid else None,
                 detail=json.dumps(detail), source=[f'concurrent verified GET {records[0]["endpoint"]} bucket={options.buckets[provider]} key={records[0].get("loaded_key")}; upload windows only'])
