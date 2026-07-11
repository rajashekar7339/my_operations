from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
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

TASKS = [
    {
        "id": "tps",
        "title": "TPS Calculator",
        "path": "/tps_calculator",
    },
    {
        "id": "dashboard",
        "title": "App Dashboard",
        "path": "/app_dashboard",
    },
]


def _render_shell(request: Request, active_task: str):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "tasks": TASKS,
            "active_task": active_task,
        },
    )


@app.get("/")
async def index():
    return RedirectResponse(url="/tps_calculator", status_code=307)


@app.get("/tps_calculator", response_class=HTMLResponse)
async def tps_calculator(request: Request):
    return _render_shell(request, "tps")


@app.get("/app_dashboard", response_class=HTMLResponse)
async def app_dashboard(request: Request):
    return _render_shell(request, "dashboard")
