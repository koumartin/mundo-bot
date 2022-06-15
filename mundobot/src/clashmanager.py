import json
import datetime
import os
from typing import Dict, Tuple

from position import Position



class Clash:
    def __init__(self, name: str, date: str, guild_id: int, clash_channel_id: int,  channel_id: int, message_id: int, role_id: int, status_id: int):
        self.name = name
        try:
            self.date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
        except ValueError:
            self.date = datetime.datetime.fromisoformat(date).date()
        self.guild_id = guild_id
        self.clash_channel_id = clash_channel_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.role_id = role_id
        self.status_id = status_id


class ClashManager:
    # Clashes are stored as dict--> clash_name : Clash
    clashes: Dict[str, Clash]
    players: Dict[str, Dict[str, Position]]

    def __init__(self, path: str):
        self.path = path
        self.clashes = {}
        self.players = {}
        with open(os.path.join(self.path, "../clash/clash.json"), "r") as f:
            try:
                json_dict: Dict = json.load(f)
                if len(json_dict) > 0:
                    for (name, date_str, guild, clash_channel, channel, message, role, status) in json_dict.values():
                        c = Clash(name, date_str, guild, clash_channel, channel, message, role, status)
                        self.clashes[name] = c
            except Exception as e:
                print(e)
                pass

    def check_clashes(self) -> Dict[str, Clash]:
        clash: Clash
        curr_date = datetime.date.today()
        popped = {}
        for name, clash in self.clashes.items():
            if curr_date > clash.date:
                popped[name] = clash

        for name in popped:
            self.clashes.pop(name)
            self.players.pop(name)

        self.dump_to_json(clash_flag=True)
        return popped

    def dump_to_json(self, clash_flag=False, player_flag=False):
        if clash_flag:
            with open(os.path.join(self.path, "../clash/clash.json"), "w") as f:
                dump_dict = {}
                for name, clash in self.clashes.items():
                    dump_dict[name] = list(clash.__dict__.values())

                json.dump(dump_dict, f, indent=4, default=serialize)
        if player_flag:
            with open(os.path.join(self.path, "clash/players.json"), "w") as f:
                json.dump(self.players, f, indent=4, default=serialize)

    def add_clash(self, clash: Clash):
        self.clashes[clash.name] = clash

        self.dump_to_json(clash_flag=True)

    def remove_clash(self, clash_name: str):
        pop = self.clashes.pop(clash_name)

        self.dump_to_json(clash_flag=True)
        return pop

    # Adds player to its position and additionally puts that into json for readable form
    def register_player(self, clash_name: str, player_name: str, team_role: Position):
        self.players[clash_name][player_name] = team_role

        self.dump_to_json(player_flag=True)

    def unregister_player(self, clash_name: str, player_name: str):
        self.players[clash_name].pop(player_name)

        self.dump_to_json(player_flag=True)


def serialize(obj):
    if isinstance(obj, Position):
        return str(obj)
    if isinstance(obj, datetime.date):
        return str(obj)
    return str(obj)
