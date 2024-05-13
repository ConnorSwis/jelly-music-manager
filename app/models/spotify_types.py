from spotdl.types.artist import Artist
from spotdl.types.album import Album
from typing import Any, Dict, List, Tuple

from spotdl.types.song import Song
from spotdl import SpotifyClient
from spotdl.types.playlist import Playlist as Playlist_
from spotdl.types.album import Album as Album_
from spotdl.types.artist import Artist as Artist_

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
    def get_metadata(url: str) -> Tuple[Dict[str, Any], List[Song]]:
        metadata, songs = Playlist_.get_metadata(url)
        metadata.update(spotify.playlist(url))

        unique_song_ids = {}
        for song in songs:
            if song.song_id not in unique_song_ids:
                unique_song_ids[song.song_id] = song
        unique_songs = list(unique_song_ids.values())

        return metadata, unique_songs


class Track(Song):
    @staticmethod
    def get_metadata(url):
        return Song.from_url(url)
