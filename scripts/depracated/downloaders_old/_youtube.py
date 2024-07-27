from __future__ import unicode_literals
import yt_dlp


def set_ydl_opts(format, start=None, end=None):

    assert isinstance(format, str), "Format must be a string"

    vidformats = ['mp4', 'mkv', 'mpeg']
    audformats = ['wav', 'mp3']

    # Define the common options for yt-dlp
    ydl_opts_common = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    postprocessor_args = []
    
    if start is not None:
        postprocessor_args += ['-ss', start]
    if end is not None:
        postprocessor_args += ['-to', end]

    if format in vidformats:
        ydl_opts = {
            **ydl_opts_common,
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': f'{format}',
            }],
            'postprocessor_args': postprocessor_args,
        }
    elif format in audformats:
        ydl_opts = {
            **ydl_opts_common,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': f'{format}',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '48000',
                *postprocessor_args
            ],
            'prefer_ffmpeg': True,
            'keepvideo': False
        }
    else:
        raise ValueError(f"Unsupported format: {format}")

    print(f"Set ydl_opts for format: {format}")

    return ydl_opts

def clip_size(info_dict,start,end):

    # video_length = info_dict.get('duration', 0)  # Get video length in seconds

    # if isinstance(start, (int, float)) and isinstance(end, (int, float)):
    #     start = start if start >= 0 else 0
    #     end = end if end <= video_length else video_length
    #     clip_length = end - start
    # else:
    #     clip_length = video_length

    clip_ratio = 1 # clip_length / video_length

    filesize_mb = clip_ratio * (info_dict.get('filesize') or info_dict.get('filesize_approx')) / (1024 * 1024)  # Convert bytes to megabytes

    return filesize_mb

def verify_media(info_dict,start,end):
    print("Verifying...")

    max_size = 24  # Maximum file size in MB

    filesize_mb = clip_size(info_dict,start,end)

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


def youtube_downloader(url, destination, format, start=None, end=None):
    ydl_opts = set_ydl_opts(format, start, end)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Extracting video information...")
        info_dict = ydl.extract_info(url, download=False)

        verify_media(info_dict, start, end)

        title = info_dict.get('title', None)

        filename = f'{destination}/{title}.{format}'

        ydl.download([url])

    print(f"Downloaded: {filename}")
    return filename
