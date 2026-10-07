from pathlib import Path
import subprocess
import sys


def test_internet_package_exports():
    from rack_bench.bench import internet
    from rack_bench.bench.internet import cli

    assert Path(internet.__file__).name == "__init__.py"
    assert callable(cli.add_arguments)
    for name in ("add_arguments", "options_from_args", "before_run", "cost_estimate",
                 "Options", "PROVIDERS", "DIRECTIONS"):
        assert getattr(internet, name) is getattr(cli, name)


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
        assert "bench" in result.stdout
