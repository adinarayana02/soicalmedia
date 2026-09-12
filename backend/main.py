from typing import Optional

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from database.db import engine, Base, get_db
from routes import auth, dashboard, analyze, zip_analyze, settings as settings_routes
from routes.auth import get_user_from_cookie

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaaS Multimodal Agent Behavior Platform")

BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.include_router(auth.router, tags=["auth"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(analyze.router, tags=["analyze"])
app.include_router(zip_analyze.router, tags=["analyze-zip"])
app.include_router(settings_routes.router, tags=["settings"])


def _page_ctx(request: Request, active: str, authenticated: Optional[bool] = None):
    if authenticated is None:
        authenticated = bool(request.cookies.get("access_token"))
    return {"request": request, "active": active, "authenticated": authenticated}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", _page_ctx(request, "home"))


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", _page_ctx(request, "login"))


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", _page_ctx(request, "signup"))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    if not get_user_from_cookie(request, db):
        return RedirectResponse(url="/login")
    ctx = _page_ctx(request, "dashboard", authenticated=True)
    return templates.TemplateResponse("dashboard.html", ctx)


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request, db: Session = Depends(get_db)):
    if not get_user_from_cookie(request, db):
        return RedirectResponse(url="/login")
    ctx = _page_ctx(request, "upload", authenticated=True)
    return templates.TemplateResponse("upload.html", ctx)


@app.get("/insights", response_class=HTMLResponse)
async def insights_page(request: Request, db: Session = Depends(get_db)):
    if not get_user_from_cookie(request, db):
        return RedirectResponse(url="/login")
    ctx = _page_ctx(request, "insights", authenticated=True)
    return templates.TemplateResponse("insights.html", ctx)


if __name__ == "__main__":
    import uvicorn

    print("Launching Multimodal SaaS Interface...")
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)
