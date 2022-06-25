"""Module providing classes of Clashmanager that manages stored Clashes."""
import datetime
from dataclasses import asdict
from typing import Dict

import pymongo
import pymongo.cursor
import pymongo.typings
from dacite import from_dict

from mundobot.clash import Clash
from mundobot.position import Position


class ClashManager:
    """Management class for storing and loading Clash instances to JSON.
    WILL BE CHANGED TO STORE AND LOAD FROM MONGODB
    """

    def __init__(self, client: pymongo.MongoClient):
        self.client = client
        self.clashes = client.clash.clashes
        self.positions = client.clash.positions

    def check_clashes(self) -> Dict[str, Clash]:
        """Finds all clashes that are expired and pops them from the dictionary.

        Returns:
            Dict[str, Clash]: Popped expired clashes.
        """

        for expired_clash in self.clashes.find(
            {"date": {"$lt": datetime.datetime.today()}}
        ):
            pass

        return {}
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

    def clashes_for_guild(self, guild_id: int) -> pymongo.cursor.Cursor:
        """Gets all clashes present for a given guild.

        Args:
            guild_id (int): Id of the guild.

        Returns:
            pymongo.cursor.Cursor: Cursor to the clashes documents.
        """
        return self.clashes.find({"guild_id": guild_id})

    def players_for_clash(self, clash_id: int) -> Dict[str, str]:
        """Gets list of players for a clash with given db id.

        Args:
            clash_id (int): Id of the clash in db.

        Returns:
            Dict[str, str]: Mapping of players to their role.
        """
        return self.positions.find_one(
            {"clash_id": clash_id},
            projection={"players": True, "_id": False},
        )["players"]

    def add_clash(self, clash: Clash) -> None:
        """Adds clash to list of clashes.

        Args:
            clash (Clash): Clash to be added.
        """
        result = self.clashes.insert_one(asdict(clash))
        self.positions.insert_one({"clash_id": result.inserted_id, "players": {}})

    def remove_clash(self, clash_name: str, guild_id: int) -> Clash:
        """Removes clash with given name and returns it.

        Args:
            clash_name (str): Name of the clash to be removed.
            guild_id (int): Id of the guild.

        Returns:
            Clash: Clash that was removed.
        """
        result = self.clashes.find_one_and_delete(
            {"name": clash_name, "guild_id": guild_id}
        )
        self.positions.delete_one({"clash_id": result["_id"]})
        return from_dict(Clash, result)

    def register_player(
        self, clash_id: int, player_name: str, team_role: Position
    ) -> None:
        """Adds player to its position in a clash.
        Args:
            clash_id (int): Id of the clash to which the player is added.
            player_name (str): Name of player to be added.
            team_role (Position): Position to which the player is added.
        """
        self.positions.find_one_and_update(
            {"clash_id": clash_id}, {"$set": {f"players.{player_name}": team_role.name}}
        )

    def unregister_player(self, clash_name: str, player_name: str) -> None:
        """Unregisters player from clash.

        Args:
            clash_name (str): Name of the clash from which to unregister.
            player_name (str): Name of the player.
        """
        self.players[clash_name].pop(player_name)
        self.dump_to_json(player_flag=True)


# def serialize(obj: object) -> str:
#     """Helper for serializing complex objects into json.

#     Args:
#         obj (object): A general object to be serialized.

#     Returns:
#         str: String serialization of the object.
#     """
#     if isinstance(obj, Position):
#         return str(obj)
#     if isinstance(obj, datetime.date):
#         return str(obj)
#     return str(obj)

#     def dump_to_json(self, clash_flag=False, player_flag=False) -> None:
#         """Writes clashes or players into json file based on param flags.

#         Args:
#             clash_flag (bool, optional): Indicates that clashes should be stored. Defaults to False.
#             player_flag (bool, optional): Indicates that players should be stored. Defaults to False.
#         """
#         if clash_flag:
#             with open(
#                 os.path.join(self.path, "../clash/clash.json"), "w", encoding="UTF-8"
#             ) as file:
#                 dump_dict = {}
#                 for name, clash in self.clashes.items():
#                     dump_dict[name] = list(clash.__dict__.values())

#                 json.dump(dump_dict, file, indent=4, default=serialize)

#         if player_flag:
#             with open(
#                 os.path.join(self.path, "clash/players.json"), "w", encoding="UTF-8"
#             ) as file:
#                 json.dump(self.players, file, indent=4, default=serialize)
