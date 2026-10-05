"""Small read-only command and file helpers; no source-specific parsing."""
from contextvars import ContextVar
from fnmatch import fnmatchcase
import importlib.metadata
import os
from pathlib import Path
import shlex
import signal
import subprocess

from .models import Check

# Optional operation observer. The caller supplies attribution; this module knows no scopes/flags.
operation_echo = ContextVar("operation_echo", default=None)


def _echo(operation):
    callback = operation_echo.get()
    if callback is not None:
        callback(operation)


class Unavailable(Exception):
    def __init__(self, source: str, detail: str):
        super().__init__(detail)
        self.source = source


def _stop(proc):
    """Bound cleanup too: a driver stuck in kernel space may not honor SIGKILL."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        proc.communicate(timeout=0.25)
        return True
    except (subprocess.TimeoutExpired, OSError, UnicodeError):
        # Never enter Popen.__exit__ or an unbounded wait for a wedged driver.
        if proc.stdout:
            proc.stdout.close()
        if proc.stderr:
            proc.stderr.close()
        return False


def dist_versions(globs):
    """{distribution: version} for installed Python distributions matching fnmatch globs."""
    found = {}
    try:
        installed = importlib.metadata.distributions()
    except Exception:
        return found
    for dist in installed:
        name = (dist.metadata["Name"] or "").strip().lower()
        if name and any(fnmatchcase(name, str(glob).lower()) for glob in globs):
            found[name] = dist.version
    return found


def run_command(args: list[str], timeout: float = 10, *, ok_codes=(0,)) -> str:
    source = shlex.join(args)
    _echo(source)
    proc = None
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                start_new_session=True, env={**os.environ, "LC_ALL": "C"})
        stdout, stderr = proc.communicate(timeout=timeout)
    except FileNotFoundError as exc:
        raise Unavailable(source, f"Command not found: {args[0]}.") from exc
    except subprocess.TimeoutExpired as exc:
        stopped = _stop(proc) if proc is not None else True
        detail = f"Command timed out after {timeout:g}s."
        if not stopped:
            detail += " Kill requested but process remained unresponsive; possible driver/kernel hang."
        raise Unavailable(source, detail) from exc
    except (OSError, UnicodeError) as exc:
        if proc is not None and proc.poll() is None:
            _stop(proc)
        raise Unavailable(source, f"Cannot execute command: {exc}.") from exc
    if proc.returncode not in ok_codes:
        reason = stderr.strip()[:300] or "source unavailable or permission denied"
        raise Unavailable(source, f"Command exited {proc.returncode}: {reason}")
    return stdout.strip()


def read_text(path: str | Path) -> str:
    _echo(f"read {path}")
    try:
        return Path(path).read_text().strip()
    except (OSError, UnicodeError) as exc:
        raise Unavailable(str(path), f"Cannot read {path}: {exc}.") from exc


def collect_check(name, collect, source):
    """Convert shared I/O/decoding failures to checks; parsing stays with callers."""
    try:
        value = collect()
    except Unavailable as exc:
        evidence = list(dict.fromkeys([*source, exc.source]))
        return Check(name, "skip", detail=str(exc), source=evidence)
    except (ValueError, KeyError, TypeError, IndexError, SyntaxError) as exc:
        return Check(name, "skip", detail=f"Cannot decode source ({type(exc).__name__}).", source=source)
    except OSError as exc:
        return Check(name, "skip", detail=f"Cannot inspect source: {exc}.", source=source)
    if value is None or value == "" or value == [] or value == {}:
        return Check(name, "skip", detail="No supported devices/data exposed by source.", source=source)
    return Check(name, "pass", value=value, detail="Successfully observed; no certification profile applied.", source=source)
