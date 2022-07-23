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
