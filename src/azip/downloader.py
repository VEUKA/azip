from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

console = Console()

MICROSOFT_DOWNLOAD_URL = (
    "https://www.microsoft.com/en-us/download/details.aspx?id=56519"
)
_DOWNLOAD_TIMEOUT_S = 60
_DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class DownloadError(Exception):
    """Raised when the JSON download cannot be completed."""


def download_json(
    destination: Optional[Path] = None,
    *,
    source_url: str = MICROSOFT_DOWNLOAD_URL,
    timeout_s: int = _DOWNLOAD_TIMEOUT_S,
) -> Path:
    """Download the target JSON file from the Microsoft download page.

    Args:
        destination: Optional path (including filename) to save the JSON file.
        source_url: URL of the Microsoft download page.
        timeout_s: Timeout in seconds for HTTP requests.

    Raises:
        DownloadError: If the download cannot be located or saved.

    Returns:
        Path to the downloaded JSON file.
    """

    maybe_destination: Optional[Path] = Path(destination) if destination else None

    try:
        # Fetch the download page
        console.print("[cyan]🌐 Opening download page...[/cyan]")
        console.print(f"   [dim]{source_url}[/dim]")

        session = requests.Session()
        session.headers.update({"User-Agent": _DEFAULT_USER_AGENT})

        response = session.get(source_url, timeout=timeout_s)
        response.raise_for_status()

        console.print("[green]✓[/green] Page loaded successfully")

        # Parse HTML to find JSON download link
        console.print("[cyan]🔍 Searching for JSON download link...[/cyan]")
        soup = BeautifulSoup(response.text, "html.parser")
        download_url = _extract_download_url(soup, source_url)

        console.print(
            f"[green]✓[/green] Found JSON file: [bold]{Path(urlparse(download_url).path).name}[/bold]"
        )
        console.print(f"   [dim]{download_url}[/dim]")

        # Download the JSON file
        console.print("[cyan]📥 Downloading file...[/cyan]")
        download_path = _download_file(
            session, download_url, maybe_destination, timeout_s
        )
        return download_path

    except requests.RequestException as exc:
        console.print("[red]✗ Failed to fetch download page[/red]")
        raise DownloadError(f"Failed to fetch download page: {exc}") from exc


def _target_path(maybe_destination: Optional[Path], suggested_name: str) -> Path:
    if maybe_destination is None:
        target = Path.cwd() / suggested_name
    else:
        target = maybe_destination
        if target.is_dir():
            target = target / suggested_name
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _extract_download_url(soup: BeautifulSoup, base_url: str) -> str:
    """Extract the JSON download URL from the parsed HTML.

    Args:
        soup: BeautifulSoup parsed HTML
        base_url: Base URL for resolving relative links

    Returns:
        Absolute URL to the JSON file

    Raises:
        DownloadError: If no JSON link is found
    """
    # Look for links ending with .json or containing .json in href
    json_links = soup.find_all("a", href=re.compile(r"\.json", re.IGNORECASE))

    if not json_links:
        raise DownloadError("JSON download link was not found on the page.")

    # Prefer links that end with .json
    for link in json_links:
        href = link.get("href", "")
        if href.endswith(".json"):
            return urljoin(base_url, href)

    # Fall back to any link containing .json
    href = json_links[0].get("href", "")
    if not href:
        raise DownloadError("JSON link did not contain a valid href attribute.")

    return urljoin(base_url, href)


def _download_file(
    session: requests.Session,
    download_url: str,
    maybe_destination: Optional[Path],
    timeout_s: int,
) -> Path:
    """Download the file from the given URL.

    Args:
        session: Requests session to use
        download_url: URL to download from
        maybe_destination: Optional destination path
        timeout_s: Timeout in seconds

    Returns:
        Path to the downloaded file

    Raises:
        DownloadError: If download fails
    """
    try:
        response = session.get(download_url, timeout=timeout_s, stream=True)
        response.raise_for_status()

        # Extract filename from URL
        suggested_name = Path(urlparse(download_url).path).name or "download.json"
        target = _target_path(maybe_destination, suggested_name)

        # Get file size if available
        total_size = int(response.headers.get("content-length", 0))

        # Write content to file with progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"   {suggested_name}", total=total_size)

            with open(target, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

        console.print(f"[green]✓[/green] Download complete: [bold]{target}[/bold]")

        # Show file size
        file_size = target.stat().st_size
        if file_size >= 1_000_000:
            size_str = f"{file_size / 1_000_000:.1f} MB"
        else:
            size_str = f"{file_size / 1_000:.1f} KB"
        console.print(f"   [dim]File size: {size_str}[/dim]")

        return target

    except requests.RequestException as exc:
        console.print("[red]✗ Download failed[/red]")
        raise DownloadError(f"Failed to download JSON file: {exc}") from exc
