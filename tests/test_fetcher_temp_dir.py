import os
from pathlib import Path
from types import SimpleNamespace
from nse_corporate_data.fetcher import NSEFetcher


def test_fetcher_creates_and_deletes_temp_dir():
    # Arrange & Act
    fetcher = NSEFetcher()

    # Assert
    assert fetcher._temp_dir is not None
    assert os.path.exists(fetcher._temp_dir)
    assert Path(fetcher._temp_dir).is_dir()

    # Act
    temp_dir_path = fetcher._temp_dir
    fetcher.close()

    # Assert
    assert not os.path.exists(temp_dir_path)


def test_fetcher_uses_provided_download_folder(tmp_path):
    # Arrange
    custom_dir = str(tmp_path / "custom_downloads")

    # Act
    fetcher = NSEFetcher(download_folder=custom_dir)

    # Assert
    assert fetcher._temp_dir is None
    assert fetcher.download_folder == Path(custom_dir)
    assert fetcher.download_folder.exists()

    # Act
    fetcher.close()

    # Assert
    # The provided directory shouldn't be deleted by the fetcher
    assert os.path.exists(custom_dir)


def test_get_quote_uses_fetcher_cache():
    # Arrange
    calls = []
    fetcher = NSEFetcher.__new__(NSEFetcher)
    fetcher._quote_cache = {}
    fetcher.nse = SimpleNamespace(
        quote=lambda symbol: calls.append(symbol) or {"priceInfo": {"close": 123.45}}
    )

    # Act
    first = fetcher.get_quote("ABC")
    second = fetcher.get_quote("ABC")

    # Assert
    assert first == {"priceInfo": {"close": 123.45}}
    assert second == {"priceInfo": {"close": 123.45}}
    assert calls == ["ABC"]
