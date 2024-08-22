import sys
sys.path.append("..")

from starlette.responses import RedirectResponse

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from pydantic import BaseModel
import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from .auth import get_current_user, get_password_hash, verify_password
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Userverification(BaseModel):
    username: str
    password: str
    newpassword: str


@router.get("/changepassword", response_class=HTMLResponse)
async def edit_password(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    

    return templates.TemplateResponse("edit-password.html", {"request": request, "user": user})


@router.post("/changepassword", response_class=HTMLResponse)
async def change_password(request: Request, username: str = Form(...), password: str = Form(...),
                      password2: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    user_db = db.query(models.Users).filter(models.Users.username == username).first()
    msg = "Sorry wrong username and password"
    if user_db is not None:
        if username==user_db.username and verify_password(password,user_db.hashed_password):
            user_db.hashed_password = get_password_hash(password2)
            db.add(user_db)
            db.commit()
            msg = "password update"
    return templates.TemplateResponse("edit-password.html",{"request": request, "user": user,"msg": msg})