from scripts.youtube import youtube_downloader
from scripts.twitter import download_twitter_video
import os

supported_formats = ('mp4', 'mp3', 'gif')

def download_media(url, format = 'mp4', start = None, end = None):

    destination = "downloads"

    if not os.path.exists(destination):
        os.makedirs(destination)

    file_name = None
    if "youtube" in url or "youtu.be" in url:
        file_name = youtube_downloader(url=url, destination=destination, format=format, start=start, end=end)
    elif "x.com" in url:
        file_name = download_twitter_video(url, destination)
    else:
        pass
    return file_name