from discord.ext import commands
import discord
from vidlib import get_bot_token, download_media, supported_formats, extract_arguments, remove_files, remove_file, MAX_size
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
    assert file_name.endswith(supported_formats), "The file is not a supported format!"
    
    with open(file_name, 'rb') as file:
        await ctx.send(file=discord.File(file, file_name))
    logging.info(f"File sent successfully: {file_name}")

@bot.command()
async def download(ctx, *, args):
    logging.info("Download command received with arguments: %s", args)
    
    try:
        url, options = extract_arguments(args)

        assert url is not None, "A valid URL must be provided."
        format = options['format']
        assert format in supported_formats, f"format '{format}' is unsupported, choose one of {supported_formats}"

        start = float(options['start']) if options['start'] is not None else None
        end = float(options['end']) if options['end'] is not None else None

        print(start, end)

        if start is not None:
            assert start >= 0, f"Invalid start time: {start}"
        if end is not None:
            assert end >= 0, f"Invalid end time: {end}"
        if start is not None and end is not None:
            assert start < end, f"Start time must be less than end time. Got start={start}, end={end}"
        
        resolution_tuple = None
        if options['resolution']:
            assert len(options['resolution'].split('x')) == 2, "Invalid resolution format. Use <width>x<height>"
            assert all(x.isdigit() for x in options['resolution'].split('x')), "Resolution values must be integers."
            assert all(int(x) > 0 for x in options['resolution'].split('x')), "Resolution values must be positive."
            assert all(int(x) <= MAX_size for x in options['resolution'].split('x')), f"Resolution values must be less than or equal to {MAX_size}"
            resolution_tuple = tuple(map(int, options['resolution'].split('x')))

        await ctx.send("Downloading media...")
        logging.info("Downloading media with options: %s", options)

        file_name, generated_files = download_media(url=url, target_format=format, start_time=start, end_time=end, resolution=resolution_tuple)

        assert os.path.exists(file_name), f"File does not exist: {file_name}"
        logging.info("Media downloaded successfully: %s", file_name)

        await ctx.send("Downloaded successfully")
        await send_file(ctx, file_name)

        await discord.utils.sleep_until(discord.utils.utcnow())
        remove_file(file_name)
        logging.info("Temporary file removed: %s", file_name)

    except Exception as e:
        logging.error("Error during download: %s", str(e))
        await ctx.send(f"An error occurred: \n{e}")

bot.run(DISCORD_BOT_TOKEN)
