from __future__ import unicode_literals
import yt_dlp


def set_ydl_opts(format):
    vidformats = ['mp4', 'mkv', 'mpeg']
    audformats = ['wav', 'mp3']

    # Define the common options for yt-dlp
    ydl_opts_common = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    if format in vidformats:
        ydl_opts = {
            **ydl_opts_common,
            'format': 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': f'{format}',
            }]
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
                '-ar', '48000'
            ],
            'prefer_ffmpeg': True,
            'keepvideo': False
        }
    else:
        print(f"Unsupported format: {format}")
        return None
    
    print(f"Set ydl_opts for format: {format}")

    return ydl_opts

def verify_media(info_dict):

    print("Verifying...")

    max_size = 24
    
    filesize_mb = (info_dict.get('filesize') or info_dict.get('filesize_approx')) / (1024 * 1024)  # Convert bytes to megabytes

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

def youtube_downloader(url, destination, format):
    
    ydl_opts = set_ydl_opts(format)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Extracting video information...")
        info_dict = ydl.extract_info(url, download=False)

        verify_media(info_dict)

        title = info_dict.get('title', None)

        filename = f'{destination}/{title}.{format}'

        ydl.download([url])

    print(f"Downloaded: {filename}")
    return filename