"""Module providing classes of Clashmanager that manages stored Clashes."""
from datetime import datetime
from dataclasses import asdict
import logging
from typing import Any, Dict, List, Tuple

from pymongo import MongoClient, collection, cursor
from dacite import from_dict

from mundobot.clash.clash import Clash, RegularPlayer
from mundobot.clash.position import (
    Position,
    PositionRecord,
    ClashPositions,
    DACITE_POSITION_CONFIG,
)
from mundobot.clash.clash_api_service import ApiClash
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

    def positions_for_clash(self, clash_id: int) -> ClashPositions:
        """Gets positions for a clash.

        Args:
            clash_id (int): Id of the clash in DB.

        Returns:
            ClashPositions: Positions in the clash.
        """
        return from_dict(
            ClashPositions,
            self.positions.find_one({"clash_id": clash_id}),
            DACITE_POSITION_CONFIG,
        )

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
        existing_positions = self.positions_for_clash(clash_id)
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
        existing_positions = self.positions_for_clash(clash_id)
        existing_players = existing_positions.players
        already_existing = next(
            (
                x
                for x in existing_players
                if x.player_name == player_name and x.position == team_role
            ),
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

    def regular_players_for_guild(self, guild_id: int) -> List[int]:
        """Gets list of ids of regular players in a guild.

        Args:
            guild_id (int): Id of the guild.

        Returns:
            List[int]: Ids of the regular players.
        """
        return [
            x["player_id"]
            for x in self.regular_players.find({"guild_id": guild_id, "active": True})
        ]

    def register_regular_player(
        self,
        guild_id: int,
        player_id: int,
        self_managing: bool = False,
        privilaged_managing: bool = False,
    ) -> None:
        """Registers a player as a regular player of a guild.

        Args:
            guild_id (int): Id of the guild.
            player_id (int): Id of the player.
        """
        current = self.regular_players.find_one(
            {"player_id": player_id, "guild_id": guild_id}
        )

        if current is None:
            new_regular = RegularPlayer(player_id, guild_id, True)
            self.regular_players.insert_one(asdict(new_regular))
            return True

        current_regular = from_dict(RegularPlayer, current)
        if current_regular.active is True:
            raise ValueError("The player is already active.")
        if current_regular.overruled == "member" and not self_managing:
            raise ValueError(
                "The player decided to not be regular and needs to start again himself."
                + " Ask player directly."
            )
        if current_regular.overruled == "server" and not privilaged_managing:
            raise ValueError(
                "The server decided to remove player from regulars."
                + " Server admin needs to register him again. Ask admin directly."
            )

        last_activated = "none"
        if self_managing is True:
            last_activated = "member"
        if privilaged_managing is True:
            last_activated = "server"
        self.regular_players.find_one_and_update(
            {"player_id": player_id, "guild_id": guild_id},
            {"$set": {"active": True, "last_activated": last_activated}},
        )
        return True

    def unregister_regular_player(
        self,
        guild_id: int,
        player_id: int,
        self_managing: bool = False,
        privilaged_managing: bool = False,
    ) -> None:
        """Unregisters a player as a regular player of a guild.

        Args:
            guild_id (int): Id of the guild.
            player_id (int): Id of the player.

        Exceptions:

        """
        current = self.regular_players.find_one(
            {"player_id": player_id, "guild_id": guild_id}
        )

        if current is None:
            raise ValueError("The player is not regular in given server.")

        current_player = from_dict(RegularPlayer, current)
        if current_player.active is not True:
            raise ValueError("The player is not currently active.")
        overrule = "none"
        if self_managing is True:
            overrule = "member"
        if privilaged_managing is True:
            overrule = "server"
        if current_player.last_activated not in (overrule, "none"):
            final_overrule = overrule
        else:
            final_overrule = "none"

        self.regular_players.update_one(
            {"player_id": player_id, "guild_id": guild_id},
            {"$set": {"active": False, "overruled": final_overrule or "none"}},
        )
        return True
