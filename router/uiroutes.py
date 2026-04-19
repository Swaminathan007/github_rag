from fastapi import APIRouter

ui_router = APIRouter(prefix="")

@ui_router.get("/")
async def get_home_page():
    return "Hello World"