"""Main entry point for usual MundoBot usage utilizing environment variables for configuration."""
import asyncio
import os
from urllib.parse import quote_plus

import dotenv

from mundobot.mundobot import MundoBot
from mundobot.api.api import start_server, MundoBotApi

dotenv.load_dotenv()

bot_token = os.environ.get("BOT_TOKEN")

# Resolving connection to database
username = os.environ.get("MONGO_USERNAME")
password = os.environ.get("MONGO_PASSWORD")
mongodb = os.environ.get("MONGODB")
if mongodb == "Docker":
    docker_container = os.environ.get("DOCKER_CONTAINER")
    if docker_container:
        connection_string = (
            f"{quote_plus(docker_container)}://{quote_plus(username)}"
            + ":{quote_plus(password)}@mongodb:27017"
        )
    else:
        connection_string = (
            f"mongodb://{quote_plus(username)}:{quote_plus(password)}@mongodb:27017"
        )
elif mongodb == "External":
    connection_string = os.environ.get("MONGO_CONNECTION_STRING")
else:
    connection_string = (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}@localhost:27017"
    )
bot = MundoBot(bot_token, connection_string)
run_api = bool(os.environ.get('RUN_API', 'False'))

if run_api:
    loop = asyncio.new_event_loop()
    api = MundoBotApi(bot)
    asyncio.set_event_loop(loop)
    loop.create_task(bot.start_running())
    start_server(api.app, loop)
else:
    bot.start_running_managed()

