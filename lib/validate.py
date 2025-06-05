import re
from lib.utils import SUPPORTED_FORMATS, MAX_VIDEO_RESOLUTION


def validate_url(url):
    if not url:
        raise ValueError("URL is required")
    if not re.match(r'https?://', url):
        raise ValueError("Invalid URL format")
    return True

def validate_format(target_format):
    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {target_format}. Supported formats: {SUPPORTED_FORMATS}")
    return True

def validate_times(start_time, end_time):
    if start_time is not None and start_time < 0:
        raise ValueError(f"Invalid start time: {start_time}")
    if end_time is not None and end_time < 0:
        raise ValueError(f"Invalid end time: {end_time}")
    if start_time is not None and end_time is not None and start_time >= end_time:
        raise ValueError(f"Start time must be less than end time. Got start={start_time}, end={end_time}")
    return True

def validate_framerate(framerate):
    if framerate is not None:
        if not isinstance(framerate, int) or framerate <= 0:
            raise ValueError(f"Invalid framerate: {framerate}. It must be a positive integer.")
        if framerate > 60:
            raise ValueError("Framerate must be less than or equal to 60")
    return True

def validate_resolution(resolution):
    if resolution:
        if len(resolution.split('x')) != 2:
            raise ValueError("Invalid resolution format. Use <width>x<height>")
        if not all(x.isdigit() for x in resolution.split('x')):
            raise ValueError("Resolution values must be positive integers.")
        width, height = map(int, resolution.split('x'))
        if width <= 0 or height <= 0:
            raise ValueError("Resolution values must be positive.")
        if width > MAX_VIDEO_RESOLUTION or height > MAX_VIDEO_RESOLUTION:
            raise ValueError(f"Resolution values must be less than or equal to {MAX_VIDEO_RESOLUTION}")
        if width * height > MAX_VIDEO_RESOLUTION**2:
            raise ValueError(f"Total resolution must be less than or equal to {MAX_VIDEO_RESOLUTION}x{MAX_VIDEO_RESOLUTION}")
    return True