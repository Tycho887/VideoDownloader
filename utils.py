import re
import logging
import os

SUPPORTED_FORMATS = ("mp4", "mp3", "gif")
MAX_SIZE_MB = 10
MAX_GIF_FRAMES = 50
MAX_GIF_LENGTH = 30 # seconds
MAX_VIDEO_RESOLUTION = 1920
KNOWN_KEYS = ('format', 'start', 'end', 'resolution', 'framerate')
DOWNLOAD_FOLDER = "./downloads" #"/mnt/ramdisk"

def remove_files():
    # Remove all mp3, mp4, and gif files in the downloads folder
    for file in os.listdir(DOWNLOAD_FOLDER):
        if file.endswith(SUPPORTED_FORMATS):
            os.remove(os.path.join(DOWNLOAD_FOLDER, file))

def remove_file(file_path):
    if os.path.isfile(file_path) and file_path.endswith(SUPPORTED_FORMATS):
        os.remove(file_path)

def extract_arguments(args):
    """
    Extract arguments from a string using regex.

    Arguments:
    args -- string containing arguments

    Returns:
    url -- URL to download media from
    options -- dictionary containing specified options
    """
    # Parse arguments using regex
    pattern = r'(?P<url>https?://\S+)|(?P<key>\w+)=(?P<value>-?[a-zA-Z0-9_\.\:x]+)'
    matches = re.findall(pattern, args)

    # Initialize default values
    url = None
    options = {
        'format': 'mp4',
        'start': None,
        'end': None,
        'resolution': None,
        'framerate': None
    }

    # Process matches
    for match in matches:
        if match[0]:
            url = match[0]  # URL matched
        elif match[1] and match[2]:
            key, value = match[1], match[2]
            if key in options:
                options[key] = value
            else:
                continue
    for key in options:
        if key not in KNOWN_KEYS:
            logging.warning(f"Unrecognized key in arguments: {key}")

    return url, options

def seconds_to_hhmmss(seconds):
    if seconds is None:
        return None
    import datetime
    return str(datetime.timedelta(seconds=int(seconds)))