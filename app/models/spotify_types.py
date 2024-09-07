from ..context import logger
from typing import Any, Dict, List, Tuple
from spotdl import SpotifyClient
from spotdl.types.album import Album as Album_
from spotdl.types.artist import Artist as Artist_
from spotdl.types.playlist import Playlist as Playlist_
from spotdl.types.song import Song

__all__ = ["Album", "Artist", "Playlist", "Track"]

_client_id = _os.getenv("SPOTIFY_ID")
_client_secret = _os.getenv("SPOTIFY_SECRET")
_spotify = _SpotifyClient.init(client_id=_client_id, client_secret=_client_secret)

_d=["album_name", "name", "year", "artists", "duration", "song_id", "album_id",]
def _filter_song_attributes(songs, attributes=_d):
    if len(attributes) == 0:
        return list(songs)
    filtered_songs = [
        {attr: obj.__dict__[attr] for attr in attributes if attr in obj.__dict__}
        for obj in songs
    ]
    return filtered_songs

def _duration(songs: _List[_Dict[str, _Any]]) -> str:
    total_duration = sum(song.duration for song in songs)
    return total_duration

class Album(_Album):
    @staticmethod
    def get_metadata(url: str, attributes=_d) -> _Tuple[_Dict[str, _Any], _List[_Song]]:
        metadata, songs = _Album.get_metadata(url)
        metadata.update(_spotify.album(url))
        metadata["total_duration"] = _duration(songs)
        metadata["tracks"] = len(songs)
        return metadata, _filter_song_attributes(songs, attributes=attributes)


class Artist(_Artist):
    @staticmethod
    def get_metadata(url: str, attributes=_d) -> _Tuple[_Dict[str, _Any], _List[_Song]]:
        metadata, songs = _Artist.get_metadata(url)
        metadata.update(_spotify.artist(url))
        metadata["total_duration"] = _duration(songs)
        metadata["tracks"] = len(songs)
        return metadata, _filter_song_attributes(songs, attributes=attributes)


class Playlist(_Playlist):
    @staticmethod
    def get_metadata(url: str):
        metadata, songs = Playlist_.get_metadata(url)
        metadata.update(spotify.playlist(url))
        unique_song_ids = set(song.song_id for song in songs)
        return metadata, songs, unique_song_ids


class Track(_Song):
    @staticmethod
    def get_metadata(url): 
        song = Song.from_url(url)
        metadata = spotify.track(url)
        return metadata, song
