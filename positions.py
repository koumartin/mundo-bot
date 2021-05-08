import enum


class Positions(enum.Enum):
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
            return Positions.ADC
        if e in ["sup", "supp", "support"]:
            return Positions.SUPPORT
        if e in ["jun", "jung", "jungler"]:
            return Positions.JUNGLE
        if e in ["mid", "middle"]:
            return Positions.MID
        if e in ["top", "top-1"]:
            return Positions.TOP
        if e in ["fill", "👍"]:
            return Positions.FILL
        if e in ["👎"]:
            return Positions.NOOB

    @staticmethod
    def accepted_reactions():
        return ["adc", "sup", "jung", "fill", "top", "mid", "top-1", "👍", "👎", "bot", "supp", "jun",
                                   "middle", "support", "jungle", "bottom", "jungler"]