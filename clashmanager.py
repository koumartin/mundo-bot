import json
import datetime
import os
from typing import Dict, Tuple

from positions import Positions


def serialize(obj):
    if isinstance(obj, Positions):
        return str(obj)
    if isinstance(obj, datetime.date):
        return str(obj)


class ClashManager:
    # Clashes are stored as dict--> clash_name : (guild_id, channel_id, message_id, date, role_id)
    clashes: Dict[str, Tuple[int, int, int, datetime.date, int]]
    players: Dict[str, Dict[str, Positions]]

    def __init__(self, path: str):
        self.path = path
        self.clashes = {}
        self.players = {}
        with open(os.path.join(self.path, "clash/clash.json"), "r") as f:
            try:
                json_dict: Dict = json.load(f)
                if len(json_dict) > 0:
                    for name, (guild, channel, message, date_str, role_id) in json_dict.items():
                        date_val = datetime.date.fromisoformat(date_str)
                        self.clashes[name] = (guild, channel, message, date_val, role_id)
            except:
                print("Ex")
                pass

        with open(os.path.join(self.path, "clash/players.json"), "r") as f:
            try:
                self.players = json.load(f)

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

        self.dump_to_json(clash_flag=True)
        return popped

    def dump_to_json(self, clash_flag=False, player_flag=False):
        if clash_flag:
            with open(os.path.join(self.path, "clash/clash.json"), "w") as f:
                json.dump(self.clashes, f, indent=4, default=serialize)
        if player_flag:
            with open(os.path.join(self.path, "clash/players.json"), "w") as f:
                json.dump(self.players, f, indent=4, default=serialize)

    def add_clash(self, name: str, date: str, guild_id: int, channel_id: int, message_id: int, role_id: int):
        date_val = datetime.datetime.strptime(date, "%d.%m.%y").date()
        self.clashes[name] = (guild_id, channel_id, message_id, date_val, role_id)

        self.dump_to_json(clash_flag=True)

    def register_player(self, clash_name: str, player_name: str, team_role: Positions):
        self.players[clash_name][player_name] = team_role

        self.dump_to_json(player_flag=True)

    def unregister_player(self, clash_name: str, player_name: str):
        self.players[clash_name].pop(player_name)

        self.dump_to_json(player_flag=True)
