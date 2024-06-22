from scripts._youtube import download_youtube_video
from scripts._twitter import download_twitter_video

def download_video(url, format):
    video_destination = "downloads"
    file_name = None
    if "youtube" in url:
        file_name = download_youtube_video(url, format, video_destination)
    elif "youtu.be" in url:
        file_name = download_youtube_video(url, format, video_destination)
    elif "x.com" in url:
        file_name = download_twitter_video(url, video_destination)
    else:
        pass
    return file_name