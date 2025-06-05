import os
import subprocess
from dataclasses import dataclass
from typing import Optional
import yt_dlp
# We want the current millisecond timestamp for unique output names
from datetime import datetime
from uuid import uuid4

def get_timestamp():
    now = datetime.now()
    midnight = datetime.combine(now.date(), datetime.min.time())
    elapsed = now - midnight
    return int(elapsed.total_seconds() * 1000)

@dataclass
class VideoJob:
    url: str
    format: str = "mp4"  # 'mp4', 'gif', 'mp3'
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    framerate: Optional[int] = None
    output_name: Optional[str] = f"job_{uuid4().hex}" # f"media_download_{get_timestamp()}"

class VideoDownloader:
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def _get_output_path(self, base_name: str, format: str) -> str:
        return os.path.join(self.download_dir, f"{base_name}_processed.{format}")

    def _download(self, url: str, format: str, filename: Optional[str]) -> str:
        ydl_format = "bestvideo[ext=mp4][vcodec!*=av01]+bestaudio/best"
        postprocessors = []

        if format == "mp3":
            ydl_format = "bestaudio"
            postprocessors.append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            })
        elif format in ("mp4", "gif"):
            ydl_format = "bestvideo[ext=mp4][vcodec!*=av01]+bestaudio/best"
            postprocessors.append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            })

        filename_template = filename or '%(title)s'
        outtmpl = os.path.join(self.download_dir, f'{filename_template}.%(ext)s')

        ydl_opts = {
            'format': ydl_format,
            'outtmpl': outtmpl,
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': format if format in ("mp4", "mp3") else None,
            'postprocessors': postprocessors,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'requested_downloads' in info and info['requested_downloads']:
                final_path = info['requested_downloads'][0]['filepath']
            else:
                final_path = ydl.prepare_filename(info)

        return final_path

    def _process(self, input_path: str, output_path: str, job: VideoJob) -> str:
        # Build FFmpeg filters
        filters = []
        if job.framerate:
            filters.append(f"fps={job.framerate}")
        if job.width and job.height:
            filters.append(f"scale={job.width}:{job.height}")
            filters.append("setsar=1")
        vf = ",".join(filters) if filters else None

        start_args = ['-ss', job.start_time] if job.start_time else []
        duration_args = []
        if job.start_time and job.end_time:
            duration_args = ['-t', self._get_duration(job.start_time, job.end_time)]
        elif job.end_time:
            duration_args = ['-to', job.end_time]

        if job.format == "gif":
            palette_path = os.path.join(self.download_dir, f"palette_{get_timestamp()}.png")

            # First pass: generate palette
            subprocess.run([
                'ffmpeg', *start_args, *duration_args,
                '-i', input_path,
                '-vf', f"{vf},palettegen" if vf else 'palettegen',
                '-y', palette_path,
                '-threads', 'auto'
            ], check=True)

            if not os.path.exists(palette_path):
                raise RuntimeError("Palette generation failed.")

            # Second pass: apply palette
            subprocess.run([
                'ffmpeg', *start_args, *duration_args,
                '-i', input_path,
                '-i', palette_path,
                '-lavfi', f"{vf} [x]; [x][1:v] paletteuse" if vf else 'paletteuse',
                '-y', output_path,
                '-threads', 'auto'
            ], check=True)
            os.remove(palette_path)
        else:
            cmd = ['ffmpeg', '-i', input_path, *start_args, *duration_args]
            if vf:
                cmd += ['-vf', vf]
            cmd += [
                '-c:v', 'libx264' if job.format == 'mp4' else 'copy',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac' if job.format != 'mp3' else 'copy',
                '-b:a', '128k',
                '-y', output_path,
                '-threads', 'auto'
            ]
            try:
               subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
               print("Error occurred while processing video:", e)

        # Remove the original unprocessed file
        if os.path.exists(input_path):
            os.remove(input_path)

        return output_path


    def _get_duration(self, start: str, end: str) -> str:
        # Calculate duration from start and end times in HH:MM:SS
        from datetime import datetime
        fmt = "%H:%M:%S"
        start_dt = datetime.strptime(start, fmt)
        end_dt = datetime.strptime(end, fmt)
        duration = (end_dt - start_dt).seconds
        return str(duration)
    
    def run_job(self, job: VideoJob) -> str:
        downloaded_path = self._download(job.url, job.format, job.output_name)
        base_name, _ = os.path.splitext(os.path.basename(downloaded_path))
        output_path = self._get_output_path(base_name, job.format)
            
        return self._process(downloaded_path, output_path, job)

# downloader = VideoDownloader()
# job = VideoJob(
#     url="https://www.youtube.com/watch?v=B94IY-wTMtE",#url="https://www.youtube.com/watch?v=40SZM77nqo4",
#     format="mp4",
#     start_time="00:00:02",  # Start trimming from 2 seconds
#     end_time="00:00:08",  # Only trim the end
#     width=200, height=200,  # Resize
#     framerate=5            # Frame rate override
# )

# downloader = VideoDownloader()
# path = downloader.run_job(job)
# print("Saved to:", path)