import os
import time
import moviepy.video.fx.all as vfx
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from lib.downloaders.twitter import download_twitter_video
from lib.downloaders.youtube import youtube_downloader as download_youtube_video
from moviepy.video.fx import resize
import re
from lib.utils.constants import SUPPORTED_FORMATS, MAX_SIZE_MB, MAX_GIF_FRAMES, MAX_GIF_LENGTH, MAX_VIDEO_RESOLUTION, KNOWN_KEYS, DOWNLOAD_FOLDER as download_folder
import logging


def remove_files():
    # Remove all mp3, mp4, and gif files in the downloads folder
    for file in os.listdir(download_folder):
        if file.endswith(SUPPORTED_FORMATS):
            os.remove(os.path.join(download_folder, file))


def remove_file(file_path):
    if os.path.isfile(file_path) and file_path.endswith(SUPPORTED_FORMATS):
        os.remove(file_path)


def get_source(url):
    if "youtube" in url or "youtu.be" in url:
        return "youtube"
    elif "x.com" in url or "twitter.com" in url:
        return "twitter"
    else:
        raise ValueError(f"Unsupported URL source. Supported sources are YouTube and Twitter.")


def download_media_from_url(url, target_format):
    source = get_source(url)
    if source == "youtube":
        return download_youtube_video(url, target_format)
    elif source == "twitter":
        return download_twitter_video(url)
    else:
        raise ValueError(f"Unsupported source: {url}")


def process_media(media_path, start_time, end_time, target_format, resolution=None):
    if not os.path.exists(media_path):
        raise FileNotFoundError(f"File does not exist: {media_path}")
    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"unsupported format: {target_format}")
    if start_time is not None and start_time < 0:
        raise ValueError(f"Invalid start time: {start_time}")
    if end_time is not None and end_time < 0:
        raise ValueError(f"Invalid end time: {end_time}")
    if resolution is not None:
        if not isinstance(resolution, tuple) or len(resolution) != 2:
            raise ValueError("Resolution must be a tuple (width, height)")

    generated_files = [media_path]
    result_path = f"{download_folder}/{os.path.basename(media_path)}_{int(time.time())}.{target_format}"

    if target_format in ["mp4", "gif"]:
        with VideoFileClip(media_path) as source_media:
            # Clip media
            duration = source_media.duration
            start_time = start_time or 0
            end_time = end_time or duration
            start_time = min(start_time, duration)
            end_time = min(end_time, duration)
            clipped_media = source_media.subclip(start_time, end_time)

            # Resize if needed
            if resolution:
                if resolution[0] > MAX_VIDEO_RESOLUTION or resolution[1] > MAX_VIDEO_RESOLUTION:
                    remove_file(media_path)
                    raise ValueError(f"Resolution too large: {resolution}")

                if resolution[1] is None:
                    aspect_ratio = clipped_media.size[1] / clipped_media.size[0]
                    height = int(resolution[0] * aspect_ratio)
                    resolution = (resolution[0], height)
                clipped_media = clipped_media.fx(resize.resize, newsize=resolution)

            # Export media
            if target_format == "gif":
                convert_to_gif(clipped_media, result_path)
            elif target_format == "mp4":
                clipped_media.write_videofile(result_path)
            else:
                raise ValueError(f"Unsupported target format: {target_format}")

            generated_files.append(result_path)

    elif target_format == "mp3":
        with AudioFileClip(media_path) as source_media:
            # Clip media
            duration = source_media.duration
            start_time = start_time or 0
            end_time = end_time or duration
            start_time = min(start_time, duration)
            end_time = min(end_time, duration)
            clipped_media = source_media.subclip(start_time, end_time)

            # Export media
            clipped_media.write_audiofile(result_path)
            generated_files.append(result_path)

    else:
        raise ValueError("Unsupported target format")

    # Check file size
    file_size_mb = os.path.getsize(result_path) / (1024 ** 2)
    if file_size_mb > MAX_SIZE_MB:
        raise ValueError(f"File size too large: {file_size_mb:.1f} MB")
    
    remove_file(media_path)

    return result_path, generated_files


def convert_to_gif(video_clip, result_path):
    """
    Convert a video clip to a GIF file.
    """
    video_length = video_clip.duration
    max_frames = MAX_GIF_FRAMES
    if video_length > MAX_GIF_LENGTH:
        raise ValueError(f"Video length exceeds {MAX_GIF_LENGTH}s or frame count exceeds {MAX_GIF_FRAMES}.")
    fps = min(max_frames / video_length, 15)  # Cap at 15 fps for quality
    if video_length * fps > max_frames:
        speed_factor = video_length / (max_frames / fps)
        video_clip = video_clip.fx(vfx.speedx, speed_factor)
        fps = max_frames / video_length  # Recalculate fps after speed adjustment
    video_clip.write_gif(result_path, fps=fps)


def download_media(url, target_format, start_time=None, end_time=None, resolution=None):
    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {target_format} \n Supported formats: {SUPPORTED_FORMATS}")
    if not url:
        raise ValueError("URL is required")

    result_path = download_media_from_url(url, target_format)
    if not os.path.exists(result_path):
        raise FileNotFoundError(f"{result_path} does not exist")

    # Adjust resolution if needed
    if resolution and resolution[1] is None:
        with VideoFileClip(result_path) as video:
            aspect_ratio = video.size[1] / video.size[0]
            height = int(resolution[0] * aspect_ratio)
            resolution = (resolution[0], height)

    # Process the media
    processed_result_path, generated_files = process_media(
        result_path,
        start_time,
        end_time,
        target_format,
        resolution
    )

    return processed_result_path, generated_files


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