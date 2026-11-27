from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models import User
from ..schemas import Register, Login, UserOut
from ..security import hash_pw, check_pw, make_token, current_user
router = APIRouter(tags=["auth"])
@router.post("/auth/register", status_code=201)
def register(d: Register, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == d.email.lower())): raise HTTPException(409, "Email already registered")
    u = User(name=d.name, email=d.email.lower(), password_hash=hash_pw(d.password), location=d.location)
    db.add(u); db.commit()
    return {"token": make_token(u.id), "user": UserOut.model_validate(u)}
@router.post("/auth/login")
def login(d: Login, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.email == d.email.lower()))
    if not u or not check_pw(d.password, u.password_hash): raise HTTPException(401, "Invalid email or password")
    return {"token": make_token(u.id), "user": UserOut.model_validate(u)}
@router.get("/users/me", response_model=UserOut)
def me(u: User = Depends(current_user)): return UserOut.model_validate(u)