"""
Mundo bot class and commands for running it.
"""
import asyncio
import os
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from uuid import UUID, getnode

import discord as dc
from dacite import from_dict
from discord.ext import commands
from discord.ext.commands.context import Context
from pymongo import MongoClient

from mundobot.clash import Clash
from mundobot.clash_api_service import ApiClash, ClashApiService
from mundobot.clashmanager import ClashManager
from mundobot.position import Position
from mundobot import helpers

# -------------------------------------------
# ADDITIONAL INFORMATION:
# Author: @koumartin
# Date: 22/3/2021
# -------------------------------------------

LOCK_REFRESH_TIMEOUT = 3  # minutes
LOCK_CHECK_TIMEOUT = 2.5 * 60  # 2.5 minutes


class MundoBot(commands.Bot):
    """Discord bot for playnig sounds in rooms and mannaging clash.

    Attributes:
        token (str): Discord API token used for communication.
        mundo_queue (Dict[dc.Guild, queue.Queue]): Queue of voice channels to play sound in.
        clash_manager (ClashManager): Clashmanger instance of this bot.
        accepted_reactions (List[str]): List of reaction names to react to.
        client (MongoClient): Client for accessing used mongodb.
    """

    def __init__(self, token: str, mongodbConnectionString: str) -> None:
        """Initializes the bot by creating connections to db and preparing token.

        Args:
            token (str): Discord api bot token.
            mongodbConnectionString (str): Connection string to mongodb.
        """
        intents: dc.Intents = dc.Intents.default()
        intents.members = True  # pylint: disable=assigning-non-slot
        commands.Bot.__init__(self, command_prefix="!", intents=intents)

        self.token = token
        self.path = os.path.dirname(os.path.abspath(__file__))

        # Create global variables
        self.playback_queue: Dict[dc.Guild, queue.Queue] = {}
        # Value is tuple of (handling, stop)
        self.playback_queue_handle: Dict[dc.Guild, Tuple[bool, bool]] = {}

        self.client = MongoClient(
            mongodbConnectionString, uuidRepresentation="standard"
        )
        self.clash_manager = ClashManager(self.client)
        self.accepted_reactions = Position.accepted_reactions()
        self.clash_api_service = ClashApiService()

        self.identifier: UUID = getnode()
        self.is_singleton = False
        self.singleton_collection = self.client.bot.singleton

        self.add_all_commands()

    def start_running(self) -> None:
        """Commands the bot to log in and start running using its api token."""
        self.loop.create_task(self.check_for_singleton())
        self.run(self.token)

    def add_all_commands(self) -> None:
        """Adds commands and events to the discord bot."""
        # -----------------------------------------------------
        # DISCORD API EVENTS
        # -----------------------------------------------------
        @self.event
        async def on_ready() -> None:
            # await self.check_expired_clashes()
            # await self.check_positions()
            print("Logged in.")

        @self.event
        async def on_voice_state_update(
            member: dc.Member, before: dc.VoiceState, after: dc.VoiceState
        ) -> None:
            """Action triggered every time a user changes their voice state.
            Bot reacts by adding the room to queue of greetings.

            Args:
                member (dc.Member): Member that moved
                before (dc.VoiceState): Original voice state including channel.
                after (dc.VoiceState): New voice state including channel.
            """
            # Ignores himself moving
            if member == self.user:
                return

            # Check if the state update was joining a room
            if before.channel != after.channel and after.channel is not None:
                print(
                    f"{member} from channel {before.channel} to \
                       {after.channel} in {after.channel.guild}"
                )
                await self.add_to_queue(member.guild, after.channel)

        @self.event
        async def on_raw_reaction_add(reaction: dc.RawReactionActionEvent) -> None:
            """Action triggered every time a user adds a reaction to a message.
            If the message is in relevant channel, than clash role is assigned.

            Args:
                reaction (dc.RawReactionActionEvent): Event of adding reaction
            """
            # Checks if reaction was made on one of initial messages
            for clash_entry in self.clash_manager.clashes_for_guild(reaction.guild_id):
                clash: Clash = from_dict(Clash, clash_entry)
                if (
                    reaction.channel_id != clash.clash_channel_id
                    or reaction.message_id != clash.message_id
                    or reaction.emoji.name not in self.accepted_reactions
                ):
                    continue

                clash_id: int = clash_entry["_id"]
                guild: dc.Guild = self.get_guild(clash.guild_id)
                position = Position.get_position(reaction.emoji.name)
                role: dc.Role = guild.get_role(clash.role_id)

                # If member is already in players for this clash,
                # than remove his reaction, send him message and ignore
                if reaction.member.name in self.clash_manager.players_for_clash(
                    clash_id
                ):
                    channel = guild.get_channel(reaction.channel_id)
                    message = await channel.fetch_message(reaction.message_id)
                    await message.remove_reaction(reaction.emoji, reaction.member)
                    await reaction.member.send("Only one position per player dummy.")
                    return

                # NOOB doesn't get player role and access to channel
                if position != Position.NOOB:
                    await reaction.member.add_roles(role)

                new_positions = self.clash_manager.register_player(
                    clash_id, reaction.member.name, position
                )

                # Update message in this clash channel
                channel = guild.get_channel(clash.channel_id)
                status_message: dc.Message = await channel.fetch_message(
                    clash.status_id
                )
                await status_message.edit(content=helpers.show_players(new_positions))
                break

        @self.event
        async def on_raw_reaction_remove(reaction: dc.RawReactionActionEvent) -> None:
            """Action triggered every time a user removes theire reaction to a message.
            If the reaction is in relevant channel, than a role in clash is removed.

            Args:
                reaction (dc.RawReactionActionEvent): Event of removing reaction.
            """
            # Checks if reaction was made on one of initial messages
            for clash_entry in self.clash_manager.clashes_for_guild(reaction.guild_id):
                clash: Clash = from_dict(Clash, clash_entry)
                if (
                    reaction.channel_id != clash.clash_channel_id
                    or reaction.message_id != clash.message_id
                    or reaction.emoji.name not in self.accepted_reactions
                ):
                    continue

                clash_id: int = clash_entry["_id"]
                guild: dc.Guild = self.get_guild(clash.guild_id)
                position = Position.get_position(reaction.emoji.name)
                member: dc.Member = guild.get_member(reaction.user_id)
                role: dc.Role = guild.get_role(clash.role_id)

                # If player had this position remove them from player and role
                if position == self.clash_manager.role_for_player(
                    clash_id, member.name
                ):
                    role = guild.get_role(clash.role_id)
                    await member.remove_roles(role)
                    new_positions = self.clash_manager.unregister_player(
                        clash_id, member.name
                    )

                    # Update message in this clash channel
                    channel = guild.get_channel(clash.channel_id)
                    status_message: dc.Message = await channel.fetch_message(
                        clash.status_id
                    )
                    await status_message.edit(
                        content=helpers.show_players(new_positions)
                    )
                break

        # -----------------------------------------------------
        # MUNDO GREET COMMANDS
        # -----------------------------------------------------
        @self.command()
        async def mundo(ctx: Context, num: int = 1) -> None:
            """Commands the bot to come into users channel and repeat num times a greeting.

            Args:
                ctx (Context): Context of the command.
                num (int, optional): Numbrer of greetings commanded. Defaults to 1.
            """
            # Guard for receiving command from DMChannel
            if not isinstance(ctx.channel, dc.TextChannel):
                await ctx.author.send("Mundo can't greet without real channel.")
                return

            await ctx.message.delete()

            print(ctx.author, "called !mundo with n =", num, "in", ctx.guild)

            if num > 30:
                await ctx.author.send(
                    "Mundo will no greet you so much. Mundo no stupid."
                )
                return
            if num < 0:
                await ctx.author.send(
                    "Mundo no stupid, unlike you. No saying negative times..."
                )
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
        async def shutup(ctx: Context, additional: str = "") -> None:
            """Commands the bot to stop repeating greetings after ending current one.
            Users without TODO permission have to add please parameter.

            Args:
                ctx (Context): Context of the command.
                additional (str, optional): Additional string value used to say please.
                    Defaults to "".
            """
            await helpers.conditional_delete(ctx.message)

            guild = ctx.guild
            voice_client = dc.utils.get(self.voice_clients, guild=guild)

            print(ctx.author, "called !shutup in", ctx.guild)

            if additional.lower() == "please" or additional.lower() == "prosím":
                await ctx.author.send(
                    "You say please so nice... Okey Mundo be silent now."
                )
            elif not ctx.author.guild_permissions.manage_channels:
                await ctx.author.send("You no tell Mundo what Mundo do!!!")
                return

            if voice_client is not None:
                voice_client.stop()
            self.playback_queue_handle[guild] = (True, True)
            self.playback_queue[guild] = queue.Queue()

        # -----------------------------------------------------
        # CLASH COMMANDS
        # -----------------------------------------------------
        @self.command()
        async def add_clash(ctx: Context, clash_name: str, date: str) -> None:
            """Adds clash to the list of registered clashes and creates a
            channel, role and registration message for it.
            WILL BECOME DEPRECATED

            Args:
                ctx (Context): Context of the command.
                clash_name (str): Name of the clash to be added.
                date (str): Date in d/m/Y format.
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            await self.add_clash_internal(ctx.guild, ctx.author, clash_name, date)

        @self.command()
        async def remove_clash(ctx: Context, clash_name: str) -> None:
            """Removes clash and all asociated lists, channels and roles.
            WILL BECOME DEPRECATED


            Args:
                ctx (Context): Context of the command.
                clash_name (str): Name of the clash to be removed.
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            await self.remove_clash_internal(ctx.guild, clash_name)

        @self.command()
        async def load_clashes(ctx: Context) -> None:
            """Loads clashes for callers server.

            Args:
                ctx (Context): Context of the command.
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            guild: dc.Guild = ctx.guild
            clashes: List[ApiClash] = self.clash_api_service.get_clashes()
            missing_clashes, surplus_clashes = self.clash_manager.get_needed_changes(
                guild.id, clashes
            )
            print(missing_clashes, surplus_clashes)
            missing_clashes.sort(key=lambda c: c.date)

            for clash in missing_clashes:
                await self.add_clash_internal(
                    guild, ctx.author, clash.name, clash.date, clash.id
                )
            for clash in surplus_clashes:
                await self.remove_clash_internal(ctx.guild, clash.name)

        @self.command()
        async def register_server(ctx: Context) -> None:
            """Registers a clash server to receive notifications about clashes.

            Args:
                ctx (Context): Context of the command
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            success = self.clash_manager.register_server(ctx.guild.id)
            if success:
                await ctx.channel.send("Server now receive clash updates.")
            else:
                await ctx.author.send(
                    "You already receive clash updates. Me no do things two, me no stupid."
                )

        @self.command()
        async def unregister_server(ctx: Context) -> None:
            """Unregisters a clash server from receiving notifications about clashes.

            Args:
                ctx (Context): Context of the command
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            success = self.clash_manager.unregister_server(ctx.guild.id)
            if success:
                await ctx.channel.send("Server now no receive clash updates.")
            else:
                await ctx.author.send(
                    "You not receive clash updates. Me no stupid to remove something no existing."
                )

    # -----------------------------------------------------
    # HELPER FUNCTION FOR CLASH INSTANCES
    # -----------------------------------------------------
    async def add_clash_internal(
        self,
        guild: dc.Guild,
        user: dc.Member,
        clash_name: str,
        date: str,
        riot_id: int = None,
    ) -> None:
        """Adds clash and generates roles, channels and messages for it.

        Args:
            clash_name (str): Name of the clash.
            date (str): Date of the clash
        """
        # Convert date from iso format if necessary
        try:
            date_converted = datetime.fromisoformat(date)
            date = date_converted.strftime("%d.%m.%Y")
        except ValueError:
            pass

        # Sends message to designated channel and also gets clash_channel
        clash_channel = helpers.find_clash_channel(guild)
        if clash_channel is None:
            await user.send("Mundo need clash text channel.")
            return
        message = await clash_channel.send(
            f"@everyone Nábor na clash {clash_name} - {date}\n"
            + "Pokud můžete a chcete si zahrát tak zareagujete svojí rolí"
            + " nebo fill rolí, případně :thumbdown: pokud nemůžete.",
            allowed_mentions=dc.AllowedMentions.all(),
        )

        # Give access to new channel to everyone above or equal to requesting user +
        # new designated role
        overwrites = {}
        author_role = max(user.roles)
        for role in guild.roles:
            overwrites[role] = dc.PermissionOverwrite(
                read_messages=(role >= author_role)
            )

        # Check if role with desired clash_name already exists, else create it and give
        # it permissions to channel
        role_name = clash_name + " Player"
        role = next((r for r in guild.roles if r.name == role_name), None)
        if role is None:
            role: dc.Role = await guild.create_role(
                name=role_name, permissions=guild.default_role.permissions
            )
            overwrites[role] = dc.PermissionOverwrite(read_messages=True)

        # Channel will be placed to category named Clash, else to no category
        category = next((c for c in guild.categories if c.name == "Clash"), None)

        # Create new channel only if no channel of such name currently exists
        channel = next(
            (
                c
                for c in guild.channels
                if c.name == clash_name.replace(" ", "-").lower()
            ),
            None,
        )
        if channel is None:
            channel = await guild.create_text_channel(
                clash_name, overwrites=overwrites, category=category
            )

        # Add message to channel and pin it
        status = await channel.send(helpers.show_players(dict()))
        await status.pin()

        # Create new Clash object to hold all data about it and supporting structure
        clash = Clash(
            clash_name,
            date,
            guild.id,
            clash_channel.id,
            channel.id,
            message.id,
            role.id,
            status.id,
            riot_id=riot_id,
        )

        # Add all this to clash manager for saving
        self.clash_manager.add_clash(clash)

    async def remove_clash_internal(self, guild: dc.Guild, clash_name: str) -> None:
        """Deletes clash and all associated propertis with it.

        Args:
            guild (dc.Guild): Guild in which the clash is removed.
            clash_name (str): Name of clash to be removed.
        """
        clash: Clash = self.clash_manager.remove_clash(clash_name, guild.id)

        if clash is None:
            return

        guild = self.get_guild(clash.guild_id)
        # Delete role and channel
        role = guild.get_role(clash.role_id)
        await role.delete()
        channel = guild.get_channel(clash.channel_id)
        await channel.delete()

        # Delete original message and notifications in general clash channel
        channel = guild.get_channel(clash.clash_channel_id)
        clash.notification_message_ids.append(clash.message_id)

        for message_id in clash.notification_message_ids:
            message = await channel.fetch_message(message_id)
            await message.delete()

    # -----------------------------------------------------
    # MUNDO GREET ADDITIONAL METHODS
    # -----------------------------------------------------
    async def add_to_queue(
        self, guild: dc.Guild, channel: dc.VoiceChannel, num: int = 1
    ) -> None:
        """Addes voice channel to the queue of channels to play sound in.

        Args:
            guild (dc.Guild): Guild in which the channel is located.
            channel (dc.VoiceChannel): The channel in which to play sound.
            num (int, optional): Number of times the sound is played. Defaults to 1.
        """
        if guild not in self.playback_queue:
            self.playback_queue[guild] = queue.Queue()

        # Put channel to a music queue
        for _ in range(num):
            self.playback_queue[guild].put(channel)

        if guild not in self.playback_queue_handle:
            self.playback_queue_handle[guild] = (False, False)

        # If queue isn't already handled start handling it
        if self.playback_queue_handle[guild][0] is False:
            await self.play_from_queue(guild)

    async def play_from_queue(self, guild: dc.Guild) -> None:
        """Play sound in next channel of the queue.

        Args:
            guild (dc.Guild): Guild in which the playing of sounds is requested.
        """
        # Finds current voice_channel in this guild
        voice_client = dc.utils.get(self.voice_clients, guild=guild)
        i = 0

        while not self.playback_queue[guild].empty():
            _, stop = self.playback_queue_handle[guild]
            if stop is True:
                self.playback_queue_handle[guild] = (False, False)
                return
            else:
                self.playback_queue_handle[guild] = (True, False)
            channel = self.playback_queue[guild].get()
            i += 1

            # In case bot isn't connected to a voice_channel yet
            if voice_client is None:
                voice_client = await channel.connect()
            # Else first disconnect bot from current channel and than connect it
            else:
                # Wait for current audio to stop playing
                while voice_client.is_playing():
                    await asyncio.sleep(0.1)
                await voice_client.move_to(channel)

            if i >= 5:
                i = 0
                await self.play_mundo_sound(
                    voice_client, "../assets/mundo-say-name-often.mp3"
                )
            else:
                await self.play_mundo_sound(voice_client, "../assets/muundo.mp3")

            while voice_client.is_playing():
                # Not clean but it iiiis what it iiiis
                await asyncio.sleep(0.1)

        if voice_client.is_connected():
            await voice_client.disconnect()
        self.playback_queue_handle[guild] = (False, False)

    async def play_mundo_sound(
        self, voice_client: dc.VoiceClient, file_name: str
    ) -> None:
        """Plays a sound specified by file_name in a VoiceClient.

        Args:
            voice_client (dc.VoiceClient): Voice client to play the sound.
            file_name (str): Name of the sound file.
        """
        audio_path = os.path.join(self.path, file_name)
        voice_client.play(dc.FFmpegPCMAudio(audio_path))

    async def check_for_singleton(self) -> None:
        """Checks for singleton property in database.
        Makes itself the singleton in case the old one is not refreshed.
        Refreshes if currently being singleton.
        """
        while True:
            current_value = self.singleton_collection.find_one()
            if not current_value["singleton_id"]:
                print("Initializing singleton")
                self.singleton_collection.insert_one(
                    {
                        "singleton_id": self.identifier,
                        "valid_until": datetime.now()
                        + timedelta(minutes=LOCK_REFRESH_TIMEOUT),
                    }
                )
            elif current_value["singleton_id"] == self.identifier:
                print("Refreshing singleton lock")
                new_time = datetime.now() + timedelta(minutes=LOCK_REFRESH_TIMEOUT)
                self.singleton_collection.update_one(
                    {"_id": current_value["_id"]},
                    {"$set": {"valid_until": new_time}},
                )
            elif datetime.now() > current_value.valid_until:
                new_time = datetime.now() + timedelta(minutes=LOCK_REFRESH_TIMEOUT)
                self.singleton_collection.update_one(
                    {"_id": current_value["_id"]},
                    {
                        "$set": {
                            "singleton_id": self.identifier,
                            "valid_until": new_time,
                        }
                    },
                )
            await asyncio.sleep(LOCK_CHECK_TIMEOUT)

    # # -----------------------------------------------------
    # # CLASH CONSISTENCY CHECKS TO BE RUN AT THE LOGIN
    # # -----------------------------------------------------
    # async def check_expired_clashes(self) -> None:
    #     """Checks if any clasches are expired and removes them.
    #     WILL BECOME DEPRECATED.
    #     """
    #     clash: Clash

    #     print("Checking expired clashes")

    #     # Gets expired clashes from clash_manager
    #     expired = self.clash_manager.check_clashes()
    #     for clash in expired.values():
    #         await self.delete_clash(clash)

    # async def check_positions(self) -> None:
    #     """Checks if positions of players in the clash match positions stored in ClashManager."""
    #     clash: Clash

    #     print("Checking player positions")
    #     return

    #     for clash in self.clash_manager.clashes.values():
    #         # Finds guild, its clash_channel and initial message
    #         self.clash_manager.players[clash.name] = {}
    #         guild = self.get_guild(clash.guild_id)
    #         channel = guild.get_channel(clash.clash_channel_id)
    #         message: dc.Message = await channel.fetch_message(clash.message_id)

    #         # Checks reactions and adds users to players dictionary
    #         for reaction in message.reactions:
    #             for user in await reaction.users().flatten():
    #                 # Delete all other reactions if user already is in players dictionary
    #                 # for this clash
    #                 if user.name in self.clash_manager.players[clash.name]:
    #                     await self.remove_reactions(
    #                         user,
    #                         message,
    #                         self.clash_manager.players[clash.name][user.name],
    #                     )
    #                     await user.send("Only one position per player dummy.")
    #                 else:
    #                     if isinstance(reaction.emoji, str):
    #                         emoji_name = reaction.emoji
    #                     else:
    #                         emoji_name = reaction.emoji.name
    #                     position = Position.get_position(emoji_name)
    #                     self.clash_manager.register_player(
    #                         clash.name, user.name, position
    #                     )
