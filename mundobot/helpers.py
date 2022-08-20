"""Module of helper functions for MundoBot."""
from datetime import datetime, timedelta
import logging
import os
from typing import List, Optional
import discord as dc
from mundobot.position import Position, ClashPositions, PositionRecord
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


def find_players(target: Position, players: List[PositionRecord]) -> str:
    """Gets names of all players with given position in registered players for clash.

    Args:
        target (Position): Position of the players.
        players (List[PositionRecord]): Records of the registerations.

    Returns:
        str: Names of all players with that position or empty string.
    """
    output = ""
    for registration in players:
        if registration.position == target:
            output += registration.player_name + " "
    return output


def show_players(positions: ClashPositions = None) -> str:
    """Creates a string containing the registered team of players in a clash.

    Args:
        positions (ClashPositions, optional): All registrations to the clash. Defaults to None.

    Returns:
        str: Formatted string of players in a team.
    """
    players = positions.players if positions is not None else []

    output = "Aktuální sestava\n"
    for position in Position:
        output += f"{str(position)} : {find_players(position, players)}\n"
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


def get_notification(
    players: List[PositionRecord], clash: Clash, regular_players: List[int]
) -> str:
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
    for registration in players:
        if registration.position in missing_positions:
            missing_positions.remove(registration.position)

    output = (
        f"Clash {clash.name} začíná za zhruba {remaining_time.days} dní, "
        + f"{remaining_hours} hodin a {remaining_minutes} minut.\n"
    )
    unique_player_ids = {
        registration.player_id
        for registration in players
        if registration.position != Position.NOOB
    }

    unique_players_count = len(unique_player_ids)
    if unique_players_count < 5:
        connection = ("je", "") if unique_players_count == 1 else ("jsou", "i")
        output += (
            f"Stále není dost hráčů. Aktuálně {connection[0]} "
            + f"přihlášen{connection[1]} pouze {unique_players_count} hráč{connection[1]}.\n"
        )
    if len(missing_positions) > 0:
        output += "Stále chybí hráči na pozice: \n"
        for position in missing_positions:
            output += str(position) + " "
        output += "\n"

    if unique_players_count < 5 or len(missing_positions) > 0:
        unresponive_players_ids = {
            id for id in regular_players if id not in unique_player_ids
        }
        if len(unresponive_players_ids) > 0:
            output += "Stále neodpověděli: \n"
            for player_id in unresponive_players_ids:
                output += f"<@{player_id}> "
        else:
            output += "Všichni již odpověděli, takže zkuste hledat jinde."
    else:
        output += (
            "Všechny pozice jsou zaplněny a hráčů je dostatek, takže pouze připomínám."
        )

    return output


def prepare_logging(
    name: str,
    console_level: Optional[int] = None,
    file_level: Optional[int] = None,
    path: Optional[str] = None,
) -> logging.Logger:
    """Prepares console and file logger with given level.
    If level is not provided than logger is not created.

    Args:
        path (Optional[str], optional): Path for file logging. Defaults to None.
        console_level (Optional[int], optional): Level of console logger. Defaults to None.
        file_level (Optional[int], optional): Level of file logger. Defaults to None.

    Returns:
        logging.Logger: Final logger.
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "[%(asctime)s %(name)s %(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger.setLevel(logging.DEBUG)
    if console_level is not None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    if file_level is not None:
        log_path = path + "/log/"
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        file_handler = logging.FileHandler(
            log_path + "bot_log_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "w",
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
