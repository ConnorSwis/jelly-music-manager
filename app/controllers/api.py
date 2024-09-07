from fastapi import HTTPException, BackgroundTasks, Request

from ..models.spotify_types import Playlist, Track, Artist, Album
from ..download import download, validate_url, get_progress_trackers_state
from fastapi.templating import Jinja2Templates as Jinja2Templates_
from collections import defaultdict
from typing import Dict, List
from spotdl.types.song import Song
from spotdl.types.artist import Artist as Artist_
from datetime import datetime

import logging
import threading


class Jinja2Templates(Jinja2Templates_):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_initialized'):
            super().__init__(*args, **kwargs)
            self._initialized = True


__all__ = ["controller"]

logger = logging.getLogger("master")
templates = Jinja2Templates(directory="app/templates")


def get_metadata(url: str, type_: str):
    return {
        "album": Album,
        "artist": Artist,
        "playlist": Playlist,
        "track": Track,
    }[type_].get_metadata(url)


def jinja_env(func):
    templates.env.filters[func.__name__] = func

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@jinja_env
def format_duration_ms(value):
    value = int(value) // 1000
    hours, remainder = divmod(value, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    elif minutes:
        return f"{minutes}:{seconds:02}"
    else:
        return f"0:{seconds:02}"


@jinja_env
def comma_separated(value: int):
    return f"{value:,}"


@jinja_env
def songs_by_album(songs: List[Song]):
    album_dict: Dict[str, List[Song]] = defaultdict(list)
    for song in songs:
        album_dict[song.album_id].append(song)
    result = []
    for album_id, album_songs in album_dict.items():
        if album_songs:
            album_info = {
                "artist": album_songs[0].album_artist,
                "artist_id": album_songs[0].artist_id,
                "tracks_count": album_songs[0].tracks_count,
                "year": album_songs[0].year,
                "cover_url": album_songs[0].cover_url,
                "id": album_id,
                "name": album_songs[0].album_name,
                "songs": album_songs,
                "artist_id": album_songs[0].artist_id,
            }
            result.append(album_info)

    return result


@jinja_env
def format_day_and_month(value):
    dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    return dt.strftime('%b %d')


class APIController:
    @staticmethod
    async def query(url: str, request: Request):
        url, valid = validate_url(url)
        if not valid:
            raise HTTPException(status_code=400, detail=url)
        metadata = list(get_metadata(url, valid))

        match valid:
            case "album":
                metadata[1] = metadata[0]["tracks"]["items"]
            case "playlist":
                metadata[1] = [
                    {
                        "added_at": song.get("added_at"),
                        **song.get("track", {})
                    }
                    for song in metadata[0]["tracks"]["items"]
                ]
            case "artist":
                metadata = [metadata[0], Artist_.from_url(url).songs]
            case "track":
                metadata = get_metadata(
                    f"https://open.spotify.com/album/{metadata[1].album_id}", "album")
        return templates.TemplateResponse(
            f"components/{valid}_info.jinja", {"request": request,
                                               valid: metadata[0], "songs": metadata[1]}
        )

    @classmethod
    async def download(cls, url: str, request: Request, background_tasks: BackgroundTasks):
        url, valid = validate_url(url)
        if not valid:
            raise HTTPException(status_code=400, detail=url)
        background_tasks.add_task(download, url, valid)
        return await cls.progress(url=url, request=request)

    @staticmethod
    async def progress(url: str, request: Request):
        url, valid = validate_url(url)
        if not valid:
            raise HTTPException(status_code=400, detail=url)
        progress_trackers = get_progress_trackers_state()
        tracker = None
        for t in progress_trackers:
            logger.info(t["tracker_id"] + " " + url)
            if t['tracker_id'] == url:
                tracker = t
                return templates.TemplateResponse(
                    "components/progress.jinja",
                    {"request": request, "tracker": tracker}
                )
        else:
            return templates.TemplateResponse(
                "components/progress.jinja",
                {"request": request, "tracker_id": url}
            )


controller = APIController()