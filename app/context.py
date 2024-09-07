from spotdl import SpotifyClient
from spotdl.types.options import SpotifyOptions
from spotdl.download.progress_handler import BAD_CHARS
from dotenv import load_dotenv

import os
import sys
import logging
from pathlib import Path
from datetime import datetime


load_dotenv()


def initialize_logger():
    master_logger = logging.getLogger('master')
    master_logger.setLevel(logging.DEBUG)
    logs_dir = get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = logs_dir.joinpath(
        f'master-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')
    file_handler = logging.FileHandler(str(log_file_path))
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(message)s'
    )

    console_handler.setFormatter(simple_formatter)
    file_handler.setFormatter(detailed_formatter)

    master_logger.addHandler(file_handler)
    master_logger.addHandler(console_handler)

    master_logger.propagate = False

    for logger_name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            logger.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
            logger.propagate = False

    master_logger.info("Logger initialized.")

    return master_logger


def get_music_dir():
    return Path(os.environ.get("MUSIC_DIR", "/music")).absolute()


def get_logs_dir():
    return Path(os.getenv("LOGS_DIR", "/logs")).absolute()


def clean(s: str) -> str:
    assert isinstance(s, str), "Input to clean must be a string"
    logger.debug(f"Cleaning string: {s}")
    cleaned = "".join(c for c in s if c not in [chr(i) for i in BAD_CHARS])
    return cleaned


logger = initialize_logger()

spotify_options: SpotifyOptions = {
    "client_id": os.getenv("SPOTIFY_ID"),
    "client_secret": os.getenv("SPOTIFY_SECRET"),
    "headless": True,
}
assert spotify_options["client_id"] and spotify_options["client_secret"], "Spotify client ID and secret must be set"

try:
    spotify: SpotifyClient = SpotifyClient.init(**spotify_options)
    logger.info("Spotify client initialized successfully.")
except Exception as e:
    logger.critical(f"Failed to initialize Spotify client: {e}")
    raise

__music_dir = get_music_dir()
try:
    if not __music_dir.exists():
        logger.debug(
            f"__music_dir does not exist. Creating directory: {__music_dir}")
        __music_dir.mkdir(parents=True, exist_ok=True)

    if not os.access(__music_dir, os.W_OK):
        logger.error(f"Cannot write to __music_dir: {__music_dir}")
        raise PermissionError(f"Cannot write to __music_dir: {__music_dir}")

    logger.debug(f"__music_dir is ready and writable: {__music_dir}")
except PermissionError as pe:
    logger.critical(f"Permission error: {pe}")
    raise
except Exception as e:
    logger.critical(f"Failed to prepare MUSIC_DIR: {e}")
    raise
