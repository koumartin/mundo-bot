import os
import re
from threading import Lock
from typing import Callable, TYPE_CHECKING
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

if TYPE_CHECKING:
    from .mundobotMc import MundobotMc

class EventHandler(FileSystemEventHandler):
    def __init__(self, log_file_path: str, player_login_callback: Callable[[str], None]):
        self.log_file_path = log_file_path
        with open(log_file_path, 'r') as f:
            f.seek(0, os.SEEK_END)  # Move to the end of the file
            self.last_position = f.tell() # Store end of the file
        self.player_login_callback = player_login_callback
    
    def on_modified(self, event):
        if event.is_directory or event.src_path != self.log_file_path:
            return
        
        print(self.last_position)
        with open(self.log_file_path, 'r') as f:
            f.seek(self.last_position)  # Move to the end of the file
            for line in f:
                player_name = self.parse_player_login(line)
                if player_name:
                    self.player_login_callback(player_name)
            self.last_position = f.tell()  # Update the last position

    def parse_player_login(self, line: str) -> str | None:
        # [21:06:23] [Server thread/INFO] [minecraft/MinecraftServer]: <player_name> joined the game
        if "joined the game" in line:
            match = re.search(r"]: (\w+) joined the game", line)
            if match:
                print(f"Detected player login: {match.group(1)}")
                return match.group(1)
        return None

class MinecraftPlayerWatch:
    def __init__(self, bot: "MundobotMc", log_file_path: str):
        self.bot = bot
        self.log_file_path = log_file_path
        self.event_queue = deque()
            
        self.event_handler = EventHandler(log_file_path, self.bot.player_logged_in_callback)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, os.path.dirname(log_file_path), recursive=False)              
        
    def start_watching(self):
        print(f"Starting to watch log file: {self.log_file_path}")
        self.observer.start()
        
    def stop_watching(self):
        self.observer.stop()
        self.observer.join()
        