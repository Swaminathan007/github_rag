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
            title="Home — py-react-ssr",
            props={
                "message": "Hello from FastAPI + React!",
                "count": 42,
            },
            meta_tags={
                "description": "A Python SSR app powered by esbuild",
                "og:title": "py-react-ssr",
            },
        )
    )