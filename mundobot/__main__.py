"""Main entry point for usual MundoBot usage utilizing environment variables for configuration."""
import asyncio
import os
from urllib.parse import quote_plus

import dotenv

from mundobot.mundobot import MundoBot

dotenv.load_dotenv()

bot_token = os.environ.get("botToken")

# Resolving connection to database
username = os.environ.get("mongoUsername")
password = os.environ.get("mongoPassword")
mongodb = os.environ.get("mongodb")
if mongodb == "Docker":
    docker_container = os.environ.get("dockerContainer")
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
    connection_string = os.environ.get("mongodbConnectionString")
else:
    connection_string = (
        f"mongodb://{quote_plus(username)}:{quote_plus(password)}@localhost:27017"
    )

bot = MundoBot(bot_token, connection_string)
bot.start_running()
