from typing import List

from fastapi import APIRouter, UploadFile
from starlette.responses import FileResponse

from ..mundobot import MundoBot


class SoundsRouter:
    def __init__(self, bot: MundoBot):
        self.bot = bot
        self.router = APIRouter(prefix='/sounds', tags=['sounds'])

        @self.router.get('/list')
        async def list_sounds(guild_id: str) -> List[str]:
            ...

        @self.router.post('/create')
        async def create_sound(guild_id: str, name: str, file: UploadFile) -> str:
            ...

        @self.router.get('/{sound_name}')
        async def get_sound(guild_id: str, sound_name: str) -> FileResponse:
            ...

        @self.router.delete('/{sound_name}')
        async def delete_sound(guild_id: str, sound_name: str) -> bool:
            ...
