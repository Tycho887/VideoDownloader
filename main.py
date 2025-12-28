from discord.ext import commands, tasks
import discord
import os
import logging
import re
from lib.download import VideoDownloader, VideoJob
import asyncio
from lib.validate import validate_url, validate_format, validate_times, validate_resolution, validate_framerate
from lib.utils import remove_files, remove_file, extract_arguments, seconds_to_hhmmss, SUPPORTED_FORMATS, DOWNLOAD_FOLDER
from dotenv import load_dotenv
import sys  # Add this import at the top

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Default log level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("bot.log", encoding='utf-8')  # Log to file
    ]
)

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

print(f"The Token is: {DISCORD_BOT_TOKEN}")

# Create an instance of a bot with all intents enabled
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Add this task function
@tasks.loop(hours=24)
async def scheduled_restart():
    # We skip the first execution (which happens immediately on start)
    if scheduled_restart.current_loop > 0:
        logging.info("Performing daily scheduled restart...")
        sys.exit(0) # Exit cleanly, Docker will restart it

@bot.event
async def on_ready():
    logging.info(f"Bot is ready, logged in as {bot.user}")
    logging.info("Clearing downloads folder...")
    remove_files()
    
    # Start the restart timer
    if not scheduled_restart.is_running():
        scheduled_restart.start()

@bot.command()
async def ping(ctx):
    logging.info("Ping command received.")
    await ctx.send("Pong!")


@bot.command()
async def guide(ctx):
    logging.info("Guide command received.")
    await ctx.send("Commands: !ping, !guide, !download <url> [format=<format>] [start=<start>] [end=<end>] [resolution=<resolution>] [framerate=<framerate>]\n"
                   "Supported formats: mp4, gif, mp3\n")


async def send_file(ctx, file_name):
    logging.info(f"Attempting to send file: {file_name}")
    assert os.path.exists(file_name), "The file does not exist!"
    assert os.path.isfile(file_name), "The file is not a file!"
    assert file_name.endswith(SUPPORTED_FORMATS), "The file is not a supported format!"
    
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

    await ctx.send("Downloading media...")
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
        
        # Check if file exists before sending
        if not os.path.exists(file_name):
             raise FileNotFoundError("Processing failed, file was not created.")

        await send_file(ctx, file_name)
    finally:
        # CRITICAL: This block runs whether the download succeeded, failed, 
        # or if sending the message failed.
        if file_name:
            remove_file(file_name)
            logging.info("Temporary file removed (or attempted): %s", file_name)
    
    return file_name

semaphore = asyncio.Semaphore(1)  # Limit to 1 job at a time

@bot.command()
async def download(ctx, *, args):
    logging.info("Download command received with arguments: %s", args)

    async with semaphore:
        file_name = None
        try:
            file_name = await handle_download(ctx, args)
            logging.info("Download completed successfully: %s", file_name)

        except Exception as e:
            logging.exception("Error during download:")
            
            # Check for "No space left on device" (Errno 28)
            # This handles both standard OSErrors and ffmpeg errors
            error_str = str(e).lower()
            if "no space left" in error_str or (hasattr(e, 'errno') and e.errno == 28):
                await ctx.send("❌ Critical Storage Error: Restarting bot to clear cache...")
                logging.critical("Disk full! Exiting to trigger Docker restart.")
                sys.exit(1)  # forcing exit so Docker restarts the container

            await ctx.send(f"❌ An error occurred: {str(e)}")
bot.run(DISCORD_BOT_TOKEN)
