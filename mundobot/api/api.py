import asyncio
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.routing import APIRoute

from mundobot.mundobot import MundoBot
from .api_login import LoginRouter, get_current_user_depends
from .api_sounds import SoundsRouter
from .dependencies import get_selected_guild_depends
from .dtos.GuildDto import GuildDto


def get_origins() -> List[str]:
    origins = [
        "http://localhost:3000",
    ] + os.environ.get('API_ORIGINS').split(',')
    return origins


def use_route_names_as_operation_ids(application: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in application.routes:
        if isinstance(route, APIRoute):
            route: APIRoute = route
            route.operation_id = route.name


class MundoBotApi:
    def __init__(self, bot: MundoBot):
        self.bot = bot
        self.app = FastAPI()
        self.app.add_middleware(CORSMiddleware, allow_origins=get_origins(), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

        self.app_login = LoginRouter()
        self.app.include_router(self.app_login.router)
        self.app_sounds = SoundsRouter(bot)
        self.app.include_router(self.app_sounds.router)

        self.add_endpoints()

        use_route_names_as_operation_ids(self.app)

    def add_endpoints(self):
        @self.app.get("/")
        async def root(user: get_current_user_depends, guild_id: get_selected_guild_depends) -> str:
            return f"""Hello, world.
Your id: {user.discord_user_id}
In guild with id: {guild_id}"""

        @self.app.get('/available-guilds', tags=['guilds'])
        async def available_guilds(user: get_current_user_depends) -> List[GuildDto]:
            return [GuildDto(id=str(guild.id), name=guild.name) for guild in self.bot.guilds if guild.get_member(user.discord_user_id) is not None]


def start_server(app: FastAPI, loop: asyncio.AbstractEventLoop):
    config = uvicorn.Config(app, loop=loop, host='0.0.0.0')
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())

