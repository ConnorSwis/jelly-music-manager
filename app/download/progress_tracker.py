from spotdl.types.album import Album
from spotdl.download.progress_handler import SongTracker
from threading import Lock
from typing import Callable, Optional
from dataclasses import dataclass
import logging


progress_trackers: list["ProgressTrackerType"] = []
progress_lock = Lock()
logger = logging.getLogger("master")


def get_progress_trackers_state():
    """
    Safely retrieves a ProgressTracker from the global progress_trackers dictionary.
    """
    with progress_lock:
        for tracker in progress_trackers:
            if tracker.tracker.progress == 100:
                progress_trackers.remove(tracker)
        return [{"tracker_id": tracker.id, "name": tracker.name, "image_url": tracker.image_url, "progress": tracker.tracker.progress} for tracker in progress_trackers]


@dataclass
class ProgressTrackerType:
    id: str
    name: str
    image_url: str
    tracker: "ProgressTracker"


class ProgressTracker:
    """
    Class to track the overall progress of downloading albums and songs.
    """

    def __init__(
        self,
        tracker_id: str,
        total_albums: int,
        image_url: Optional[str] = None,
        name: Optional[str] = None,
        on_start_album: Optional[Callable[[Album], None]] = None,
        on_update: Optional[Callable[[SongTracker, str], None]] = None,
        on_finish: Optional[Callable[[], None]] = None
    ):
        self.tracker_id = tracker_id
        self.total_albums = total_albums
        self.current_album_index = 0
        self.total_songs = 0
        self.completed_songs = 0
        self.current_album = None
        self.lock = Lock()

        with progress_lock:
            if any(tracker.id == tracker_id for tracker in progress_trackers):
                self = None
                return
            progress_trackers.append(ProgressTrackerType(id=tracker_id,
                                                         name=name, image_url=image_url, tracker=self))

        self.on_start_album = on_start_album
        self.on_update = on_update
        self.on_finish = on_finish

    def start_new_album(self, album: Album):
        with self.lock:
            self.current_album = album
            self.total_songs = len(album.songs)
            self.current_album_index += 1
            self.completed_songs = 0

        if getattr(self, "on_start_album", None):
            self.on_start_album(album)

    def update(self, song_tracker: SongTracker, status: str):
        with self.lock:
            if status == "Done" or status == "Skipped":
                self.completed_songs += 1

        if getattr(self, "on_update", None):
            self.on_update(song_tracker, status)

    def finish(self):
        logger.info(f"Finished {self.tracker_id}")
        with progress_lock:
            if self.tracker_id in progress_trackers:
                del progress_trackers[self.tracker_id]

        if getattr(self, "on_finish", None):
            self.on_finish()

    @property
    def progress(self) -> float:
        with self.lock:
            if self.current_album is None:
                return 0.0
            else:
                album_progress = (self.current_album_index - 1) / \
                    self.total_albums * 100
                current_album_song_progress = (
                    self.completed_songs / len(self.current_album.songs)) * (1 / self.total_albums) * 100

                return round(album_progress + current_album_song_progress, 2)
