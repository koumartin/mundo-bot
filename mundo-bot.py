import discord
import asyncio
import queue
import os
from clashmanager import ClashManager
from positions import Positions
from discord.ext import commands
from discord.ext.commands.context import Context as Context
from typing import Dict, Tuple

# -------------------------------------------
# ADDITIONAL INFORMATION:
# Author: @koumartin
# Date: 22/3/2021
# -------------------------------------------


class MundoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        commands.Bot.__init__(self, command_prefix='!', intents=intents)
        self.TOKEN = "ODIyNTk0ODA1NDI2NDIxNzgx.YFUjHA.7FvSQXT6jvQGGxiXeoffRxQTf3U"
        self.path = os.path.dirname(os.path.abspath(__file__))

        # Create global variables
        self.mundo_queue: Dict[discord.Guild, queue.Queue] = {}
        # Value is tuple of (handling, stop)
        self.handling_mundo_queue: Dict[discord.Guild, Tuple[bool, bool]] = {}

        self.clash: ClashManager = ClashManager(self.path)
        self.add_all_commands()
        self.accepted_reactions = Positions.accepted_reactions()

    def start_running(self):
        self.run(self.TOKEN)

    # Gives bot all events and commands
    def add_all_commands(self):
        @self.event
        async def on_ready():
            await self.check_expired_clashes()
            print("Logged in.")

        @self.event
        async def on_voice_state_update(member, before, after):
            # Ignores himself moving
            if member == self.user:
                return

            # Check if the state update was joining a room
            if before.channel != after.channel and after.channel is not None:
                print(member, "from channel", before.channel, "to", after.channel, "in", after.channel.guild)
                await self.add_to_queue(member.guild, after.channel)

        @self.event
        async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
            for name, (guild_id, channel_id, message_id, date, role_id) in self.clash.clashes.items():
                if reaction.guild_id == guild_id and reaction.channel_id == channel_id and reaction.message_id == message_id:
                    if reaction.emoji.name in self.accepted_reactions:
                        guild = self.get_guild(guild_id)
                        position = Positions.get_position(reaction.emoji.name)
                        role = guild.get_role(role_id)

                        await reaction.member.add_roles(role)
                        self.clash.register_player(name, reaction.member.name, position)

                        break

            # TODO: Keep track of players in the clash
            # TODO: Updating message at the start of channel telling who is playing
            # TODO: Mundo has to run in cloud or check if reactions are corresponding to current players in DS

        @self.event
        async def on_raw_reaction_remove(reaction: discord.RawReactionActionEvent):
            for name, (guild_id, channel_id, message_id, date, role_id) in self.clash.clashes.items():
                if reaction.guild_id == guild_id and reaction.channel_id == channel_id and reaction.message_id == message_id:
                    if reaction.emoji.name in self.accepted_reactions:
                        position = Positions.get_position(reaction.emoji.name)
                        guild = self.get_guild(guild_id)
                        member = guild.get_member(reaction.user_id)

                        if position == self.clash.players[name][member.name]:
                            role = guild.get_role(role_id)
                            await member.remove_roles(role)
                            self.clash.unregister_player(name, member.name)
                        break

        @self.command()
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
                await self.add_to_queue(ctx.guild, voice_channel, num)
            else:
                await ctx.author.send("Mundo can't greet without voice channel.")

        @self.command()
        async def shutup(ctx: Context, additional=""):
            guild = ctx.guild

            voice_client = discord.utils.get(self.voice_clients, guild=guild)

            await self.conditional_delete(ctx.message)

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
                self.handling_mundo_queue[guild] = (True, True)
                self.mundo_queue[guild] = queue.Queue()

        @self.command()
        async def add_clash(ctx: Context, name: str, date: str):
            await self.conditional_delete(ctx.message)

            if not (ctx.author.guild_permissions.manage_roles and ctx.author.guild_permissions.manage_channels):
                await ctx.author.send(
                    "Mundo no do work for lowlife like you. Get more permissions.(manage channels and roles)")
                return

            # Sends message to designated channel
            clash_channel = next((c for c in ctx.guild.text_channels if c.name == "clash"), None)
            if clash_channel is None:
                await ctx.author.send("Mundo need clash text channel.")
                return
            message = await clash_channel.send("@everyone Nábor na clash " + name + "\n"
                                        "Pokud si můžete a chcete si zahrát tak zareagujete svojí rolí nebo fill rolí.",
                                        allowed_mentions=discord.AllowedMentions.all())

            self.clash.players[name] = {}

            # Give access to new channel to everyone above or equal to requesting user + new designated role
            overwrites = {}
            author_role = max(ctx.author.roles)
            for r in ctx.guild.roles:
                overwrites[r] = discord.PermissionOverwrite(read_messages=(r >= author_role))

            # Check if role with desired name already exists, else create it and give it permissions to channel
            role_name = name + " Player"
            role = next((r for r in ctx.guild.roles if r.name == role_name), None)
            if role is None:
                role: discord.Role = await ctx.guild.create_role(name=role_name,
                                                                 permissions=ctx.guild.default_role.permissions)
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)

            # Channel will be placed to category named Clash, else to no category
            category = next((c for c in ctx.guild.categories if c.name == "Clash"), None)

            # Create new channel only if no channel of such name currently exists
            channel = next((c for c in ctx.guild.channels if c.name == name.replace(" ", "-").lower()), None)
            if channel is None:
                await ctx.guild.create_text_channel(name, overwrites=overwrites, category=category)

            # Add all this to clash manager for saving
            self.clash.add_clash(name, date, ctx.guild.id, clash_channel.id, message.id, role.id)

    # -----------------------------------------------------
    # Additional non Discord API functions for cleaner code
    # -----------------------------------------------------
    async def check_expired_clashes(self):
        expired = self.clash.check_clashes()
        for name, (guild_id, channel_id, message_id, date, role_id) in expired.items():
            guild = self.get_guild(guild_id)

            # Delete role and channel
            role_name = name + " Player"
            roles = (r for r in guild.roles if r.name == role_name)
            for r in roles:
                await r.delete()
            channels = (c for c in guild.text_channels if c.name == name.replace(" ", "-").lower())
            for c in channels:
                await c.delete()

            # Delete original message
            channel = guild.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            await message.delete()

    async def add_to_queue(self, guild: discord.Guild, channel: discord.VoiceChannel, num=1):
        if guild not in self.mundo_queue:
            self.mundo_queue[guild] = queue.Queue()

        # Put channel to a music queue
        for _ in range(num):
            self.mundo_queue[guild].put(channel)

        if guild not in self.handling_mundo_queue:
            self.handling_mundo_queue[guild] = (False, False)

        # If queue isn't already handled start handling it
        if self.handling_mundo_queue[guild][0] is False:
            await self.play_from_queue(guild)

    async def play_from_queue(self, guild: discord.Guild):
        # Finds current voice_channel in this guild
        voice_client = discord.utils.get(self.voice_clients, guild=guild)
        i = 0

        while not self.mundo_queue[guild].empty():
            handling, stop = self.handling_mundo_queue[guild]
            if stop is True:
                self.handling_mundo_queue[guild] = (False, False)
                return
            else:
                self.handling_mundo_queue[guild] = (True, False)
            channel = self.mundo_queue[guild].get()
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
                await self.play_mundo_sound(voice_client, "assets/mundo-say-name-often.mp3")
            else:
                await self.play_mundo_sound(voice_client, "assets/muundo.mp3")

            while voice_client.is_playing():
                # Not clean but it iiiis what it iiiis
                await asyncio.sleep(.1)

        if voice_client.is_connected():
            await voice_client.disconnect()
        self.handling_mundo_queue[guild] = (False, False)

    async def play_mundo_sound(self, voice_client: discord.VoiceClient, file_name):
        # Play muundo.mp3
        audio_path = os.path.join(self.path, file_name)
        voice_client.play(discord.FFmpegPCMAudio(audio_path))

    async def conditional_delete(self, message: discord.Message):
        if isinstance(message.channel, discord.TextChannel):
            await message.delete()


if __name__ == "__main__":
    bot = MundoBot()
    bot.start_running()



'''
bot = commands.Bot(command_prefix='!')
TOKEN = "ODIyNTk0ODA1NDI2NDIxNzgx.YFUjHA.7FvSQXT6jvQGGxiXeoffRxQTf3U"
path = os.path.dirname(os.path.abspath(__file__))
clash: ClashManager

# Create global variables
mundo_queue: Dict[discord.Guild, queue.Queue] = {}
# Value is tuple of (handling, stop)
handling_mundo_queue: Dict[discord.Guild, Tuple[bool, bool]] = {}

accepted_reactions = ['👍']


@bot.event
async def on_ready():
    global clash
    clash = ClashManager(path)
    await check_expired_clashes()

    print("Logged in.")


@bot.event
async def on_voice_state_update(member, before, after):
    # Ignores himself moving
    if member == bot.user:
        return

    # Check if the state update was joining a room
    if before.channel != after.channel and after.channel is not None:
        print(member, "from channel", before.channel, "to", after.channel, "in", after.channel.guild)
        await add_to_queue(member.guild, after.channel)


@bot.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
    global clash
    clashes = clash.clashes
    for name, (guild_id, channel_id, message_id, date, role_id) in clashes:
        if reaction.guild_id == guild_id and reaction.channel_id == channel_id and reaction.message_id == message_id:
            if reaction.emoji in accepted_reactions:
                guild = bot.get_guild(guild_id)
                role = guild.get_role(role_id)
                reaction.member.add_role(role)

    # TODO: Read if reaction is one of desired
    # TODO: Give user role associated with the clash
    # TODO: Keep track of players in the clash
    # TODO: Updating message at the start of channel telling who is playing


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
    global clash
    await conditional_delete(ctx.message)

    if not (ctx.author.guild_permissions.manage_roles and ctx.author.guild_permissions.manage_channels):
        await ctx.author.send("Mundo no do work for lowlife like you. Get more permissions.(manage channels and roles)")
        return

    # Sends message to designated channel
    clash_channel = next((c for c in ctx.guild.text_channels if c.name == "clash"), None)
    if clash_channel is None:
        await ctx.author.send("Mundo need clash text channel.")
        return
    message = await clash_channel.send("@everyone Nábor na clash " + name + "\n"
                                      "Pokud si můžete a chcete si zahrát tak zareagujete svojí rolí nebo fill rolí.",
                                       allowed_mentions=discord.AllowedMentions.all())

    # Give access to new channel to everyone above or equal to requesting user + new designated role
    overwrites = {}
    author_role = max(ctx.author.roles)
    for r in ctx.guild.roles:
        overwrites[r] = discord.PermissionOverwrite(read_messages=(r >= author_role))

    # Check if role with desired name already exists, else create it and give it permissions to channel
    role_name = name + " Player"
    role = next((r for r in ctx.guild.roles if r.name == role_name), None)
    if role is None:
        role: discord.Role = await ctx.guild.create_role(name=role_name,
                                                         permissions=ctx.guild.default_role.permissions)
        overwrites[role] = discord.PermissionOverwrite(read_messages=True)

    # Channel will be placed to category named Clash, else to no category
    category = next((c for c in ctx.guild.categories if c.name == "Clash"), None)

    # Create new channel only if no channel of such name currently exists
    channel = next((c for c in ctx.guild.channels if c.name == name.replace(" ", "-").lower()), None)
    if channel is None:
        await ctx.guild.create_text_channel(name, overwrites=overwrites, category=category)

    # Add all this to clash manager for saving
    clash.add_clash(name, date, ctx.guild.id, clash_channel.id, message.id, role.id)
'''
