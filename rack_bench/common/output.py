"""Human/JSON rendering and result artifact writes; no collection logic."""
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from .models import Result


def render_json(results: list[Result]) -> str:
    return json.dumps({"schema_version": 1, "results": [asdict(result) for result in results]},
                      indent=2, ensure_ascii=True, allow_nan=False) + "\n"


def show_operation(check_name, operation):
    print(f"[{check_name}] {operation}", flush=True)


def render_human(results: list[Result], *, quiet=False) -> str:
    lines = []
    for result in results:
        lines.extend([f"{result.scope} @ {result.host}", f"{'STATUS':6} {'CHECK':28} VALUE / DETAIL"])
        for check in result.checks:
            if quiet and check.status == "pass":
                continue
            value = check.detail if check.status == "skip" else json.dumps(check.value, ensure_ascii=True)
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
