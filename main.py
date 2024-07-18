from discord.ext import commands
import discord
from scripts.downloaders import download_media, supported_formats, convert_to_gif
from API_key.token import DISCORD_BOT_TOKEN
import os
# import youtube_dl
# import asyncio

CHANNEL_ID = 1257450460730753147 #1252712820567703582

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Bot is ready")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

async def send_file(ctx, file_name):
    try:
        assert os.path.exists(file_name), "The file does not exist!"
        assert os.path.isfile(file_name), "The file is not a file!"
        assert file_name.endswith(supported_formats), "The file is not a supported format!"

        await ctx.send(file=discord.File(file_name))
        os.remove(file_name)
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

@bot.command()
async def download(ctx, url, format='mp4', tStart=None, tEnd=None):
    GIF = False
    if format.lower() == "gif":
        format = "mp4"
        GIF = True

    await ctx.send("Downloading media...")
    try:
        file_name = download_media(url, format)
    except ValueError as e:
        await ctx.send(f"Failed safety checks: {e}")
        return
    except Exception as e:
        await ctx.send(f"Error downloading: {e}")
        return

    await ctx.send("Downloaded successfully")

    if GIF:
        await ctx.send("Converting to GIF...")
        try:
            file_name = convert_to_gif(file_name, tStart, tEnd)
        except Exception as e:
            await ctx.send(f"Error converting to GIF: {e}")
            return
        await ctx.send("Converted successfully")

    await send_file(ctx, file_name)

# @bot.command()
# async def join(ctx):
#     if ctx.author.voice is None:
#         await ctx.send("You are not connected to a voice channel.")
#         return

#     channel = ctx.author.voice.channel
#     if ctx.voice_client is None:
#         await channel.connect()
#     else:
#         await ctx.voice_client.move_to(channel)

# @bot.command()
# async def leave(ctx):
#     if ctx.voice_client is not None:
#         await ctx.voice_client.disconnect()
#         await ctx.send("Disconnected from the voice channel.")
#     else:
#         await ctx.send("I am not connected to a voice channel.")

# @bot.command()
# async def play(ctx, url):
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
#     }

#     try:
#         if ctx.author.voice is None:
#             await ctx.send("You are not connected to a voice channel.")
#             return

#         channel = ctx.author.voice.channel
#         if ctx.voice_client is None:
#             await channel.connect()

#         voice_client = ctx.voice_client
#         if not voice_client.is_playing():
#             with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(url, download=False)
#                 url2 = info['formats'][0]['url']
#                 voice_client.play(discord.FFmpegPCMAudio(url2))
#                 await ctx.send(f"Now playing: {info['title']}")
#         else:
#             await ctx.send("I am already playing a song!")
#     except Exception as e:
#         await ctx.send(f"An error occurred: {e}")

bot.run(DISCORD_BOT_TOKEN)
