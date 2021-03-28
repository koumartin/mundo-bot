import discord
import asyncio
import queue
import os
from discord.ext import commands

# -------------------------------------------
# ADDITIONAL INFORMATION:
# Author: @koumartin
# Date: 22/3/2021
# Not really thread safe but I am lazy
# -------------------------------------------

# client = discord.Client()
# Command bot might be used later
bot = commands.Bot(command_prefix='!')

TOKEN = "ODIyNTk0ODA1NDI2NDIxNzgx.YFUjHA.7FvSQXT6jvQGGxiXeoffRxQTf3U"

# Create global variables
mundo_queue = {}
handling_mundo_queue = {}



@bot.event
async def on_ready():
    print("Logged in.")


@bot.event
async def on_voice_state_update(member, before, after):
    # Ignores himself moving
    if member == bot.user:
        return

    # Check if the state update was joining a room
    if before.channel != after.channel and after.channel is not None:

        await add_to_queue(member.guild, after.channel)

        print(str(member) + " from channel " + str(before.channel) + " to " + str(after.channel))


@bot.command()
async def mundo(ctx, num=1):
    await ctx.message.delete()

    if num > 30:
        await ctx.author.send("Mundo will no greet you so much. Mundo no stupid.")
        return
    if num < 0:
        await ctx.author.send("Mundo no stupid, unlike you. No saying negative times...")
        return

    if ctx.author.voice is not None:
        voice_channel = ctx.author.voice.channel
    else:
        voice_channel = None

    if voice_channel is not None:
        await add_to_queue(ctx.guild, voice_channel, num)
    else:
        await ctx.author.send("Mundo can't greet without voice channel.")


@bot.command()
async def shutup(ctx, additional=""):
    guild = ctx.guild

    voice_client = discord.utils.get(bot.voice_clients, guild=guild)

    await ctx.message.delete()

    if ctx.author.name != "KoudyCZ" and additional.lower() != "please":
        await ctx.author.send("You no tell Mundo what Mundo do!!!")
        return
    else:
        if additional.lower() == "please":
            await ctx.author.send("You say please so nice... Okey Mundo be silent now.")
        if voice_client is not None:
            voice_client.stop()
        handling_mundo_queue[guild] = (True, True)
        mundo_queue[guild] = queue.Queue()


# -----------------------------------------------------
# Additional non Discord API functions for cleaner code
# -----------------------------------------------------
async def add_to_queue(guild, channel, num=1):
    global handling_mundo_queue, mundo_queue
    if guild not in mundo_queue:
        mundo_queue[guild] = queue.Queue()

    # Put channel to a music queue
    for _ in range(num):
        mundo_queue[guild].put(channel)

    if guild not in handling_mundo_queue:
        handling_mundo_queue[guild] = (False, False)

    # If queue isn't already handled start handling it
    if handling_mundo_queue[guild][0] is False:
        await play_from_queue(guild)


async def play_from_queue(guild):
    global handling_mundo_queue, mundo_queue

    # Finds current voice_channel in this guild
    voice_client = discord.utils.get(bot.voice_clients, guild=guild)
    i = 0

    while not mundo_queue[guild].empty():
        handling, stop = handling_mundo_queue[guild]
        if stop is True:
            handling_mundo_queue[guild] = (False, False)
            return
        else:
            handling_mundo_queue[guild] = (True, False)
        channel = mundo_queue[guild].get()
        i += 1

        # In case bot isn't connected to a voice_channel yet
        if voice_client is None:
            voice_client = await channel.connect()
        # Else first disconnect bot from current channel and than connect it
        else:
            # Wait for current audio to stop playing
            while voice_client.is_playing():
                await asyncio.sleep(.1)
            await voice_client.move_to(channel)

        if i >= 5:
            i = 0
            await play_mundo_sound(voice_client, "mundo-say-name-often.mp3")
        else:
            await play_mundo_sound(voice_client, "muundo.mp3")

        while voice_client.is_playing():
            # Not clean but it iiiis what it iiiis
            await asyncio.sleep(.1)

    if voice_client.is_connected():
        await voice_client.disconnect()
    handling_mundo_queue[guild] = False


async def play_mundo_sound(voice_client, file_name):
    # Play muundo.mp3
    audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    voice_client.play(discord.FFmpegPCMAudio(audio_path))

# RUN THE CLIENT
bot.run(TOKEN)
