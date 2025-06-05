import pytest
import os
from lib import (
    download_media,
    extract_arguments,
    validate_url,
    validate_format,
    validate_times,
    validate_resolution,
)

@pytest.fixture
def setup_download_folder():
    folder = "downloads"
    os.makedirs(folder, exist_ok=True)
    yield folder
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))
    os.rmdir(folder)

def test_download_valid_youtube():
    url = "https://www.youtube.com/watch?v=hMgq4wDKTqc"
    options = "format=mp4 start=0 end=10 resolution=1920x1080"
    args = f"{url} {options}"
    url, extracted_options = extract_arguments(args)
    result, _ = download_media(
        url=url,
        target_format=extracted_options['format'],
        start_time=float(extracted_options['start']),
        end_time=float(extracted_options['end']),
        resolution=tuple(map(int, extracted_options['resolution'].split('x'))),
    )
    assert os.path.exists(result)
    os.remove(result)

def test_download_invalid_url():
    with pytest.raises(ValueError, match="Invalid URL format"):
        validate_url("not_a_url")

def test_download_unsupported_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        validate_format("avi")

def test_download_large_resolution():
    with pytest.raises(ValueError, match="Resolution values must be less than or equal to"):
        validate_resolution("3840x2160")

def test_download_negative_times():
    with pytest.raises(ValueError, match="Invalid start time"):
        validate_times(-5, 10)
    with pytest.raises(ValueError, match="Invalid end time"):
        validate_times(5, -10)

def test_download_start_greater_than_end():
    with pytest.raises(ValueError, match="Start time must be less than end time"):
        validate_times(15, 10)

def test_download_edge_case_resolution():
    # Very small resolution
    resolution = "1x1"
    assert validate_resolution(resolution)

    # Valid maximum resolution
    resolution = "1920x1080"
    assert validate_resolution(resolution)

# def test_download_large_files(setup_download_folder):
#     # Simulate downloading a large file (e.g., by mocking or providing a large file)
#     url = "https://www.youtube.com/watch?v=2Zdyu2lE-dM"
#     options = "format=mp4 start=0 end=300 resolution=1920x1080"
#     args = f"{url} {options}"
#     url, extracted_options = extract_arguments(args)
#     with pytest.raises(ValueError, match="File size too large"):
#         download_media(
#             url=url,
#             target_format=extracted_options['format'],
#             start_time=float(extracted_options['start']),
#             end_time=float(extracted_options['end']),
#             resolution=tuple(map(int, extracted_options['resolution'].split('x'))),
#         )

# def test_download_missing_arguments():
#     args = "format=mp4 start=0 end=10"
#     with pytest.raises(ValueError, match="URL is required"):
#         url, _ = extract_arguments(args)

#     args = "https://www.youtube.com/watch?v=hMgq4wDKTqc start=10 end=20"
#     with pytest.raises(ValueError, match="Unsupported format"):
#         url, options = extract_arguments(args)
#         validate_format(options['format'])

def test_download_varied_inputs():
    valid_inputs = [
        "https://www.youtube.com/watch?v=hMgq4wDKTqc format=mp4 start=0 end=10 resolution=1920x1080",
        "https://x.com/CanYouPetTheDog/status/1876021679148957917 format=gif start=0 end=15 resolution=640x480",
        "https://www.youtube.com/watch?v=hMgq4wDKTqc format=mp3 start=5 end=60",
    ]
    for args in valid_inputs:
        url, options = extract_arguments(args)
        assert validate_url(url)
        assert validate_format(options['format'])
        assert validate_times(float(options['start']), float(options['end']))
        if 'resolution' in options and options['resolution']:
            assert validate_resolution(options['resolution'])
