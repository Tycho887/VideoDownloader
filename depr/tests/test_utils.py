import pytest
import os
from lib.utils.constants import DOWNLOAD_FOLDER as download_folder

from lib import (
    get_source,
    process_media,
    download_media,
    remove_files,
    extract_arguments,
)

@pytest.fixture
def setup_download_folder():
    os.makedirs(download_folder, exist_ok=True)
    yield download_folder
    remove_files()


def test_get_source_youtube():
    url = "https://www.youtube.com/watch?v=example"
    assert get_source(url) == "youtube"


def test_get_source_twitter():
    url = "https://x.com/example/status/12345"
    assert get_source(url) == "twitter"


def test_get_source_invalid():
    url = "https://example.com"
    with pytest.raises(ValueError, match="Unsupported URL source. Supported sources are YouTube and Twitter."):
        get_source(url)


def test_extract_arguments():
    args = "https://example.com format=mp4 start=10 end=20 resolution=1920x1080"
    url, options = extract_arguments(args)
    assert url == "https://example.com"
    assert options["format"] == "mp4"
    assert options["start"] == "10"
    assert options["end"] == "20"
    assert options["resolution"] == "1920x1080"


def test_process_media_invalid_file():
    with pytest.raises(FileNotFoundError, match="File does not exist:"):
        process_media("nonexistent_file.mp4", 0, 10, "mp4")


def test_process_media_invalid_format():
    with pytest.raises(ValueError, match=f"unsupported format: avi"):
        process_media("tests/data/test.mp4", 0, 10, "avi")


def test_download_media_invalid_url():
    with pytest.raises(ValueError, match="URL is required"):
        download_media("", "mp4")


def test_remove_files(setup_download_folder):
    test_file = os.path.join(setup_download_folder, "test.mp4")
    with open(test_file, "w") as f:
        f.write("dummy data")
    assert os.path.exists(test_file)
    remove_files()
    assert not os.path.exists(test_file)
