from ..context import logger
from typing import Any, Dict, List, Tuple
from spotdl import SpotifyClient
from spotdl.types.album import Album as Album_
from spotdl.types.artist import Artist as Artist_
from spotdl.types.playlist import Playlist as Playlist_
from spotdl.types.song import Song

__all__ = ["Album", "Artist", "Playlist", "Track"]


spotify = SpotifyClient()


class Album(Album_):
    @staticmethod
    def get_metadata(url: str) -> Tuple[Dict[str, Any], List[Song]]:
        metadata, songs = Album_.get_metadata(url)
        metadata.update(spotify.album(url))
        return metadata, songs


class Artist(Artist_):
    @staticmethod
    def get_metadata(url: str) -> Tuple[Dict[str, Any], List[Song]]:
        metadata, songs = Artist_.get_metadata(url)
        metadata.update(spotify.artist(url))
        return metadata, songs


class Playlist(Playlist_):
    @staticmethod
    def get_metadata(url: str):
        metadata, songs = Playlist_.get_metadata(url)
        metadata.update(spotify.playlist(url))
        unique_song_ids = set(song.song_id for song in songs)
        return metadata, songs, unique_song_ids


class Track(Song):
    @staticmethod
    def get_metadata(url): 
        song = Song.from_url(url)
        metadata = spotify.track(url)
        return metadata, song