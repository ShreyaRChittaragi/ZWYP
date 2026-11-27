import logging, os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .database import Base, engine
from .routers import auth, items, swaps, matches
from .routers.items import UPLOADS
from .seed_images import generate, STATIC
log = logging.getLogger("zwyp")
Base.metadata.create_all(engine)
generate()  # ensure demo/placeholder illustrations exist
app = FastAPI(title="ZWYP API", description="Peer-to-peer barter marketplace", version="0.2.0")
# Local dev origins always allowed; FRONTEND_URL adds the deployed frontend (comma-separated for several).
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
ORIGINS += [o.strip().rstrip("/") for o in os.getenv("FRONTEND_URL", "").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=list(dict.fromkeys(ORIGINS)), allow_methods=["*"], allow_headers=["*"])
UPLOADS.mkdir(parents=True, exist_ok=True)  # same directory items.py writes to (UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")
app.mount("/static/seed", StaticFiles(directory=STATIC), name="seed-images")
@app.exception_handler(IntegrityError)
async def integrity(_: Request, exc: IntegrityError):
    log.warning("integrity error: %s", exc); return JSONResponse({"detail": "That operation conflicts with existing data."}, 409)
@app.exception_handler(SQLAlchemyError)
async def db_error(_: Request, exc: SQLAlchemyError):
    log.exception("database error"); return JSONResponse({"detail": "A database error occurred. Please try again."}, 500)
for r in (auth, items, swaps, matches): app.include_router(r.router, prefix="/api")