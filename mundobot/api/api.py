import asyncio
from typing import List

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
import uvicorn

from mundobot.mundobot import MundoBot
from .api_login import LoginRouter, get_current_user_depends


class MundoBotApi:
    def __init__(self, bot: MundoBot):
        self.bot = bot
        self.app = FastAPI()
        self.app_login = LoginRouter()
        self.app.include_router(self.app_login.router)

        @self.app.get("/")
        async def root(user: get_current_user_depends) -> str:
            print(user)
            return "Hello, world." + user.discord_user_id

        @self.app.get('/sounds/list')
        async def list_sounds(guild_id: str) -> List[str]:
            ...

        @self.app.post('/sounds/create')
        async def create_sound() -> str:
            ...

        @self.app.get('/sounds/{sound_name}')
        async def get_sound(guild_id: str, sound_name: str) -> FileResponse:
            ...

        @self.app.delete('/sounds/{sound_name}')
        async def delete_sound(sound_name: str) -> bool:
            ...

        @self.app.get('/available-guilds')
        async def available_guilds() -> List[int]:
            return [x for x in map(lambda x: x.id, self.bot.guilds)]


def start_server(app: FastAPI, loop: asyncio.AbstractEventLoop):
    config = uvicorn.Config(app, loop=loop)
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())

