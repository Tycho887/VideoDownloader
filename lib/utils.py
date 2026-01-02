import re
import logging
import os

SUPPORTED_FORMATS = ("mp4", "mp3", "gif")
MAX_SIZE_MB = 10  # Discord's limit for non-boosted servers
MAX_GIF_FRAMES = 50
MAX_GIF_LENGTH = 30 # seconds
MAX_VIDEO_RESOLUTION = 1920
SAFE_GIF_WIDTH = 320    # Downscale GIFs to this width
SAFE_GIF_FPS = 15       # Cap GIF framerate
MAX_GIF_LENGTH = 30     # Max seconds for a GIF
KNOWN_KEYS = ('format', 'start', 'end', 'resolution', 'framerate')
DOWNLOAD_FOLDER = "/mnt/ramdisk"

# --- New Error Classes ---
class VideoDownloadError(Exception):
    """Base class for video download errors."""
    pass

class VideoSourceTooLarge(VideoDownloadError):
    """Error 1001: The source video is too large to download safely."""
    def __init__(self, message="Video attempting to download is too big (Error 1001)"):
        self.message = message
        super().__init__(self.message)

class VideoOutputTooLarge(VideoDownloadError):
    """Error 1002: The processed video is still above the limit."""
    def __init__(self, message="Video result is above 10MB limit (Error 1002)"):
        self.message = message
        super().__init__(self.message)
# -------------------------

def remove_files():
    # Remove all mp3, mp4, and gif files in the downloads folder
    try:
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating download folder: {e}")
        return
    for file in os.listdir(DOWNLOAD_FOLDER):
        if file.endswith(SUPPORTED_FORMATS):
            os.remove(os.path.join(DOWNLOAD_FOLDER, file))

def remove_file(file_path):
    if os.path.isfile(file_path): # Removed extension check to allow removing temp files safely
        os.remove(file_path)

def extract_arguments(args):
    """
    Extract arguments from a string using regex.
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