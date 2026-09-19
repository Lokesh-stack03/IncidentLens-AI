from fastapi import FastAPI
from backend.app.database.database import Base, engine
from backend.app.database import models
from backend.app.core.config import settings
from backend.app.routers.health import router as health_router
from backend.app.routers.integrations import router as integrations_router
Base.metadata.create_all(bind=engine)
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
app.include_router(integrations_router)