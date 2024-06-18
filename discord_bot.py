from discord.ext import commands
import discord
from scripts import download_youtube_video, download_twitter_video
from API_key.token import DISCORD_BOT_TOKEN
import os

CHANNEL_ID = 1252712820567703582

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Bot is ready")

def download_video(url):
    file_name = None
    if "youtube" in url:
        file_name = download_youtube_video(url)
    elif "twitter" in url:
        file_name = download_twitter_video(url)
    return file_name

@bot.command()
async def download(ctx, url):
    await ctx.send("Downloading video...")
    file_name = download_video(url)
    if file_name:
        await ctx.send(f"Video downloaded successfully as {file_name}")
        if os.path.exists(file_name):
            try:
                await ctx.send(file=discord.File(file_name))
            except discord.errors.HTTPException as e:
                await ctx.send(f"Error sending file: {e}")
    else:
        await ctx.send("Failed to download the video.")

bot.run(DISCORD_BOT_TOKEN)
