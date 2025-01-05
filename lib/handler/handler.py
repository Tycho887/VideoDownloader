from lib.downloaders import download_youtube_video, download_twitter_video
from lib.handler.editor import MediaEditor
import os
from moviepy.video.io.VideoFileClip import VideoFileClip

supported_formats = ("mp4", "mp3", "gif")

class ProcessWrapper:

    def __init__(self, url, format, resolution=None) -> None:
        assert format in supported_formats, f"Unsupported format: {format}"
        assert url is not None, "URL is required"

        self.source_url = url
        self.target_format = format
        self.resolution = resolution  # Add resolution to ProcessWrapper

        self.download_folder = "downloads"
        self.result_path = None

        self.run()

    def run(self):
        self.get_source()
        self.download_media()

    def get_source(self):
        url = self.source_url

        if "youtube" in url or "youtu.be" in url:
            self.source = "youtube"
        elif "x.com" in url:
            self.source = "twitter"
        else:
            raise ValueError(f"Unsupported source: {url}")    
    
    def download_media(self):
        if self.source == "youtube":
            self.result_path = download_youtube_video(self.source_url, 
                                                     self.download_folder, 
                                                     self.target_format)
        elif self.source == "twitter":
            self.result_path = download_twitter_video(self.source_url, 
                                                     self.download_folder)
        else:
            raise ValueError(f"Unsupported source: {self.source_url}")


def download_media(url, format, start, end, resolution=None):
    process_wrapper = ProcessWrapper(url, format)

    result_path = process_wrapper.result_path
    assert os.path.exists(result_path), f"{result_path} does not exist, content: {os.listdir('downloads')}"

    # If resolution is a single value, maintain aspect ratio
    if resolution and resolution[1] is None:  # Resolution provided as (width, None)
        with VideoFileClip(result_path) as video:
            aspect_ratio = video.size[1] / video.size[0]  # height / width
            height = int(resolution[0] * aspect_ratio)
            resolution = (resolution[0], height)

    # Pass the final resolution (adjusted or not) to MediaEditor
    media_editor = MediaEditor(process_wrapper.result_path, start, end, format, resolution)
    return media_editor.result_path, media_editor.generated_files

