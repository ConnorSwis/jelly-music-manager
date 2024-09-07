from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from .context import *
from .routes.api import router as api_router


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router)


@app.get("/")
async def read_index():
    return FileResponse('app/static/index.html')


@app.get("/favicon.ico")
async def read_favicon():
    return FileResponse('app/static/favicon.ico')
