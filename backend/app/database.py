import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "zwyp.db"  # always backend/zwyp.db, whatever the cwd
DB_PATH = Path(os.getenv("DB_PATH") or DEFAULT_DB_PATH)  # override with DB_PATH (e.g. a Render disk path)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
# expire_on_commit=False so objects can be serialised after commit without lazy reloads
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
class Base(DeclarativeBase): pass
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()