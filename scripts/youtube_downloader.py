import yt_dlp
import os
import sys

# Add the 

def download_youtube_video(url):
    # Ensure the downloads directory exists
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # Define the options for yt-dlp
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            video_ext = info_dict.get('ext', 'mp4')  # Default to mp4 if no ext found
            video_filename = f'downloads/{video_title}.{video_ext}'

        print(f"Downloaded: {video_filename}")
        return video_filename
    except yt_dlp.DownloadError as e:
        print(f"An error occurred: {e}")
        return None
