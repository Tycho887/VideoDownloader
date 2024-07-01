from moviepy.editor import VideoFileClip, vfx

def convert_to_gif(video_path, start_time, end_time, max_frames=100):
    """Convert a video to a GIF with a maximum of 50 frames.

    Args:
        video_path (str): The path to the video file.
        start_time (float): The start time of the GIF in seconds.
        end_time (float): The end time of the GIF in seconds.
        max_frames (int): The maximum number of frames in the GIF. Default is 50.
    """
    
    # Load the video and create the GIF destination path
    video = VideoFileClip(video_path)
    gif_path = video_path.replace(video_path.split('.')[-1], 'gif')

    # Convert start_time and end_time to float and create a subclip
    video = video.subclip(float(start_time), float(end_time))

    # Ensure the video is no longer than 30 seconds
    assert video.duration <= 30, "The video is too long to convert to a GIF"

    # Calculate the necessary FPS to keep the total frames <= max_frames
    fps = min(max_frames / video.duration, 15)  # Cap at 15 fps for quality

    # Check if we need to speed up the video to meet the frame limit
    if video.duration * fps > max_frames:
        # Adjust speed so that the number of frames will be within the limit
        speed_factor = video.duration / (max_frames / fps)
        video = video.fx(vfx.speedx, speed_factor)
        fps = max_frames / video.duration  # Recalculate fps after speed adjustment

    # Save the GIF with the calculated fps
    video.write_gif(gif_path, fps=fps)

    return gif_path