from __future__ import unicode_literals
import yt_dlp
import os
import re
from lib.utils.constants import DOWNLOAD_FOLDER as download_folder


def sanitize_filename(filename):
    # Define the set of illegal characters for filenames
    illegal_chars = r'[<>:"/\\|?*]'
    # Replace illegal characters with an underscore
    sanitized_filename = re.sub(illegal_chars, '_', filename)
    return sanitized_filename


def set_ydl_opts(format, sanitized_title):

    assert format in ['mp3', 'mp4', 'gif'], "Format must be 'mp3', 'mp4', or 'gif'"

    # Define the common options for yt-dlp
    ydl_opts = {
        'outtmpl': f'{download_folder}/{sanitized_title}.%(ext)s'
    }
    # Map quality settings to yt-dlp format selectors

    if format == 'mp3':
        # Download only audio
        ydl_opts.update({
            'format': f'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'postprocessor_args': ['-ar', '48000'],
            'prefer_ffmpeg': True,
            'keepvideo': False
        })
    elif format == 'mp4':
        # Download video and audio
        ydl_opts.update({
            'format': f'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        })
    elif format == 'gif':
        # Download video only, but we will handle conversion to GIF separately
        ydl_opts.update({
            'format': f'bestvideo/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        })

    return ydl_opts


def verify_media(info_dict):

    max_size = 1024  # Maximum file size in MB

    filesize_mb = (info_dict.get('filesize') or info_dict.get('filesize_approx')) / (1024 ** 2)  # Convert bytes to megabytes

    error_messages = {
        'playlist': "The provided URL is a playlist, which is not supported.",
        'live': "The url is a live stream, which is not supported.",
        'unavailable': "The video is unavailable or removed.",
        'size': lambda size: f"The file size is {size:.2f} MB, which exceeds the limit of {max_size} MB."
    }

    # Check for unsupported conditions
    if 'entries' in info_dict:
        raise ValueError(error_messages['playlist'])
    if info_dict.get('is_live', False):
        raise ValueError(error_messages['live'])
    if not info_dict.get('title'):
        raise ValueError(error_messages['unavailable'])
    if filesize_mb > max_size:
        raise ValueError(error_messages['size'](filesize_mb))


def youtube_downloader(url, format):

    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)

        verify_media(info_dict)

        title = info_dict.get('title', None)
        sanitized_title = sanitize_filename(title)

        if format == 'gif':
            format = 'mp4'

        ydl_opts = set_ydl_opts(format, sanitized_title)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    return f'{download_folder}/{sanitized_title}.{format}'