"""Collection summary data; human presentation belongs to common.output."""
import json

from rack_bench.common.models import Check
from .targets import reason, run_prefix, targets


def summary(provider, options):
    name = f"internet.{provider}.summary"
    try:
        selected = targets(provider, options)
    except ValueError as exc:
        return Check(name, "skip", detail=reason(exc))
    checks = {name: check for name, check in getattr(options, "_internet_checks", {}).items()
              if name.startswith(f"internet.{provider}.") and not name.endswith(".summary")}
    if not checks:
        return Check(name, "skip", detail="needs preceding provider checks; none were selected")
    state = getattr(options, "_transfer_reports", {}).get(provider, {})
    totals = {"uploaded": 0, "downloaded": 0}
    baseline = checks.get(f"internet.{provider}.latency.ttfb")
    if baseline:
        try:
            for region in json.loads(baseline.detail).get("regions", []):
                totals["uploaded"] += region["bytes_uploaded"]
                totals["downloaded"] += region["bytes_downloaded"]
        except (ValueError, TypeError):
            pass  # A plain-text SKIP reason has no byte observations.
    for direction, label in (("up", "uploaded"), ("down", "downloaded")):
        for region in state.get(direction, []):
            totals[label] += sum(r["progress_bytes_lower_bound"] for r in region["runs_detail"])
            if direction == "up":
                totals["uploaded"] += region.get("loaded_setup_bytes", 0)
                totals["downloaded"] += sum(r.get("loaded_bytes", 0) for r in region["runs_detail"])
    value = {"region": selected[0]["region"], "endpoint": selected[0]["endpoint"], "tool": options.tool,
             "bytes": totals, "checks": {key.rsplit(f"internet.{provider}.", 1)[1]:
                                          {"status": c.status, "value": c.value} for key, c in checks.items()}}
    detail = {"regions": selected, "prefix": run_prefix(options), "directions": options.directions,
              "profile": options.profile, "byte_semantics": "application payload progress lower bounds, including baseline and loaded probes; excludes protocol/control traffic",
              "cleanup": [{"region": r["region"], "status": r["cleanup"], "errors": r.get("cleanup_errors", [])}
                          for r in state.get("up", [])],
              "selection": "only checks actually collected; missing checks were filtered, never silently run"}
    return Check(name, "pass", value, detail=json.dumps(detail), source=[t["endpoint"] for t in selected])
