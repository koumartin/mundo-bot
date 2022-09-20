"""Module containing playback related classes of PlaybackManager and PlaybackItem."""
import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from typing import Dict, List, Optional

import discord as dc
import requests
from bson.binary import Binary
from pymongo import MongoClient


@dataclass
class PlaybackItem:
    """Dataclass containing playback queue values."""

    channel: dc.VoiceChannel
    sound: str


@dataclass
class PlaybackStatus:
    """Dataclass containing guild playback status values."""

    playing: bool
    stop: bool


SOUND_NAME_REGEX = r"[a-zA-Z0-9.-_]+"
DOWNLOAD_REGEX = r"https:\/\/drive\.google\.com\/uc\?((id=[\w-]+)|(export=download))&((id=[\w-]+)|(export=download))"
MAX_LENGTH = 16000000
COMMON_SOUNDS = ["mundo", "hello-there", "badumtss", "mundo-say-name-often"]
DISPLAYED_COMMON_SOUNDS = ["mundo", "hello-there", "badumtss"]


class PlaybackManager:
    """Class responsible for downloading, caching and playing sounds in VoiceClients."""

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
        sound_name: str,
        num: int = 1,
    ) -> None:
        """Addes voice channel to the queue of channels to play sound in.

        Args:
            guild_id (int): Id of guild in which the channel is located.
            channel (dc.VoiceChannel): The channel in which to play sound.
            sound (str, optional): Sound which should be played.
            num (int, optional): Number of times the sound is played. Defaults to 1.
        """
        if guild_id not in self.playback_queue:
            self.playback_queue[guild_id] = Queue()

        # Put channel to a music queue
        for _ in range(num):
            self.playback_queue[guild_id].put(PlaybackItem(channel, sound_name))

        if guild_id not in self.playback_queue_handle:
            self.playback_queue_handle[guild_id] = PlaybackStatus(False, False)

        # If queue isn't already handled start handling it
        if self.playback_queue_handle[guild_id].playing is False:
            await self.play_from_queue(guild_id)

    async def shutup(self, guild: dc.Guild):
        """Stops playback for a guild.

        Args:
            guild (dc.Guild): Guild for which the playback should be stopped.
        """
        self.playback_queue_handle[guild] = PlaybackStatus(True, True)
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
        mundo_repetitions = 0

        while not self.playback_queue[guild_id].empty():
            status = self.playback_queue_handle[guild_id]
            if status.stop is True:
                self.playback_queue_handle[guild_id] = PlaybackStatus(False, False)
                return
            else:
                self.playback_queue_handle[guild_id] = PlaybackStatus(True, False)

            playback_item = self.playback_queue[guild_id].get()
            mundo_repetitions = (
                mundo_repetitions + 1 if playback_item.sound == "mundo" else 0
            )

            # In case bot isn't connected to a voice_channel yet
            if voice_client is None:
                voice_client = await playback_item.channel.connect()
            # Else first disconnect bot from current channel and than connect it
            else:
                # Wait for current audio to stop playing
                while voice_client.is_playing():
                    await asyncio.sleep(0.1)
                await voice_client.move_to(playback_item.channel)

            if mundo_repetitions >= 5:
                mundo_repetitions = 0
                await self.play_sound(voice_client, "mundo-say-name-often", guild_id)
            else:
                await self.play_sound(voice_client, playback_item.sound, guild_id)

            while voice_client.is_playing():
                # Not clean but it iiiis what it iiiis
                await asyncio.sleep(0.1)

        if voice_client.is_connected():
            await voice_client.disconnect()
        self.playback_queue_handle[guild_id] = PlaybackStatus(False, False)

    async def play_sound(
        self, voice_client: dc.VoiceClient, sound_name: str, guild_id: int
    ) -> None:
        """Plays a sound specified by file_name in a VoiceClient.

        Args:
            voice_client (dc.VoiceClient): Voice client to play the sound.
            file_name (str): Name of the sound file.
        """
        path = self.find_sound(sound_name, guild_id)
        voice_client.play(dc.FFmpegPCMAudio(str(path)))

    def download_and_save(self, sound_name: str, guild_id: int, sound_url: str) -> bool:
        """Downloads a sound from google drive using direct download link
        and saves it to database and local sound cache.

        Args:
            sound_name (str): Name of the sound unique in the guild.
            guild_id (int): Id of the guild.
            sound_url (str): Url of the direct download link.

        Returns:
            bool: Success of the operation.
        """
        # Check if provided sound_name is valid
        if (
            re.match(SOUND_NAME_REGEX, sound_name) is None
            or sound_name in COMMON_SOUNDS
        ):
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

        if int(res.headers["content-length"]) > MAX_LENGTH:
            return False

        # if self.save_to_database(sound_name, guild_id, res.content) is False:
        #     return False

        self.save_to_local_cache(sound_name, guild_id, res.content)
        return True

    def find_sound(
        self, sound_name: str, guild_id: int, transfer: bool = True
    ) -> Optional[Path]:
        """Finds path of the sound file either in assets or in local cache.

        Args:
            sound_name (str): Name of the sound.
            guild_id (int): Id of the guild.
            transfer (bool): Flag to indicat if the sound should be
            loaded from database if not found. Defaults to True.

        Returns:
            Path: File path of the sound.
        """
        if sound_name in COMMON_SOUNDS:
            filepath = f"{self.path}/default_sounds/{sound_name}.mp3"
        else:
            filepath = f"{self.path}/sounds/{guild_id}_{sound_name}.mp3"

        path = Path(filepath)
        if path.exists():
            return path
        return self.transfer_from_database(sound_name, guild_id) if transfer else None

    def save_to_database(self, sound_name: str, guild_id: int, content: bytes) -> bool:
        """Saves a sound binary file to the database.

        Args:
            sound_name (str): Name of the sound unique for the guild.
            guild_id (int): Id of the guild.
            content (bytes): Binary content of the sound file.

        Returns:
            bool: Success of the operation.
        """
        existing_sound = self.sounds_data.find_one(
            {"name": sound_name, "guild_id": guild_id}
        )
        if existing_sound is not None:
            return False

        res = self.sounds.insert_one({"data": Binary(content)})
        self.sounds_data.insert_one(
            {"name": sound_name, "guild_id": guild_id, "sound_id": res.inserted_id}
        )
        return True

    def save_to_local_cache(
        self, sound_name: str, guild_id: int, content: bytes
    ) -> Path:
        """Saves a sound binary file to local sound cache.

        Args:
            sound_name (str): Name of the sound unique for the guild.
            guild_id (int): Id of the guild.
            content (bytes): Binary content of the sound file.

        Returns:
            Path: Path of the saved cached sound.
        """
        filepath = f"{self.path}/sounds/{guild_id}_{sound_name}.mp3"
        path = Path(filepath)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        return path

    def transfer_from_database(self, sound_name: str, guild_id: int) -> Path:
        """Transferes sound from database to local cache storage.

        Args:
            sound_name (str): Name of the sound.
            guild_id (int): Id of the guild.

        Returns:
            Path: Path of the saved cached sound.
        """
        sound_info = self.sounds_data.find_one(
            {"name": sound_name, "guild_id": guild_id}
        )
        sound = self.sounds.find_one({"_id": sound_info["sound_id"]})

        return self.save_to_local_cache(sound_name, guild_id, sound["data"])

    def delete_sound(self, sound_name: str, guild_id: int) -> None:
        """Deletes a sound from database and local cache.

        Args:
            sound_name (str): Name of the sound.
            guild_id (int): Id of the guild.
        """
        if sound_name in COMMON_SOUNDS:
            return

        res = self.sounds_data.find_one_and_delete(
            {"guild_id": guild_id, "name": sound_name}
        )
        if res is not None:
            self.sounds.delete_one({"_id": res["sound_id"]})

        sound_path = self.find_sound(sound_name, guild_id, False)
        if sound_path is not None:
            sound_path.unlink()

    def list_sounds_for_guild(self, guild_id: int) -> str:
        """Lists all sounds available for a server.

        Args:
            guild_id (int): Id of the guild.

        Returns:
            str: String containing names of all available sound names.
        """
        sound_names = [
            info["name"] for info in self.sounds_data.find({"guild_id": guild_id})
        ]
        return "\n".join(["  ".join(DISPLAYED_COMMON_SOUNDS), "  ".join(sound_names)])
