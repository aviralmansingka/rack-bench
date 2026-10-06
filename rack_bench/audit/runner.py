"""Explicit audit dispatch, ordered collection and name-based filtering."""
from fnmatch import fnmatchcase
from functools import partial
import socket

from rack_bench.common.host import operation_echo
from rack_bench.common.models import Result
from rack_bench.common.output import emit, show_operation

from . import system, topology

# CLI subcommand name -> scope module exposing CHECKS: {check name -> probe fn}
SCOPES = {
    "topology": topology,
    "system": system,
}


def collect(scope=None, *, only=(), skip=(), show_command=False):
    results = []
    for name in [scope] if scope else SCOPES:
        result = Result(scope=name, host=socket.gethostname())
        for check_name, probe in SCOPES[name].CHECKS.items():
            if only and not any(fnmatchcase(check_name, pattern) for pattern in only):
                continue
            if any(fnmatchcase(check_name, pattern) for pattern in skip):
                continue
            token = operation_echo.set(partial(show_operation, check_name) if show_command else None)
            try:
                check = probe()
            finally:
                operation_echo.reset(token)
            if check.name != check_name:
                raise ValueError(f"Registered check {check_name} returned mismatched name {check.name}.")
            result.checks.append(check)
            if name == "software" and check.status in ("pass", "warn") and check.value is not None:
                result.manifest[check_name.removeprefix("software.")] = check.value
        results.append(result)
    if SCOPES and not any(result.checks for result in results):
        raise ValueError("No audit checks matched --only/--skip.")
    return results


def run(scope=None, *, only=(), skip=(), json_target=None, run_dir=None, show_command=False, quiet=False):
    results = collect(scope, only=only, skip=skip, show_command=show_command and not quiet)
    emit(results, stage="audit", json_target=json_target, run_dir=run_dir, quiet=quiet)
    return int(any(check.status == "fail" for result in results for check in result.checks))
