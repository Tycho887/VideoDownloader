from discord.ext import commands
import discord
import os
import logging
import re
from download import VideoDownloader, VideoJob
import asyncio
from validate import validate_url, validate_format, validate_times, validate_resolution
from utils import remove_files, remove_file, extract_arguments, seconds_to_hhmmss, SUPPORTED_FORMATS, DOWNLOAD_FOLDER

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Default log level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("bot.log", encoding='utf-8')  # Log to file
    ]
)

DISCORD_BOT_TOKEN = os.getenv("DOWNLOAD_BOT_TOKEN")

# Create an instance of a bot with all intents enabled
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    logging.info(f"Bot is ready, logged in as {bot.user}")
    logging.info("Clearing downloads folder...")
    remove_files()


@bot.command()
async def ping(ctx):
    logging.info("Ping command received.")
    await ctx.send("Pong!")


@bot.command()
async def guide(ctx):
    logging.info("Guide command received.")
    await ctx.send("Commands: !ping, !guide, !download <url> [format=<format>] [start=<start>] [end=<end>] [resolution=<resolution>]")


async def send_file(ctx, file_name):
    logging.info(f"Attempting to send file: {file_name}")
    assert os.path.exists(file_name), "The file does not exist!"
    assert os.path.isfile(file_name), "The file is not a file!"
    assert file_name.endswith(SUPPORTED_FORMATS), "The file is not a supported format!"
    
    with open(file_name, 'rb') as file:
        await ctx.send(file=discord.File(file, file_name))
    logging.info(f"File sent successfully: {file_name}")

@bot.command()
async def download(ctx, *, args):
    logging.info("Download command received with arguments: %s", args)

    try:
        url, options = extract_arguments(args)

        validate_url(url)
        format = options['format'].lower()
        validate_format(format)

        start = float(options['start']) if options['start'] else None
        end = float(options['end']) if options['end'] else None
        validate_times(start, end)

        resolution = options['resolution']
        resolution_tuple = tuple(map(int, resolution.split('x'))) if resolution else None

        framerate = int(options['framerate']) if options['framerate'] else None

        await ctx.send("Downloading media...")
        logging.info("Downloading with parsed options: %s", options)
        
        print(f"Downloading {url} with format {format}, start {start}, end {end}, resolution {resolution}, framerate {framerate}")

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
        file_name = await asyncio.to_thread(downloader.run_job, job)
        await send_file(ctx, file_name)
        remove_file(file_name)
        logging.info("Temporary file removed: %s", file_name)

    except Exception as e:
        logging.exception("Error during download:")
        await ctx.send(f"❌ An error occurred: {str(e)}")

    finally:
        remove_file(file_name)

bot.run(DISCORD_BOT_TOKEN)
