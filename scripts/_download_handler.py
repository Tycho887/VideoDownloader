from scripts._youtube import download_youtube_video
from scripts._twitter import download_twitter_video
import os

def download_video(url, format):
    video_destination = "downloads"

    if not os.path.exists(video_destination):
        os.makedirs(video_destination)

    file_name = None
    if "youtube" in url or "youtu.be" in url:
        file_name = download_youtube_video(url, format, video_destination)
    elif "x.com" in url:
        file_name = download_twitter_video(url, video_destination)
    else:
        pass
    return file_name