import os
import re
import subprocess
from typing import List, Union
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, HttpUrl, model_validator

from app.models.spotify_types import Album, Artist, Playlist, Track


api_router = APIRouter()

MUSIC_DIR = "music"

if not os.path.exists(MUSIC_DIR):
    os.mkdir(MUSIC_DIR)


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
        self.url = str(clean_url)
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
def _create_m3u8(playlist):
    playlist, tracks = playlist
    m3u8_content = "#EXTM3U\n"
    m3u8_content += f"#SPOTIFY-ID:{playlist['id']}\n"
    m3u8_content += "\n".join([f"{_clean_filename(track['album_name'])}/{_clean_filename(track['name'])}.mp3" for track in tracks])
    m3u8_path = os.path.join(MUSIC_DIR, f"{playlist['name']}.m3u8")

    with open(m3u8_path, "w") as m3u8_file:
        m3u8_file.write(m3u8_content)

    return playlist['name'], m3u8_path


def _download_album(url_or_album: Union[str, Album]):
    url, album = None, None

    if isinstance(url_or_album, str):
        url = url_or_album
        album = Album.get_metadata(url)
    else:
        album = url_or_album
        url = album[0]['url']

    try:
        name = _clean_filename(album[0]['name'])
        album_dir = os.path.join(MUSIC_DIR, name)
        os.makedirs(album_dir, exist_ok=True)
        spotdl_file = re.sub(r'[^\w\-_\.]', '', name.replace(' ', '')) + '.spotdl'
        command = ["spotdl", "sync", url, "--save-file", spotdl_file]
        process = subprocess.Popen(command, cwd=album_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode('utf-8')
            raise HTTPException(status_code=500, detail=f"Download failed for album '{name}' from '{url}': {error_message}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download album '{name}' from '{url}': {str(e)}")


def _download(data, background_tasks: BackgroundTasks):
    resource = data["resource"]
    data = data["data"]
    if resource == "album":
        background_tasks.add_task(_download_album, data)
    elif resource == "artist":
        for album in data[0]['albums']:
            background_tasks.add_task(_download_album, album)
    elif resource == "playlist":
        _create_m3u8(data)
        for album in data[0]['albums']:
            background_tasks.add_task(_download_album, album)
    elif resource == "track":
        background_tasks.add_task(_download_album, data["album_url"])
    return data


################################# controller #################################
class SpotifyController:
    @staticmethod
    def query(spotify_url: SpotifyURL):
        url = spotify_url.url
        resource = spotify_url.resource
        
        DataClass = {'album': Album, 'artist': Artist, 'playlist': Playlist, 'track': Track}.get(resource)
        if not DataClass:
            raise HTTPException(status_code=400, detail="Unsupported Spotify content type")
        try:
            data = DataClass.get_metadata(url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch metadata: {str(e)}")

        if resource == 'track':
            resource = 'album'
        return {"resource": resource, "data": data}
    
    @classmethod
    def download(cls, spotify_url: SpotifyURL, background_tasks: BackgroundTasks):
        query = cls.query(spotify_url)
        _download(query, background_tasks)
        return query


################################## endpoints ##################################
@api_router.get("/query/", summary="Retrieve Spotify content metadata based on URL")
async def query(spotify_url: SpotifyURL = Depends()):
    return SpotifyController.query(spotify_url)

@api_router.get("/download/", summary="Download content based on Spotify URL")
async def download(background_tasks: BackgroundTasks, spotify_url: SpotifyURL = Depends()):
    return SpotifyController.download(spotify_url, background_tasks)
