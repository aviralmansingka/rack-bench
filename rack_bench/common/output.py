"""Human/JSON rendering and result artifact writes; no collection logic."""
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from .models import Result


def render_json(results: list[Result]) -> str:
    return json.dumps({"schema_version": 1, "results": [asdict(result) for result in results]},
                      indent=2, ensure_ascii=True, allow_nan=False) + "\n"


def show_operation(check_name, operation):
    print(f"[{check_name}] {operation}", flush=True)


def show_cost_estimate(estimates):
    costs = ", ".join(f"{provider.upper()} ~${cost}" for provider, cost in estimates.items())
    print("Certify reference estimate at 10 Gbit/s: ~2.2 TB per provider; " + costs + ".\n"
          "Not adjusted for overrides or check/direction filters; actual charges may vary.\n"
          "Bulk transfers are live; small-object requests may incur charges too. "
          "Nearest band uses full windows; far bands omit bulk and cap single-stream at 32 MiB each direction.", file=sys.stderr)


def internet_summary(value):
    """Compact full-provider rollup; the probe supplies data, never display text."""
    checks = value.get("checks", {})
    rates = []
    for direction in ("upload", "download"):
        check = checks.get(f"{direction}.throughput", {})
        if check.get("status") == "pass":
            rates.append(f"{direction}={check['value']:.2f} MiB/s")
    counts = Counter(check["status"] for check in checks.values())
    payload = value.get("bytes", {})
    return (f"{value['region']} {value['endpoint']} tool={value['tool']}; " +
            ", ".join(rates or ["no sustained rate observed"]) +
            f"; bytes up={payload.get('uploaded', 0)} down={payload.get('downloaded', 0)}; " +
            " ".join(f"{status.upper()}={counts[status]}" for status in ("pass", "warn", "fail", "skip")))


def render_human(results: list[Result], *, quiet=False) -> str:
    lines = []
    for result in results:
        lines.extend([f"{result.scope} @ {result.host}", f"{'STATUS':6} {'CHECK':28} VALUE / DETAIL"])
        for check in result.checks:
            if quiet and check.status == "pass":
                continue
            value = check.detail if check.status == "skip" else json.dumps(check.value, ensure_ascii=True)
            if (check.status == "pass" and check.name.startswith("internet.") and
                    check.name.endswith(".summary") and isinstance(check.value, dict) and "checks" in check.value):
                value = internet_summary(check.value)
            if check.status in ("warn", "fail") and check.detail:
                value += "; " + check.detail
            if check.expected is not None:
                value += "; expected=" + json.dumps(check.expected)
            value = " ".join(value.splitlines())
            lines.append(f"{check.status.upper():6} {check.name:28} {value}")
    counts = Counter(check.status for result in results for check in result.checks)
    lines.append("Summary: " + " ".join(f"{s.upper()}={counts[s]}" for s in ("pass", "warn", "fail", "skip")))
    return "\n".join(lines) + "\n"


def emit(results: list[Result], *, stage: str, json_target=None, run_dir=None, quiet=False):
    human, machine = render_human(results), render_json(results)
    directory = Path(run_dir) if run_dir else Path("rack-bench-runs") / datetime.now(
        timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{stage}.out").write_text(human)
    (directory / f"{stage}.values.json").write_text(machine)
    if json_target and json_target != "-":
        target = Path(json_target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(machine)
    print(machine if json_target == "-" else render_human(results, quiet=quiet), end="")
