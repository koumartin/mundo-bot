"""
Mundo bot class and commands for running it.
"""
import asyncio
import os
import queue
from typing import Dict, Tuple
from urllib.parse import quote_plus
from dacite import from_dict

import discord as dc
import dotenv
from discord.ext import commands
from discord.ext.commands.context import Context
from pymongo import MongoClient

from mundobot.clashmanager import ClashManager
from mundobot.clash import Clash
from mundobot.position import Position

# -------------------------------------------
# ADDITIONAL INFORMATION:
# Author: @koumartin
# Date: 22/3/2021
# -------------------------------------------


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

        self.client = MongoClient(mongodbConnectionString)
        self.clash_manager: ClashManager = ClashManager(self.client)
        self.accepted_reactions = Position.accepted_reactions()

        self.add_all_commands()

    def start_running(self) -> None:
        """Commands the bot to log in and start running using its api token."""
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
                await status_message.edit(content=self.show_players(new_positions))
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
                    await status_message.edit(content=self.show_players(new_positions))
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
            await self.conditional_delete(ctx.message)

            guild = ctx.guild
            voice_client = dc.utils.get(self.voice_clients, guild=guild)

            print(ctx.author, "called !shutup in", ctx.guild)

            # TODO: REDO WITH PERMISSIONS
            if (
                ctx.author.name != "KoudyCZ"
                and ctx.author.name != "adjalS"
                and additional.lower() != "please"
                and additional.lower() != "prosím"
            ):
                await ctx.author.send("You no tell Mundo what Mundo do!!!")
                return

            if additional.lower() == "please" or additional.lower() == "prosím":
                await ctx.author.send(
                    "You say please so nice... Okey Mundo be silent now."
                )
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
            await self.conditional_delete(ctx.message)

            # Check caller permissions
            if not (
                ctx.author.guild_permissions.manage_roles
                and ctx.author.guild_permissions.manage_channels
            ):
                await ctx.author.send(
                    "Mundo no do work for lowlife like you. \
                    Get more permissions.(manage channels and roles)"
                )
                return

            # Sends message to designated channel and also gets clash_channel
            clash_channel = next(
                (c for c in ctx.guild.text_channels if c.name == "clash"), None
            )
            if clash_channel is None:
                await ctx.author.send("Mundo need clash text channel.")
                return
            message = await clash_channel.send(
                f"@everyone Nábor na clash {clash_name} - {date}\n",
                "Pokud můžete a chcete si zahrát tak zareagujete svojí rolí"
                + " nebo fill rolí, případně :thumbdown: pokud nemůžete.",
                allowed_mentions=dc.AllowedMentions.all(),
            )

            # Give access to new channel to everyone above or equal to requesting user +
            # new designated role
            overwrites = {}
            author_role = max(ctx.author.roles)
            for role in ctx.guild.roles:
                overwrites[role] = dc.PermissionOverwrite(
                    read_messages=(role >= author_role)
                )

            # Check if role with desired clash_name already exists, else create it and give
            # it permissions to channel
            role_name = clash_name + " Player"
            role = next((r for r in ctx.guild.roles if r.name == role_name), None)
            if role is None:
                role: dc.Role = await ctx.guild.create_role(
                    name=role_name, permissions=ctx.guild.default_role.permissions
                )
                overwrites[role] = dc.PermissionOverwrite(read_messages=True)

            # Channel will be placed to category named Clash, else to no category
            category = next(
                (c for c in ctx.guild.categories if c.name == "Clash"), None
            )

            # Create new channel only if no channel of such name currently exists
            channel = next(
                (
                    c
                    for c in ctx.guild.channels
                    if c.name == clash_name.replace(" ", "-").lower()
                ),
                None,
            )
            if channel is None:
                channel = await ctx.guild.create_text_channel(
                    clash_name, overwrites=overwrites, category=category
                )

            # Add message to channel and pin it
            status = await channel.send(self.show_players(dict()))
            await status.pin()

            # Create new Clash object to hold all data about it and supporting structure
            clash = Clash(
                clash_name,
                date,
                ctx.guild.id,
                clash_channel.id,
                channel.id,
                message.id,
                role.id,
                status.id,
            )

            # Add all this to clash manager for saving
            self.clash_manager.add_clash(clash)

        @self.command()
        async def remove_clash(ctx: Context, clash_name: str) -> None:
            """Removes clash and all asociated lists, channels and roles.
            WILL BECOME DEPRECATED


            Args:
                ctx (Context): Context of the command.
                clash_name (str): Name of the clash to be removed.
            """
            await self.conditional_delete(ctx.message)

            # Check caller permissions
            if not (
                ctx.author.guild_permissions.manage_roles
                and ctx.author.guild_permissions.manage_channels
            ):
                await ctx.author.send(
                    "Mundo no do work for lowlife like you. Get more permissions."
                    "(manage channels and roles)"
                )
                return

            clash: Clash = self.clash_manager.remove_clash(clash_name, ctx.guild.id)
            await self.delete_clash(clash)

    # -----------------------------------------------------
    # HELPER FOR DELETING ALL CLASH BELONGINGS
    # -----------------------------------------------------
    async def delete_clash(self, clash: Clash) -> None:
        """Deletes clash and all associated propertis with it.

        Args:
            clash (Clash): Clash object to be removed.
        """
        guild = self.get_guild(clash.guild_id)
        # Delete role and channel
        role_name = clash.name + " Player"
        roles = (r for r in guild.roles if r.name == role_name)
        for role in roles:
            await role.delete()
        channels = (
            channel
            for channel in guild.text_channels
            if channel.name == clash.name.replace(" ", "-").lower()
        )
        for channel in channels:
            await channel.delete()
        # Delete original message in general clash channel
        channel = guild.get_channel(clash.clash_channel_id)
        message = await channel.fetch_message(clash.message_id)
        await message.delete()

    # -----------------------------------------------------
    # METHODS FOR CREATING STRING OF CURRENTLY REGISTERED PLAYERS FOR GIVEN CLASH
    # -----------------------------------------------------
    def show_players(self, players: Dict[str, str]) -> str:
        """Creates a string containing the registered team of players in a clash.

        Args:
            players (Dict[str, str]): Dictionary of players and theire role as string.

        Returns:
            str: Formatted string of players in a team.
        """
        players_modified = dict(map(lambda x: (x[0], Position[x[1]]), players.items()))

        output = "Aktuální sestava\n"
        for position in Position:
            output += (
                f"{str(position)} : {self.find_players(position, players_modified)}\n"
            )
        return output

    @staticmethod
    def find_players(target: Position, players: Dict[str, Position]) -> str:
        """Gets names of all players with given position in registered players for clash.

        Args:
            target (Position): Position of the players.
            players (Dict[str, Position]): Dictionary of registered players.

        Returns:
            str: Names of all players with that position or empty string.
        """
        output = ""
        for player, position in players.items():
            if position == target:
                output += player + " "
        return output

    @staticmethod
    async def remove_reactions(
        user: dc.Member | dc.User, message: dc.Message, pos: Position
    ) -> None:
        """Removes a reaction associated with position from the messsage.

        Args:
            user (dc.Member | dc.User): User or Member for which teh reaction is removed.
            message (dc.Message): Message on which the reaction is removed.
            pos (Position): Position associated with removed reaction.
        """
        for reaction in message.reactions:
            if isinstance(reaction.emoji, str):
                emoji_name = reaction.emoji
            else:
                emoji_name = reaction.emoji.name
            if Position.get_position(emoji_name) != pos:
                users = await reaction.users().flatten()
                for user in users:
                    if user == user:
                        await message.remove_reaction(reaction.emoji, user)

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
    # CONDITIONAL DELETE
    # ----------------------------------------------------
    @staticmethod
    async def conditional_delete(message: dc.Message) -> None:
        """Deletes a message if it is in a TextChannel.

        Args:
            message (dc.Message): Message that might be deleted.
        """
        if isinstance(message.channel, dc.TextChannel):
            await message.delete()


# -----------------------------------------------------
# MAIN
# -----------------------------------------------------
if __name__ == "__main__":
    dotenv.load_dotenv()

    bot_token = os.environ.get("botToken")

    # Resolving connection to database
    username = os.environ.get("mongoUsername")
    password = os.environ.get("mongoPassword")
    if os.environ.get("DOCKER") == "true":
        connection_string = (
            f"mongodb://{quote_plus(username)}:{quote_plus(password)}@mongodb:27017"
        )
    else:
        connection_string = (
            f"mongodb://{quote_plus(username)}:{quote_plus(password)}@localhost:27017"
        )

    bot = MundoBot(bot_token, connection_string)
    bot.start_running()

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
