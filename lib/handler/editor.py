from lib.downloaders import download_youtube_video, download_twitter_video
import os
from moviepy import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import time
from moviepy.video.fx import resize
from moviepy.video import fx

class MediaEditor:

    def __init__(self, media_path, start_time, end_time, target_format, resolution=None) -> None:
        assert os.path.exists(media_path), f"File does not exist: {media_path}"
        assert target_format in ["gif", "mp4", "mp3"], f"Unsupported format: {target_format}"
        assert start_time is None or start_time >= 0, f"Invalid start time: {start_time}"
        assert end_time is None or end_time >= 0, f"Invalid end time: {end_time}"
        if resolution:
            assert isinstance(resolution, tuple) and len(resolution) == 2, "Resolution must be a tuple (width, height)"
        
        self.source_media_path = media_path
        self.start_time = start_time
        self.end_time = end_time
        self.target_format = target_format
        self.max_size = 10 # MB
        self.result_path = None
        self.generated_files = [media_path]
        self.resolution = resolution  # Store resolution for resizing

        if target_format in ["mp4", "gif"]:
            self.source_media = VideoFileClip(media_path)
        elif target_format == "mp3":
            self.source_media = AudioFileClip(media_path)
        else:
            raise ValueError(f"Unsupported format: {target_format}")

        self.run()

    def run(self):
        self._clip_media()
        if self.resolution and self.target_format in ["mp4", "gif"]:
            self._resize_media()
        self.export_media()
        if self.file_too_large():
            raise ValueError(f"File size too large: {os.path.getsize(self.result_path) / (1024 ** 2):.1f} MB")

    def _clip_media(self):
        print("Clipping media")

        if self.start_time is None or self.start_time > self.source_media.duration:
            self.start_time = 0
        if self.end_time is None or self.end_time > self.source_media.duration:
            self.end_time = self.source_media.duration

        if self.start_time is not None and self.end_time is not None:
            self.source_media = self.source_media.subclip(float(self.start_time), float(self.end_time))

    def _resize_media(self):
        """Resize the video to the target resolution."""
        print("Resizing media")

        if self.resolution[1] is None:
            # Maintain aspect ratio
            aspect_ratio = self.source_media.size[1] / self.source_media.size[0]
            height = int(self.resolution[0] * aspect_ratio)
            self.resolution = (self.resolution[0], height)
        
        # Apply the resize effect
        self.source_media = self.source_media.fx(resize.resize, newsize=self.resolution)

    def _convert_to_gif(self):
        video_length = self.source_media.duration
        max_frames = 50

        assert video_length <= 30, "The video is too long to convert to a GIF"
        fps = min(max_frames / video_length, 15)  # Cap at 15 fps for quality

        if video_length * fps > max_frames:
            speed_factor = video_length / (max_frames / fps)
            self.source_media = self.source_media.fx(vfx.speedx, speed_factor)
            fps = max_frames / video_length  # Recalculate fps after speed adjustment

        self.source_media.write_gif(self.result_path, fps=fps)

    def file_too_large(self):
        file_size = os.path.getsize(self.result_path) / (1024 ** 2)
        return file_size > self.max_size

    def export_media(self):
        self.result_path = f"downloads/media{time.strftime('%H%M%S')}.{self.target_format}"

        if self.target_format == "gif":
            self._convert_to_gif()
        elif self.target_format == "mp4":
            self.source_media.write_videofile(self.result_path)
        elif self.target_format == "mp3":
            self.source_media.write_audiofile(self.result_path)
        else:
            raise ValueError(f"Unsupported format: {self.target_format}")

        self.generated_files.append(self.result_path)

        # Ensure the media file is closed
        if self.source_media:
            self.source_media.close()

        # Ensure proper cleanup of temp files created by moviepy
        if hasattr(self.source_media, 'reader') and self.source_media.reader:
            self.source_media.reader.close()
        if hasattr(self.source_media, 'audio') and self.source_media.audio and hasattr(self.source_media.audio, 'reader'):
            self.source_media.audio.reader.close_proc()
