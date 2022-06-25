"""Enum class of positions in clash with helper functions."""
from __future__ import annotations
import enum
from functools import reduce
from typing import List, Optional


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

    @staticmethod
    def accepted_reactions() -> List[str]:
        """Gets list of all emoji names for which get_position will return value.

        Returns:
            List[str]: List of emoji names for which get_position will return value.
        """
        return reduce(lambda acc, pos: acc + pos.value, Position, [])
