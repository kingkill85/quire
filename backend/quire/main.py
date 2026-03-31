from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from quire.config import settings
from quire.services.verso import VersoClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
    app.state.verso = VersoClient(
        base_url=settings.verso_url,
        email=settings.verso_app_password_email,
        app_password=settings.verso_app_password,
    )
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


@app.get("/api/health")
async def health():
    verso_ok = await app.state.verso.health_check()
    return {
        "status": "ok" if verso_ok else "degraded",
        "version": "0.1.0",
        "verso": "connected" if verso_ok else "unreachable",
    }
