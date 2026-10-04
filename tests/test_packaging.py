from pathlib import Path
import subprocess
import sys


def test_package_smoke():
    import rack_bench

    assert rack_bench is not None
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[1] / "main.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Hello from rack-bench!"
