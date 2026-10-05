"""Host helper tests extracted from the audit-stage CLI, scope and system tests."""
import subprocess
import unittest
from unittest.mock import Mock, call, patch

from rack_bench.common.host import (
    Unavailable, collect_check, operation_echo, read_text, run_command,
)


class HostTests(unittest.TestCase):
    def test_command_errors_have_evidence(self):
        for error in (FileNotFoundError(), subprocess.TimeoutExpired("lscpu", 10)):
            with self.subTest(error=error), patch("subprocess.Popen", side_effect=error):
                with self.assertRaises(Unavailable) as caught:
                    run_command(["lscpu", "--json"])
                self.assertEqual(caught.exception.source, "lscpu --json")
        with patch("subprocess.Popen", return_value=Mock(returncode=1, communicate=Mock(return_value=("", "Permission denied")))):
            with self.assertRaises(Unavailable) as caught:
                run_command(["dmidecode", "--type", "memory"])
            self.assertIn("Permission denied", str(caught.exception))

    def test_file_permission_failure(self):
        with patch("pathlib.Path.read_text", side_effect=PermissionError("denied")):
            with self.assertRaises(Unavailable) as caught:
                read_text("/proc/meminfo")
            self.assertEqual(caught.exception.source, "/proc/meminfo")

    def test_timeout_cleanup_is_bounded_even_if_sigkill_cannot_reap_child(self):
        proc = Mock(pid=123456)
        proc.communicate.side_effect = subprocess.TimeoutExpired("example", 1)
        with patch("subprocess.Popen", return_value=proc), patch("os.killpg"):
            with self.assertRaises(Unavailable) as caught:
                run_command(["example"], timeout=1)
        self.assertIn("remained unresponsive", str(caught.exception))
        self.assertEqual(proc.communicate.call_count, 2)
        proc.wait.assert_not_called()
        proc.stdout.close.assert_called_once()

    def test_collect_check_handles_parse_errors(self):
        def parse():
            raise ValueError("bad source")
        check = collect_check("example", parse, ["example source"])
        self.assertEqual(check.status, "skip")

    def test_operation_echo_observes_commands_and_file_reads(self):
        observer = Mock()
        token = operation_echo.set(observer)
        try:
            with patch("subprocess.Popen", return_value=Mock(returncode=0, communicate=Mock(return_value=("ok", "")))), \
                 patch("pathlib.Path.read_text", return_value="ok"):
                run_command(["example", "argument with spaces"])
                read_text("/proc/example")
        finally:
            operation_echo.reset(token)
        self.assertEqual(observer.call_args_list, [
            call("example 'argument with spaces'"), call("read /proc/example"),
        ])


if __name__ == "__main__":
    unittest.main()
