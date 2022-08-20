"""
Mundo bot class and commands for running it.
"""
import asyncio
import os
import queue
import logging
import signal
from datetime import datetime, timedelta
import sys
import traceback
from typing import Dict, Iterable, List, Optional, Tuple
from uuid import UUID, getnode
import certifi

import discord as dc
from dacite import from_dict
from discord.ext import commands
from discord.ext.commands.context import Context
from pymongo import MongoClient
import schedule

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

LOCK_REFRESH_TIMEOUT = 1.5  # minutes
LOCK_CHECK_TIMEOUT = 4 * 60  # 4 minutes
LOCK_CHECK_TIMEOUT_OWNER = 60
LOCK_CHECK_TIMEOUT_INITIAL = 5


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
            mongodbConnectionString,
            uuidRepresentation="standard",
            tlsCAFile=certifi.where(),
        )
        self.clash_manager = ClashManager(self.client)
        self.accepted_reactions = Position.accepted_reactions()
        self.clash_api_service = ClashApiService()

        self.identifier: UUID = UUID(int=getnode())
        self.is_singleton = False
        self.checking_done = False
        self.job: Optional[schedule.Job] = None
        self.singleton_collection = self.client.bot.singleton

        self.logger = helpers.prepare_logging(
            "bot",
            logging.DEBUG,
            logging.WARNING,
            self.path,
        )
        self.add_all_commands()

    def start_running(self) -> None:
        """Commands the bot to log in and start running using its api token."""
        self.loop.create_task(self.check_for_singleton_job())
        self.run(self.token)

    def add_all_commands(self) -> None:
        """Adds commands and events to the discord bot."""
        # -----------------------------------------------------
        # DISCORD API EVENTS
        # -----------------------------------------------------
        @self.event
        async def on_ready() -> None:
            self.logger.info("Logged in.")
            for signame in ("SIGINT", "SIGTERM"):
                self.loop.add_signal_handler(
                    getattr(signal, signame),
                    lambda: asyncio.create_task(self.termination_handler()),
                )

        @self.event
        async def on_command_error(ctx: Context, error: commands.CommandError) -> None:
            """Changes the behaviour of command error to ignore CheckFailures.

            Args:
                ctx (Context): Context of the failing command.
                error (commands.CommandError): Command error instance.
            """
            if isinstance(error, commands.errors.CheckFailure):
                pass
            else:
                self.logger.error("Ignoring exception in command %s", ctx.command)
                traceback.print_exception(
                    type(error), error, error.__traceback__, file=sys.stderr
                )

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
            if not self.is_singleton:
                return

            # Ignores himself moving
            if member == self.user:
                return

            # Check if the state update was joining a room
            if before.channel != after.channel and after.channel is not None:
                self.logger.info(
                    "%s from channel %s to %s in %s",
                    member,
                    before.channel,
                    after.channel,
                    after.channel.guild,
                )
                await self.add_to_queue(member.guild, after.channel)

        @self.event
        async def on_raw_reaction_add(reaction: dc.RawReactionActionEvent) -> None:
            """Action triggered every time a user adds a reaction to a message.
            If the message is in relevant channel, than clash role is assigned.

            Args:
                reaction (dc.RawReactionActionEvent): Event of adding reaction
            """
            if not self.is_singleton:
                return

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

                self.logger.info(
                    "%s is registering for %s position in %s of %s server.",
                    reaction.member.name,
                    position,
                    clash.name,
                    guild.name,
                )

                # NOOB doesn't get player role and access to channel
                if position != Position.NOOB:
                    await reaction.member.add_roles(role)

                new_positions = self.clash_manager.register_player(
                    clash_id, reaction.member.id, reaction.member.name, position
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
            if not self.is_singleton:
                return

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

                self.logger.info(
                    "%s is unregistering from %s position in %s of %s server.",
                    member.name,
                    position,
                    clash.name,
                    guild.name,
                )

                role = guild.get_role(clash.role_id)
                await member.remove_roles(role)
                new_positions = self.clash_manager.unregister_player(
                    clash_id, member.name, position
                )

                # Update message in this clash channel
                channel = guild.get_channel(clash.channel_id)
                status_message: dc.Message = await channel.fetch_message(
                    clash.status_id
                )
                await status_message.edit(content=helpers.show_players(new_positions))
                break

        # -----------------------------------------------------
        # MUNDO GREET COMMANDS
        # -----------------------------------------------------
        @self.command()
        @self.single_handle()
        async def mundo(ctx: Context, num: int = 1) -> None:
            """Commands the bot to come into users channel and repeat num times a greeting.

            Args:
                ctx (Context): Context of the command.
                num (int, optional): Number of greetings commanded. Defaults to 1.
            """
            # Guard for receiving command
            # if not isinstance(ctx.author.voice, dc.TextChannel):
            #     await ctx.author.send("Mundo can't greet without real channel.")
            #     return

            await helpers.conditional_delete(ctx.message)

            self.logger.info(
                "%s called !mundo with n = %d in %s", ctx.author, num, ctx.guild
            )

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
        @self.single_handle()
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

            self.logger.info("%s called !shutup in %s", ctx.author, ctx.guild)

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
        @self.single_handle()
        async def add_clash(ctx: Context, clash_name: str, date: str) -> None:
            """Adds clash to the list of registered clashes and creates a
            channel, role and registration message for it.

            DEPRECATED
            ---

            Args:
                ctx (Context): Context of the command.
                clash_name (str): Name of the clash to be added.
                date (str): Date in d/m/Y format.
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            self.logger.info(
                "%s added clash %s on %s in %s", ctx.author, clash_name, date, ctx.guild
            )

            await self.add_clash_internal(ctx.guild, clash_name, date, ctx.author)

        @self.command()
        @self.single_handle()
        async def remove_clash(ctx: Context, clash_name: str) -> None:
            """Removes clash and all asociated lists, channels and roles.

            DEPRECATED
            ---

            Args:
                ctx (Context): Context of the command.
                clash_name (str): Name of the clash to be removed.
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            self.logger.info(
                "%s removed clash %s in %s", ctx.author, clash_name, ctx.guild
            )

            await self.remove_clash_internal(ctx.guild, clash_name)

        @self.command()
        @self.single_handle()
        async def load_clashes(ctx: Context) -> None:
            """Loads clashes for callers server.

            Args:
                ctx (Context): Context of the command.
            """
            await helpers.conditional_delete(ctx.message)

            if not await helpers.check_permissions(ctx.author):
                return

            self.logger.info("%s loaded clashes for %s", ctx.author, ctx.guild)

            guild: dc.Guild = ctx.guild
            await self.load_clashes_for_guild(guild.id)

        @self.command()
        @self.single_handle()
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
                self.logger.info(
                    "%s registered %s for clash updates", ctx.author, ctx.guild
                )
            else:
                await ctx.author.send(
                    "You already receive clash updates. Me no do things two, me no stupid."
                )

        @self.command()
        @self.single_handle()
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
                self.logger.info(
                    "%s unregistered %s for clash updates", ctx.author, ctx.guild
                )
            else:
                await ctx.author.send(
                    "You not receive clash updates. Me no stupid to remove something no existing."
                )

        @self.command()
        @self.single_handle()
        async def regular_players(ctx: Context) -> None:
            await helpers.conditional_delete(ctx.message)

            guild: dc.Guild = ctx.guild
            self.logger.info(
                "Getting list of regular players in %s",
                guild.name,
            )
            regular_player_ids = self.clash_manager.regular_players_for_guild(guild.id)
            regular_players: Iterable[dc.Member | None] = map(
                lambda x: guild.get_member(x).name, regular_player_ids
            )

            message = "Častí hráči pro tento server jsou\n" + " ".join(regular_players)
            await ctx.channel.send(message)

        @self.command()
        @self.single_handle()
        async def register_as_regular(ctx: Context, name: Optional[str] = None) -> None:
            await helpers.conditional_delete(ctx.message)

            guild: dc.Guild = ctx.guild
            player: dc.Member
            if name is None:
                player = ctx.author
            else:
                if not await helpers.check_permissions(ctx.author):
                    return
                player = guild.get_member_named(name)

            self.logger.info(
                "%s is registering as regular player in %s",
                player.name,
                guild.name,
            )

            if player is None:
                ctx.author.send("Hráč neexistuje.")
                return

            try:
                self.clash_manager.register_regular_player(
                    guild.id, player.id, not bool(name), bool(name)
                )
            except ValueError as error:
                await ctx.author.send(error.args[0])
                return

            if name is None:
                await ctx.author.send("Nyní jsi častým hráčem na serveru " + guild.name)
            else:
                await ctx.author.send(
                    name + " je nyní častým hráčem na serveru " + guild.name
                )
                await player.send("Nyní jsi častým hráčem na serveru " + guild.name)

        @self.command()
        @self.single_handle()
        async def unregister_as_regular(ctx: Context, name: Optional[str]) -> None:
            await helpers.conditional_delete(ctx.message)

            guild: dc.Guild = ctx.guild
            player: dc.Member
            if name is None:
                player = ctx.author
            else:
                if not await helpers.check_permissions(ctx.author):
                    return
                player = guild.get_member_named(name)

            if player is None:
                ctx.author.send("Hráč neexistuje.")
                return

            self.logger.info(
                "%s is unregistering from being regular player in %s",
                player.name,
                guild.name,
            )

            try:
                self.clash_manager.unregister_regular_player(
                    guild.id, player.id, not bool(name), bool(name)
                )
            except ValueError as error:
                await ctx.author.send(error.args[0])
                return

            if name is None:
                await ctx.author.send(
                    "Nadále nejsi častým hráčem na serveru " + guild.name
                )
            else:
                await ctx.author.send(
                    name + " nadále není častým hráčem na serveru " + guild.name
                )
                await player.send("Nadále nejsi častým hráčem na serveru " + guild.name)

        @self.command()
        @self.single_handle()
        async def test(_: Context) -> None:
            """Testing function

            Args:
                ctx (Context): Context of the command.
            """
            await self.run_notifications()

    # -----------------------------------------------------
    # HELPER FUNCTION FOR CLASH INSTANCES
    # -----------------------------------------------------
    async def add_clash_internal(
        self,
        guild: dc.Guild,
        clash_name: str,
        date: str,
        user: Optional[dc.Member] = None,
        riot_id: Optional[int] = None,
    ) -> None:
        """Adds clash and generates roles, channels and messages for it.

        Args:
            guild (dc.Guild): Guild for which the clash is created.
            clash_name (str): Name of the clash.
            date (str): Date of the clash
            user (Optional[dc.Member]): User which will receive error and
            whose permissions will be the baseline.
            riot_id (Optional[int]): Id of clash in riot database.
        """
        # Convert date from iso format if necessary
        try:
            date_converted = datetime.fromisoformat(date)
            date = date_converted.strftime("%d.%m.%Y")
        except ValueError:
            pass

        # Sends message to designated channel and also gets clash_channel
        clash_channel = helpers.find_text_channel_by_name(guild, "clash")
        if clash_channel is None:
            self.logger.warning("%s is missing clash channel.", guild)
            if user is not None:
                await user.send("Mundo need clash text channel.")
            else:
                default_channel: dc.TextChannel = guild.system_channel
                if (
                    default_channel is not None
                    and default_channel.permissions_for(guild.me).send_messages
                ):
                    await default_channel.send(
                        "Mundo need clash text channel to send clash update."
                    )
            return
        message: dc.Message = await clash_channel.send(
            f"@everyone Nábor na clash {clash_name} - {date}\n"
            + "Pokud můžete a chcete si zahrát tak zareagujete svojí rolí"
            + " nebo fill rolí, případně :thumbdown: pokud nemůžete.",
            allowed_mentions=dc.AllowedMentions.all(),
        )

        # Give access to new channel to everyone above or equal to requesting user +
        # new designated role
        if user is None:
            user = guild.owner
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
        channel = helpers.find_text_channel_by_name(guild, clash_name)
        if channel is None:
            channel = await guild.create_text_channel(
                clash_name, overwrites=overwrites, category=category
            )

        # Add message to channel and pin it
        status: dc.Message = await channel.send(helpers.show_players())
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

        notification_times = helpers.prepare_notification_times(clash)

        # Add all this to clash manager for saving
        self.clash_manager.add_clash(clash, notification_times)

    async def remove_clash_internal(self, guild: dc.Guild, clash_name: str) -> None:
        """Deletes clash and all associated propertis with it.

        Args:
            guild (dc.Guild): Guild in which the clash is removed.
            clash_name (str): Name of clash to be removed.
        """
        clash: Clash = self.clash_manager.remove_clash(clash_name, guild.id)

        if clash is None:
            return

        await self.remove_individual_clash(clash)

    async def remove_individual_clash(self, clash: Clash) -> None:
        """Removes all discord properties related to clash.

        Args:
            clash (Clash): Clash which is being deleted.
        """
        guild: dc.Guild = self.get_guild(clash.guild_id)
        # Delete role and channel
        role: dc.Role = guild.get_role(clash.role_id)
        await role.delete()
        channel: dc.TextChannel = guild.get_channel(clash.channel_id)
        await channel.delete()

        # Delete original message and notifications in general clash channel
        channel = guild.get_channel(clash.clash_channel_id)
        clash.notification_message_ids.append(clash.message_id)

        for message_id in clash.notification_message_ids:
            message: dc.Message = await channel.fetch_message(message_id)
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

    # -----------------------------------------------------
    # PERIODIC CLASH MANAGEMENT METHODS
    # -----------------------------------------------------
    async def run_notifications(self) -> None:
        """Gets all overdue notifications and sends them out."""
        overdue_clashes = self.clash_manager.get_overdue_notifications()

        for clash_entry in overdue_clashes:
            clash = from_dict(Clash, clash_entry)
            guild: dc.Guild = self.get_guild(clash.guild_id)
            clash_channel: dc.TextChannel = guild.get_channel(clash.clash_channel_id)
            players = self.clash_manager.positions_for_clash(clash_entry["_id"]).players
            regular_players = self.clash_manager.regular_players_for_guild(guild.id)
            message: dc.Message = await clash_channel.send(
                helpers.get_notification(players, clash, regular_players)
            )
            clash.notification_message_ids.append(message.id)
            self.clash_manager.update_notification_ids(
                clash_entry["_id"], clash.notification_message_ids
            )

    async def load_clashes_for_guild(self, guild_id: int) -> None:
        """Makes clashes for a guild consistent with list of clashes from Riot.

        Args:
            guild_id (int): Id of the guild to check.
        """
        guild = self.get_guild(guild_id)
        clashes: List[ApiClash] = self.clash_api_service.get_clashes()
        missing_clashes, surplus_clashes = self.clash_manager.get_needed_changes(
            guild.id, clashes
        )
        missing_clashes.sort(key=lambda c: c.date)

        for clash in missing_clashes:
            await self.add_clash_internal(guild, clash.name, clash.date, clash.id)
        for clash in surplus_clashes:
            await self.remove_clash_internal(guild, clash.name)

    async def run_clash_checking(self) -> None:
        """Checks removes expired clashes and sends notification that should have been send."""
        guild_ids = self.clash_manager.get_registered_server_ids()

        for guild_id in guild_ids:
            await self.load_clashes_for_guild(guild_id)

        await self.run_notifications()

    # -----------------------------------------------------
    # SINGLETON METHODS
    # -----------------------------------------------------
    def set_checking_not_done(self):
        """Sets checking done to false."""
        self.checking_done = False

    async def gain_control(self) -> None:
        """Gains control over singleton and schedules periodic tasks."""
        self.is_singleton = True
        self.job = schedule.every(1).hours.do(self.set_checking_not_done)

    async def check_for_singleton(self, run_checking: bool) -> bool:
        """Checks for singleton and refreshes it or gains it if possible."""
        current_value = self.singleton_collection.find_one()

        # Uninitialized singleton is initialized and singleton lock is gained
        if current_value is None or not current_value["singleton_id"]:
            self.logger.info("Initializing singleton")
            self.singleton_collection.insert_one(
                {
                    "singleton_id": self.identifier,
                    "valid_until": datetime.now()
                    + timedelta(minutes=LOCK_REFRESH_TIMEOUT),
                }
            )
            await self.gain_control()
        # Singleton lock is held and refreshed
        elif current_value["singleton_id"] == self.identifier:
            self.logger.info("Refreshing singleton lock")
            new_time = datetime.now() + timedelta(minutes=LOCK_REFRESH_TIMEOUT)
            self.singleton_collection.update_one(
                {"_id": current_value["_id"]},
                {"$set": {"valid_until": new_time}},
            )
            if not self.is_singleton:
                await self.gain_control()
        # Singleton lock is gained
        elif datetime.now() > current_value["valid_until"]:
            self.logger.info("Gaining singleton lock")
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
            await self.gain_control()
        # Singleton lock is held by diffenet instance
        else:
            self.logger.info("Waiting for singleton clearing")
            if self.is_singleton:
                self.logger.info("Losing singleton instance")
                self.is_singleton = False
                if self.job is not None:
                    schedule.cancel_job(self.job)

        if run_checking and self.is_singleton and not self.checking_done:
            await self.run_clash_checking()

    async def check_for_singleton_job(self) -> None:
        """Checks for singleton property in database.
        Makes itself the singleton in case the old one is not refreshed.
        Refreshes if currently being singleton.
        """
        await asyncio.sleep(LOCK_CHECK_TIMEOUT_INITIAL)
        while True:
            await self.check_for_singleton(True)
            await asyncio.sleep(
                LOCK_CHECK_TIMEOUT
                if not self.is_singleton
                else LOCK_CHECK_TIMEOUT_OWNER
            )

    def single_handle(self):
        """Decorator that allows to check if instance is singleton holder."""

        async def single_handle_check(_):
            if not self.is_singleton:
                self.check_for_singleton(False)
            return self.is_singleton

        return commands.check(single_handle_check)

    async def termination_handler(self):
        """Shortens own singleton lock during termination."""
        self.logger.info("Terminating bot. Shortening singleton lock time.")
        if self.is_singleton:
            self.singleton_collection.update_one(
                {},
                {"$set": {"valid_until": datetime.now()}},
            )
        await self.close()

    # # -----------------------------------------------------
    # # CLASH CONSISTENCY CHECKS TO BE RUN AT THE LOGIN
    # # -----------------------------------------------------
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
