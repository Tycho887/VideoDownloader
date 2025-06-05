import pytest
from utils import extract_arguments, seconds_to_hhmmss, remove_file, SUPPORTED_FORMATS
import os

# Argument Parsing Tests
@pytest.mark.parametrize("input,expected_url,expected_options", [
    (
        "https://youtube.com/watch?v=abc format=mp4 start=5 end=10 resolution=200x200",
        "https://youtube.com/watch?v=abc",
        {'format': 'mp4', 'start': '5', 'end': '10', 'resolution': '200x200'}
    ),
    (
        "start=15 end=30 https://vimeo.com/123 format=gif",
        "https://vimeo.com/123",
        {'format': 'gif', 'start': '15', 'end': '30'}
    ),
    (
        "https://tiktok.com/@user/video/123 framerate=30",
        "https://tiktok.com/@user/video/123",
        {'framerate': '30'}
    ),
    (
        "https://streamable.com/abc resolution=640x480 format=mp4",
        "https://streamable.com/abc",
        {'format': 'mp4', 'resolution': '640x480'}
    )
])
def test_argument_parsing(input, expected_url, expected_options):
    url, options = extract_arguments(input)
    assert url == expected_url
    for key, value in expected_options.items():
        assert options[key] == value

# Time Conversion Tests
@pytest.mark.parametrize("seconds,expected", [
    (0, "0:00:00"),
    (65, "0:01:05"),
    (3665, "1:01:05"),
    (9000, "2:30:00"),
    (None, None)
])
def test_seconds_conversion(seconds, expected):
    assert seconds_to_hhmmss(seconds) == expected

# File Cleanup Tests
def test_file_removal(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    
    # Test valid removal
    remove_file(str(test_file))
    assert not test_file.exists()
    
    # Test invalid file
    remove_file("non_existent_file.txt")  # Should not raise error