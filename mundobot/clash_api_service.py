"""Module for managing connection to Riot API."""
import datetime
import os
from typing import Any, Dict, List, Tuple

import dotenv
from riotwatcher import LolWatcher


class ClashApiService:
    """Manages methods for connection to Riot API."""

    def __init__(self, api_key: str = "") -> None:
        api_key: str
        if not api_key:
            self.api_key = os.environ.get("riotApiKey")
        else:
            self.api_key = api_key
        self.lol_watcher_clash = LolWatcher(api_key=self.api_key).clash

    @staticmethod
    def map_clash_dto_to_clash(dto: Dict[str, Any]) -> Tuple[int, str, str]:
        """Converts TournamentDto to tuple of id, name and date.

        Args:
            dto (TournamentDto): Clash instance in Riot data.

        Returns:
            Tuple[int, str, str]: Id, name and date of the dto in a tuple.
        """
        name_main: str = dto["nameKey"].replace("_", " ").title()
        name_second: str = dto["nameKeySecondary"].replace("_", " ").title()
        name_full: str = name_main + " Cup - " + name_second
        date: str = datetime.datetime.fromtimestamp(
            dto["schedule"][0]["startTime"] / 1000
        ).isoformat()
        return (dto["id"], name_full, date)

    def get_clashes(self) -> List[Tuple[int, str, str]]:
        """Gets all clashes from Riot Api in form of (id, name, date).

        Returns:
            List[Tuple[int, str, str]]: Clashes in form of (id, name, date).
        """
        response = self.lol_watcher_clash.tournaments("eun1")
        # Map reponses to Clash data structure
        return list(map(self.map_clash_dto_to_clash, response))


if __name__ == "__main__":
    dotenv.load_dotenv()
    serv = ClashApiService()
    print(serv.get_clashes())
