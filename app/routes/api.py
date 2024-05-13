from multiprocessing import Pool
from typing import Tuple
from urllib.parse import urlparse, urlunparse
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from fastapi import BackgroundTasks, HTTPException, Query, APIRouter
from app.models.spotify_types import Playlist, Track, Artist, Album
import logging

log = logging.getLogger(__name__)

api_router = APIRouter()


def validate_url(url) -> Tuple[str, str | bool]:
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return "INVALID_URL", False
        sanitized_url = urlunparse(parsed_url._replace(query=""))
        if parsed_url.netloc == "open.spotify.com":
            valid_paths = {"album", "artist", "track", "playlist"}
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) == 2 and path_parts[0] in valid_paths:
                return sanitized_url, path_parts[0]
            else:
                return "INCORRECT_SPOTIFY_TYPE", False
        else:
            return "INVALID_SPOTIFY_URL.", False
    except Exception as e:
        return f"INVALID_URL", False


def download_albums(album_urls):
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(download_album, album_urls))

    # Use multiprocessing instead
    with Pool(processes=2) as pool:
        pool.map(download_album, album_urls)


def playlist_to_m3u8(playlist: Playlist):
    # return playlist.playlist_name, "\n".join([f"{track.artist_name} - {track.name}" for track in playlist[1]])
    print('ooga')
    return ...


def download_album(url_or_album: str | object):
    if isinstance(url_or_album, str):
        url = url_or_album
        album = Album.get_metadata(url)[1][0]
    else:
        album = url_or_album
    try:
        name = re.sub(r'[<>:"/\\|?*]', '', album.album_name)
        base_dir = "./albums"
        album_dir = os.path.join(base_dir, name)
        os.makedirs(album_dir, exist_ok=True)
        command = f"spotdl sync {url} --save-file '{name}.spotdl'".split()
        result = subprocess.run(command, cwd=album_dir,
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        return result.stdout
    except Exception as e:
        log.error(f"Error downloading {url}: {str(e)}")


@api_router.get("/query/")
async def query(url: str = Query(..., description="The search query")):
    url, valid = validate_url(url)
    if not valid:
        raise HTTPException(status_code=400, detail=url)
    return {'album': Album, 'artist': Artist, 'playlist': Playlist,
            'track': Track}[valid].get_metadata(url)


def download(data_and_type):
    data, valid = data_and_type
    match valid:
        case "album":
            download_album(data[0]["url"])
        case "artist":
            albums = data[0]['albums']
            download_albums(albums)
        case "playlist":
            name, m3u8 = playlist_to_m3u8(data)
            with open(f"{name}.m3u8", "w") as f:
                f.write(m3u8)
            download_albums(data[1])
        case "track":
            download_album(data["album_url"])


@api_router.get("/download/")
async def download_endpoint(background_tasks: BackgroundTasks, url: str = Query(None)):
    url, valid = validate_url(url)
    if not valid:
        raise HTTPException(status_code=400, detail=url)
    data = {'album': Album, 'artist': Artist, 'playlist': Playlist,
            'track': Track}[valid].get_metadata(url)

    background_tasks.add_task(download, (data, valid))
    return data
    # match valid:
    #     case "album":
    #         album = Album.get_metadata(url)
    #         background_tasks.add_task(download_album, url)

    #     case "artist":
    #         albums = Artist.get_metadata(url)[0]['albums']
    #         background_tasks.add_task(download_albums, albums)

    #     case "playlist":
    #         playlist = Playlist.get_metadata(url)
    #         albums = [
    #             'https://open.spotify.com/album/{}'.format(track.album_id) for track in playlist[1]]
    #         background_tasks.add_task(download_albums, albums)

    #     case "track":
    #         track = Track.get_metadata(url)
    #         url = 'https://open.spotify.com/album/{}'.format(track.album_id)
    #         background_tasks.add_task(download_album, url)

    #     case _:
    #         raise HTTPException(status_code=400, detail="Not implemented")
