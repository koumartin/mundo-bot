"""Module providing Clash dataclass for storing League clash data."""
from dataclasses import dataclass, field
import datetime
from typing import List, Optional


@dataclass
class Clash:
    """Class for storing clash data."""

    name: str
    date_string: str
    guild_id: int
    clash_channel_id: int
    channel_id: int
    message_id: int
    role_id: int
    status_id: int
    notification_message_ids: List[int] = field(default_factory=lambda: [])
    riot_id: Optional[int] = None
    date: datetime.datetime = None

    def __post_init__(self):
        if self.date is None:
            try:
                self.date = datetime.datetime.strptime(self.date_string, "%d.%m.%Y")
            except ValueError:
                self.date = datetime.datetime.fromisoformat(self.date_string).replace(
                    hour=0, minute=0, second=0
                )


@dataclass
class RegularPlayer:
    """Class used for storing regular players in the DB."""

    player_id: int
    guild_id: int
    # Represents if the player is considered as regular at the moment
    active: bool
    # Represents if the next change needs to be done by privileged member
    # member -> Only concened member can activate
    # server -> Only member high permission user in server can activate
    # none   -> All available users can activate
    overruled: str = "none"
    # Signals who activated this last
    last_activated: str = "none"
