from typing import List

from fastapi import APIRouter, UploadFile, HTTPException
from starlette import status
from starlette.responses import FileResponse

from .dependencies import get_selected_guild_depends
from .dtos.SoundDto import SoundDto
from ..mundobot import MundoBot
from ..playback import MAX_LENGTH


class SoundsRouter:
    def __init__(self, bot: MundoBot):
        self.bot = bot
        self.router = APIRouter(prefix='/sounds', tags=['sounds'])
        self.add_endpoints()

    # TODO: Apply
    def verify_guild_access(self, guild_id: int, user_id: int) -> None:
        guild = self.bot.get_guild(guild_id)
        if guild is None or guild.get_member(user_id) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User does not have access to this guild')

    def add_endpoints(self):
        @self.router.get('/list')
        async def list_sounds(guild_id: get_selected_guild_depends) -> List[SoundDto]:
            default_sounds, guild_sounds = self.bot.playback_manager.list_sounds_for_guild(guild_id)
            return [SoundDto(name=sound, default=True) for sound in default_sounds] + [SoundDto(name=sound, default=False) for sound in guild_sounds]

        @self.router.get('/{name}', responses={200: {'content': {'audio/mp3': {}}, 'description': 'Requested audio file'}})
        async def get_sound(name: str, guild_id: get_selected_guild_depends) -> FileResponse:
            file_path = self.bot.playback_manager.find_sound(name, guild_id)
            if file_path is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Sound not found')
            return FileResponse(file_path, media_type='audio/mp3', filename=name)

        @self.router.post('/create')
        async def create_sound(name: str, file: UploadFile, guild_id: get_selected_guild_depends) -> SoundDto:
            if file.size > MAX_LENGTH:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File too large')

            self.bot.playback_manager.save_to_local_cache(name, guild_id, await file.read())
            self.bot.playback_manager.save_to_database(name, guild_id, await file.read())
            return SoundDto(name=name, default=False)

        @self.router.delete('/{name}')
        async def delete_sound(name: str, guild_id: get_selected_guild_depends) -> None:
            self.bot.playback_manager.delete_sound(name, guild_id)
