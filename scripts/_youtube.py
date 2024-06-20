import yt_dlp
import os
import sys


class params:

    def __init__(self, url, destination, format):
        assert os.path.exists(destination), "The video destination does not exist!"
        assert format in ["mp4", "mp3", "mkv", "webm", "wav", "mov"], "Invalid format! Supported formats are: mp4, mkv, webm, mp3, wav, mov"
        self.url = url
        self.destination = destination
        self.format = format

        self.get_ydl_opts()

    def get_ydl_opts(self):
        # For each format, define the options for yt-dlp
        if self.format in ["mp4", "mkv", "webm", "mov"]:
            self.ydl_opts = {
                'outtmpl': f'{self.destination}/%(title)s.%(ext)s',
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': self.format,
            }
            self.backup_format = "mp4"
        
        elif self.format in ["mp3", "wav"]:
            self.ydl_opts = {
                'outtmpl': f'{self.destination}/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format,
                    'preferredquality': '192',
                }]
            }
            self.backup_format = "mp3"

        

def download_youtube_video(url, video_destination, format="mp4"):

    ydl_opts = params(url, video_destination, format).ydl_opts

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', None)
            video_ext = info_dict.get('ext', 'mp4')  # Default to mp4 if no ext found
            video_filename = f'{video_destination}/{video_title}.{video_ext}'

        print(f"Downloaded: {video_filename}")
        return video_filename
    except yt_dlp.DownloadError as e:
        print(f"An error occurred: {e}")
        return None