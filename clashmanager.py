import json
import datetime
import os
from typing import Dict, Tuple


class ClashManager:
    # Clashes are stored as dict--> clash_name : (guild_id, channel_id, message_id, date)
    clashes: Dict[str, Tuple[int, int, int, datetime.date]]

    def __init__(self, path: str):
        self.path = path
        self.clashes = {}
        with open(os.path.join(self.path, "clash/clash.json"), "r") as log:
            try:
                json_dict: Dict = json.load(log)
                if len(json_dict) > 0:
                    for name, (guild, channel, message, date_str) in json_dict.items():
                        date_val = datetime.date.fromisoformat(date_str)
                        self.clashes[name] = (guild, channel, message, date_val)
            except:
                print("Ex")
                pass

    def check_clashes(self) -> Dict[str, Tuple[int, int, int, datetime.date]]:
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

    def add_clash(self, name: str, date: str, guild_id: int, channel_id: int, message_id: int):
        date_val = datetime.datetime.strptime(date, "%d.%m.%y").date()
        self.clashes[name] = (guild_id, channel_id, message_id, date_val)

        self.dump_to_json()
