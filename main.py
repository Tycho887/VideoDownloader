from discord.ext import commands
import discord
# from lib import get_bot_token, download_media, supported_formats, extract_arguments, remove_files, remove_file, MAX_size
from lib import *
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Default log level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("bot.log", encoding='utf-8')  # Log to file
    ]
)

DISCORD_BOT_TOKEN = get_bot_token()

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

        # Extract arguments
        url, options = extract_arguments(args)

        # Perform validations
        validate_url(url)
        format = options['format'].lower()
        validate_format(format)

        start = float(options['start']) if options['start'] else None
        end = float(options['end']) if options['end'] else None
        validate_times(start, end)

        resolution = options['resolution']
        if resolution:
            validate_resolution(resolution)
            resolution_tuple = tuple(map(int, resolution.split('x')))
        else:
            resolution_tuple = None

        # Proceed with download and processing
        await ctx.send("Downloading media...")
        logging.info("Downloading media with options: %s", options)

        file_name, generated_files = download_media(
            url=url, target_format=format, start_time=start, end_time=end, resolution=resolution_tuple
        )

        await send_file(ctx, file_name)
        remove_file(file_name)
        logging.info("Temporary file removed: %s", file_name)

    except Exception as e:
        logging.error("Error during download: %s", str(e))
        await ctx.send(f"An error occurred: {e}")
    
    finally:

        # Clean up
        remove_files()


bot.run(DISCORD_BOT_TOKEN)
