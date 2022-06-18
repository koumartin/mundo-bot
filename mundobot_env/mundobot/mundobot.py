import asyncio
import os
import queue
from typing import Dict, Tuple

import dotenv

import discord
from discord.ext import commands
from discord.ext.commands.context import Context as Context

from pymongo import MongoClient

from mundobot.clashmanager import Clash, ClashManager
from mundobot.position import Position

# -------------------------------------------
# ADDITIONAL INFORMATION:
# Author: @koumartin
# Date: 22/3/2021
# -------------------------------------------


class MundoBot(commands.Bot):
    def __init__(self, token):
        intents = discord.Intents.default()
        intents.members = True
        commands.Bot.__init__(self, command_prefix='!', intents=intents)
        self.TOKEN = token
        self.path = os.path.dirname(os.path.abspath(__file__))

        # Create global variables
        self.mundo_queue: Dict[discord.Guild, queue.Queue] = {}
        # Value is tuple of (handling, stop)
        self.handling_mundo_queue: Dict[discord.Guild, Tuple[bool, bool]] = {}

        self.clash_manager: ClashManager = ClashManager(self.path)
        self.add_all_commands()
        self.accepted_reactions = Position.accepted_reactions()

    def start_running(self):
        self.run(self.TOKEN)

    def add_all_commands(self):
        # -----------------------------------------------------
        # DISCORD API EVENTS
        # -----------------------------------------------------
        @self.event
        async def on_ready():
            await self.check_expired_clashes()
            await self.check_positions()
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
            clash: Clash
            # Checks if reaction was made on one of initial messages
            for clash in self.clash_manager.clashes.values():
                if reaction.guild_id == clash.guild_id and reaction.channel_id == clash.clash_channel_id and \
                        reaction.message_id == clash.message_id and reaction.emoji.name in self.accepted_reactions:
                    # Gets guild, position and role for this clash
                    guild = self.get_guild(clash.guild_id)
                    position = Position.get_position(reaction.emoji.name)
                    role = guild.get_role(clash.role_id)

                    # If member is already in players for this clash, remove his reaction, send him message and ignore
                    if reaction.member.name in self.clash_manager.players[clash.name]:
                        channel = guild.get_channel(reaction.channel_id)
                        message = await channel.fetch_message(reaction.message_id)
                        await message.remove_reaction(reaction.emoji, reaction.member)
                        await reaction.member.send("Only one position per player dummy.")
                        return

                    # NOOB doesn't get player role and access to channel
                    if position != Position.NOOB:
                        await reaction.member.add_roles(role)

                    self.clash_manager.register_player(clash.name, reaction.member.name, position)

                    # Update message in this clash channel
                    channel = guild.get_channel(clash.channel_id)
                    status_message: discord.Message = await channel.fetch_message(clash.status_id)
                    await status_message.edit(content=self.show_players(self.clash_manager.players[clash.name]))
                    break

        @self.event
        async def on_raw_reaction_remove(reaction: discord.RawReactionActionEvent):
            clash: Clash
            # Checks if reaction was made on one of initial messages
            for clash in self.clash_manager.clashes.values():
                if reaction.guild_id == clash.guild_id and reaction.channel_id == clash.clash_channel_id and \
                        reaction.message_id == clash.message_id and reaction.emoji.name in self.accepted_reactions:
                    # Gets guild, position and role for this clash
                    position = Position.get_position(reaction.emoji.name)
                    guild = self.get_guild(clash.guild_id)
                    member = guild.get_member(reaction.user_id)

                    # If player had this position remove hem from player and role
                    if position == self.clash_manager.players[clash.name][member.name]:
                        role = guild.get_role(clash.role_id)
                        await member.remove_roles(role)
                        self.clash_manager.unregister_player(clash.name, member.name)

                        # Update message in this clash channel
                        channel = guild.get_channel(clash.channel_id)
                        status_message: discord.Message = await channel.fetch_message(clash.status_id)
                        await status_message.edit(content=self.show_players(self.clash_manager.players[clash.name]))
                    break

        # -----------------------------------------------------
        # MUNDO GREET COMMANDS
        # -----------------------------------------------------
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
            await self.conditional_delete(ctx.message)

            guild = ctx.guild
            voice_client = discord.utils.get(self.voice_clients, guild=guild)

            print(ctx.author, "called !shutup in", ctx.guild)

            # TODO: REDO WITH PERMISSIONS
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

        # -----------------------------------------------------
        # CLASH COMMANDS
        # -----------------------------------------------------
        @self.command()
        async def add_clash(ctx: Context, clash_name: str, date: str):
            await self.conditional_delete(ctx.message)

            # Check caller permissions
            if not (ctx.author.guild_permissions.manage_roles and ctx.author.guild_permissions.manage_channels):
                await ctx.author.send(
                    "Mundo no do work for lowlife like you. Get more permissions.(manage channels and roles)")
                return

            # Sends message to designated channel and also gets clash_channel
            clash_channel = next((c for c in ctx.guild.text_channels if c.name == "clash"), None)
            if clash_channel is None:
                await ctx.author.send("Mundo need clash text channel.")
                return
            message = await clash_channel.send("@everyone Nábor na clash " + clash_name + " - " + date + "\n"
                                "Pokud můžete a chcete si zahrát tak zareagujete svojí rolí nebo fill rolí, případně"
                                 " :thumbdown: pokud nemůžete.", allowed_mentions=discord.AllowedMentions.all())

            # Give access to new channel to everyone above or equal to requesting user + new designated role
            overwrites = {}
            author_role = max(ctx.author.roles)
            for r in ctx.guild.roles:
                overwrites[r] = discord.PermissionOverwrite(read_messages=(r >= author_role))

            # Check if role with desired clash_name already exists, else create it and give it permissions to channel
            role_name = clash_name + " Player"
            role = next((r for r in ctx.guild.roles if r.name == role_name), None)
            if role is None:
                role: discord.Role = await ctx.guild.create_role(name=role_name,
                                                                 permissions=ctx.guild.default_role.permissions)
                overwrites[role] = discord.PermissionOverwrite(read_messages=True)

            # Channel will be placed to category named Clash, else to no category
            category = next((c for c in ctx.guild.categories if c.name == "Clash"), None)

            # Create new channel only if no channel of such name currently exists
            channel = next((c for c in ctx.guild.channels if c.name == clash_name.replace(" ", "-").lower()), None)
            if channel is None:
                channel = await ctx.guild.create_text_channel(clash_name, overwrites=overwrites, category=category)

            # Add players dictionary to clash_manager
            self.clash_manager.players[clash_name] = {}

            # Add message to channel and pin it
            status = await channel.send(self.show_players(self.clash_manager.players[clash_name]))
            await status.pin()

            # Create new Clash calss to hold all data about it and supporting structure
            clash = Clash(clash_name, date, ctx.guild.id, clash_channel.id, channel.id, message.id, role.id, status.id)

            # Add all this to clash manager for saving
            self.clash_manager.add_clash(clash)

        @self.command()
        async def remove_clash(ctx: Context, clash_name: str):
            await self.conditional_delete(ctx.message)

            # Check caller permissions
            if not (ctx.author.guild_permissions.manage_roles and ctx.author.guild_permissions.manage_channels):
                await ctx.author.send("Mundo no do work for lowlife like you. Get more permissions."
                                      "(manage channels and roles)")
                return

            clash: Clash = self.clash_manager.remove_clash(clash_name)
            await self.delete_clash(clash)

    # -----------------------------------------------------
    # HELPER FOR DELETING ALL CLASH BELONGINGS
    # -----------------------------------------------------
    async def delete_clash(self, clash: Clash):
        guild = self.get_guild(clash.guild_id)
        # Delete role and channel
        role_name = clash.name + " Player"
        roles = (r for r in guild.roles if r.name == role_name)
        for r in roles:
            await r.delete()
        channels = (c for c in guild.text_channels if c.name == clash.name.replace(" ", "-").lower())
        for c in channels:
            await c.delete()
        # Delete original message in general clash channel
        channel = guild.get_channel(clash.clash_channel_id)
        message = await channel.fetch_message(clash.message_id)
        await message.delete()

    # -----------------------------------------------------
    # METHODS FOR CREATING STRING OF CURRENTLY REGISTERED PLAYERS FOR GIVEN CLASH
    # -----------------------------------------------------
    def show_players(self, players) -> str:
        output = "Aktuální sestava\n"
        for position in Position:
            output += str(position) + ": " + self.find_player(position, players) + "\n"
        return output

    @staticmethod
    def find_player(target: Position, players: Dict[str, Position]) -> str:
        output = ""
        for player, position in players.items():
            if position == target:
                output += player + " "
        return output

    # -----------------------------------------------------
    # CLASH CONSISTENCY CHECKS TO BE RUN AT THE LOGIN
    # -----------------------------------------------------
    async def check_expired_clashes(self):
        clash: Clash

        print("Checking expired clashes")

        # Gets expired clashes from clash_manager
        expired = self.clash_manager.check_clashes()
        for clash in expired.values():
            await self.delete_clash(clash)

    async def check_positions(self):
        clash: Clash

        print("Checking player positions")

        for clash in self.clash_manager.clashes.values():
            # Finds guild, its clash_channel and initial message
            self.clash_manager.players[clash.name] = {}
            guild = self.get_guild(clash.guild_id)
            channel = guild.get_channel(clash.clash_channel_id)
            message: discord.Message = await channel.fetch_message(clash.message_id)

            # Checks reactions and adds users to players dictionary
            for reaction in message.reactions:
                for user in await reaction.users().flatten():
                    # Delete all other reactions if user already is in players dictionary for this clash
                    if user.name in self.clash_manager.players[clash.name]:
                        await self.remove_reactions(user, message, self.clash_manager.players[clash.name][user.name])
                        await user.send("Only one position per player dummy.")
                    else:
                        if isinstance(reaction.emoji, str):
                            emoji_name = reaction.emoji
                        else:
                            emoji_name = reaction.emoji.name
                        position = Position.get_position(emoji_name)
                        self.clash_manager.register_player(clash.name, user.name, position)

    @staticmethod
    async def remove_reactions(user, message: discord.Message, pos: Position):
        for reaction in message.reactions:
            if isinstance(reaction.emoji, str):
                emoji_name = reaction.emoji
            else:
                emoji_name = reaction.emoji.name
            if Position.get_position(emoji_name) != pos:
                users = await reaction.users().flatten()
                for u in users:
                    if u == user:
                        await message.remove_reaction(reaction.emoji, user)

    # -----------------------------------------------------
    # MUNDO GREET ADDITIONAL METHODS
    # -----------------------------------------------------
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
                await self.play_mundo_sound(voice_client, "../assets/mundo-say-name-often.mp3")
            else:
                await self.play_mundo_sound(voice_client, "../assets/muundo.mp3")

            while voice_client.is_playing():
                # Not clean but it iiiis what it iiiis
                await asyncio.sleep(.1)

        if voice_client.is_connected():
            await voice_client.disconnect()
        self.handling_mundo_queue[guild] = (False, False)

    async def play_mundo_sound(self, voice_client: discord.VoiceClient, file_name):
        audio_path = os.path.join(self.path, file_name)
        voice_client.play(discord.FFmpegPCMAudio(audio_path))

    # -----------------------------------------------------
    # CONDITIONAL DELETE
    # -----------------------------------------------------
    @staticmethod
    async def conditional_delete(message: discord.Message):
        if isinstance(message.channel, discord.TextChannel):
            await message.delete()


# -----------------------------------------------------
# MAIN
# -----------------------------------------------------
if __name__ == "__main__":
    dotenv.load_dotenv()

    bot = MundoBot(os.environ.get("botToken"))
    bot.start_running()
