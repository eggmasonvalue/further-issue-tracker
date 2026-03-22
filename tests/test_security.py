from pathlib import Path, PureWindowsPath, PurePosixPath
from urllib.parse import urlparse
import os
import pytest

def get_filename(xbrl_url):
    parsed_url = urlparse(xbrl_url)
    # The fix we implemented in the codebase uses Path(parsed_url.path).name
    filename = Path(parsed_url.path).name
    return filename

def test_normal_url():
    assert get_filename("https://example.com/data/report.xml") == "report.xml"

def test_path_traversal_unix():
    assert get_filename("https://example.com/../../etc/passwd") == "passwd"

def test_path_traversal_windows_logic():
    # Simulate Windows Path behavior
    url = "https://example.com/..\\..\\..\\windows\\system32\\cmd.exe"
    parsed = urlparse(url)
    filename = PureWindowsPath(parsed.path).name
    assert filename == "cmd.exe"

def test_query_params():
    assert get_filename("https://example.com/api/get?file=test.xml") == "get"

def test_empty_path():
    assert get_filename("https://example.com/") == ""
