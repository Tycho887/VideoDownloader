from discord.ext import commands
import discord
from lib.handler import download_media, supported_formats
# from API_key.token import DISCORD_BOT_TOKEN
from lib.utils import get_bot_token
import os

DISCORD_BOT_TOKEN = get_bot_token()

# Create an instance of a bot with all intents enabled
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot is ready, logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def guide(ctx):
    await ctx.send("Commands: !ping, !guide, !download <url> <format> <start> <end> <resolution (optional)>")

async def send_file(ctx, file_name):
    # Remove error handling here, let any issue raise normally
    assert os.path.exists(file_name), "The file does not exist!"
    assert os.path.isfile(file_name), "The file is not a file!"
    assert file_name.endswith(supported_formats), "The file is not a supported format!"
    
    # Open the file and send it
    with open(file_name, 'rb') as file:
        await ctx.send(file=discord.File(file, file_name))

def remove_files():
    # Remove all mp3, mp4, and gif files in the downloads folder
    for file in os.listdir("downloads"):
        if file.endswith(supported_formats):
            os.remove(os.path.join("downloads", file))

@bot.command()
async def download(ctx, url, format='mp4', start=None, end=None, resolution=None):
    # Convert start and end to float if provided
    start = float(start) if start is not None else None
    end = float(end) if end is not None else None

    # Validate format
    assert format in supported_formats, f"Unsupported format: {format}"
    assert url is not None, "URL is required"
    assert isinstance(start, (int, float)) or start is None, "Invalid start time"
    assert isinstance(end, (int, float)) or end is None, "Invalid end time"

    # Process resolution
    resolution_tuple = None

    if resolution:
        resolution_values = [int(x) for x in resolution.split('x')]
        if len(resolution_values) == 1:
            resolution_tuple = (resolution_values[0], None)  # Keep aspect ratio
        elif len(resolution_values) == 2:
            resolution_tuple = (resolution_values[0], resolution_values[1])  # Full resize
        else:
            raise ValueError("Invalid resolution format. Use <width>x<height> or just <width>.")

    await ctx.send("Downloading media...")

    # Pass resolution to download_media
    file_name, generated_files = download_media(url=url, format=format, start=start, end=end, resolution=resolution_tuple)
    
    # Check if file exists
    assert os.path.exists(file_name), f"File does not exist: {file_name}"

    await ctx.send("Downloaded successfully")
    
    await send_file(ctx, file_name)

    # Ensure all pending tasks (like file sending) are completed before removing files
    await discord.utils.sleep_until(discord.utils.utcnow())

    remove_files()

bot.run(DISCORD_BOT_TOKEN)
