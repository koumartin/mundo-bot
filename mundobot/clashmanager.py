"""Module providing classes of Clashmanager that manages stored Clashes."""
import datetime
from dataclasses import asdict
from typing import Any, Dict, List

import pymongo
import pymongo.cursor
import pymongo.typings
import pymongo.collection
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

    def check_clashes(self) -> List[Clash]:
        """Finds all clashes that are expired and pops them from the DB.

        Returns:
            List[Clash]: Popped expired clashes.
        """

        expired_clashes: List[Clash] = []
        for expired_clash_entry in self.clashes.find(
            {"date": {"$lt": datetime.datetime.today()}}
        ):
            expired_clashes.append(from_dict(Clash, expired_clash_entry))
            self.clashes.delete_one({"_id": expired_clash_entry["_id"]})
            self.positions.delete_one({"clash_id": expired_clash_entry["_id"]})

        return expired_clashes

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

    def role_for_player(self, clash_id: int, player_name: str) -> Position | None:
        """Gets the position of the player in given clash.

        Args:
            clash_id (int): Id of the clash.
            player_name (str): Name of the player.

        Returns:
            Position | None: Position of the player or None if the player does not have position.
        """
        players_for_clash = self.players_for_clash(clash_id)
        try:
            return Position[players_for_clash[player_name]]
        except KeyError:
            return None

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
    ) -> Dict[str, Any]:
        """Adds player to its position in a clash.

        Args:
            clash_id (int): Id of the clash to which the player is added.
            player_name (str): Name of player to be added.
            team_role (Position): Position to which the player is added.

        Returns:
            Dict[str, Any]: Positions dictionary after modification.
        """
        return self.positions.find_one_and_update(
            {"clash_id": clash_id},
            {"$set": {f"players.{player_name}": team_role.name}},
            return_document=pymongo.collection.ReturnDocument.AFTER,
        )["players"]

    def unregister_player(self, clash_id: str, player_name: str) -> Dict[str, Any]:
        """Unregisters player from clash.

        Args:
            clash_id (int): Id of the clash from which the player is removed.
            player_name (str): Name of the player.

        Returns:
            Dict[str, Any]: Positions dictionary after modification.
        """
        return self.positions.find_one_and_update(
            {"clash_id": clash_id},
            {"$unset": {f"players.{player_name}": ""}},
            return_document=pymongo.collection.ReturnDocument.AFTER,
        )["players"]


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
