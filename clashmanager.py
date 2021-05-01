import json
import datetime
import os
from typing import Dict


class ClashManager:

    def __init__(self, path: str):
        self.path = path
        self.clashes: Dict[str, datetime.date] = {}
        with open(os.path.join(self.path, "clash/clash.json"), "r") as log:
            try:
                json_dict: Dict = json.load(log)
                for name, date_str in json_dict.items():
                    self.clashes[name] = datetime.date.fromisoformat(date_str)
            except:
                pass

    def check_clashes(self) -> Dict[str, datetime.date]:
        curr_date = datetime.date.today()
        popped = {}
        for name, date in self.clashes.items():
            if curr_date > self.clashes[name]:
                popped[name] = date

        for name in popped:
            self.clashes.pop(name)

        self.dump_to_json()
        return popped

    def dump_to_json(self):
        with open(os.path.join(self.path, "clash/clash.json"), "w") as log:
            json.dump(self.clashes, log, indent=4, default=str)

    def add_clash(self, name: str, date: str) -> Dict[str, datetime.date]:
        date_val = datetime.datetime.strptime(date, "%d.%m.%y").date()
        self.clashes[name] = date_val

        self.dump_to_json()

        return self.clashes
