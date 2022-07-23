"""Module of helper functions for MundoBot."""
from datetime import datetime, timedelta
from typing import Dict, List
import discord as dc
from mundobot.position import Position
from mundobot.clash import Clash


# Predefined times at which notifications for clash will happen
NOTIFICATION_DELTAS = [
    timedelta(days=-6, hours=-12),  # Week before at noon
    timedelta(days=-1, hours=-12),  # Two days before at noon
    timedelta(hours=9),  # Same day in the morning
]


def find_text_channel_by_name(guild: dc.Guild, name: str) -> dc.TextChannel:
    """Finds text channel with given name in guild.

    Args:
        guild (dc.Guild): Guild to search in.
        name (str): Name of the channel to search for.

    Returns:
        dc.TextChannel: Text channel that is found or None if no exists.
    """
    name = name.replace(" ", "-").lower()
    return next(
        (c for c in guild.text_channels if c.name == name),
        None,
    )


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


def prepare_notification_times(clash: Clash) -> List[datetime]:
    """Calculates times for clash notifications.

    Args:
        clash (Clash): Clash for which notofication should be created.

    Returns:
        List[datetime]: List of notification times.
    """
    clash_time = clash.date
    return [clash_time + delta for delta in NOTIFICATION_DELTAS]


def get_notification(players: Dict[str, str], clash: Clash) -> str:
    """Gets notification message for a clash.

    Args:
        players (Dict[str, str]): List of players registered for the clash.
        clash (Clash): Clash instance for which the notification is made.

    Returns:
        str: Notification string.
    """
    # Prepare time to the clash
    approximate_start_time = clash.date + timedelta(hours=21)
    remaining_time = approximate_start_time - datetime.now()
    remaining_hours = remaining_time.seconds // (60 * 60)
    remaining_time -= timedelta(hours=remaining_hours)
    remaining_minutes = remaining_time.seconds // 60
    remaining_time -= timedelta(minutes=remaining_minutes)

    # Prepare missing positions
    missing_positions = list(Position)
    missing_positions.remove(Position.FILL)
    missing_positions.remove(Position.NOOB)
    for position_str in players.values():
        position = Position[position_str]
        if position in missing_positions:
            missing_positions.remove(position)

    output = (
        f"Clash {clash.name} začíná za zhruba {remaining_time.days} dní, "
        + f"{remaining_hours}hodin a {remaining_minutes} minut.\n"
    )
    unique_players = set(
        player
        for player, position in players.items()
        if Position[position] != Position.NOOB
    )
    connection = ("je", "") if len(unique_players) == 1 else ("jsou", "i")

    if len(unique_players) < 5:
        output += (
            f"Stále není dost hráčů. Aktuálně {connection[0]} "
            + f"přihlášen{connection[1]} pouze {len(unique_players)} hráč{connection[1]}.\n"
        )
    if len(missing_positions) > 0:
        output += "Stále chybí hráči na pozice: \n"
        for position in missing_positions:
            output += str(position) + " "
    else:
        output += "Všechny pozice jsou zaplněny, takže pouze připomínám."

    return output
