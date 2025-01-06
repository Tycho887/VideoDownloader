from discord.ext import commands
import discord
from lib.handler import download_media, supported_formats
# from API_key.token import DISCORD_BOT_TOKEN
from lib.utils import get_bot_token
import os
import re

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

def extract_arguments(args):
    """
    Extract arguments from a string using regex.

    Arguments:
    args -- string containing arguments

    Returns:
    url -- URL to download media from
    options -- dictionary containing specified options
    """
    # Parse arguments using regex
    pattern = r'(?P<url>https?://\S+)|(?P<key>\w+)=(?P<value>[\w:\.x]+)'
    matches = re.findall(pattern, args)

    # Initialize default values
    url = None
    options = {
        'format': 'mp4',
        'start': None,
        'end': None,
        'resolution': None,
    }

    # Process matches
    for match in matches:
        if match[0]:
            url = match[0]  # URL matched
        elif match[1] and match[2]:
            key, value = match[1], match[2]
            if key in options:
                options[key] = value

    return url, options

@bot.command()
async def download(ctx, *, args):
    """
    Download media from a provided URL with specified options.

    Example usage:
    !download https://example.com/video resolution=1920x1080 format=mp4 start=30 end=120
    """
    # Extract arguments
    url, options = extract_arguments(args)

    # Validate URL
    assert url is not None, "A valid URL must be provided."

    # Validate and convert options
    format = options['format']
    assert format in supported_formats, f"Unsupported format: {format}"

    start = float(options['start']) if options['start'] is not None else None
    end = float(options['end']) if options['end'] is not None else None
    
    resolution_tuple = None
    if options['resolution']:
        resolution_values = [int(x) for x in options['resolution'].split('x')]
        if len(resolution_values) == 1:
            resolution_tuple = (resolution_values[0], None)  # Keep aspect ratio
        elif len(resolution_values) == 2:
            resolution_tuple = (resolution_values[0], resolution_values[1])  # Full resize
        else:
            raise ValueError("Invalid resolution format. Use <width>x<height> or just <width>.")

    await ctx.send("Downloading media...")

    # Download media
    file_name, generated_files = download_media(url=url, format=format, start=start, end=end, resolution=resolution_tuple)

    # Validate file existence
    assert os.path.exists(file_name), f"File does not exist: {file_name}"

    await ctx.send("Downloaded successfully")

    # Send file
    await send_file(ctx, file_name)

    # Ensure all tasks are completed before cleanup
    await discord.utils.sleep_until(discord.utils.utcnow())

    remove_files()



# @bot.command()
# async def download(ctx, *, args):
#     """
#     Download media from a provided URL with specified options.

#     Example usage:
#     !download "link" resolution=1920x1080 format=mp4 start=30 end=120
#     """
#     # Parse arguments using regex
#     pattern = r'"(?P<url>.+?)"|(?P<key>\w+)=(?P<value>[\w:\.x]+)'
#     matches = re.findall(pattern, args)

#     # Initialize default values
#     url = None
#     options = {
#         'format': 'mp4',
#         'start': None,
#         'end': None,
#         'resolution': None,
#     }

#     # Process matches
#     for match in matches:
#         if match[0]:
#             url = match[0]  # URL matched
#         elif match[1] and match[2]:
#             key, value = match[1], match[2]
#             if key in options:
#                 options[key] = value

#     # Validate URL
#     assert url is not None, "A valid URL must be provided in quotes."

#     # Validate and convert options
#     format = options['format']
#     assert format in supported_formats, f"Unsupported format: {format}"

#     start = float(options['start']) if options['start'] is not None else None
#     end = float(options['end']) if options['end'] is not None else None
    
#     resolution_tuple = None
#     if options['resolution']:
#         resolution_values = [int(x) for x in options['resolution'].split('x')]
#         if len(resolution_values) == 1:
#             resolution_tuple = (resolution_values[0], None)  # Keep aspect ratio
#         elif len(resolution_values) == 2:
#             resolution_tuple = (resolution_values[0], resolution_values[1])  # Full resize
#         else:
#             raise ValueError("Invalid resolution format. Use <width>x<height> or just <width>.")

#     await ctx.send("Downloading media...")

#     # Download media
#     file_name, generated_files = download_media(url=url, format=format, start=start, end=end, resolution=resolution_tuple)

#     # Validate file existence
#     assert os.path.exists(file_name), f"File does not exist: {file_name}"

#     await ctx.send("Downloaded successfully")

#     # Send file
#     await send_file(ctx, file_name)

#     # Ensure all tasks are completed before cleanup
#     await discord.utils.sleep_until(discord.utils.utcnow())

#     remove_files()

bot.run(DISCORD_BOT_TOKEN)
