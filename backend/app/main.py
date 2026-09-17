from fastapi import FastAPI

from backend.app.core.config import settings
from backend.app.routers.health import router as health_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


@app.get("/")
def root():
    return {
        "message": "Welcome to IncidentLens AI",
        "status": "success"
    }


app.include_router(health_router)