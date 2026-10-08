"""Sequential, verified 100 KiB GET baseline; no bulk or loaded transfers."""
import json
import math
import time

from rack_bench.common.host import _echo
from rack_bench.common.models import Check
from .s3client import CredentialError, ProtocolError, S3Client, S3Error, SeededPayload
from .stats import describe
from .targets import reason, run_prefix, targets

OBJECT_SIZE = 100 * 1024
SAMPLES = 20  # Also the hard per-far-band GET budget.
TIMING_FIELDS = {"connect_ms": "connect_seconds",
                 "response_first_byte_ms": "response_first_byte_seconds",
                 "headers_ms": "headers_seconds",
                 "body_first_byte_ms": "first_byte_seconds",
                 "total_ms": "elapsed_seconds"}


def timing_sample(timing):
    values = {name: getattr(timing, field) for name, field in TIMING_FIELDS.items()}
    if any(value is None or not math.isfinite(value) or value < 0 for value in values.values()):
        raise ProtocolError("missing or invalid GET timing", timing=timing)
    if not (values["connect_ms"] <= values["response_first_byte_ms"] <= values["headers_ms"] <=
            values["body_first_byte_ms"] <= values["total_ms"]) or timing.attempts != 1:
        raise ProtocolError("invalid GET timing order or retried measurement", timing=timing)
    if timing.bytes_received != OBJECT_SIZE:
        raise ProtocolError("GET did not receive the full 100 KiB object", timing=timing)
    return {name: value * 1000 for name, value in values.items()}


def latency_probe(provider, options, *, client_factory=S3Client, cpu_clock=time.process_time):
    name = f"internet.{provider}.latency.ttfb"
    try:
        selected = targets(provider, options)
    except ValueError as exc:
        return Check(name, "skip", detail=reason(exc))
    bucket = options.buckets.get(provider)
    if not bucket:
        return Check(name, "skip", detail=f"missing bucket configuration: --buckets {provider}=<name>")
    if options.tool != "stdlib":
        return Check(name, "skip", detail="Warp execution not implemented; use --tool stdlib")
    prefix = run_prefix(options)
    records, sources = [], []
    for target in selected:
        record = dict(target, runs_detail=[], bytes_uploaded=0, bytes_downloaded=0)
        records.append(record)
        if target["reason"]:
            record["status"] = "skip"
            continue
        key = f'{prefix}{provider}/{target["region"]}/latency.bin'
        payload = SeededPayload(key, OBJECT_SIZE)
        record.update(key=key, seed=payload.seed, size=payload.size, chunk_size=payload.chunk_size)
        host = target["host"] if provider == "r2" else f'{bucket}.{target["host"]}'
        url = f'https://{host}/' + (f'{bucket}/' if provider == "r2" else "") + key
        sources.append(f"PUT {url}; {target['runs']} x {SAMPLES} sequential GETs; " +
                       ("retain (--keep-data)" if options.keep_data else f"DELETE {url}"))
        client = None
        try:
            client = client_factory(bucket, target["region"], provider=provider)
            cpu_start = cpu_clock()
            # s3client prepares MD5/CRC32/SHA256 before PUT timing; GET regenerates
            # and compares every byte. Setup PUT is never a baseline sample.
            _echo(f"PUT {url} (baseline setup, not a sample)")
            upload = client.put_object(key, payload)
            record["setup_cpu_ms"] = (cpu_clock() - cpu_start) * 1000
            record["setup_seconds"] = upload.timing.elapsed_seconds
            record["bytes_uploaded"] = upload.timing.bytes_sent
            for _ in range(target["runs"]):
                samples = []
                run = {"samples": samples}
                record["runs_detail"].append(run)
                for _ in range(SAMPLES):
                    cpu_start = cpu_clock()
                    _echo(f"GET {url}")
                    response = client.get_object(key, payload=payload)
                    record["bytes_downloaded"] += response.timing.bytes_received
                    sample = timing_sample(response.timing)
                    sample["cpu_ms"] = (cpu_clock() - cpu_start) * 1000
                    samples.append(sample)
                run["stats"] = {field: describe([s[field] for s in samples])
                                for field in (*TIMING_FIELDS, "cpu_ms")}
            ordered = sorted(record["runs_detail"], key=lambda r: r["stats"]["response_first_byte_ms"]["p50"])
            record["baseline_ms"] = ordered[len(ordered) // 2]["stats"]["response_first_byte_ms"]
            record["status"] = "pass"
        except (S3Error, CredentialError, ValueError, OSError) as exc:
            record.update(status="skip", reason=f"{type(exc).__name__}: {reason(exc)}")
        finally:
            if client is not None and not options.keep_data:
                try:
                    # Delete only our exact key, including after an ambiguous failed PUT.
                    # Never list the bucket root or delete someone else's prefix.
                    _echo(f"DELETE {url}")
                    client.delete_object(key)
                    record["cleanup"] = "deleted owned key"
                except (S3Error, OSError) as exc:
                    record.update(status="skip", cleanup_error=f"{type(exc).__name__}: {exc}")
                    record["reason"] = record.get("reason") or "owned-key cleanup failed"
            elif options.keep_data:
                record["cleanup"] = "retained (--keep-data)"
    primary = records[0]
    detail = {"regions": records, "prefix": prefix, "bucket": bucket,
              "baseline_field": "response_first_byte_ms",
              "timing_semantics": "connect_ms is TCP+TLS duration; response/header/body/total are cumulative from request start, not additive phases",
              "cpu_semantics": "process CPU per GET includes regeneration/verification and transport; setup CPU includes hashing/generation",
              "selection": "nearest band; certify drops best/worst runs ranked by response TTFB p50; light bands are one run"}
    status = primary["status"]
    if status == "skip":
        detail["reason"] = primary["reason"]
    else:
        detail["baseline_ms"] = primary["baseline_ms"]
    return Check(name, status, value=primary["baseline_ms"]["p50"] if status == "pass" else None,
                 detail=json.dumps(detail), source=sources)
