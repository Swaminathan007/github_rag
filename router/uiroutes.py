from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from reactrender import ReactSSR,Config,RenderConfig

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
            title="Home",
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
@ui_router.get("/repos",response_class=HTMLResponse)
async def get_repos_page():
    return engine.render(
        RenderConfig(
            file="pages/Repos.tsx",
            title="Repos",
            props={
                "repos": [],
            },
            meta_tags={
                "description": "Repos",
                "og:title": "GITHUB RAG",
            },
        )
    )
@ui_router.get("/chat/{repo_name}",response_class=HTMLResponse)
async def get_chat_page(repo_name: str):
    return engine.render(
        RenderConfig(
            file="pages/Chat.tsx",
            title="Chat",
            props={
                "repo_name": repo_name,
            },
            meta_tags={
                "description": "Repo chat",
                "og:title": "GITHUB RAG",
            },
        )
    )