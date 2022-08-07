"""Module providing classes of Clashmanager that manages stored Clashes."""
from datetime import datetime
from dataclasses import asdict
import logging
from typing import Any, Dict, List, Tuple

from pymongo import MongoClient, collection, cursor
from dacite import from_dict

from mundobot.clash import Clash
from mundobot.position import (
    Position,
    PositionRecord,
    ClashPositions,
    DACITE_POSITION_CONFIG,
)
from mundobot.clash_api_service import ApiClash
from mundobot import helpers


class ClashManager:
    """Management class for storing and loading Clash instances to MongoDb."""

    def __init__(self, client: MongoClient):
        self.client = client
        self.clashes: collection.Collection = client.clash.clashes
        self.positions: collection.Collection = client.clash.positions
        self.notifications: collection.Collection = client.clash.notifications
        self.registered_servers: collection.Collection = client.clash.registered_servers
        self.regular_players: collection.Collection = client.clash.regular_players
        self.logger = helpers.prepare_logging("mng", logging.WARNING)

    def clashes_for_guild(self, guild_id: int) -> cursor.Cursor:
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

    def add_clash(
        self, clash: Clash, notification_times: List[datetime] = None
    ) -> None:
        """Adds clash to list of clashes.

        Args:
            clash (Clash): Clash to be added.
        """
        result = self.clashes.insert_one(asdict(clash))
        self.positions.insert_one({"clash_id": result.inserted_id, "players": []})

        if notification_times is None or not isinstance(notification_times, list):
            return

        self.notifications.insert_many(
            [
                {
                    "clash_id": result.inserted_id,
                    "time": x,
                    "notified": False,
                }
                for x in notification_times
            ]
        )

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
        if result is None:
            return None
        self.positions.delete_one({"clash_id": result["_id"]})
        self.notifications.delete_many({"clash_id": result["_id"]})
        return from_dict(Clash, result)

    def register_player(
        self, clash_id: int, player_id: int, player_name: str, team_role: Position
    ) -> ClashPositions:
        """Adds player to its position in a clash.

        Args:
            clash_id (int): Id of the clash to which the player is added.
            player_id (int): Id of the player.
            player_name (str): Name of player to be added.
            team_role (Position): Position to which the player is added.

        Returns:
            ClashPositions: Positions after modification.
        """
        existing_positions = from_dict(
            ClashPositions,
            self.positions.find_one({"clash_id": clash_id}),
            DACITE_POSITION_CONFIG,
        )
        existing_players = existing_positions.players
        already_existing = next(
            (
                x
                for x in existing_players
                if x.player_name == player_name and x.position == team_role
            ),
            None,
        )

        if already_existing is not None:
            self.logger.warning("This combination already exists. Skipping.")
            return existing_positions

        existing_players.append(PositionRecord(player_id, player_name, team_role))
        new_players = list(map(lambda x: x.as_dict(), existing_players))

        return from_dict(
            ClashPositions,
            self.positions.find_one_and_update(
                {"clash_id": clash_id},
                {"$set": {"players": new_players}},
                return_document=collection.ReturnDocument.AFTER,
            ),
            DACITE_POSITION_CONFIG,
        )

    def unregister_player(
        self, clash_id: int, player_name: str, team_role: Position
    ) -> Dict[str, Any]:
        """Unregisters player from clash.

        Args:
            clash_id (int): Id of the clash from which the player is removed.
            player_name (str): Name of the player.
            team_role (Position): Position of the player in the clash.

        Returns:
            ClashPositions: Positions after modification.
        """
        existing_positions = from_dict(
            ClashPositions,
            self.positions.find_one({"clash_id": clash_id}),
            DACITE_POSITION_CONFIG,
        )
        existing_players = existing_positions.players
        already_existing = next(
            [
                x
                for x in existing_players
                if x.player_name == player_name and x.position == str(team_role)
            ],
            None,
        )

        if already_existing is None:
            self.logger.warning("This combination is not registered. Skipping.")
            return existing_positions

        existing_players.remove(already_existing)
        new_players = list(map(lambda x: x.as_dict(), existing_players))

        return from_dict(
            ClashPositions,
            self.positions.find_one_and_update(
                {"clash_id": clash_id},
                {"$set": {"players": new_players}},
                return_document=collection.ReturnDocument.AFTER,
            ),
            DACITE_POSITION_CONFIG,
        )

    def get_needed_changes(
        self, guild_id: int, confirmed_clashes: List[ApiClash]
    ) -> Tuple[List[ApiClash], List[Clash]]:
        """Finds all clashes that are missing in the saved clashes for a guild
        as well as clashes that are not present in confirmed clashes list.

        Args:
            guild_id (int): Id of the guild to check.
            confirmed_clashes (List[ApiClash]): List of clashes against which to compare.

        Returns:
            Tuple[List[ApiClash], List[Clash]]: List of not present clashes
            and a list of surplus clashes.
        """
        missing_names = [c.name for c in confirmed_clashes]
        surplus_clashes = []
        all_clashes = self.clashes.find({"guild_id": guild_id})
        for clash in all_clashes:
            if clash["name"] in missing_names:
                missing_names.remove(clash["name"])
            else:
                surplus_clashes.append(from_dict(Clash, clash))

        missing_clashes = list(
            filter(lambda c: c.name in missing_names, confirmed_clashes)
        )
        return (missing_clashes, surplus_clashes)

    def register_server(self, server_id: int) -> bool:
        """Registers a server for clash updates.

        Args:
            server_id (int): Id of the server to receive updtes.

        Returns:
            bool: Success of the operation.
        """
        existing_server = self.registered_servers.find_one({"server_id": server_id})
        if existing_server is None:
            self.registered_servers.insert_one({"server_id": server_id})
            return True
        return False

    def unregister_server(self, server_id: int) -> bool:
        """Unregisters a server from clash updates.

        Args:
            server_id (int): Id of the server to be unregistered.

        Returns:
            bool: Success of the operation.
        """
        deleted_server = self.registered_servers.delete_one({"server_id": server_id})
        return deleted_server.deleted_count > 0

    def get_registered_server_ids(self) -> List[int]:
        """Gets ids of all servers that are registered for clash updates.

        Returns:
            List[int]: List of ids of registered servers.
        """
        return [result["server_id"] for result in self.registered_servers.find()]

    def get_overdue_notifications(self) -> cursor.Cursor:
        """Gets all unique Clash instances that have overdue notifications.

        Returns:
            cursor.Cursor: Cursor of clashes that have overdue notification.
        """
        overdue_notifications = self.notifications.find(
            {"time": {"$lt": datetime.now()}, "notified": False}
        )
        clashes = self.clashes.find(
            {"_id": {"$in": overdue_notifications.distinct("clash_id")}}
        )
        ids = [notification["_id"] for notification in overdue_notifications]
        self.notifications.update_many(
            {"_id": {"$in": ids}}, {"$set": {"notified": True}}
        )
        return clashes

    def update_notification_ids(
        self, clash_id: int, notification_message_ids: List[int]
    ) -> None:
        """Updates notification message ids array of a clash.

        Args:
            clash_id (int): Id of the clash to update.
            notification_message_ids (List[int]): New list of notification message ids.
        """
        self.clashes.update_one(
            {"_id": clash_id},
            {"$set": {"notification_message_ids": notification_message_ids}},
        )

    def get_regular_players(self, guild_id: int) -> List[int]:
        """Gets list to all players in guild that are regular clash players.

        Args:
            guild_id (int): Id of the guild.

        Returns:
            List[int]: List of regular player ids.
        """
        return [
            player["id"] for player in self.regular_players.find({"guild_id": guild_id})
        ]

    def register_regular_player(self, guild_id: int, player) -> None:
        pass

    def unregister_regular_player(self, guild_id: int, player) -> None:
        pass
