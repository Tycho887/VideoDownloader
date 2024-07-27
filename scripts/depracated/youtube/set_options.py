def set_ydl_opts(format):

    assert format in ['mp3', 'mp4', 'gif'], "Format must be 'mp3', 'mp4', or 'gif'"

    # Define the common options for yt-dlp
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s'
    }
    # Map quality settings to yt-dlp format selectors

    if format == 'mp3':
        # Download only audio
        ydl_opts.update({
            'format': f'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }],
            'postprocessor_args': ['-ar', '48000'],
            'prefer_ffmpeg': True,
            'keepvideo': False
        })
    elif format == 'mp4':
        # Download video and audio
        ydl_opts.update({
            'format': f'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        })
    elif format == 'gif':
        # Download video only, but we will handle conversion to GIF separately
        ydl_opts.update({
            'format': f'bestvideo/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        })

    return ydl_opts