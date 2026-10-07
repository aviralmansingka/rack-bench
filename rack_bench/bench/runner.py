"""Explicit bench dispatch, ordered collection and name-based filtering."""
from fnmatch import fnmatchcase
from functools import partial
import socket

from rack_bench.common.host import operation_echo
from rack_bench.common.models import Result
from rack_bench.common.output import emit, show_cost_estimate, show_operation

from . import internet

# CLI category name -> module exposing CHECKS: {check name -> probe(options)}
CATEGORIES = {"internet": internet}


def collect(category=None, *, options=None, only=(), skip=(), show_command=False):
    options = options if options is not None else internet.Options()
    results = []
    for name in [category] if category else CATEGORIES:
        result = Result(scope=name, host=socket.gethostname())
        for check_name, probe in CATEGORIES[name].CHECKS.items():
            if name == "internet" and check_name.split(".")[1] not in options.providers:
                continue
            if only and not any(fnmatchcase(check_name, pattern) for pattern in only):
                continue
            if any(fnmatchcase(check_name, pattern) for pattern in skip):
                continue
            token = operation_echo.set(partial(show_operation, check_name) if show_command else None)
            try:
                check = probe(options)
            finally:
                operation_echo.reset(token)
            if check.name != check_name:
                raise ValueError(f"Registered check {check_name} returned mismatched name {check.name}.")
            result.checks.append(check)
        results.append(result)
    if CATEGORIES and not any(result.checks for result in results):
        raise ValueError("No bench checks matched --only/--skip/providers.")
    return results


def run(category=None, *, options=None, only=(), skip=(), json_target=None, run_dir=None,
        show_command=False, quiet=False):
    options = options if options is not None else internet.Options()
    if (category is None or category == "internet") and options.profile == "certify":
        show_cost_estimate(internet.cost_estimate(options))
        if not options.yes:
            raise ValueError("The certify profile requires --yes to accept the cost estimate.")
    results = collect(category, options=options, only=only, skip=skip,
                      show_command=show_command and not quiet)
    emit(results, stage="bench", json_target=json_target, run_dir=run_dir, quiet=quiet)
    return int(any(check.status == "fail" for result in results for check in result.checks))
