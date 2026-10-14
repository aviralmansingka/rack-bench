"""Download policy: verified range GET windows over this run's upload manifest.
The shared transfer instrument supplies measurement and grading; this module
reads only the options-local manifest and never manufactures a setup upload.
"""
from rack_bench.common.models import Check
from .s3client import S3Client
from .targets import bucket_names, reason, run_prefix
from .transfer import ERRORS, MIB, plan, prerequisites, transfer_check, transfer_window


def download_reports(provider, options, *, client_factory=S3Client, window=transfer_window):
    prerequisites(provider, options, "down")
    state = getattr(options, "_transfer_reports", {}).get(provider, {})
    if "down" in state:
        return state["down"]
    if not state.get("up"):
        raise ValueError(f"needs internet.{provider}.upload objects from this run; no pre-seeded data")
    records = state["down"] = []
    names = bucket_names(provider, options)
    for upload in state["up"]:
        record = {key: upload[key] for key in ("region", "endpoint", "host", "band", "runs", "reason", "buckets")}
        record["runs_detail"] = []
        records.append(record)
        if record["reason"]:
            continue
        if not upload["objects"] or any(r["status"] != "pass" for r in upload["runs_detail"]):
            record["reason"] = "needs completed objects from successful upload windows"
            continue
        clients = {}
        try:
            # One client per bucket: each downloaded object is read from the
            # bucket its upload record names, whatever the stream assignment.
            for name in names:
                clients[name] = client_factory(name, upload["region"], provider=provider)
        except ERRORS as exc:
            for created in clients.values():
                created.close()
            record["reason"] = f"{type(exc).__name__}: {reason(exc)}"
            continue
        for concurrency, kind, runs in plan(upload, options):
            for index in range(runs):
                run, _ = window(clients[names[0]], direction="down", prefix=run_prefix(options),
                                concurrency=concurrency, duration=options.duration,
                                objects=upload["objects"], owned=[], one_object=upload["band"] == "light",
                                part_size=options.part_size * MIB, buckets=names, clients=clients,
                                provider=provider,
                                host=upload["host"] if provider in ("r2", "gcs") else f'{names[0]}.{upload["host"]}')
                run.update(kind=kind, run=index)
                record["runs_detail"].append(run)
        for client in clients.values():
            client.close()  # parent-side pooled sockets; worker sockets died with their threads/processes
    return records


def download_probe(provider, metric, options):
    try:
        records = download_reports(provider, options)
        return transfer_check(provider, "down", metric, options, records)
    except ERRORS as exc:
        return Check(f"internet.{provider}.download.{metric}", "skip", detail=reason(exc))
