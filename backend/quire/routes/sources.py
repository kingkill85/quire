import asyncio

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/api/sources")
async def list_sources(request: Request):
    registry = request.app.state.sources

    async def check_source(source):
        try:
            available = await source.is_available()
        except Exception:
            available = False
        return {
            "name": source.name,
            "display_name": source.display_name,
            "available": available,
        }

    results = await asyncio.gather(*[check_source(s) for s in registry.all()])
    return {"sources": results}
