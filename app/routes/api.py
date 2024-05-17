import logging
import os
import re
import subprocess
from multiprocessing import Pool
from typing import List, Union
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, HttpUrl, model_validator

from app.models.spotify_types import Album, Artist, Playlist, Track

log = logging.getLogger(__name__)

api_router = APIRouter()

############################## helper functions  ##############################
def _clean_filename(s):
    return re.sub(r'[<>:"/\\|?*]', '', s)

############################### pydantic models ###############################
class SpotifyURL(BaseModel):
    url: str
    resource: str = '' 

    @model_validator(mode='after')
    def clean_url_and_define_resource(self) -> 'SpotifyURL':
        parsed = urlparse(self.url)
        clean_url = urlunparse(parsed._replace(query=''))
        parts = parsed.path.split('/')
        if len(parts) > 2 and parts[1] in ['track', 'album', 'artist', 'playlist']:
            self.resource = parts[1]
        else:
            raise ValueError('Invalid Spotify URL or unrecognized resource type.')
        self.url = clean_url
        return self

    @model_validator(mode='after')
    def validate_resource(self) -> 'SpotifyURL':
        valid_resources = ['track', 'album', 'artist', 'playlist']
        if self.resource not in valid_resources:
            raise ValueError(f'Resource must be one of {valid_resources}')
        return self


class AlbumDownload(BaseModel):
    urls: List[HttpUrl]

############################# download functions ##############################
def _download_albums(album_urls: AlbumDownload):
    with Pool(processes=2) as pool:
        pool.map(_download_album, album_urls)


def _create_m3u8(playlist):
    playlist, tracks = playlist
    m3u8_content = "#EXTM3U\n"
    m3u8_content += f"#SPOTIFY-ID:{playlist['id']}\n"
    m3u8_content += "\n".join([f"{_clean_filename(track.album_name)}/{_clean_filename(track.name)}.mp3" for track in tracks])
    m3u8_path = os.path.join("./music", f"{playlist['name']}.m3u8")

    with open(m3u8_path, "w") as m3u8_file:
        m3u8_file.write(m3u8_content)

    return playlist['name'], m3u8_path


def _download_album(url_or_album: Union[str, Album]):
    if isinstance(url_or_album, str):
        url = url_or_album
        album = Album.get_metadata(url)
    else:
        album = url_or_album
        url = album[0]['url']
    try:
        name = _clean_filename(album[0]['name'])
        base_dir = "./music"
        album_dir = os.path.join(base_dir, name)
        os.makedirs(album_dir, exist_ok=True)
        spotdl_file = re.sub(r'[^\w\-_\.]', '', name.replace(' ', '')) + '.spotdl'
        command = f"spotdl sync {url} --save-file {spotdl_file}".split()
        result = subprocess.run(command, cwd=album_dir, text=True, capture_output=True)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)
        log.info(f"Downloaded {name} from {url}")
    except Exception as e:
        log.error(f"{type(e)} Error downloading {url}: {e}")


def _download(data, resource):
    match resource:
        case "album":
            _download_album(data)
        case "artist":
            _download_albums(data[0]['albums'])
        case "playlist":
            _download_albums(data[0]['albums'])
            _create_m3u8(data)
        case "track":
            _download_album(data["album_url"])

################################## endpoints ##################################
@api_router.get("/query/", summary="Retrieve Spotify content metadata based on URL")
async def query(spotify_url: SpotifyURL = Depends()):
    url_str = str(spotify_url.url)
    resource = spotify_url.resource
    metadata_func = {'album': Album, 'artist': Artist, 'playlist': Playlist, 'track': Track}.get(resource)

    if not metadata_func:
        log.error(f"Unsupported Spotify content type from URL: {url_str}")
        raise HTTPException(status_code=400, detail="Unsupported Spotify content type")

    try:
        metadata = metadata_func.get_metadata(url_str)
    except Exception as e:
        log.error(f"Failed to fetch metadata for {url_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metadata: {str(e)}")

    return {"resource": resource, "data": metadata}


@api_router.get("/download/", summary="Download Spotify content based on URL")
async def download(background_tasks: BackgroundTasks, spotify_url: SpotifyURL = Depends()):
    url_str = str(spotify_url.url)
    resource = spotify_url.resource
    metadata_func = {'album': Album, 'artist': Artist, 'playlist': Playlist, 'track': Track}.get(resource)
    
    if not metadata_func:
        raise HTTPException(status_code=400, detail="Invalid Spotify type")
    
    try:
        data = metadata_func.get_metadata(url_str)
    except Exception as e:
        log.error(f"Error fetching metadata for {url_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metadata: {str(e)}")

    try:
        background_tasks.add_task(_download, data, resource)
    except Exception as e:
        log.error(f"Error scheduling download task for {url_str}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule download task: {str(e)}")

    return {"resource": resource, "data": data}