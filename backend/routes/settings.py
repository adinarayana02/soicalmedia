from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from database.db import get_db
from database.models import (
    Upload,
    AnalysisResult,
    Message,
    UrlData,
    Interaction,
    AccountProfile,
    SearchHistory,
    Preference,
)
from routes.auth import get_current_user, get_user_from_cookie

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    recent_uploads = (
        db.query(Upload)
        .filter(Upload.user_id == user.id)
        .order_by(Upload.created_at.desc())
        .limit(10)
        .all()
    )
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "history": recent_uploads,
            "authenticated": True,
            "active": "settings",
        },
    )


@router.post("/api/account/purge")
def purge_user_data(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    uid = current_user.id
    for model in (
        AnalysisResult,
        Upload,
        Message,
        UrlData,
        Interaction,
        AccountProfile,
        SearchHistory,
        Preference,
    ):
        db.query(model).filter(model.user_id == uid).delete()
    db.commit()
    return {"ok": True, "message": "Behavioral data cleared for your account."}
