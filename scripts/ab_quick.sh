#!/usr/bin/env bash
# ab_quick.sh — quick A/B helper for rack-bench internet throughput changes.
#
#   ./ab_quick.sh run baseline      # record current code, pinned flags
#   ./ab_quick.sh run candidate     # after your change
#   ./ab_quick.sh compare [DIR_A DIR_B]   # defaults: ab-runs/{baseline,candidate}
#
# Quick mode runs each window ONCE (no median-of-3), so noise control comes
# from the A/B pairing. If a delta is near the threshold, record two
# baselines on unchanged code to calibrate noise.
set -euo pipefail

FIXED_FLAGS=(--profile quick --providers r2 --directions up,down
             --tool stdlib --object-size 64 --concurrent 32 --duration 60s)

code_hash() {
    local rb py pkg
    rb="$(command -v rack-bench || true)"
    [ -z "$rb" ] && rb="$HOME/.local/bin/rack-bench"
    py="$(sed -n '1s|^#!||p' "$rb" 2>/dev/null || true)"
    pkg="$("$py" -c 'import rack_bench,os;print(os.path.dirname(rack_bench.__file__))' 2>/dev/null || true)"
    if [ -n "$pkg" ]; then
        find "$pkg" -name '*.py' -exec md5sum {} + | sort | md5sum | cut -d' ' -f1
    else
        echo n/a
    fi
}

case "${1:-}" in
run)
    label="${2:?usage: ab_quick.sh run <label> [extra rack-bench flags]}"
    shift 2
    dir="ab-runs/$label"
    [ -e "$dir" ] && { echo "refusing to overwrite existing $dir" >&2; exit 2; }
    if [ -f "$HOME/.rack-bench.env" ]; then set -a; . "$HOME/.rack-bench.env"; set +a; fi
    RB="$(command -v rack-bench || true)"
    [ -z "$RB" ] && RB="$HOME/.local/bin/rack-bench"
    "$RB" bench internet "${FIXED_FLAGS[@]}" "$@" --run-dir "$dir"
    mkdir -p "$dir"
    printf 'flags=%s\ncode_hash=%s\nts=%s\nhost=%s\n' \
        "${FIXED_FLAGS[*]}" "$(code_hash)" "$(date -u +%FT%TZ)" "$(hostname)" > "$dir/ab.meta"
    echo "saved $dir"
    ;;
compare)
    a="${2:-ab-runs/baseline}"; b="${3:-ab-runs/candidate}"
    python3 - "$a" "$b" <<'PY'
import json, sys, statistics as st

def load(dirp):
    res = json.load(open(f"{dirp}/bench.values.json"))["results"][0]
    out = {}
    for c in res["checks"]:
        name = c["name"]
        if not name.endswith(("upload.throughput", "download.throughput")):
            continue
        d = "up" if "upload" in name else "down"
        det = json.loads(c["detail"]) if isinstance(c["detail"], str) else c["detail"]
        regions = det.get("regions") or []
        region = next((r for r in regions if r.get("runs_detail")), None)
        runs = (region or {}).get("runs_detail", [])
        bulk = [r for r in runs if r.get("kind") == "bulk"]
        bulk = max(bulk, key=lambda r: r.get("concurrency", 0)) if bulk else {}
        # median single run, matching the tool's own reduce_runs (len 1 or 3)
        singles = sorted((r for r in runs if r.get("kind") == "single"),
                         key=lambda r: r.get("mib_per_sec") or 0)
        single = singles[len(singles) // 2] if singles else {}
        ss = det.get("single_stream") or (region or {}).get("single_stream") or {}
        samples = [s for r in runs for s in (r.get("samples") or [])]
        cms = [s["connect_ms"] for s in samples if s.get("connect_ms") is not None]
        errs = sum(len(r.get("errors") or []) for r in runs)
        out[d] = {"bulk": bulk.get("mib_per_sec"), "conc": bulk.get("concurrency"),
                  "single": single.get("mib_per_sec") or ss.get("mib_per_sec"),
                  "expected": ss.get("expected_mib_per_sec"),
                  "ratio": ss.get("single_to_expected"),
                  "finding": ss.get("finding"), "connect_ms": st.median(cms) if cms else None,
                  "n_parts": len(samples), "errors": errs}
    return out

a, b = load(sys.argv[1]), load(sys.argv[2])
for path in (sys.argv[1], sys.argv[2]):
    try:
        meta = dict(l.strip().split("=", 1) for l in open(f"{path}/ab.meta") if "=" in l)
        print(f"meta {path}: code_hash={meta.get('code_hash','?')[:12]} ts={meta.get('ts','?')}")
    except OSError:
        print(f"meta {path}: none (pre-existing run dir)")
print()

def row(metric, key, fmt="{:.1f}"):
    def cell(side, d):
        v = side.get(d, {}).get(key)
        if v is None:
            return "-"
        if isinstance(v, (int, float)):
            return fmt.format(v)
        return str(v)
    print(f"{metric:<28} {cell(a,'up'):>9} {cell(b,'up'):>9}   {cell(a,'down'):>9} {cell(b,'down'):>9}")

print(f"{'':<28} {'A up':>9} {'B up':>9}   {'A down':>9} {'B down':>9}")
print("-" * 68)
row("single-stream MiB/s", "single")
row("bulk MiB/s (max conc)", "bulk")
row("median connect_ms/part", "connect_ms", fmt="{:.1f}")
row("single_to_expected", "ratio", fmt="{:.3f}")
row("transfer errors", "errors", fmt="{}")

def delta(d, key):
    av, bv = a.get(d, {}).get(key), b.get(d, {}).get(key)
    if not av or not bv: return None
    return bv / av

print()
verdicts = []
for d in ("up", "down"):
    s = delta(d, "single")
    c = delta(d, "connect_ms")
    if s is None: verdicts.append(f"{d}: no data"); continue
    if s >= 1.25 or (s >= 1.10 and c and c <= 0.5):
        v = "IMPROVED"
    elif s <= 0.90:
        v = "REGRESSED"
    else:
        v = "within noise (+/-10%)"
    verdicts.append(f"{d}: single x{s:.2f}, connect x{c:.2f} -> {v}" if c else f"{d}: single x{s:.2f} -> {v}")
print("\n".join(verdicts))
improved = sum(1 for v in verdicts if "IMPROVED" in v)
regressed = sum(1 for v in verdicts if "REGRESSED" in v)
print()
if regressed: print("VERDICT: REGRESSED - do not keep this change")
elif improved == 2 or (improved == 1 and len([v for v in verdicts if "noise" in v]) == 1):
    print("VERDICT: HELPED - confirm with one certify run before claiming")
else: print("VERDICT: INCONCLUSIVE - calibrate noise with two same-code baselines")
if a.get("up", {}).get("finding") and "window/loss defect" in str(a["up"]["finding"]):
    still = "window/loss defect" in str(b.get("up", {}).get("finding") or "")
    print(f"upload window-defect finding: {'STILL PRESENT' if still else 'CLEARED'}")
PY
;;
*)
    sed -n '2,8p' "$0"; exit 2 ;;
esac
