from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from quire.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)
    yield


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
    return {"status": "ok", "version": "0.1.0"}
