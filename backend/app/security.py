import bcrypt, jwt, os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
SECRET = os.getenv("ZWYP_SECRET", "dev-secret-change-me")
bearer = HTTPBearer(auto_error=False)
hash_pw = lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
check_pw = lambda p, h: bcrypt.checkpw(p.encode(), h.encode())
def make_token(uid): return jwt.encode({"sub": str(uid), "exp": datetime.utcnow() + timedelta(days=7)}, SECRET, "HS256")
def current_user(creds=Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        uid = int(jwt.decode(creds.credentials, SECRET, ["HS256"])["sub"])
    except Exception:
        raise HTTPException(401, "Not authenticated")
    u = db.get(User, uid)
    if not u: raise HTTPException(401, "Not authenticated")
    return u
