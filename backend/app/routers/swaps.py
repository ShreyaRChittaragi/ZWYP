from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from ..database import get_db
from ..models import SwapRequest, Item, User, Conversation, Message
from ..schemas import SwapIn, SwapOut, MsgIn, MsgOut
from ..security import current_user
router = APIRouter(tags=["swaps"])
ACTIVE = ("pending", "accepted")
def _involving(ids): return or_(SwapRequest.target_item_id.in_(ids), SwapRequest.offered_item_id.in_(ids))
def _ids(s): return [s.target_item_id, s.offered_item_id]
def _accepted_conflict(db, ids, exclude_id=None):
    q = select(SwapRequest).where(SwapRequest.status == "accepted", _involving(ids))
    if exclude_id: q = q.where(SwapRequest.id != exclude_id)
    return db.scalar(q.limit(1))
def _get(db, sid):
    s = db.get(SwapRequest, sid)
    if not s: raise HTTPException(404, "Swap not found")
    return s
def _conv(db, s, u):
    if u.id not in (s.owner_id, s.requester_id): raise HTTPException(403, "Not your conversation")
    c = db.scalar(select(Conversation).where(Conversation.swap_id == s.id))
    if not c: c = Conversation(swap_id=s.id); db.add(c); db.flush()
    return c
@router.post("/swaps", response_model=SwapOut, status_code=201)
def create(d: SwapIn, u: User = Depends(current_user), db: Session = Depends(get_db)):
    t, o = db.get(Item, d.target_item_id), db.get(Item, d.offered_item_id)
    if not t or not o or "removed" in (t.status, o.status): raise HTTPException(404, "Item not found")
    if t.status != "available" or o.status != "available": raise HTTPException(409, "One of these items is no longer available")
    if t.owner_id == u.id: raise HTTPException(400, "You cannot request your own listing")
    if o.owner_id != u.id: raise HTTPException(403, "You can only offer your own items")
    if _accepted_conflict(db, [t.id, o.id]): raise HTTPException(409, "One of these items is already reserved in an accepted swap")
    dup = db.scalar(select(SwapRequest).where(SwapRequest.requester_id == u.id, SwapRequest.target_item_id == t.id,
                    SwapRequest.offered_item_id == o.id, SwapRequest.status.in_(ACTIVE)))
    if dup: raise HTTPException(409, "You already have an active request for this swap")
    s = SwapRequest(requester_id=u.id, owner_id=t.owner_id, target_item_id=t.id, offered_item_id=o.id, note=d.note.strip())
    db.add(s); db.flush()
    c = Conversation(swap_id=s.id); db.add(c); db.flush()
    if s.note: db.add(Message(conversation_id=c.id, sender_id=u.id, body=s.note))
    db.commit(); db.refresh(s)
    return SwapOut.model_validate(s)
@router.get("/swaps", response_model=list[SwapOut])
def mine(u: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(SwapRequest).where(or_(SwapRequest.requester_id == u.id, SwapRequest.owner_id == u.id)).order_by(SwapRequest.id.desc())).all()
    return [SwapOut.model_validate(s) for s in rows]
RULES = {"accept": ("owner", ("pending",), "accepted"), "reject": ("owner", ("pending",), "rejected"),
         "cancel": ("requester", ("pending",), "cancelled"), "complete": ("either", ("accepted",), "completed")}
@router.post("/swaps/{sid}/{action}", response_model=SwapOut)
def act(sid: int, action: str, u: User = Depends(current_user), db: Session = Depends(get_db)):
    if action not in RULES: raise HTTPException(404, "Unknown action")
    s = _get(db, sid); who, allowed, new = RULES[action]
    if u.id not in {"owner": {s.owner_id}, "requester": {s.requester_id}, "either": {s.owner_id, s.requester_id}}[who]:
        raise HTTPException(403, "You are not allowed to do that on this request")
    if s.status not in allowed: raise HTTPException(409, f"This request is already {s.status}")
    if action in ("accept", "complete"):
        if s.target_item.status != "available" or s.offered_item.status != "available":
            raise HTTPException(409, "One of the items is no longer available")
    if action == "accept" and _accepted_conflict(db, _ids(s), s.id):
        raise HTTPException(409, "One of these items is already part of another accepted swap")
    s.status = new
    if action == "complete": s.target_item.status = s.offered_item.status = "swapped"
    if action in ("accept", "complete"):
        # Every other pending request touching either item can no longer be fulfilled.
        for other in db.scalars(select(SwapRequest).where(SwapRequest.status == "pending", SwapRequest.id != s.id, _involving(_ids(s)))):
            other.status = "rejected" if other.target_item_id in _ids(s) else "cancelled"
    db.commit(); db.refresh(s)
    return SwapOut.model_validate(s)
@router.get("/messages")
def conversations(u: User = Depends(current_user), db: Session = Depends(get_db)):
    out = []
    for s in db.scalars(select(SwapRequest).where(or_(SwapRequest.requester_id == u.id, SwapRequest.owner_id == u.id)).order_by(SwapRequest.id.desc())):
        c = db.scalar(select(Conversation).where(Conversation.swap_id == s.id))
        last = db.scalar(select(Message).where(Message.conversation_id == c.id).order_by(Message.id.desc())) if c else None
        other = s.owner if s.requester_id == u.id else s.requester
        out.append({"swap_id": s.id, "with": other.name, "status": s.status, "title": f"{s.offered_item.title} ⇄ {s.target_item.title}", "last": last.body if last else ""})
    return out
@router.get("/messages/{sid}", response_model=list[MsgOut])
def thread(sid: int, u: User = Depends(current_user), db: Session = Depends(get_db)):
    c = _conv(db, _get(db, sid), u); db.commit()
    return [MsgOut.model_validate(m) for m in db.scalars(select(Message).where(Message.conversation_id == c.id).order_by(Message.id))]
@router.post("/messages/{sid}", response_model=MsgOut, status_code=201)
def send(sid: int, d: MsgIn, u: User = Depends(current_user), db: Session = Depends(get_db)):
    if not d.body.strip(): raise HTTPException(422, "Message cannot be empty")
    c = _conv(db, _get(db, sid), u)
    m = Message(conversation_id=c.id, sender_id=u.id, body=d.body.strip()); db.add(m); db.commit(); db.refresh(m)
    return MsgOut.model_validate(m)
@router.get("/users/me/dashboard")
def dashboard(u: User = Depends(current_user), db: Session = Depends(get_db)):
    swaps = db.scalars(select(SwapRequest).where(or_(SwapRequest.requester_id == u.id, SwapRequest.owner_id == u.id))).all()
    items = db.scalars(select(Item).where(Item.owner_id == u.id, Item.status == "available")).all()
    return {"active_listings": len(items),
            "incoming_pending": sum(1 for s in swaps if s.owner_id == u.id and s.status == "pending"),
            "outgoing_pending": sum(1 for s in swaps if s.requester_id == u.id and s.status == "pending"),
            "completed": sum(1 for s in swaps if s.status == "completed")}