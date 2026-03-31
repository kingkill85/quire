from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from quire.config import settings
from quire.routes.download import router as download_router
from quire.routes.search import router as search_router
from quire.routes.sources import router as sources_router
from quire.services.cf_bypass import ExternalBypass, InternalBypass, NoBypass
from quire.services.download_queue import DownloadQueue
from quire.services.verso import VersoClient
from quire.sources.setup import create_registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
    app.state.verso = VersoClient(
        base_url=settings.verso_url,
        email=settings.verso_app_password_email,
        app_password=settings.verso_app_password,
    )
    app.state.sources = create_registry()
    app.state.download_queue = DownloadQueue(
        max_concurrent=settings.max_concurrent_downloads,
    )
    if settings.cf_bypass == "external":
        app.state.cf_bypass = ExternalBypass(flaresolverr_url=settings.flaresolverr_url)
    elif settings.cf_bypass == "internal":
        app.state.cf_bypass = InternalBypass()
    else:
        app.state.cf_bypass = NoBypass()
    yield
    await app.state.verso.close()


app = FastAPI(title="Quire", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(download_router)
app.include_router(sources_router)


@app.get("/api/health")
async def health():
    verso_ok = await app.state.verso.health_check()
    return {
        "status": "ok" if verso_ok else "degraded",
        "version": "0.1.0",
        "verso": "connected" if verso_ok else "unreachable",
        "sources": app.state.sources.list_sources(),
    }
