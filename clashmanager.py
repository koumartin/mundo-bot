import json
import datetime
import os
from typing import Dict, Tuple


class ClashManager:
    # Clashes are stored as dict--> clash_name : (guild_id, channel_id, message_id, date, role_id)
    clashes: Dict[str, Tuple[int, int, int, datetime.date, int]]
    players: Dict[str, Dict[str, str]]

    def __init__(self, path: str):
        self.path = path
        self.clashes = {}
        self.players = {}
        with open(os.path.join(self.path, "clash/clash.json"), "r") as log:
            try:
                json_dict: Dict = json.load(log)
                if len(json_dict) > 0:
                    for name, (guild, channel, message, date_str, role_id) in json_dict.items():
                        date_val = datetime.date.fromisoformat(date_str)
                        self.clashes[name] = (guild, channel, message, date_val, role_id)
            except:
                print("Ex")
                pass

    def check_clashes(self) -> Dict[str, Tuple[int, int, int, datetime.date, int]]:
        curr_date = datetime.date.today()
        popped = {}
        for name, data in self.clashes.items():
            if curr_date > data[3]:
                popped[name] = data

        for name in popped:
            self.clashes.pop(name)

        self.dump_to_json()
        return popped

    def dump_to_json(self):
        with open(os.path.join(self.path, "clash/clash.json"), "w") as log:
            json.dump(self.clashes, log, indent=4, default=str)

    def add_clash(self, name: str, date: str, guild_id: int, channel_id: int, message_id: int, role_id: int):
        date_val = datetime.datetime.strptime(date, "%d.%m.%y").date()
        self.clashes[name] = (guild_id, channel_id, message_id, date_val, role_id)

        self.dump_to_json()
