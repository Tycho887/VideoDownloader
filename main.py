from discord.ext import commands, tasks
import discord
import os
import logging
import asyncio
import sys
from lib.download import VideoDownloader, VideoJob
from lib.validate import validate_url, validate_format, validate_times, validate_resolution, validate_framerate
from lib.utils import (
    remove_files, remove_file, extract_arguments, seconds_to_hhmmss, 
    SUPPORTED_FORMATS, DOWNLOAD_FOLDER, 
    VideoSourceTooLarge, VideoOutputTooLarge # Import new errors
)
from dotenv import load_dotenv

# ... [Keep Logging and Setup code same as before] ...
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding='utf-8')
    ]
)

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# ... [Keep scheduled_restart, on_ready, ping, guide same as before] ...

async def send_file(ctx, file_name):
    logging.info(f"Attempting to send file: {file_name}")
    # ... [Keep existing assertions] ...
    
    with open(file_name, 'rb') as file:
        await ctx.send(file=discord.File(file, file_name))
    logging.info(f"File sent successfully: {file_name}")

async def handle_download(ctx, args):
    url, options = extract_arguments(args)

    validate_url(url)
    format = options['format'].lower()
    validate_format(format)

    start = float(options['start']) if options['start'] else None
    end = float(options['end']) if options['end'] else None
    validate_times(start, end)

    resolution = options['resolution']
    resolution_tuple = tuple(map(int, resolution.split('x'))) if resolution else None
    validate_resolution(resolution)

    framerate = int(options['framerate']) if options['framerate'] else None
    validate_framerate(framerate)

    await ctx.send("Downloading and processing media...")
    logging.info("Downloading with parsed options: %s", options)

    downloader = VideoDownloader(download_dir=DOWNLOAD_FOLDER)
    job = VideoJob(
            url=url,
            format=format,
            start_time=seconds_to_hhmmss(start),
            end_time=seconds_to_hhmmss(end),
            width=resolution_tuple[0] if resolution_tuple else None,
            height=resolution_tuple[1] if resolution_tuple else None,
            framerate=framerate
    )

    file_name = None
    try:
        # Run the blocking download/process in a thread
        file_name = await asyncio.to_thread(downloader.run_job, job)
        
        if not os.path.exists(file_name):
             raise FileNotFoundError("Processing failed, file was not created.")

        await send_file(ctx, file_name)
    finally:
        if file_name:
            remove_file(file_name)
            logging.info("Temporary file removed (or attempted): %s", file_name)
    
    return file_name

semaphore = asyncio.Semaphore(1)

@bot.command()
async def download(ctx, *, args):
    logging.info("Download command received with arguments: %s", args)

    async with semaphore:
        try:
            await handle_download(ctx, args)
            
        except VideoSourceTooLarge:
            await ctx.send("❌ Error 1001: Video attempting to download is too big.")
            logging.warning("Handled Error 1001: Source too large.")

        except VideoOutputTooLarge:
            await ctx.send("❌ Error 1002: Processed video is above 10MB.")
            logging.warning("Handled Error 1002: Output too large.")

        except Exception as e:
            logging.exception("Error during download:")
            
            error_str = str(e).lower()
            if "no space left" in error_str or (hasattr(e, 'errno') and e.errno == 28):
                await ctx.send("❌ Critical Storage Error: Restarting bot...")
                sys.exit(1)

            await ctx.send(f"❌ An error occurred: {str(e)}")

bot.run(DISCORD_BOT_TOKEN)