from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from routers import convert, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("uploads/input", exist_ok=True)
    os.makedirs("uploads/output", exist_ok=True)
    yield


app = FastAPI(
    title="Converto",
    description="Self-hosted document & image converter",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(convert.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")

if os.path.exists("static/index.html"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        return FileResponse("static/index.html")
