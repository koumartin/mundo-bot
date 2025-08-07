import discord as dc
from discord.ext import commands

from .minecraft_player_watch import MinecraftPlayerWatch


class MundobotMc(commands.Bot):
    
    def __init__(self, bot_token: str):
        intents: dc.Intents = dc.Intents.default()
        commands.Bot.__init__(self, command_prefix="!", intents=intents)
        self.token = bot_token
        
    def set_config(self, discord_channel_name: str, log_file_path: str) -> None:
        """Sets the configuration for the bot, including the Discord channel name and log file path."""
        self.discord_channel_name = discord_channel_name
        self.log_file_path = log_file_path
        self.player_logged_in_watcher = MinecraftPlayerWatch(self, log_file_path)
        
    def start_running(self) -> None:
        """Commands the bot to log in and start running using its api token."""
        self.player_logged_in_watcher.start_watching()
        self.run(self.token)

    def start_running_managed(self):
        self.player_logged_in_watcher.start_watching()
        self.run(self.token)
        
    def player_logged_in_callback(self, player_name: str) -> None:
        self.send_player_logged_in(player_name)
        
    def send_player_logged_in(self, player_name: str) -> None:
        for guild in self.guilds:
            channel = [channel for channel in guild.text_channels if channel.name == self.discord_channel_name]
            for channel in channel:
                channel.send(f"Právě se připojil {player_name}. Everyone, get in here! Jdeme kopat.")