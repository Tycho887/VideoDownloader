from discord.ext import commands
import discord
from scripts.handler import download_media, supported_formats
from API_key.token import DISCORD_BOT_TOKEN
import os

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
    await ctx.send("Commands: !ping, !guide, !download <url> <format> <start> <end>")

async def send_file(ctx, file_name):
    try:
        assert os.path.exists(file_name), "The file does not exist!"
        assert os.path.isfile(file_name), "The file is not a file!"
        assert file_name.endswith(supported_formats), "The file is not a supported format!"
        
        # Open the file and send it
        with open(file_name, 'rb') as file:
            await ctx.send(file=discord.File(file, file_name))

    except discord.errors.HTTPException as e:
        print(f"Error sending file: {e}")
        await ctx.send(f"Error sending file: {e}")
        return
    except AssertionError as e:
        print(f"Error sending file: {e}")
        await ctx.send(f"Error sending file: {e}")
        return
    except FileNotFoundError as e:
        print(f"Error sending file: {e}")
        await ctx.send(f"Error sending file: {e}")
        return

def remove_files():
    # We want to remove all mp3, mp4, and gif files in the downloads folder
    for file in os.listdir("downloads"):
        if file.endswith(supported_formats):
            try:
                os.remove(os.path.join("downloads", file))
            except Exception as e:
                print(f"Error removing file: {e}")
                continue

@bot.command()
async def download(ctx, url, format='mp4', start=None, end=None):

    try:
        start = float(start) if start is not None else None
        end = float(end) if end is not None else None
    except ValueError as e:
        await ctx.send(f"Input format is: !download <url> <format> <start> <end>")
        return

    try:
        assert format in supported_formats, f"Unsupported format: {format}"
        assert url is not None, "URL is required"
        assert isinstance(start, (int, float)) or start is None, "Invalid start time"
        assert isinstance(end, (int, float)) or end is None, "Invalid end time"
    except AssertionError as e:
        await ctx.send(f"Input format is: !download <url> <format> <start> <end>")
        return

    await ctx.send("Downloading media...")

    try:
        file_name, generated_files = download_media(url=url, format=format, start=start, end=end)
        assert os.path.exists(file_name), f"File does not exist: {file_name}"
    except ValueError as e:
        await ctx.send(f"Failed safety checks: {e}")
        remove_files()
        return
    except Exception as e:
        await ctx.send(f"Error downloading: {e}")
        remove_files()
        return

    await ctx.send("Downloaded successfully")

    await send_file(ctx, file_name)

    # Ensure all pending tasks (like file sending) are completed before removing files
    await discord.utils.sleep_until(discord.utils.utcnow())

    remove_files()

bot.run(DISCORD_BOT_TOKEN)
