from spotdl import SpotifyClient
from spotdl.types.song import Song
from spotdl.types.album import Album
from spotdl.types.artist import Artist
from spotdl.types.playlist import Playlist
from spotdl.utils.config import create_settings
from spotdl.download.progress_handler import SongTracker
from spotdl.download.downloader import Downloader as Downloader_
from spotdl.types.options import DownloaderOptionalOptions, DownloaderOptions
from spotdl.download.progress_handler import ProgressHandler as ProgressHandler_

from .progress_tracker import ProgressTracker
from .create_arguments import create_arguments
from ..context import get_music_dir, clean

import os
import logging
from pathlib import Path
from asyncio import AbstractEventLoop
from typing import Any, Dict, List, Tuple, Callable, Type, TypeVar, cast
from urllib.parse import urlparse, urlunparse
from dataclasses import dataclass, fields, is_dataclass


logger = logging.getLogger("master")
spotify = SpotifyClient()


class ProgressHandler(ProgressHandler_):
    def __init__(
        self,
        simple_tui: bool = False,
        update_callback: Callable[[Any, str], None] | None = None,
        web_ui: bool = False,
    ):
        super().__init__(simple_tui, update_callback, web_ui)


class Downloader(Downloader_):
    def __init__(
        self,
        settings: DownloaderOptionalOptions | DownloaderOptions | None = None,
        *,
        loop: AbstractEventLoop | None = None,
        update_callback=None,
    ):
        super().__init__(settings, loop)
        self.progress_handler = ProgressHandler(
            settings.get("simple_tui"), update_callback
        )


def get_music_format():
    return os.getenv("MUSIC_FORMAT", "mp3")


def get_album_dir(album_name: str, artist_name: str) -> Path:
    assert isinstance(album_name, str), "album_name should be a string"
    assert isinstance(artist_name, str), "artist_name should be a string"

    album_dir = (
        get_music_dir()
        .joinpath(f"{clean(artist_name)} - {clean(album_name)}")
        .absolute()
    )
    return album_dir


def update_callback(
    song_tracker: SongTracker, status: str, progress_tracker: ProgressTracker
):
    assert isinstance(
        song_tracker, SongTracker
    ), "song_tracker should be an instance of SongTracker"
    assert isinstance(status, str), "status should be a string"
    assert isinstance(
        progress_tracker, ProgressTracker
    ), "progress_tracker should be an instance of ProgressTracker"

    logger.debug("Updating callback for song: "
                 f"{song_tracker.song_name} with status: {status}")
    try:
        progress_tracker.update(song_tracker, status)
    except Exception as e:
        logger.error(f"Failed to update progress tracker: {e}")
        raise


def validate_url(url: str) -> Tuple[str, str | bool]:
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return "INVALID_URL", False

        # Strip the query from the URL
        sanitized_url = urlunparse(parsed_url._replace(query=""))

        if parsed_url.netloc == "open.spotify.com":
            valid_paths = {"album", "artist", "track", "playlist"}
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) == 2 and path_parts[0] in valid_paths:
                return sanitized_url, path_parts[0]
            else:
                return "INCORRECT_SPOTIFY_TYPE", False
        else:
            return "INVALID_SPOTIFY_URL", False
    except Exception as e:
        return "INVALID_URL", False


def download_album(album: Album, progress_tracker: ProgressTracker):
    logger.info(f"Starting download for album: {album}")
    try:
        assert isinstance(album, Album), "album should be an instance of Album"
        if not album.songs:
            logger.error(
                f"Album: {album} does not contain any songs. Skipping download."
            )
            return

        album_dir = get_album_dir(album.name, album.songs[0].artist)
        logger.debug(f"Generated album directory path: {album_dir}")

        if not album_dir.exists():
            logger.info(
                "Album directory does not exist. "
                f"Creating directory: {album_dir}"
            )
            album_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Album directory created: {album_dir}")

        if not os.access(album_dir, os.W_OK):
            logger.error(f"Cannot write to album directory: {album_dir}")
            raise PermissionError(
                f"Cannot write to album directory: {album_dir}")
        progress_tracker.start_new_album(album)

        arguments = create_arguments(
            operation="sync",
            query=[album],
            headless=True,
            output=str(album_dir.joinpath(
                "{track-number} - {title}.{output-ext}")),
            format=get_music_format(),
            save_file=album_dir.joinpath(f"{clean(album.name)}.spotdl"),
            simple_tui=True,
            sync_without_deleting=True,
            log_level="DEBUG",
            overwrite="skip",
            preload=True,
        )

        _, downloader_settings, _ = create_settings(arguments)
        downloader = Downloader(
            downloader_settings,
            update_callback=lambda tracker, status: update_callback(
                tracker, status, progress_tracker
            ),
        )

        downloader.download_multiple_songs(album.songs)
        logger.info(f"Download completed for album: {album.name}")

    except AssertionError as ae:
        logger.error(f"Assertion error: {ae}")
        raise
    except PermissionError as pe:
        logger.error(f"Permission error: {pe}")
        raise
    except Exception as e:
        logger.error(f"Error occurred while downloading album: {e}")
        raise


def download_artist(artist: Artist, progress_tracker: ProgressTracker):
    for album_url in artist.albums:
        album = Album.from_url(album_url)
        download_album(album, progress_tracker)
    progress_tracker.finish()


@dataclass
class _DownloadPlaylist_PlaylistMetadata:
    name: str
    url: str
    description: str
    author_name: str
    author_url: str
    cover_url: str


def download_playlist(
    playlist_metadata: _DownloadPlaylist_PlaylistMetadata, songs: List[Song]
):
    try:
        playlist_metadata = verify_dataclass(
            playlist_metadata, _DownloadPlaylist_PlaylistMetadata
        )
        create_m3u8(playlist_metadata, songs)
        album_ids = {song.album_id for song in songs}
        progress_tracker = ProgressTracker(
            playlist_metadata.url,
            len(album_ids),
            image_url=playlist_metadata.cover_url,
            name=playlist_metadata.name,
        )
        if progress_tracker is None:
            raise Exception("Download already exists")
        for album_id in album_ids:
            album = Album.from_url(
                f"https://open.spotify.com/album/{album_id}")
            download_album(album, progress_tracker)

        progress_tracker.finish()

        logger.debug("Finished downloading playlist.")
    except AssertionError as ae:
        logger.error(f"Assertion error: {ae}")
        raise
    except Exception as e:
        logger.error(f"Failed to download playlist: {e}")
        raise


def download(
    url,
    type_,
):
    match type_:
        case "album":
            download_album_from_url(url)
        case "artist":
            download_artist_from_url(url)
        case "playlist":
            download_playlist_from_url(url)
        case "track":
            song = Song.from_url(url)
            url = "https://open.spotify.com/album/" + song.album_id
            download_album_from_url(url)


@dataclass
class _CreateM3U8PlaylistMetadata:
    name: str
    url: str
    description: str
    author_name: str
    author_url: str
    cover_url: str


def create_m3u8(playlist_metadata: _CreateM3U8PlaylistMetadata, songs: List[Song]):
    logger.debug("Creating m3u8 playlist file.")
    try:

        playlist_metadata = verify_dataclass(
            playlist_metadata, _CreateM3U8PlaylistMetadata
        )

        m3u8_content = []

        m3u8_content.append(f"#EXTM3U")
        m3u8_content.append(f"#PLAYLIST:{clean(playlist_metadata.name)}")
        m3u8_content.append(f"#URL:{playlist_metadata.url}")
        m3u8_content.append(
            f"#DESCRIPTION:{clean(playlist_metadata.description)}")
        m3u8_content.append(f"#AUTHOR:{clean(playlist_metadata.author_name)}")
        m3u8_content.append(f"#AUTHOR_URL:{playlist_metadata.author_url}")
        m3u8_content.append(f"#COVER_URL:{playlist_metadata.cover_url}")
        m3u8_content.append("")

        for song in songs:
            album_dir = get_album_dir(song.album_name, song.artist)
            song_path = album_dir.joinpath(
                f"{song.track_number} - "
                f"{clean(song.name)}.{get_music_format()}"
            )
            m3u8_content.append(
                f"#EXTINF:{song.duration},"
                f"{clean(song.artist)} - {clean(song.name)}"
            )
            m3u8_content.append(str(song_path))
            m3u8_content.append("")

        m3u8_path = get_music_dir().joinpath(
            f"{clean(playlist_metadata.name)} by "
            f"{clean(playlist_metadata.author_name)}.m3u8"
        )
        logger.debug(f"Writing m3u8 content to file: {m3u8_path}")
        m3u8_path.write_text("\n".join(m3u8_content), encoding="utf-8")
        logger.debug(f"m3u8 file created: {m3u8_path}")
    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        raise
    except Exception as e:
        logger.error(f"Failed to create m3u8 file: {e}")
        raise


def download_album_from_url(url):
    album = Album.from_url(url)
    metadata = spotify.album(album.url)
    progress_tracker = ProgressTracker(
        album.url,
        total_albums=1,
        image_url=metadata["images"][0]["url"],
        name=album.name,
    )
    download_album(album, progress_tracker)


def download_artist_from_url(url):
    artist = Artist.from_url(url)
    metadata = spotify.artist(artist.url)
    progress_tracker = ProgressTracker(
        artist.url,
        total_albums=len(artist.albums),
        name=artist.name,
        image_url=metadata["images"][0]["url"],
    )
    download_artist(artist, progress_tracker)


def download_playlist_from_url(url):
    playlist_metadata, songs = Playlist.get_metadata(url)
    logger.info(playlist_metadata)
    download_playlist(playlist_metadata, songs)


_DataclassT = TypeVar("_DataclassT")


def verify_dataclass(obj: Any, dataclass_type: Type[_DataclassT]) -> _DataclassT:
    """
    Verifies that the provided object conforms to the structure of the specified dataclass,
    including any nested dataclasses, and returns an instance of the dataclass with the validated values.

    Args:
        obj: The object to verify.
        dataclass_type: The dataclass type to verify against.

    Returns:
        An instance of the dataclass with values from the provided object.

    Raises:
        ValueError: If the object does not conform to the dataclass structure.
    """
    assert is_dataclass(
        dataclass_type
    ), f"{dataclass_type} is not a dataclass."

    kwargs: Dict[str, Any] = {}

    for field in fields(dataclass_type):
        field_name = field.name
        field_type = field.type
        value = None
        if isinstance(obj, dict):
            value = obj.get(field_name, None)
        elif hasattr(obj, field_name):
            value = getattr(obj, field_name, None)
        assert (
            value is not None
        ), f"Field '{field_name}' is missing in the provided object."

        if is_dataclass(field_type):
            value = verify_dataclass(value, field_type)
        else:
            assert isinstance(
                value, field_type
            ), f"Field '{field_name}' should be of type {field_type} but got {type(value)}."

        kwargs[field_name] = value

    return cast(_DataclassT, dataclass_type(**kwargs))
