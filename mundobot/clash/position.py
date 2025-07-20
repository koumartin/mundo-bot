"""Enum class of positions in clash with helper functions."""
from __future__ import annotations
import enum
from functools import reduce
from typing import Dict, List, Optional
from dataclasses import dataclass
from dacite.config import Config

from bson import ObjectId


class Position(enum.Enum):
    """Enum class of positions in the clash."""

    TOP = ["top", "top-1"]
    JUNGLE = ["jun", "jung", "jungler"]
    MID = ["mid", "middle"]
    BOT = ["adc", "bot", "bottom"]
    SUPPORT = ["sup", "supp", "support"]
    FILL = ["fill", "👍"]
    NOOB = ["noob", "👎"]

    def __str__(self):
        return self.name

    @staticmethod
    def get_position(emoji_name: str) -> Optional[Position]:
        """Gets Position that correspponds to the emoji name given.

        Args:
            emoji_name (str): Emoji for which the Position is found.

        Returns:
            Optional[Position]: If emoji corresponds to a Position,
            that Position is returned else None.
        """
        emoji_name = emoji_name.lower()
        for position in Position:
            if emoji_name in position.value:
                return position
        return None

    @staticmethod
    def accepted_reactions() -> List[str]:
        """Gets list of all emoji names for which get_position will return value.

        Returns:
            List[str]: List of emoji names for which get_position will return value.
        """
        return reduce(lambda acc, pos: acc + pos.value, Position, [])


@dataclass
class PositionRecord:
    """Class used for storing individual player position records into DB."""

    player_id: int
    player_name: str
    position: Position

    def as_dict(self) -> Dict:
        """Convertor to serialized format.

        Returns:
            Dict: Serialized PositionRecord.
        """
        return {
            "player_id": self.player_id,
            "player_name": self.player_name,
            "position": str(self.position),
        }


@dataclass
class ClashPositions:
    """Class used for storing positions in clashes into DB."""

    clash_id: ObjectId
    players: List[PositionRecord]


DACITE_POSITION_CONFIG = Config(type_hooks={Position: lambda x: Position[x]})
