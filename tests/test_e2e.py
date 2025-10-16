"""End-to-end tests for the azip CLI.

These tests perform real HTTP requests to verify the entire workflow.
They are slower than unit tests and may fail if the external service is unavailable.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from azip.downloader import download_json


@pytest.mark.e2e
def test_download_json_e2e(tmp_path: Path) -> None:
    """Test downloading the actual JSON file from Microsoft.

    This is a real E2E test that makes actual HTTP requests.
    It may be slow and can fail if the service is unavailable.
    """
    destination = tmp_path / "ServiceTags.json"

    # Perform real download
    result = download_json(destination=destination, timeout_s=30)

    # Verify the file was created
    assert result.exists()
    assert result.is_file()

    # Verify it's a valid JSON file
    with result.open() as f:
        data = json.load(f)

    # Basic structure validation
    assert "changeNumber" in data
    assert "cloud" in data
    assert "values" in data
    assert isinstance(data["values"], list)

    # Verify file size is reasonable (should be multiple MB)
    assert result.stat().st_size > 100_000  # At least 100KB


@pytest.mark.e2e
def test_cli_command_e2e(tmp_path: Path) -> None:
    """Test the CLI command end-to-end using subprocess.

    This verifies the entire CLI flow including command parsing.
    """
    import subprocess
    import sys

    destination = tmp_path / "test_output.json"

    # Run the CLI command using the current Python interpreter
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "azip",
            "get",
            "-f",
            str(destination),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Check command succeeded
    assert result.returncode == 0
    assert "Downloaded file saved to" in result.stdout

    # Verify the file was created
    assert destination.exists()

    # Verify it's valid JSON
    with destination.open() as f:
        data = json.load(f)

    assert "changeNumber" in data
