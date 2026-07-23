from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import satellites

settings = get_settings()

app = FastAPI(title="Satellite ML Visualizer API")

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
