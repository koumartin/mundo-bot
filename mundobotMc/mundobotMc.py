import discord as dc
from discord.ext import commands


class MundobotMc(commands.Bot):
    
    def __init__(self, bot_token: str):
        intents: dc.Intents = dc.Intents.default()
        commands.Bot.__init__(self, command_prefix="!", intents=intents)
        self.token = bot_token
        
    def start_running(self) -> None:
        """Commands the bot to log in and start running using its api token."""
        self.run(self.token)

    def start_running_managed(self):
        self.run(self.token)