from __future__ import unicode_literals
import yt_dlp
import os
import sys


vidformats = ['mp4', 'mkv', 'mpeg']
audformats = ['wav', 'mp3']

def download_youtube_video(url, format, video_destination):
    # Define the options for yt-dlp
    if format in vidformats:
        ydl_opts = {
            'outtmpl': f'{video_destination}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            #'merge_output_format': f'{format}',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': f'{format}',
            }]
        }
    elif format in audformats:
        ydl_opts = {
            'outtmpl': f'{video_destination}/%(title)s.%(ext)s',
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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            video_ext = info_dict.get('ext', f'{format}')  # Default to mp4 if no ext found
            video_filename = f'{video_destination}/{video_title}.{video_ext}'

        print(f"Downloaded: {video_filename}")
        return video_filename
    except yt_dlp.DownloadError as e:
        print(f"An error occurred: {e}")
        return None