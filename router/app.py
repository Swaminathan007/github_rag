from fastapi import FastAPI
from .app_health import router as health_router
from .api import api_router

app = FastAPI()

app.include_router(health_router)
app.include_router(api_router)
    