import discord
from discord.ext import commands

client = commands.Bot(command_prefix="!")
TOKEN = "ODIyNTk0ODA1NDI2NDIxNzgx.YFUjHA.7FvSQXT6jvQGGxiXeoffRxQTf3U"


@client.command()
async def play(ctx, url : str):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name="Obecné")
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    await voiceChannel.connect()

client.run(TOKEN)