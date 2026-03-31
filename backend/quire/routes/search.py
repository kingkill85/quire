import asyncio
from dataclasses import asdict

from fastapi import APIRouter, Query, Request

router = APIRouter()


@router.get("/api/search")
async def search(
    request: Request,
    q: str = Query(..., min_length=1),
    sources: str | None = Query(None),
    max_results: int = Query(25, ge=1, le=100),
):
    registry = request.app.state.sources

    if sources:
        source_names = [s.strip() for s in sources.split(",")]
        source_list = [registry.get(name) for name in source_names]
        source_list = [s for s in source_list if s is not None]
    else:
        source_list = registry.all()

    async def search_source(source):
        try:
            return await source.search(q, max_results=max_results)
        except Exception as e:
            return {"source": source.name, "error": str(e)}

    raw_results = await asyncio.gather(
        *[search_source(s) for s in source_list],
        return_exceptions=True,
    )

    results = []
    errors = []
    for r in raw_results:
        if isinstance(r, list):
            results.extend([asdict(item) for item in r])
        elif isinstance(r, dict) and "error" in r:
            errors.append(r)
        elif isinstance(r, Exception):
            errors.append({"error": str(r)})

    return {"results": results, "errors": errors, "total": len(results)}
