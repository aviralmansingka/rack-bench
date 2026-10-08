"""Download policy: verified range GET windows over this run's upload manifest.
The shared transfer instrument supplies measurement and grading; this module
reads only the options-local manifest and never manufactures a setup upload.
"""
from rack_bench.common.models import Check
from .s3client import S3Client
from .targets import reason, run_prefix
from .transfer import ERRORS, plan, prerequisites, transfer_check, transfer_window


def download_reports(provider, options, *, client_factory=S3Client, window=transfer_window):
    prerequisites(provider, options, "down")
    state = getattr(options, "_transfer_reports", {}).get(provider, {})
    if "down" in state:
        return state["down"]
    if not state.get("up"):
        raise ValueError(f"needs internet.{provider}.upload objects from this run; no pre-seeded data")
    records = state["down"] = []
    for upload in state["up"]:
        record = {key: upload[key] for key in ("region", "endpoint", "host", "band", "runs", "reason")}
        record["runs_detail"] = []
        records.append(record)
        if record["reason"]:
            continue
        if not upload["objects"] or any(r["status"] != "pass" for r in upload["runs_detail"]):
            record["reason"] = "needs completed objects from successful upload windows"
            continue
        try:
            client = client_factory(options.buckets[provider], upload["region"], provider=provider)
        except ERRORS as exc:
            record["reason"] = f"{type(exc).__name__}: {reason(exc)}"
            continue
        for concurrency, kind, runs in plan(upload, options):
            for index in range(runs):
                run, _ = window(client, direction="down", prefix=run_prefix(options),
                                concurrency=concurrency, duration=options.duration,
                                objects=upload["objects"], owned=[], one_object=upload["band"] == "light",
                                host=upload["host"] if provider == "r2" else f'{options.buckets[provider]}.{upload["host"]}')
                run.update(kind=kind, run=index)
                record["runs_detail"].append(run)
    return records


def download_probe(provider, metric, options):
    try:
        records = download_reports(provider, options)
        return transfer_check(provider, "down", metric, options, records)
    except ERRORS as exc:
        return Check(f"internet.{provider}.download.{metric}", "skip", detail=reason(exc))
