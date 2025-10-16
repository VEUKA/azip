from __future__ import annotations

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from azip.downloader import (
    MICROSOFT_DOWNLOAD_URL,
    DownloadError,
    _extract_download_url,
    _target_path,
)


def test_target_path_with_none_destination() -> None:
    """Test _target_path when destination is None."""
    result = _target_path(None, "test.json")
    assert result == Path.cwd() / "test.json"


def test_target_path_with_file_destination(tmp_path: Path) -> None:
    """Test _target_path with a file destination."""
    destination = tmp_path / "output.json"
    result = _target_path(destination, "test.json")
    assert result == destination


def test_target_path_with_directory_destination(tmp_path: Path) -> None:
    """Test _target_path with a directory destination."""
    destination = tmp_path
    destination.mkdir(exist_ok=True)
    result = _target_path(destination, "test.json")
    assert result == destination / "test.json"


def test_target_path_creates_parent_directories(tmp_path: Path) -> None:
    """Test that _target_path creates parent directories."""
    destination = tmp_path / "subdir" / "nested" / "output.json"
    result = _target_path(destination, "test.json")
    assert result == destination
    assert result.parent.exists()


def test_extract_download_url_with_json_link() -> None:
    """Test _extract_download_url successfully extracts URL from link."""
    html = """
    <html>
        <body>
            <a href="/downloads/file.json">Download JSON</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://example.com/page"

    result = _extract_download_url(soup, base_url)

    assert result == "https://example.com/downloads/file.json"


def test_extract_download_url_with_absolute_url() -> None:
    """Test _extract_download_url with absolute URL."""
    html = """
    <html>
        <body>
            <a href="https://cdn.example.com/data.json">Download</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://example.com/page"

    result = _extract_download_url(soup, base_url)

    assert result == "https://cdn.example.com/data.json"


def test_extract_download_url_prefers_exact_match() -> None:
    """Test that _extract_download_url prefers links ending with .json."""
    html = """
    <html>
        <body>
            <a href="/api?format=json&data=something">API</a>
            <a href="/downloads/ServiceTags.json">Download JSON</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://example.com/"

    result = _extract_download_url(soup, base_url)

    # Should prefer the one ending with .json
    assert result.endswith("ServiceTags.json")


def test_extract_download_url_no_links_raises_error() -> None:
    """Test _extract_download_url raises error when no JSON link found."""
    html = """
    <html>
        <body>
            <a href="/downloads/file.pdf">Download PDF</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://example.com/page"

    with pytest.raises(DownloadError, match="JSON download link was not found"):
        _extract_download_url(soup, base_url)


def test_extract_download_url_empty_href_raises_error() -> None:
    """Test _extract_download_url raises error when href is empty."""
    html = """
    <html>
        <body>
            <a href="">Download JSON</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://example.com/page"

    # Empty href won't match the .json pattern, so we get "not found" error
    with pytest.raises(DownloadError, match="JSON download link was not found"):
        _extract_download_url(soup, base_url)


def test_microsoft_download_url_constant() -> None:
    """Test that the Microsoft download URL constant is defined."""
    assert isinstance(MICROSOFT_DOWNLOAD_URL, str)
    assert "microsoft.com" in MICROSOFT_DOWNLOAD_URL.lower()
    assert "download" in MICROSOFT_DOWNLOAD_URL.lower()


def test_download_error_is_exception() -> None:
    """Test that DownloadError is a proper exception."""
    error = DownloadError("Test error")
    assert isinstance(error, Exception)
    assert str(error) == "Test error"
