import discord
from discord.ext import commands

client = discord.Client()

TOKEN = "ODIyNTk0ODA1NDI2NDIxNzgx.YFUjHA.7FvSQXT6jvQGGxiXeoffRxQTf3U"


@client.event
async def on_ready():
    print("Logged in.")


@client.event
async def on_voice_state_update(member, before, after):
    # Checks if user moved from channel to channel
    if member == client.user:
        print("Me to " + str(after.channel))
        return


    if before.channel != after.channel and after.channel is not None:

        try:
            voice = discord.utils.get(client.voice_clients,  guild=member.guild)
            if voice is not None:
                if not voice.is_connected():
                    await after.channel.connect()
                else:
                    await voice.disconnect()
                    await after.channel.connect()
            else:
                await after.channel.connect()

        except Exception as err:
            print(err)

        print(str(member) + " from channel " + str(before.channel) + " to " + str(after.channel))


client.run(TOKEN)
