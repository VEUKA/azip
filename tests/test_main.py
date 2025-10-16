from __future__ import annotations

import subprocess
import sys


def test_main_module_can_be_executed() -> None:
    """Test that the __main__ module can be executed via python -m azip."""
    # Test that we can at least import the module
    result = subprocess.run(
        [sys.executable, "-m", "azip", "--help"],
        capture_output=True,
        text=True,
    )

    # Should either show help or error (exit code 0 or 2 for missing subcommand)
    assert result.returncode in (0, 2)
    assert "Usage:" in result.stdout or "Usage:" in result.stderr
