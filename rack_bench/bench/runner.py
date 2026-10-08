"""Explicit bench dispatch, ordered collection and name-based filtering."""
from fnmatch import fnmatchcase
from functools import partial
import socket

from rack_bench.common.host import operation_echo
from rack_bench.common.models import Result
from rack_bench.common.output import emit, show_operation

from . import internet

# Category modules own Options, add_arguments, options_from_args, and CHECKS.
# Optional selected_checks(options) and before_run(options) hooks own policy.
CATEGORIES = {"internet": internet}


def add_categories(parser, *, parents):
    categories = parser.add_subparsers(dest="category")
    for name, module in CATEGORIES.items():
        module.add_arguments(categories.add_parser(name, parents=parents))


def options_from_args(args):
    return CATEGORIES[args.category].options_from_args(args) if args.category else None


def collect(category=None, *, options=None, only=(), skip=(), show_command=False):
    if category is None and options is not None:
        raise ValueError("Category-specific options require a category.")
    selected = [(name, CATEGORIES[name], options if options is not None else CATEGORIES[name].Options())
                for name in ([category] if category else CATEGORIES)]
    # Gate every selected category before any probe, including full-stage runs.
    for name, module, category_options in selected:
        if hasattr(module, "before_run"):
            module.before_run(category_options)
    results = []
    for name, module, category_options in selected:
        result = Result(scope=name, host=socket.gethostname())
        checks = module.selected_checks(category_options) if hasattr(module, "selected_checks") else module.CHECKS.items()
        try:
            for check_name, probe in checks:
                if only and not any(fnmatchcase(check_name, pattern) for pattern in only):
                    continue
                if any(fnmatchcase(check_name, pattern) for pattern in skip):
                    continue
                token = operation_echo.set(partial(show_operation, check_name) if show_command else None)
                try:
                    check = probe(category_options)
                finally:
                    operation_echo.reset(token)
                if check.name != check_name:
                    raise ValueError(f"Registered check {check_name} returned mismatched name {check.name}.")
                result.checks.append(check)
        finally:
            if hasattr(module, "after_run"):
                token = operation_echo.set(partial(show_operation, f"{name}.cleanup") if show_command else None)
                try:
                    module.after_run(category_options, result)
                finally:
                    operation_echo.reset(token)
        results.append(result)
    if CATEGORIES and not any(result.checks for result in results):
        raise ValueError("No bench checks matched the selection.")
    return results


def run(category=None, *, options=None, only=(), skip=(), json_target=None, run_dir=None,
        show_command=False, quiet=False):
    results = collect(category, options=options, only=only, skip=skip,
                      show_command=show_command and not quiet)
    emit(results, stage="bench", json_target=json_target, run_dir=run_dir, quiet=quiet)
    return int(any(check.status == "fail" for result in results for check in result.checks))
