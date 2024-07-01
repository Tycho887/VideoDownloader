from scripts._youtube import youtube_downloader
from scripts._twitter import download_twitter_video
import os

supported_formats = ('mp4', 'mkv', 'mpeg', 'wav', 'mp3', 'gif')

def download_media(url, format = 'mp4'):

    destination = "downloads"

    if not os.path.exists(destination):
        os.makedirs(destination)

    file_name = None
    if "youtube" in url or "youtu.be" in url:
        file_name = youtube_downloader(url, destination, format)
    elif "x.com" in url:
        file_name = download_twitter_video(url, destination)
    else:
        pass
    return file_name