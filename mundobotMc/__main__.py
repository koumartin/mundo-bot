import os
import dotenv
from .mundobotMc import MundobotMc


dotenv.load_dotenv()

bot_token = os.environ.get("botToken")
discord_channel_name = os.environ.get("mcAnnouncementsDiscordChannelName")
log_file_path = os.environ.get("logFilePath")

bot = MundobotMc(bot_token)
bot.set_config(discord_channel_name, log_file_path)

bot.start_running_managed()
