import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models import Item, User
from ..schemas import ItemOut
from ..security import current_user
router = APIRouter(prefix="/matches", tags=["matches"])
STOP = {"a","an","the","or","and","any","of","for","with","to","in","good","new","old","like","something"}
toks = lambda s: {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}
def wants_item(wants: str, it: Item):
    """Return shared keywords if `wants` text describes item `it` (title/category)."""
    shared = toks(wants) & (toks(it.title) | toks(it.category) | toks(it.description))
    return shared
@router.get("")
def matches(u: User = Depends(current_user), db: Session = Depends(get_db)):
    mine = db.scalars(select(Item).where(Item.owner_id == u.id, Item.status == "available")).all()
    others = db.scalars(select(Item).where(Item.owner_id != u.id, Item.status == "available")).all()
    out = []
    for m in mine:
        for o in others:
            i_want = wants_item(m.wants, o); they_want = wants_item(o.wants, m)
            if not i_want and not they_want: continue
            why = []
            if i_want and they_want: why.append(f"Mutual match: you want {sorted(i_want)[0]}, they want {sorted(they_want)[0]}")
            elif they_want: why.append(f"{o.owner.name} is looking for “{o.wants}”, which fits your {m.title}")
            else: why.append(f"You're looking for “{m.wants}”, which fits their {o.title}")
            if m.category == o.category: why.append("Same category")
            if m.location == o.location: why.append(f"Both in {o.location}")
            out.append({"kind": "mutual" if i_want and they_want else "partial", "my_item": ItemOut.model_validate(m),
                        "their_item": ItemOut.model_validate(o), "reasons": why,
                        "rank": (2 if i_want and they_want else 1) * 10 + (m.location == o.location) * 2 + (m.category == o.category)})
    out.sort(key=lambda x: -x["rank"])
    return {"matches": out[:20], "cycles": cycles(db, u)}
def cycles(db, u):
    """Find 3-way chains A→B→C→A where each user's item satisfies the next user's wants."""
    items = db.scalars(select(Item).where(Item.status == "available")).all()
    gives = lambda a, b: a.owner_id != b.owner_id and wants_item(b.wants, a)  # a's item satisfies b's wish
    found, seen = [], set()
    for a in items:
        for b in items:
            if not gives(a, b): continue
            for c in items:
                if len({a.owner_id, b.owner_id, c.owner_id}) == 3 and gives(b, c) and gives(c, a):
                    key = frozenset((a.id, b.id, c.id))
                    if key in seen or u.id not in (a.owner_id, b.owner_id, c.owner_id): continue
                    seen.add(key); found.append([ItemOut.model_validate(x) for x in (a, b, c)])
    return found[:3]
