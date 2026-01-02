import os
import subprocess
import math
import logging
import json
from dataclasses import dataclass
from typing import Optional, Tuple
import yt_dlp
from datetime import datetime
from uuid import uuid4
from lib.utils import VideoSourceTooLarge, VideoOutputTooLarge, MAX_SIZE_MB, SAFE_GIF_WIDTH, SAFE_GIF_FPS, MAX_GIF_LENGTH

def get_timestamp():
    now = datetime.now()
    midnight = datetime.combine(now.date(), datetime.min.time())
    elapsed = now - midnight
    return int(elapsed.total_seconds() * 1000)

@dataclass
class VideoJob:
    url: str
    format: str = "mp4"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    framerate: Optional[int] = None
    output_name: Optional[str] = None
    
    def __post_init__(self):
        if not self.output_name:
            self.output_name = f"job_{uuid4().hex}"

class VideoDownloader:
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

    def _get_output_path(self, base_name: str, format: str) -> str:
        return os.path.join(self.download_dir, f"{base_name}_processed.{format}")

    def _probe_file(self, file_path: str) -> dict:
        """Uses ffprobe to extract width, height, and duration safely."""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Find the video stream
            video = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), None)
            fmt = data.get('format', {})
            
            return {
                'width': int(video.get('width', 0)) if video else 0,
                'height': int(video.get('height', 0)) if video else 0,
                'duration': float(fmt.get('duration', 0))
            }
        except Exception as e:
            logging.warning(f"Failed to probe file: {e}")
            return {'width': 0, 'height': 0, 'duration': 0}

    def _download(self, url: str, format: str, filename: Optional[str]) -> Tuple[str, int, int]:
        # ... [Same download logic as previous step] ...
        ydl_format = "bestvideo[ext=mp4][vcodec!*=av01]+bestaudio/best"
        postprocessors = []

        if format == "mp3":
            ydl_format = "bestaudio"
            postprocessors.append({'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'})
        elif format in ("mp4", "gif"):
            ydl_format = "bestvideo[ext=mp4][vcodec!*=av01]+bestaudio/best"
            postprocessors.append({'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'})

        filename_template = filename or '%(title)s'
        outtmpl = os.path.join(self.download_dir, f'{filename_template}.%(ext)s')
        
        # 100MB limit for source file
        max_dl_size = 100 * 1024 * 1024 

        ydl_opts = {
            'format': ydl_format,
            'outtmpl': outtmpl,
            'noplaylist': True,
            'quiet': True,
            'max_filesize': max_dl_size,
            'merge_output_format': format if format in ("mp4", "mp3") else None,
            'postprocessors': postprocessors,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if 'requested_downloads' in info and info['requested_downloads']:
                    final_path = info['requested_downloads'][0]['filepath']
                else:
                    final_path = ydl.prepare_filename(info)
                return final_path, info.get('width', 0), info.get('height', 0)

        except yt_dlp.utils.DownloadError as e:
            if "File is larger than max-filesize" in str(e):
                raise VideoSourceTooLarge()
            raise e

    def _process(self, input_path: str, output_path: str, job: VideoJob) -> str:
        # 1. Start with user requested filters
        filters = []
        start_args = ['-ss', job.start_time] if job.start_time else []
        duration_args = []
        if job.start_time and job.end_time:
            duration_args = ['-t', self._get_duration(job.start_time, job.end_time)]
        elif job.end_time:
            duration_args = ['-to', job.end_time]

        # 2. SAFETY CHECK: Proactively downscale for GIFs
        if job.format == "gif":
            meta = self._probe_file(input_path)
            
            # A. Enforce Duration Limit (Max 30s)
            # If user didn't specify end time, and video is long, cut it.
            if not duration_args and meta['duration'] > MAX_GIF_LENGTH:
                logging.warning(f"Video duration {meta['duration']}s > {MAX_GIF_LENGTH}s. Clipping GIF.")
                duration_args = ['-t', str(MAX_GIF_LENGTH)]
            
            # B. Enforce Resolution Limit (Max 320px width)
            # Use requested width OR source width
            target_w = job.width or meta['width']
            
            if target_w > SAFE_GIF_WIDTH:
                logging.info(f"Downscaling GIF width from {target_w} to {SAFE_GIF_WIDTH} to save RAM.")
                job.width = SAFE_GIF_WIDTH
                job.height = -1 # FFmpeg auto-calc height
            
            # C. Enforce FPS Limit (Max 15)
            target_fps = job.framerate or 30 # assume source is 30 usually
            if target_fps > SAFE_GIF_FPS:
                logging.info(f"Lowering GIF fps from {target_fps} to {SAFE_GIF_FPS}.")
                job.framerate = SAFE_GIF_FPS

        # 3. Build Filter Chain (with updated safety values)
        if job.framerate:
            filters.append(f"fps={job.framerate}")
        
        if job.width or job.height:
            w = job.width if job.width else -1
            h = job.height if job.height else -1
            
            # libx264 needs even dimensions, GIF palettegen doesn't strictly, 
            # but good practice. For GIF with scale=-1, it's usually fine.
            if job.format == 'mp4' and w != -1 and w % 2 != 0: w -= 1
            if job.format == 'mp4' and h != -1 and h % 2 != 0: h -= 1
            
            filters.append(f"scale={w}:{h}")
            if job.format == 'mp4': filters.append("setsar=1")

        vf = ",".join(filters) if filters else None

        try:
            if job.format == "gif":
                palette_path = os.path.join(self.download_dir, f"palette_{get_timestamp()}.png")
                try:
                    # Pass 1: Palette
                    subprocess.run([
                        'ffmpeg', *start_args, *duration_args,
                        '-i', input_path,
                        '-vf', f"{vf},palettegen" if vf else 'palettegen',
                        '-y', palette_path,
                        '-threads', 'auto'
                    ], check=True, capture_output=True)

                    # Pass 2: GIF Generation
                    subprocess.run([
                        'ffmpeg', *start_args, *duration_args,
                        '-i', input_path,
                        '-i', palette_path,
                        '-lavfi', f"{vf} [x]; [x][1:v] paletteuse" if vf else 'paletteuse',
                        '-y', output_path,
                        '-threads', 'auto'
                    ], check=True, capture_output=True)
                finally:
                    if os.path.exists(palette_path):
                        os.remove(palette_path)
            else:
                # MP4/MP3
                cmd = ['ffmpeg', '-i', input_path, *start_args, *duration_args]
                if vf: cmd += ['-vf', vf]
                cmd += [
                    '-c:v', 'libx264' if job.format == 'mp4' else 'copy',
                    '-preset', 'fast', '-crf', '23',
                    '-c:a', 'aac' if job.format != 'mp3' else 'copy',
                    '-b:a', '128k',
                    '-y', output_path, '-threads', 'auto'
                ]
                subprocess.run(cmd, check=True, capture_output=True)

        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise e
        
        return output_path

    def _get_duration(self, start: str, end: str) -> str:
        from datetime import datetime
        fmt = "%H:%M:%S"
        start_dt = datetime.strptime(start, fmt)
        end_dt = datetime.strptime(end, fmt)
        duration = (end_dt - start_dt).seconds
        return str(duration)
    
    def run_job(self, job: VideoJob) -> str:
        downloaded_path, native_w, native_h = self._download(job.url, job.format, job.output_name)
        
        try:
            base_name, _ = os.path.splitext(os.path.basename(downloaded_path))
            output_path = self._get_output_path(base_name, job.format)
            
            self._process(downloaded_path, output_path, job)
            
            # Post-process check for file size (Auto-resize loop)
            # Only needed for MP4s usually, but good generic safety
            for attempt in range(5):
                if not os.path.exists(output_path): break
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                if size_mb <= MAX_SIZE_MB:
                    return output_path

                logging.info(f"File size {size_mb:.2f}MB > {MAX_SIZE_MB}MB. Scaling down.")
                ratio = math.sqrt((size_mb / MAX_SIZE_MB) * 1.1)
                
                # Use current job settings or native if unset
                current_w = job.width or native_w
                current_h = job.height or native_h

                job.width = int(current_w / ratio)
                job.height = int(current_h / ratio)
                
                self._process(downloaded_path, output_path, job)

            final_size = os.path.getsize(output_path) / (1024 * 1024)
            if final_size > MAX_SIZE_MB:
                if os.path.exists(output_path): os.remove(output_path)
                raise VideoOutputTooLarge(f"Final size {final_size:.2f}MB is still over limit.")

            return output_path

        finally:
            if os.path.exists(downloaded_path):
                os.remove(downloaded_path)