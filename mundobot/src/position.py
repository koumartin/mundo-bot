import enum


class Position(enum.Enum):
    TOP = 1
    JUNGLE = 2
    MID = 3
    BOT = 4
    SUPPORT = 5
    FILL = 6
    NOOB = 7

    def __str__(self):
        return self.name

    @staticmethod
    def get_position(emoji_name: str):
        e = emoji_name.lower()
        if e in ["adc", "bot", "bottom"]:
            return Position.ADC
        if e in ["sup", "supp", "support"]:
            return Position.SUPPORT
        if e in ["jun", "jung", "jungler"]:
            return Position.JUNGLE
        if e in ["mid", "middle"]:
            return Position.MID
        if e in ["top", "top-1"]:
            return Position.TOP
        if e in ["fill", "👍"]:
            return Position.FILL
        if e in ["👎"]:
            return Position.NOOB

    @staticmethod
    def accepted_reactions():
        return ["adc", "sup", "jung", "fill", "top", "mid", "top-1", "👍", "👎", "bot", "supp", "jun",
                "middle", "support", "jungle", "bottom", "jungler"]
