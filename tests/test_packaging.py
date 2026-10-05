from pathlib import Path
import subprocess
import sys


def test_package_smoke():
    import rack_bench

    assert rack_bench is not None
    for command in (
        [sys.executable, str(Path(__file__).resolve().parents[1] / "main.py")],
        [sys.executable, "-m", "rack_bench"],
        ["rack-bench"],
    ):
        result = subprocess.run([*command, "--help"], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "usage: rack-bench" in result.stdout
        assert "audit" in result.stdout
