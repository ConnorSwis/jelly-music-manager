import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from .routes import api_router


load_dotenv()

client_id = os.getenv("SPOTIFY_ID")
client_secret = os.getenv("SPOTIFY_SECRET")

if not client_id or not client_secret:
    raise Exception(
        "Client ID and Client Secret must be set as environment variables.")

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api_router)

@app.get("/")
async def read_index():
    return FileResponse('app/static/index.html')

@app.get("/health")
async def read_health():
    return {"status": "ok"}

@app.get("/favicon.ico")
async def read_favicon():
    return FileResponse('app/static/favicon.ico')
 