import os
import yt_dlp
from typing import Optional, Tuple

def download_video_segment(
    url: str,
    start_time: str,  # Format: "HH:MM:SS" or "MM:SS" or "SS"
    end_time: str,     # Format: same as start_time
    output_dir: str = "./downloads",
    resolution: Optional[Tuple[int, int]] = 'auto',  # (width, height)
    format: str = "mp4",  # "mp4", "webm", etc.
) -> str:
    """
    Downloads a segment of a video using yt-dlp.

    Args:
        url: Video URL (YouTube, Twitter, etc.)
        start_time: Start timestamp (e.g., "00:01:30")
        end_time: End timestamp (e.g., "00:01:40")
        output_dir: Directory to save the video (default: "./downloads")
        resolution: Optional (width, height) tuple (e.g., (640, 480))
        format: Output format (e.g., "mp4", "webm")

    Returns:
        str: Filename of the downloaded video.
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": f"bestvideo[ext={format}]+bestaudio[ext=m4a]/best[ext={format}]/best",
        "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
        "force_keyframes_at_cuts": True,
        "download_ranges": lambda info_dict, ydl: [
            {"start_time": start_time, "end_time": end_time}
        ],
        "postprocessors": [],
    }

    # Add resolution scaling if specified
    if resolution:
        width, height = resolution
        ydl_opts["postprocessors"].append(
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": format,
                "when": "after_filter",
            }
        )
        ydl_opts["postprocessor_args"] = [
            "-vf",
            f"scale={width}:{height},setsar=1:1",
        ]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename

# # Example: Download a 10-second clip (1:30 to 1:40) at 720p resolution
# filename = download_video_segment(
#     url="https://www.youtube.com/watch?v=Po7EpuGfZRI",
#     start_time="00:01:30",
#     end_time="00:01:40",
#     resolution=(1280, 720),
#     format="mp4",
# )
# print(f"Downloaded: {filename}")