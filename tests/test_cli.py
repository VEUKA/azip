from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from azip.cli import app, main
from azip.downloader import DownloadError


@pytest.fixture(name="runner")
def fixture_runner() -> CliRunner:
    return CliRunner()


def test_get_command_with_filename(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    runner: CliRunner,
) -> None:
    captured: dict[str, object] = {}

    def fake_download(
        destination: Path | None,
        *,
        source_url: str,
        timeout_s: int,
    ) -> Path:  # type: ignore[override]
        captured["destination"] = destination
        captured["source_url"] = source_url
        captured["timeout_s"] = timeout_s
        # Return the destination path that was passed in
        if destination:
            destination.write_text("{}", encoding="utf-8")
            return destination
        # Fallback if no destination provided
        target = tmp_path / "custom.json"
        target.write_text("{}", encoding="utf-8")
        return target

    monkeypatch.setattr("azip.cli.download_json", fake_download)

    target_path = tmp_path / "requested.json"
    result = runner.invoke(app, ["get", "--filename", str(target_path)])

    assert result.exit_code == 0
    assert "requested.json" in result.stdout
    assert captured["destination"] == target_path
    source_url = captured.get("source_url")
    assert isinstance(source_url, str)
    assert "microsoft.com" in source_url


def test_get_command_default_filename(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    runner: CliRunner,
) -> None:
    def fake_download(
        destination: Path | None,
        *,
        source_url: str,
        timeout_s: int,
    ) -> Path:  # type: ignore[override]
        assert destination is None
        target = tmp_path / "download.json"
        target.write_text("{}", encoding="utf-8")
        return target

    monkeypatch.setattr("azip.cli.download_json", fake_download)

    result = runner.invoke(app, ["get"])

    assert result.exit_code == 0
    assert "download.json" in result.stdout


def test_get_command_with_download_error(
    monkeypatch: pytest.MonkeyPatch,
    runner: CliRunner,
) -> None:
    """Test that DownloadError is handled gracefully."""

    def fake_download_error(
        destination: Path | None,
        *,
        source_url: str,
        timeout_s: int,
    ) -> Path:  # type: ignore[override]
        raise DownloadError("Simulated download failure")

    monkeypatch.setattr("azip.cli.download_json", fake_download_error)

    result = runner.invoke(app, ["get"])

    assert result.exit_code == 1
    # Error message goes to stdout in typer's CliRunner
    output = result.stdout + result.stderr
    assert "Error:" in output or "Simulated download failure" in output


def test_get_command_with_custom_source_url(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    runner: CliRunner,
) -> None:
    """Test that custom source URL is passed to download_json."""
    captured: dict[str, object] = {}

    def fake_download(
        destination: Path | None,
        *,
        source_url: str,
        timeout_s: int,
    ) -> Path:  # type: ignore[override]
        captured["source_url"] = source_url
        target = tmp_path / "test.json"
        target.write_text("{}", encoding="utf-8")
        return target

    monkeypatch.setattr("azip.cli.download_json", fake_download)

    custom_url = "https://example.com/custom"
    result = runner.invoke(app, ["get", "--source-url", custom_url])

    assert result.exit_code == 0
    assert captured["source_url"] == custom_url


def test_main_function(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the main() entry point function."""
    called = []

    def fake_app() -> None:
        called.append(True)

    monkeypatch.setattr("azip.cli.app", fake_app)

    main()

    assert len(called) == 1


def test_app_requires_subcommand(runner: CliRunner) -> None:
    """Test that running the app without a subcommand shows help."""
    result = runner.invoke(app, [])

    # When no command is provided, Typer shows help or errors
    assert result.exit_code != 0 or "Usage:" in result.stdout
