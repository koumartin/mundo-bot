"""Module of helper functions for MundoBot."""
from typing import Dict
import discord as dc
from mundobot.position import Position


def find_clash_channel(guild: dc.Guild) -> dc.TextChannel:
    """Finds a channel named clash in the guild.

    Args:
        guild (dc.Guild): Guild to find the channel in.

    Returns:
        dc.TextChannel: Clash text channel.
    """
    return next((c for c in guild.text_channels if c.name == "clash"), None)


async def conditional_delete(message: dc.Message) -> None:
    """Deletes a message if it is in a TextChannel.

    Args:
        message (dc.Message): Message that might be deleted.
    """
    if isinstance(message.channel, dc.TextChannel):
        await message.delete()


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


def show_players(players: Dict[str, str]) -> str:
    """Creates a string containing the registered team of players in a clash.

    Args:
        players (Dict[str, str]): Dictionary of players and theire role as string.

    Returns:
        str: Formatted string of players in a team.
    """
    players_modified = dict(map(lambda x: (x[0], Position[x[1]]), players.items()))

    output = "Aktuální sestava\n"
    for position in Position:
        output += f"{str(position)} : {find_players(position, players_modified)}\n"
    return output


async def check_permissions(member: dc.Member) -> bool:
    """Checks if member has manage_roles and manage_channels permissions.

    Args:
        member (dc.Member): Member to be checked.

    Returns:
        bool: Resulting answer.
    """
    ret = True
    if not (
        member.guild_permissions.manage_roles
        and member.guild_permissions.manage_channels
    ):
        await member.send(
            "Mundo no do work for lowlife like you. \
                Get more permissions.(manage channels and roles)"
        )
        ret = False

    return ret


async def remove_reactions(
    target_user: dc.Member | dc.User, message: dc.Message, pos: Position
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
                if user == target_user:
                    await message.remove_reaction(reaction.emoji, target_user)
