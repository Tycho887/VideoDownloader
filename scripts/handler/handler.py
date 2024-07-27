from scripts.downloaders import download_youtube_video, download_twitter_video
from scripts.handler.editor import MediaEditor
import os

supported_formats = ("mp4", "mp3", "gif")

class ProcessWrapper:

    def __init__(self,url,format) -> None:

        assert format in supported_formats, f"Unsupported format: {format}"
        assert url is not None, "URL is required"

        self.source_url = url
        self.target_format = format

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

def download_media(url, format, start, end):
    process_wrapper = ProcessWrapper(url,format)
    result_path = process_wrapper.result_path
    assert os.path.exists(result_path), f"{result_path} does not exist, content: {os.listdir('downloads')}"
    media_editor = MediaEditor(process_wrapper.result_path, start, end, format)
    return media_editor.result_path, media_editor.generated_files