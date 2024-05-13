from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from spotdl.types.song import Song
from spotdl import Spotdl, SpotifyClient
import os
from dotenv import load_dotenv
import logging

log = logging.getLogger(__name__)


load_dotenv()


client_id = os.getenv("SPOTIFY_ID")
client_secret = os.getenv("SPOTIFY_SECRET")

if not client_id or not client_secret:
    raise Exception(
        "Client ID and Client Secret must be set as environment variables.")


# Spotdl(client_id=client_id, client_secret=client_secret)
spotify = SpotifyClient.init(client_id=client_id, client_secret=client_secret)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def read_index():
    return FileResponse('app/static/index.html')


@app.get("/favicon.ico")
async def read_favicon():
    return FileResponse('app/static/favicon.ico')
