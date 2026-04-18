from fastapi import APIRouter
from .repo_routes import repo_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(repo_router)