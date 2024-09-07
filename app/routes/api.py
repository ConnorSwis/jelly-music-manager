from fastapi import APIRouter, BackgroundTasks, Query, Request, Form
from ..controllers.api import controller
from typing import Optional

MUSIC_DIR = "music"

router = APIRouter()


@router.get("/query/")
async def query(request: Request, url: str = Query(..., description="The search query")):
    return await controller.query(url, request)


@router.post("/download/")
async def download(request: Request, background_tasks: BackgroundTasks, url: str = Query(..., description="The Download URL")):
    return await controller.download(url, request, background_tasks)


@router.get("/progress/")
async def progress(request: Request, url: Optional[str] = Query(None, description="The search query")):
    return await controller.progress(url, request)
