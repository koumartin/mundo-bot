import asyncio
import os
import re
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import Dict, List, Optional

import discord as dc
import requests
from bson.binary import Binary
from pymongo import MongoClient

PlaybackStatus = namedtuple("PlaybackStatus", ["playing", "stop"])
SOUND_NAME_REGEX = r"[a-zA-Z0-9.-_]+"
DOWNLOAD_REGEX = r"https://drive\.google\.com/uc\?id=[\w-]+&export=download"
MAX_LENGTH = 16000000


class PlaybackManager:
    def __init__(
        self, client: MongoClient, path: str, voice_clients: List[dc.VoiceClient]
    ) -> None:
        self.client = client
        self.sounds = client.bot.sounds
        self.sounds_data = client.bot.sounds_data
        self.voice_clients = voice_clients
        self.path = path
        self.playback_queue: Dict[int, Queue[PlaybackItem]] = {}
        self.playback_queue_handle: Dict[int, PlaybackStatus] = {}

    async def add_to_queue(
        self,
        guild_id: int,
        channel: dc.VoiceChannel,
        num: int = 1,
        sound_name: Optional[str] = None,
    ) -> None:
        """Addes voice channel to the queue of channels to play sound in.

        Args:
            guild_id (int): Id of guild in which the channel is located.
            channel (dc.VoiceChannel): The channel in which to play sound.
            num (int, optional): Number of times the sound is played. Defaults to 1.
            sound (str, optional): Sound which should be played else mundo sound will be played. Defaults to None.
        """
        if guild_id not in self.playback_queue:
            self.playback_queue[guild_id] = Queue()

        # Put channel to a music queue
        for _ in range(num):
            self.playback_queue[guild_id].put(channel)

        if guild_id not in self.playback_queue_handle:
            self.playback_queue_handle[guild_id] = (False, False)

        # If queue isn't already handled start handling it
        if self.playback_queue_handle[guild_id][0] is False:
            await self.play_from_queue(guild_id)

    async def shutup(self, guild: dc.Guild):
        """Stops playback for a guild.

        Args:
            guild (dc.Guild): Guild for which the playback should be stopped.
        """
        self.playback_queue_handle[guild] = (True, True)
        self.playback_queue[guild] = Queue()

    async def play_from_queue(self, guild_id: int) -> None:
        """Play sound in next channel of the queue.

        Args:
            guild_id (int): Id of guild in which the playing of sounds is requested.
        """
        # Finds current voice_channel in this guild
        voice_client: dc.VoiceClient = dc.utils.get(
            self.voice_clients, guild_id=guild_id
        )
        i = 0

        while not self.playback_queue[guild_id].empty():
            _, stop = self.playback_queue_handle[guild_id]
            if stop is True:
                self.playback_queue_handle[guild_id] = (False, False)
                return
            else:
                self.playback_queue_handle[guild_id] = (True, False)
            channel = self.playback_queue[guild_id].get()
            i += 1

            # In case bot isn't connected to a voice_channel yet
            if voice_client is None:
                voice_client = await channel.connect()
            # Else first disconnect bot from current channel and than connect it
            else:
                # Wait for current audio to stop playing
                while voice_client.is_playing():
                    await asyncio.sleep(0.1)
                await voice_client.move_to(channel)

            if i >= 5:
                i = 0
                await self.play_mundo_sound(
                    voice_client, "../assets/mundo-say-name-often.mp3"
                )
            else:
                await self.play_mundo_sound(voice_client, "../assets/muundo.mp3")

            while voice_client.is_playing():
                # Not clean but it iiiis what it iiiis
                await asyncio.sleep(0.1)

        if voice_client.is_connected():
            await voice_client.disconnect()
        self.playback_queue_handle[guild_id] = (False, False)

    async def play_mundo_sound(
        self, voice_client: dc.VoiceClient, file_name: str
    ) -> None:
        """Plays a sound specified by file_name in a VoiceClient.

        Args:
            voice_client (dc.VoiceClient): Voice client to play the sound.
            file_name (str): Name of the sound file.
        """
        audio_path = os.path.join(self.path, file_name)
        voice_client.play(dc.FFmpegPCMAudio(audio_path))

    def download_and_save(self, sound_name: str, guild_id: int, sound_url: str) -> bool:
        # Check if provided sound_name is valid
        if re.match(SOUND_NAME_REGEX, sound_name) is None:
            return False

        # Check if the provided link is direct download link of google
        if re.match(DOWNLOAD_REGEX, sound_url) is None:
            return False
        res = requests.get(sound_url)

        # Check if the request was successful and if the content is audio
        if res.status_code != 200 or res.headers["content-type"] not in (
            "audio/mpeg",
            "audio/mp3",
        ):
            return False

        if res.headers["content-length"] > MAX_LENGTH:
            return False

        if self.save_to_database(sound_name, guild_id, res.content) is False:
            return False

        self.save_to_local_cache(sound_name, guild_id, res.content)
        return True

    def find_sound(self, sound_name: str, guild_id: int) -> str:
        filepath = f"{self.path}/sounds/{guild_id}_{sound_name}.mp3"
        if os.path.exists(filepath):
            return filepath
        return self.transfer_from_database(sound_name, guild_id)

    def save_to_database(self, sound_name: str, guild_id: int, content: bytes) -> bool:
        existing_sound = self.sounds_data.find_one(
            {"name": sound_name, "guild_id": guild_id}
        )
        if existing_sound is not None:
            return False

        res = self.sounds.insert_one({"data": Binary(content)})
        self.sounds_data.index_information(
            {"name": sound_name, "guild_id": guild_id, "sound_id": res.inserted_id}
        )
        return True

    def save_to_local_cache(
        self, sound_name: str, guild_id: int, content: bytes
    ) -> str:
        filepath = f"{self.path}/sounds/{guild_id}_{sound_name}.mp3"
        if not os.path.exists(filepath):
            Path(filepath).write_bytes(content)
            return filepath

    def transfer_from_database(self, sound_name: str, guild_id: int) -> str:
        sound_info = self.sounds_data.find_one(
            {"name": sound_name, "guild_id": guild_id}
        )
        sound = self.sounds.find_one({"_id": sound_info["sound_id"]})

        return self.save_to_local_cache(sound_name, guild_id, sound["data"])


@dataclass
class PlaybackItem:
    channel: dc.VoiceChannel
    sound: int
