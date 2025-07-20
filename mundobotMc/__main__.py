import os
import dotenv
from .mundobotMc import MundobotMc


dotenv.load_dotenv()

bot_token = os.environ.get("botToken")

bot = MundobotMc(bot_token)

bot.start_running_managed()
