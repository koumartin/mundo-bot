import discord
import asyncio
import queue
import os
from clashmanager import ClashManager
from discord.ext import commands
from discord.ext.commands.context import Context as Context
from typing import Dict, Tuple

# -------------------------------------------
# ADDITIONAL INFORMATION:
# Author: @koumartin
# Date: 22/3/2021
# -------------------------------------------

bot = commands.Bot(command_prefix='!')
TOKEN = "ODIyNTk0ODA1NDI2NDIxNzgx.YFUjHA.7FvSQXT6jvQGGxiXeoffRxQTf3U"
path = os.path.dirname(os.path.abspath(__file__))
clash: ClashManager

# Create global variables
mundo_queue: Dict[discord.Guild, queue.Queue] = {}
# Value is tuple of (handling, stop)
handling_mundo_queue: Dict[discord.Guild, Tuple[bool, bool]] = {}


@bot.event
async def on_ready():
    global clash
    clash = ClashManager(path)
    await check_expired_clashes(clash)

    print("Logged in.")


async def check_expired_clashes(clash):
    expired = clash.check_clashes()
    for name, date in expired.items():
        for guild in bot.guilds:
            role_name = name + " Player"
            roles = (r for r in guild.roles if r.name == role_name)
            for r in roles:
                await r.delete()
            channels = (c for c in guild.channels if c.name == name.replace(" ", "-").lower())
            for c in channels:
                await c.delete()


@bot.event
async def on_voice_state_update(member, before, after):
    # Ignores himself moving
    if member == bot.user:
        return

    # Check if the state update was joining a room
    if before.channel != after.channel and after.channel is not None:
        print(member, "from channel", before.channel, "to", after.channel, "in", after.channel.guild)
        await add_to_queue(member.guild, after.channel)


@bot.command()
async def mundo(ctx: Context, num=1):
    # Guard for receiving command from DMChannel
    if not isinstance(ctx.channel, discord.TextChannel):
        await ctx.author.send("Mundo can't greet without real channel.")
        return

    await ctx.message.delete()

    print(ctx.author, "called !mundo with n =", num, "in", ctx.guild)

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
async def shutup(ctx: Context, additional=""):
    guild = ctx.guild

    voice_client = discord.utils.get(bot.voice_clients, guild=guild)

    await conditional_delete(ctx.message)

    print(ctx.author, "called !shutup in", ctx.guild)

    # Remake
    if ctx.author.name != "KoudyCZ" and ctx.author.name != "adjalS" \
            and additional.lower() != "please" and additional.lower() != "prosím":
        await ctx.author.send("You no tell Mundo what Mundo do!!!")
        return
    else:
        if additional.lower() == "please" and additional.lower() == "prosím":
            await ctx.author.send("You say please so nice... Okey Mundo be silent now.")
        if voice_client is not None:
            voice_client.stop()
        handling_mundo_queue[guild] = (True, True)
        mundo_queue[guild] = queue.Queue()


@bot.command()
async def add_clash(ctx: Context, name: str, date: str):
    await conditional_delete(ctx.message)

    if ctx.author.name != "KoudyCZ":
        return
    clash.add_clash(name, date)


    overwrites = {}
    author_role = max(ctx.author.roles)
    for r in ctx.guild.roles:
        overwrites[r] = discord.PermissionOverwrite(read_messages = r >= author_role)

    role_name = name + " Player"
    role = next((r for r in ctx.guild.roles if r.name == role_name), None)
    if role is None:
        role: discord.Role = await ctx.guild.create_role(name=role_name,
                                                         permissions=ctx.guild.default_role.permissions)
        overwrites[role] = discord.PermissionOverwrite(read_messages=True)

    category = next((c for c in ctx.guild.categories if c.name == "Clash"))
    channel = next((c for c in ctx.guild.channels if c.name == name.replace(" ", "-").lower()), None)
    if channel is None:
        await ctx.guild.create_text_channel(name, overwrites=overwrites, category=category)


# -----------------------------------------------------
# Additional non Discord API functions for cleaner code
# -----------------------------------------------------
async def add_to_queue(guild: discord.Guild, channel: discord.VoiceChannel, num=1):
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


async def play_from_queue(guild: discord.Guild):
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
            await play_mundo_sound(voice_client, "assets/mundo-say-name-often.mp3")
        else:
            await play_mundo_sound(voice_client, "assets/muundo.mp3")

        while voice_client.is_playing():
            # Not clean but it iiiis what it iiiis
            await asyncio.sleep(.1)

    if voice_client.is_connected():
        await voice_client.disconnect()
    handling_mundo_queue[guild] = (False, False)


async def play_mundo_sound(voice_client: discord.VoiceClient, file_name):
    # Play muundo.mp3
    audio_path = os.path.join(path, file_name)
    voice_client.play(discord.FFmpegPCMAudio(audio_path))


async def conditional_delete(message: discord.Message):
    if isinstance(message.channel, discord.TextChannel):
        await message.delete()



# RUN THE CLIENT
bot.run(TOKEN)
