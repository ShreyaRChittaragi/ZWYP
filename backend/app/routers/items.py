import os, uuid, pathlib
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..database import get_db
from ..imaging import validate_image, ImageError, MAX_BYTES
from ..models import Item, User, SwapRequest
from ..schemas import ItemOut
from ..security import current_user
router = APIRouter(prefix="/items", tags=["items"])
CATS = ["Electronics","Books","Fashion","Sports","Musical Instruments","Home & Living","Accessories","Other"]
CONDS = ["New","Like New","Good","Fair"]
UPLOADS = pathlib.Path(os.getenv("UPLOAD_DIR") or pathlib.Path(__file__).resolve().parents[2] / "uploads")  # override with UPLOAD_DIR
PLACEHOLDER = "/static/seed/placeholder.svg"
@router.get("")
def list_items(q: str = "", category: str = "", location: str = "", condition: str = "",
               page: int = Query(1, ge=1), size: int = Query(12, ge=1, le=50), db: Session = Depends(get_db)):
    s = select(Item).where(Item.status == "available")
    if q.strip(): s = s.where(Item.title.ilike(f"%{q.strip()}%"))
    if category: s = s.where(Item.category == category)
    if location: s = s.where(Item.location == location)
    if condition: s = s.where(Item.condition == condition)
    total = db.scalar(select(func.count()).select_from(s.subquery()))
    rows = db.scalars(s.order_by(Item.created_at.desc(), Item.id.desc()).offset((page-1)*size).limit(size)).all()
    return {"total": total, "page": page, "items": [ItemOut.model_validate(r) for r in rows]}
@router.get("/facets")
def facets(db: Session = Depends(get_db)):
    locs = db.scalars(select(Item.location).where(Item.status == "available").distinct().order_by(Item.location)).all()
    return {"categories": CATS, "conditions": CONDS, "locations": locs}
@router.get("/mine", response_model=list[ItemOut])
def mine(u: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Item).where(Item.owner_id == u.id, Item.status != "removed").order_by(Item.id.desc())).all()
    return [ItemOut.model_validate(r) for r in rows]
@router.get("/{item_id}")
def detail(item_id: int, db: Session = Depends(get_db)):
    it = db.get(Item, item_id)
    if not it or it.status == "removed": raise HTTPException(404, "Item not found")
    sim = db.scalars(select(Item).where(Item.category == it.category, Item.id != it.id, Item.status == "available").limit(4)).all()
    return {"item": ItemOut.model_validate(it), "similar": [ItemOut.model_validate(s) for s in sim]}
@router.post("", response_model=ItemOut, status_code=201)
async def create(title: str = Form(..., min_length=3, max_length=120), description: str = Form(..., min_length=10),
                 category: str = Form(...), condition: str = Form(...), location: str = Form(..., min_length=2, max_length=80),
                 wants: str = Form(..., min_length=2, max_length=200), value_inr: int = Form(0, ge=0, le=10_000_000),
                 image: UploadFile | None = File(None), u: User = Depends(current_user), db: Session = Depends(get_db)):
    if category not in CATS: raise HTTPException(422, "Invalid category")
    if condition not in CONDS: raise HTTPException(422, "Invalid condition")
    url = PLACEHOLDER
    if image is not None and image.filename:
        data = await image.read(MAX_BYTES + 1)  # never buffer more than limit + 1 byte
        try: ext = validate_image(data)  # checks real content, size and dimensions; ext comes from detected format
        except ImageError as e: raise HTTPException(422, str(e))
        UPLOADS.mkdir(parents=True, exist_ok=True)
        name = f"{uuid.uuid4().hex}{ext}"; (UPLOADS / name).write_bytes(data); url = f"/uploads/{name}"
    it = Item(owner_id=u.id, title=title.strip(), description=description.strip(), category=category, condition=condition,
              location=location.strip(), wants=wants.strip(), value_inr=value_inr, image_url=url)
    db.add(it); db.commit(); db.refresh(it)
    return ItemOut.model_validate(it)
@router.delete("/{item_id}", status_code=204)
def delete(item_id: int, u: User = Depends(current_user), db: Session = Depends(get_db)):
    it = db.get(Item, item_id)
    if not it or it.status == "removed": raise HTTPException(404, "Item not found")
    if it.owner_id != u.id: raise HTTPException(403, "Not your listing")
    if it.status == "swapped": raise HTTPException(409, "This item has already been swapped")
    inv = (SwapRequest.target_item_id == it.id) | (SwapRequest.offered_item_id == it.id)
    if db.scalar(select(SwapRequest.id).where(SwapRequest.status == "accepted", inv).limit(1)):
        raise HTTPException(409, "This item is part of an accepted swap. Complete or reject it first.")
    for r in db.scalars(select(SwapRequest).where(SwapRequest.status == "pending", inv)): r.status = "cancelled"
    it.status = "removed"; db.commit()