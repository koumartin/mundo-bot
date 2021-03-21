import discord
import asyncio
import queue
import os
from discord.ext import commands

# -------------------------------------------
# NOT SUITABLE FOR USE IN MULTIPLE GUILDS YET
# Solution might be to have dictionary of handling queue running and guilds
# -------------------------------------------

client = discord.Client()
# Command bot might be used later
# bot = commands.Bot(command_prefix='!')

TOKEN = "ODIyNTk0ODA1NDI2NDIxNzgx.YFUjHA.7FvSQXT6jvQGGxiXeoffRxQTf3U"

# Create global variables
music_queue = queue.Queue()
is_handling_queue = False


@client.event
async def on_ready():
    print("Logged in.")


@client.event
async def on_voice_state_update(member, before, after):
    # Ignores himself moving
    if member == client.user:
        return

    # Check if the state update was joining a room
    if before.channel != after.channel and after.channel is not None:

        # Put channel to a music queue
        music_queue.put((after.channel, member.guild))
        # If queue isn't already handled start handling it
        if not is_handling_queue:
            await play_from_queue()

        print(str(member) + " from channel " + str(before.channel) + " to " + str(after.channel))


async def play_from_queue():
    global is_handling_queue, music_queue

    while not music_queue.empty():
        is_handling_queue = True
        channel, guild = music_queue.get()

        # Finds current voice_channel in this guild
        voice = discord.utils.get(client.voice_clients, guild=guild)

        # In case bot isn't connected to a voice_channel yet
        if voice is None:
            voice_client = await channel.connect()
        # Else first disconnect bot from current channel and than connect it
        else:
            # Wait for current audio to stop playing
            while voice.is_playing():
                await asyncio.sleep(.1)
            voice_client = await voice.move_to(channel)

        # Play muundo.mp3
        audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "muundo.mp3")
        voice_client.play(discord.FFmpegPCMAudio(audio_path))

        while voice_client.is_playing():
            # Not clean but it iiiis what it iiiis
            await asyncio.sleep(.1)

        await voice_client.disconnect()

    is_handling_queue = False

# RUN THE CLIENT
client.run(TOKEN)
