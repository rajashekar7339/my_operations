from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers.calculators import router as calculators_router
from app.routers.dashboard import router as dashboard_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="My Operations", version="1.0.0")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(calculators_router)
app.include_router(dashboard_router)

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "tasks": [
                {
                    "id": "tps",
                    "title": "TPS Calculator",
                },
                {
                    "id": "dashboard",
                    "title": "App Dashboard",
                },
            ]
        },
    )
