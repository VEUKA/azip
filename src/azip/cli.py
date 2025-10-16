from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .downloader import MICROSOFT_DOWNLOAD_URL, DownloadError, download_json

app = typer.Typer(help="Command line utilities for Microsoft download automation.")


@app.callback(invoke_without_command=False)
def root() -> None:
    """Require a subcommand to be specified."""
    # No-op callback; Typer will display help when no command is provided.
    pass


@app.command()
def get(
    filename: Optional[Path] = typer.Option(
        None,
        "--filename",
        "-f",
        help="Path (including filename) to save the downloaded JSON.",
    ),
    source_url: str = typer.Option(
        MICROSOFT_DOWNLOAD_URL,
        "--source-url",
        help="Override the source download page URL.",
        hidden=True,
    ),
) -> None:
    """Download the JSON file from Microsoft."""

    try:
        saved_path = download_json(filename, source_url=source_url, timeout_s=60)
        # Additional simple message for scripts/automation
        typer.echo(f"Downloaded file saved to {saved_path}")
    except DownloadError as exc:
        typer.secho(f"Error: {exc}", err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc


def main() -> None:
    """Entry point for `python -m azip`."""

    app()
