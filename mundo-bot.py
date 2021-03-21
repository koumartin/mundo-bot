import discord
from discord.ext import commands

client = discord.Client()
bot = commands.Bot(command_prefix='!')

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

        # TODO: Later create a queue and service it
        # Finds current voice_channel in this guild
        voice = discord.utils.get(client.voice_clients, guild=member.guild)
        
        # In case bot isn't connected to a voice_channel yet
        if voice is None:
            voice_client = await after.channel.connect()
        # Else first disconnect bot from current channel and than connect it
        else:
            voice_client = await voice.move_to(after.channel)

        





        print(str(member) + " from channel " + str(before.channel) + " to " + str(after.channel))


client.run(TOKEN)
