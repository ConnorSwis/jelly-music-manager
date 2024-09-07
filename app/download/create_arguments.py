from typing import Any, Dict, List, Optional, Tuple, Union
from argparse import Namespace


def create_arguments(
    operation: str,
    query: List[str],
    audio_providers: Optional[List[str]] = None,
    lyrics_providers: Optional[List[str]] = None,
    genius_token: Optional[str] = None,
    config: bool = False,
    search_query: Optional[str] = None,
    filter_results: bool = True,
    album_type: Optional[str] = None,
    only_verified_results: bool = False,
    user_auth: bool = False,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    auth_token: Optional[str] = None,
    cache_path: Optional[str] = None,
    no_cache: bool = False,
    max_retries: Optional[int] = None,
    headless: bool = False,
    use_cache_file: bool = False,
    ffmpeg: Optional[str] = None,
    threads: Optional[int] = None,
    bitrate: str = "auto",
    ffmpeg_args: Optional[str] = None,
    format: Optional[str] = None,
    save_file: Optional[str] = None,
    preload: bool = False,
    output: Optional[str] = None,
    m3u: Optional[str] = None,
    cookie_file: Optional[str] = None,
    overwrite: Optional[str] = "force",
    restrict: Optional[str] = "strict",
    print_errors: bool = False,
    save_errors: Optional[str] = None,
    sponsor_block: bool = False,
    archive: Optional[str] = None,
    playlist_numbering: bool = False,
    scan_for_songs: bool = False,
    fetch_albums: bool = False,
    id3_separator: Optional[str] = None,
    ytm_data: bool = False,
    add_unavailable: bool = False,
    generate_lrc: bool = False,
    force_update_metadata: bool = False,
    sync_without_deleting: bool = False,
    max_filename_length: Optional[int] = None,
    yt_dlp_args: Optional[str] = None,
    detect_formats: Optional[List[str]] = None,
    redownload: bool = False,
    skip_album_art: bool = False,
    ignore_albums: Optional[List[str]] = None,
    skip_explicit: bool = False,
    proxy: Optional[str] = None,
    create_skip_file: bool = False,
    respect_skip_file: bool = False,
    sync_remove_lrc: bool = False,
    host: Optional[str] = None,
    port: Optional[int] = None,
    keep_alive: bool = False,
    allowed_origins: Optional[List[str]] = None,
    web_use_output_dir: bool = False,
    keep_sessions: bool = False,
    force_update_gui: bool = False,
    web_gui_repo: Optional[str] = None,
    web_gui_location: Optional[str] = None,
    enable_tls: bool = False,
    cert_file: Optional[str] = None,
    key_file: Optional[str] = None,
    ca_file: Optional[str] = None,
    log_level: Optional[str] = None,
    simple_tui: bool = False,
    log_format: Optional[str] = None,
    download_ffmpeg: bool = False,
    generate_config: bool = False,
    check_for_updates: bool = False,
    profile: bool = False,


) -> Namespace:
    """
    Manually create the Namespace object with the arguments.

    ### Arguments
    - operation (str): The operation to perform (e.g., "download", "save", "web", "sync", "meta", "url").
    - query (List[str]): Spotify/YouTube URL for a song/playlist/album/artist/etc. to download.
    - audio_providers (Optional[List[str]]): The audio provider(s) to use. You can provide more than one for fallback.
    - lyrics_providers (Optional[List[str]]): The lyrics provider(s) to use. You can provide more than one for fallback.
    - genius_token (Optional[str]): Genius access token.
    - config (bool): Use the config file to download songs.
    - search_query (Optional[str]): The search query to use, with variables for dynamic searching.
    - filter_results (bool): Whether to filter search results.
    - album_type (Optional[str]): Type of the album to search for (e.g., "album", "single").
    - only_verified_results (bool): Use only verified results.
    - user_auth (bool): Login to Spotify using OAuth.
    - client_id (Optional[str]): The client ID to use when logging in to Spotify.
    - client_secret (Optional[str]): The client secret to use when logging in to Spotify.
    - auth_token (Optional[str]): Authorization token to use for logging in to Spotify.
    - cache_path (Optional[str]): Path to store the Spotify cache file.
    - no_cache (bool): Disable caching (both requests and token).
    - max_retries (Optional[int]): Maximum number of retries to perform when getting metadata.
    - headless (bool): Run in headless mode.
    - use_cache_file (bool): Use the cache file to get metadata.
    - ffmpeg (Optional[str]): The ffmpeg executable to use.
    - threads (Optional[int]): Number of threads to use when downloading songs.
    - bitrate (str): Constant/variable bitrate to use for the output file (e.g., "auto", "320k").
    - ffmpeg_args (Optional[str]): Additional ffmpeg arguments as a string.
    - format (Optional[str]): The format to download the song in.
    - save_file (Optional[str]): File to save/load the songs data from/to. Must end with .spotdl.
    - preload (bool): Preload the download URL to speed up the download process.
    - output (Optional[str]): Specify the downloaded file name format.
    - m3u (Optional[str]): Name of the m3u file to save the songs to.
    - cookie_file (Optional[str]): Path to cookies file.
    - overwrite (Optional[str]): How to handle existing/duplicate files (e.g., "force", "skip", "metadata").
    - restrict (Optional[str]): Restrict filenames to a sanitized set of characters for compatibility.
    - print_errors (bool): Print errors on exit, useful for long playlists.
    - save_errors (Optional[str]): Save errors to a file.
    - sponsor_block (bool): Use the sponsor block to download songs from YouTube.
    - archive (Optional[str]): File name for an archive of already downloaded songs.
    - playlist_numbering (bool): Set each track in a playlist to have the playlist's name as its album.
    - scan_for_songs (bool): Scan the output directory for existing files.
    - fetch_albums (bool): Fetch all albums from songs in query.
    - id3_separator (Optional[str]): Separator used in the ID3 tags (supported for mp3 files).
    - ytm_data (bool): Use YouTube Music data instead of Spotify data when downloading.
    - add_unavailable (bool): Add unavailable songs to the m3u/archive files when downloading.
    - generate_lrc (bool): Generate LRC files for downloaded songs (requires `synced` lyrics provider).
    - force_update_metadata (bool): Force update metadata for songs that already have metadata.
    - sync_without_deleting (bool): Sync without deleting songs that are not in the query.
    - max_filename_length (Optional[int]): Maximum file name length (won't override OS limits).
    - yt_dlp_args (Optional[str]): Arguments to pass to yt-dlp.
    - detect_formats (Optional[List[str]]): Detect already downloaded songs with a different format.
    - redownload (bool): Redownload the local song in a different format for the meta operation.
    - skip_album_art (bool): Skip downloading album art for the meta operation.
    - ignore_albums (Optional[List[str]]): Ignore songs from the specified albums.
    - skip_explicit (bool): Skip explicit songs.
    - proxy (Optional[str]): HTTP(s) proxy server for downloading songs.
    - create_skip_file (bool): Create a skip file for successfully downloaded files.
    - respect_skip_file (bool): Skip downloading if a .skip file exists.
    - sync_remove_lrc (bool): Remove LRC files when using sync operation.
    - host (Optional[str]): The host to use for the web server.
    - port (Optional[int]): The port to run the web server on.
    - keep_alive (bool): Keep the web server alive even when no clients are connected.
    - allowed_origins (Optional[List[str]]): Allowed origins for the web server.
    - web_use_output_dir (bool): Use the output directory instead of the session directory for downloads.
    - keep_sessions (bool): Keep the session directory after the web server is closed.
    - force_update_gui (bool): Refresh the web server directory with a fresh git checkout.
    - web_gui_repo (Optional[str]): Custom web GUI repo to use for the web server.
    - web_gui_location (Optional[str]): Path to the web GUI directory for the web server.
    - enable_tls (bool): Enable TLS on the web server.
    - cert_file (Optional[str]): Path to the TLS certificate file (PEM format).
    - key_file (Optional[str]): Path to the TLS private key file (PEM format).
    - ca_file (Optional[str]): Path to the TLS Certificate Authority file (PEM format).
    - log_level (Optional[str]): Select log level.
    - simple_tui (bool): Use a simple TUI.
    - log_format (Optional[str]): Custom logging format to use.
    - download_ffmpeg (bool): Download FFmpeg to spotDL directory.
    - generate_config (bool): Generate a config file, overwriting any existing config.
    - check_for_updates (bool): Check for a new version.
    - profile (bool): Run in profile mode (useful for debugging).

    ### Returns
    - Namespace: A Namespace object containing the arguments.
    """
    return Namespace(
        operation=operation,
        query=query,
        audio_providers=audio_providers,
        lyrics_providers=lyrics_providers,
        genius_token=genius_token,
        config=config,
        search_query=search_query,
        filter_results=filter_results,
        album_type=album_type,
        only_verified_results=only_verified_results,
        user_auth=user_auth,
        client_id=client_id,
        client_secret=client_secret,
        auth_token=auth_token,
        cache_path=cache_path,
        no_cache=no_cache,
        max_retries=max_retries,
        headless=headless,
        use_cache_file=use_cache_file,
        ffmpeg=ffmpeg,
        threads=threads,
        bitrate=bitrate,
        ffmpeg_args=ffmpeg_args,
        format=format,
        save_file=save_file,
        preload=preload,
        output=output,
        m3u=m3u,
        cookie_file=cookie_file,
        overwrite=overwrite,
        restrict=restrict,
        print_errors=print_errors,
        save_errors=save_errors,
        sponsor_block=sponsor_block,
        archive=archive,
        playlist_numbering=playlist_numbering,
        scan_for_songs=scan_for_songs,
        fetch_albums=fetch_albums,
        id3_separator=id3_separator,
        ytm_data=ytm_data,
        add_unavailable=add_unavailable,
        generate_lrc=generate_lrc,
        force_update_metadata=force_update_metadata,
        sync_without_deleting=sync_without_deleting,
        max_filename_length=max_filename_length,
        yt_dlp_args=yt_dlp_args,
        detect_formats=detect_formats,
        redownload=redownload,
        skip_album_art=skip_album_art,
        ignore_albums=ignore_albums,
        skip_explicit=skip_explicit,
        proxy=proxy,
        create_skip_file=create_skip_file,
        respect_skip_file=respect_skip_file,
        sync_remove_lrc=sync_remove_lrc,
        host=host,
        port=port,
        keep_alive=keep_alive,
        allowed_origins=allowed_origins,
        web_use_output_dir=web_use_output_dir,
        keep_sessions=keep_sessions,
        force_update_gui=force_update_gui,
        web_gui_repo=web_gui_repo,
        web_gui_location=web_gui_location,
        enable_tls=enable_tls,
        cert_file=cert_file,
        key_file=key_file,
        ca_file=ca_file,
        log_level=log_level,
        simple_tui=simple_tui,
        log_format=log_format,
        download_ffmpeg=download_ffmpeg,
        generate_config=generate_config,
        check_for_updates=check_for_updates,
        profile=profile,
    )
