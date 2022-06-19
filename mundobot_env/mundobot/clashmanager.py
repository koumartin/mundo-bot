"""Module providing classes of Clash and Clashmanager that manages stored Clashes."""
from dataclasses import dataclass
import json
import datetime
import os
from typing import Dict

from mundobot.position import Position


@dataclass
class Clash:
    """Class for storing clash data."""

    name: str
    date: str
    guild_id: int
    clash_channel_id: int
    channel_id: int
    message_id: int
    role_id: int
    status_id: int

    def __post_init__(self):
        try:
            self.date = datetime.datetime.strptime(self.date, "%d.%m.%Y").date()
        except ValueError:
            self.date = datetime.datetime.fromisoformat(self.date).date()


class ClashManager:
    """Management class for storing and loading Clash instances to JSON.
    WILL BE CHANGED TO STORE AND LOAD FROM MONGODB
    """

    # Clashes are stored as dict--> clash_name : Clash
    clashes: Dict[str, Clash]
    players: Dict[str, Dict[str, Position]]

    def __init__(self, path: str):
        self.path = path
        self.clashes: Dict[str, Clash] = {}
        self.players: Dict[str, Dict[str, Position]] = {}

        with open(
            os.path.join(self.path, "../clash/clash.json"), mode="r", encoding="UTF-8"
        ) as file:
            try:
                json_dict: Dict = json.load(file)
                if len(json_dict) > 0:
                    for (
                        name,
                        date_str,
                        guild,
                        clash_channel,
                        channel,
                        message,
                        role,
                        status,
                    ) in json_dict.values():
                        clash = Clash(
                            name,
                            date_str,
                            guild,
                            clash_channel,
                            channel,
                            message,
                            role,
                            status,
                        )
                        self.clashes[name] = clash
            except Exception as ex:
                print(ex)

    def check_clashes(self) -> Dict[str, Clash]:
        """Finds all clashes that are expired and pops them from the dictionary.

        Returns:
            Dict[str, Clash]: Popped expired clashes.
        """
        clash: Clash
        curr_date = datetime.date.today()
        popped = {}
        for name, clash in self.clashes.items():
            if curr_date > clash.date:
                popped[name] = clash

        for name in popped:
            self.clashes.pop(name)
            self.players.pop(name)

        self.dump_to_json(clash_flag=True)
        return popped

    def dump_to_json(self, clash_flag=False, player_flag=False) -> None:
        """Writes clashes or players into json file based on param flags.

        Args:
            clash_flag (bool, optional): Indicates that clashes should be stored. Defaults to False.
            player_flag (bool, optional): Indicates that players should be stored. Defaults to False.
        """
        if clash_flag:
            with open(
                os.path.join(self.path, "../clash/clash.json"), "w", encoding="UTF-8"
            ) as file:
                dump_dict = {}
                for name, clash in self.clashes.items():
                    dump_dict[name] = list(clash.__dict__.values())

                json.dump(dump_dict, file, indent=4, default=serialize)

        if player_flag:
            with open(
                os.path.join(self.path, "clash/players.json"), "w", encoding="UTF-8"
            ) as file:
                json.dump(self.players, file, indent=4, default=serialize)

    def add_clash(self, clash: Clash) -> None:
        """Adds clash to list of clashes.

        Args:
            clash (Clash): Clash to be added.
        """
        self.clashes[clash.name] = clash

        self.dump_to_json(clash_flag=True)

    def remove_clash(self, clash_name: str) -> Clash:
        """Removes clash with given name and returns it.

        Args:
            clash_name (str): Name of the clash to be removed.

        Returns:
            Clash: Clash that was removed.
        """
        pop = self.clashes.pop(clash_name)

        self.dump_to_json(clash_flag=True)
        return pop

    def register_player(
        self, clash_name: str, player_name: str, team_role: Position
    ) -> None:
        """Adds player to its position in a clash and additionally
        puts that into json for readable form.

        Args:
            clash_name (str): Name of the clash to which the player is added.
            player_name (str): Name of player to be added.
            team_role (Position): Position to which the player is added.
        """
        self.players[clash_name][player_name] = team_role

        self.dump_to_json(player_flag=True)

    def unregister_player(self, clash_name: str, player_name: str) -> None:
        """Unregisters player from clash.

        Args:
            clash_name (str): Name of the clash from which to unregister.
            player_name (str): Name of the player.
        """
        self.players[clash_name].pop(player_name)
        self.dump_to_json(player_flag=True)


def serialize(obj: object) -> str:
    """Helper for serializing complex objects into json.

    Args:
        obj (object): A general object to be serialized.

    Returns:
        str: String serialization of the object.
    """
    if isinstance(obj, Position):
        return str(obj)
    if isinstance(obj, datetime.date):
        return str(obj)
    return str(obj)
