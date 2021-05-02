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
        if e == "adc" or e == "bot" or e == "bottom":
            return Positions.ADC
        if e == "sup" or e == "supp" or e == "support":
            return Positions.SUPPORT
        if e == "jun" or e == "jung" or e == "jungler":
            return Positions.JUNGLE
        if e == "mid" or e == "middle":
            return Positions.MID
        if e == "top" or e == "top-1":
            return Positions.TOP
        if e == "fill" or e == "👍":
            return Positions.FILL
        if e == "👎":
            return Positions.NOOB

    @staticmethod
    def accepted_reactions():
        return ["adc", "sup", "jung", "fill", "top", "mid", "top-1", "👍", "👎", "bot", "supp", "jun",
                                   "middle", "support", "jungle", "bottom", "jungler"]