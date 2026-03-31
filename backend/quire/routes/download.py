import asyncio

from fastapi import APIRouter, Request
from pydantic import BaseModel

from quire.services.download_queue import DownloadQueue, DownloadStatus

router = APIRouter()


class DownloadRequest(BaseModel):
    source: str
    url: str
    title: str
    author: str


@router.post("/api/download")
async def start_download(request: Request, body: DownloadRequest):
    queue: DownloadQueue = request.app.state.download_queue
    sources = request.app.state.sources
    verso = request.app.state.verso

    source = sources.get(body.source)
    if not source:
        return {"error": f"Unknown source: {body.source}"}, 400

    item = queue.add(
        source=body.source,
        url=body.url,
        title=body.title,
        author=body.author,
    )

    asyncio.create_task(_download_and_upload(queue, source, verso, item.id))

    return {"item": item.to_dict()}


@router.get("/api/downloads")
async def list_downloads(request: Request):
    queue: DownloadQueue = request.app.state.download_queue
    items = queue.list_all()
    return {"items": [item.to_dict() for item in items]}


@router.get("/api/downloads/{item_id}")
async def get_download(request: Request, item_id: str):
    queue: DownloadQueue = request.app.state.download_queue
    item = queue.get(item_id)
    if not item:
        return {"error": "Not found"}, 404
    return {"item": item.to_dict()}


@router.delete("/api/downloads/{item_id}")
async def cancel_download(request: Request, item_id: str):
    queue: DownloadQueue = request.app.state.download_queue
    queue.cancel(item_id)
    return {"status": "cancelled"}


async def _download_and_upload(queue, source, verso, item_id: str):
    try:
        item = queue.get(item_id)
        if not item or item.status == DownloadStatus.CANCELLED:
            return

        queue.update_status(item_id, DownloadStatus.DOWNLOADING, progress=0.0)
        file_content, filename = await source.download(item.url)
        queue.update_status(item_id, DownloadStatus.DOWNLOADING, progress=100.0)

        queue.update_status(item_id, DownloadStatus.UPLOADING)
        result = await verso.upload_book(file_content, filename)
        verso_book_id = result.get("book", {}).get("id")

        queue.update_status(
            item_id, DownloadStatus.COMPLETE, progress=100.0, verso_book_id=verso_book_id
        )
    except Exception as e:
        queue.update_status(item_id, DownloadStatus.ERROR, error=str(e))
