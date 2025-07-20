from bson import ObjectId
from mundobot.clash.position import Position, ClashPositions
from dacite import from_dict, config

dictionary = {
    "clash_id": ObjectId(),
    "players": [{"player_id": 1, "player_name": "name", "position": "MID"}],
}

x = Position["MID"]
print(x)

from_dict(
    ClashPositions,
    dictionary,
    config.Config(type_hooks={Position: lambda x: Position[x]}),
)
