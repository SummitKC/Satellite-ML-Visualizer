import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import satellites
from app.services.satcat_fetcher import periodic_satcat_refresh_loop
from app.services.satellite_cache import periodic_refresh_loop

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    tasks = [
        asyncio.create_task(periodic_refresh_loop()),
        asyncio.create_task(periodic_satcat_refresh_loop()),
    ]
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task


app = FastAPI(title="Satellite ML Visualizer API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(satellites.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
