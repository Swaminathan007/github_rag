from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from reactrender import ReactSSR,Config,RenderConfig
from .llm_init import get_llm

ui_router = APIRouter(prefix="")

engine = ReactSSR(
    Config(
        frontend_dir="./frontend/src",
        asset_route="/assets",
        production=True,
        tailwind_css_path= "@radix-ui/themes/styles.css"
    )
)

@ui_router.get("/", response_class=HTMLResponse)
async def get_home_page():
    return engine.render(
        RenderConfig(
            file="pages/Home.tsx",
            title="Home — py-react-ssr",
            props={
                "message": "Hello from FastAPI + React!",
                "count": 42,
            },
            meta_tags={
                "description": "Upload repo and chat with it",
                "og:title": "Github RAG",
            },
        )
    )
@ui_router.get("/chat",response_class=HTMLResponse)
async def get_chat_page():
    return engine.render(
        RenderConfig(
            file="pages/Chat.tsx",
            title="Chat",
            props={
                "repo": "",
            },
            meta_tags={
                "description": "Repo chat",
                "og:title": "GITHUB RAG",
            },
        )
    )