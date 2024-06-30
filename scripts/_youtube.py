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


def check_valid_url(url, max_duration=600, max_size=25):
    """
    Check if the URL is valid based on duration and size constraints.

    Args:
    - url (str): The URL to check.
    - max_duration (int): Maximum duration in seconds. Default is 600 (10 minutes).
    - max_size (float): Maximum file size in megabytes. If None, no size check is performed.

    Returns:
    - bool: True if the URL meets the requirements, False otherwise.
    """
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            # Check if URL is a playlist
            if 'entries' in info_dict:
                raise ValueError("The provided URL is a playlist, which is not supported.")
            
            # Check if the video duration exceeds the maximum allowed duration
            if info_dict.get('duration', 0) > max_duration:
                raise ValueError(f"The video is longer than {max_duration} seconds, which is not supported.")
            
            # Check if the video is a live stream
            if info_dict.get('is_live', False):
                raise ValueError("The video is a live stream, which is not supported.")
            
            # Check for invalid video IDs or removed videos
            if 'title' not in info_dict or not info_dict['title']:
                raise ValueError("The video is unavailable or removed.")
            
            # Check if the video size exceeds the maximum allowed size
            if max_size is not None:
                filesize_bytes = info_dict.get('filesize', None)
                if filesize_bytes is None:
                    # Try to estimate the file size if exact size is not available
                    filesize_bytes = info_dict.get('filesize_approx', None)
                
                if filesize_bytes is not None:
                    filesize_mb = filesize_bytes / (1024 * 1024)  # Convert bytes to megabytes
                    if filesize_mb > max_size:
                        raise ValueError(f"The video file size is {filesize_mb:.2f} MB, which exceeds the limit of {max_size} MB.")
                else:
                    print("Warning: Unable to determine file size. Skipping size check.")

    except yt_dlp.DownloadError as e:
        print(f"DownloadError: {e}")
        return False
    except yt_dlp.utils.ExtractorError as ee:
        print(f"ExtractorError: {ee}")
        return False
    except KeyError as ke:
        print(f"KeyError: {ke}")
        return False
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return False
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        return False
    
    print("Valid URL")
    return True

def send_download_request(url, video_destination, ydl_opts):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            video_ext = info_dict.get('ext', f'{format}')
            video_filename = f'{video_destination}/{video_title}.{video_ext}'
            info_dict = ydl.extract_info(url, download=True)
    except yt_dlp.DownloadError as e:
        print(f"An error occurred: {e}")
        return None
    except ValueError as ve:
        print(f"An error occurred: {ve}")
        return None

    print(f"Downloaded: {video_filename}")
    return video_filename



def download_youtube_video(url, video_destination, format='mp4'):
    
    ydl_opts = set_ydl_opts(format)

    if ydl_opts is None:
        return None
    
    if check_valid_url(url):
        return send_download_request(url, video_destination, ydl_opts)
    else:
        return None