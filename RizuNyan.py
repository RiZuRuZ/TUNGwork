import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
import re

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='=', intents=intents)

# Global variable to hold the song queue
song_queue = []

# Sanitize the filename
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace invalid characters with underscores

# Create downloads directory if it doesn't exist
os.makedirs('downloads', exist_ok=True)


# Download song function
async def download_song(url):
    loop = asyncio.get_event_loop()
    ydl = yt_dlp.YoutubeDL({
        'format': 'bestaudio',
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Specify the output template
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })

    def run_download():
        return ydl.extract_info(url, download=True)

    # Run the download in a separate thread
    info = await loop.run_in_executor(None, run_download)

    # Get the original downloaded filename
    original_filename = os.path.join('downloads', f"{info['id']}.mp3")
    
    # Sanitize the filename
    sanitized_filename = sanitize_filename(info['title'])
    download_path = os.path.join('downloads', f"{sanitized_filename}.mp3")

    # Check if the file already exists and create a unique filename if it does
    if os.path.exists(download_path):
        base, ext = os.path.splitext(download_path)
        counter = 1
        # Generate a new filename until an unused one is found
        while os.path.exists(download_path):
            download_path = f"{base} ({counter}){ext}"
            counter += 1

    # Rename the file
    try:
        os.rename(original_filename, download_path)
    except FileNotFoundError:
        print(f"File {original_filename} not found. It may not have been downloaded correctly.")
        raise

    return download_path  # Return the sanitized download path

# Command to join a voice channel
@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'Joined {channel}')
    else:
        await ctx.send('You need to be in a voice channel to use this command.')

# Command to play a song
@bot.command()
async def play(ctx, url: str):
    # Check if the bot is connected to a voice channel
    if ctx.voice_client is None:
        await ctx.send("I am not connected to a voice channel. Please join a voice channel first.")
        return
    
    await ctx.send(f"Downloading song from: {url}")
    
    try:
        downloaded_song = await download_song(url)
        # Add only the filename to the queue
        song_queue.append(os.path.basename(downloaded_song))  # Append just the filename to the queue
        await ctx.send(f'Added to queue: {os.path.basename(downloaded_song)}')
        
        # Check if audio is currently playing
        if len(song_queue) == 1 and not ctx.voice_client.is_playing():
            await play_next(ctx)
        else:
            await ctx.send('Song added to queue. Currently playing another song.')
    except Exception as e:
        await ctx.send(f"An error occurred while downloading the song: {e}")

# Play next song function
async def play_next(ctx):
    global song_queue
    if song_queue:
        current_song = song_queue.pop(0)  # Get the next song
        normalized_path = os.path.join('downloads', current_song)
        
        if os.path.exists(normalized_path):
            ctx.voice_client.play(discord.FFmpegPCMAudio(normalized_path), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
            await ctx.send(f'Now playing: {current_song}')
            print(f"Playing song: {current_song}")  # Debug line
        else:
            print(f"File {normalized_path} not found or invalid.")
            await ctx.send(f"Error: Could not play {current_song}")
            await play_next(ctx)  # Skip to the next song if the file is invalid
    else:
        print("Queue is empty")

# Command to stop the music
@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('Stopped the music.')
    else:
        await ctx.send('No music is currently playing.')

# Command to pause the music
@bot.command(name='pause')
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send('Paused the music.')
    else:
        await ctx.send('No music is currently playing.')

# Command to resume the music
@bot.command(name='resume')
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send('Resumed the music.')
    else:
        await ctx.send('No music is currently paused.')

# Command to see the current queue
@bot.command(name='queue')
async def queue(ctx):
    if song_queue:
        await ctx.send('Current queue:\n' + '\n'.join(song_queue))
    else:
        await ctx.send('Queue is empty.')

# Command to skip the current song
@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('Skipped the current song.')
    else:
        await ctx.send('No music is currently playing.')

# Command to leave the voice channel
@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('Disconnected from the voice channel.')
    else:
        await ctx.send('I am not in a voice channel.')

# Run the bot
bot.run('')
