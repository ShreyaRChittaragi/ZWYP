"""Safe, repeatable demo seeding. Never drops tables or deletes user-created data.
- Users are matched by email, listings by (owner, title), swaps by (requester, target, offered).
- Existing rows are left alone; only missing demo rows are created.
- Legacy demo swaps that violate ownership rules (from the first seed version) are removed.
- Legacy picsum.photos demo images are replaced with the local illustrations."""
from sqlalchemy import select
from app.database import Base, engine, SessionLocal
from app.models import User, Item, SwapRequest, Conversation, Message
from app.security import hash_pw
from app.seed_images import generate

USERS = [("Aarav Mehta", "aarav@zwyp.demo", "Bengaluru"), ("Priya Nair", "priya@zwyp.demo", "Bengaluru"),
         ("Rohan Verma", "rohan@zwyp.demo", "Mumbai"), ("Ishita Rao", "ishita@zwyp.demo", "Hyderabad"), ("Karan Singh", "karan@zwyp.demo", "Delhi")]
# (owner index, title, category, condition, wants, value INR, description, image slug)
ITEMS = [
 (0, "Fender Acoustic Guitar", "Musical Instruments", "Good", "Mirrorless camera or DSLR", 14000, "Fender CD-60 acoustic, great tone, comes with a padded gig bag.", "guitar"),
 (1, "Canon EOS 1500D DSLR", "Electronics", "Good", "Acoustic guitar or keyboard", 22000, "Includes 18-55mm lens, two batteries and charger. Low shutter count.", "camera"),
 (2, "Mountain Bike 21-speed", "Sports", "Good", "Treadmill or gym equipment", 12000, "Hero Sprint 26T MTB, recently serviced, new tyres.", "bike"),
 (3, "Set of Harry Potter Books", "Books", "Like New", "Fiction novels or board games", 3500, "Complete 7-book paperback set, minimal wear.", "books"),
 (4, "Sony WH-1000XM3 Headphones", "Electronics", "Like New", "Smartwatch or tablet", 11000, "Noise cancelling, case and cable included.", "headphones"),
 (0, "Leather Jacket (M)", "Fashion", "Good", "Sneakers or backpack", 5000, "Genuine leather biker jacket, size M, barely worn.", "jacket"),
 (1, "Yamaha Digital Keyboard", "Musical Instruments", "Like New", "DSLR camera or drawing tablet", 9000, "Yamaha PSR-E373, 61 keys with stand and adapter.", "keyboard"),
 (2, "Instant Pot Pressure Cooker", "Home & Living", "New", "Air fryer or coffee machine", 6000, "6-litre, unused, still boxed.", "cooker"),
 (3, "Treadmill (foldable)", "Sports", "Good", "Mountain bike or cycle", 15000, "Motorised foldable treadmill, 12 programs.", "treadmill"),
 (4, "Apple Watch SE", "Electronics", "Good", "Headphones or earbuds", 16000, "GPS 40mm, new strap included.", "watch"),
 (0, "Ray-Ban Aviator Sunglasses", "Accessories", "Like New", "Watch or wallet", 4500, "Original with case.", "sunglasses"),
 (1, "Nike Air Max Sneakers (UK 9)", "Fashion", "Good", "Plant pots or home decor", 4000, "Worn a handful of times.", "sneakers"),
 (2, "Board Game Collection", "Other", "Good", "Books or novels", 2500, "Catan, Ticket to Ride and Codenames.", "boardgames"),
 (3, "Drawing Tablet Wacom One", "Electronics", "Like New", "Keyboard or guitar", 5500, "Wacom One small, works with Mac and Windows.", "tablet"),
 (4, "Philips Air Fryer", "Home & Living", "Good", "Pressure cooker or blender", 4200, "4.1L, works perfectly.", "airfryer"),
 (3, "Ceramic Plant Pots (set of 4)", "Home & Living", "New", "Leather jacket or fashion", 1200, "Handmade pots with bamboo stands.", "pots"),
]
# (requester idx, offered item idx, target item idx, status, note, reply from owner or None)
# Rule: requester owns the offered item; target belongs to someone else.
SWAPS = [
 (1, 1, 0, "pending", "Hi! Would love your guitar for my DSLR.", None),
 (2, 2, 8, "pending", "Treadmill for the bike?", None),
 (4, 14, 7, "accepted", "Air fryer for your pressure cooker?", "Sounds great, let's meet this weekend."),
 (0, 0, 3, "rejected", "Guitar for the books?", None),
 (3, 13, 6, "completed", "Swapped tablet for keyboard!", "Done, thanks! Enjoy the tablet."),
]

def repair_invalid_swaps(db):
    n = 0
    for s in db.scalars(select(SwapRequest)).all():
        t, o = db.get(Item, s.target_item_id), db.get(Item, s.offered_item_id)
        if (o.owner_id != s.requester_id or t.owner_id == s.requester_id or t.owner_id != s.owner_id):
            for c in db.scalars(select(Conversation).where(Conversation.swap_id == s.id)).all():
                for m in db.scalars(select(Message).where(Message.conversation_id == c.id)).all(): db.delete(m)
                db.delete(c)
            db.delete(s); n += 1
    return n

def main():
    Base.metadata.create_all(engine); generate()
    db = SessionLocal(); made = {"users": 0, "items": 0, "swaps": 0}
    try:
        fixed = repair_invalid_swaps(db); db.flush()
        users = []
        for name, email, city in USERS:
            u = db.scalar(select(User).where(User.email == email))
            if not u:
                u = User(name=name, email=email, location=city, password_hash=hash_pw("zwyp1234"), bio="Swapping things I no longer need.")
                db.add(u); db.flush(); made["users"] += 1
            users.append(u)
        items = []
        for o, title, cat, cond, wants, val, desc, slug in ITEMS:
            it = db.scalar(select(Item).where(Item.owner_id == users[o].id, Item.title == title))
            if not it:
                it = Item(owner_id=users[o].id, title=title, category=cat, condition=cond, location=users[o].location, wants=wants,
                          value_inr=val, description=desc, image_url=f"/static/seed/{slug}.svg")
                db.add(it); db.flush(); made["items"] += 1
            elif it.image_url.startswith("https://picsum.photos"): it.image_url = f"/static/seed/{slug}.svg"
            items.append(it)
        for r, off, tgt, status, note, reply in SWAPS:
            req, offered, target = users[r], items[off], items[tgt]
            assert offered.owner_id == req.id and target.owner_id != req.id, f"invalid seed swap {(r, off, tgt)}"
            if db.scalar(select(SwapRequest).where(SwapRequest.requester_id == req.id, SwapRequest.target_item_id == target.id, SwapRequest.offered_item_id == offered.id)): continue
            s = SwapRequest(requester_id=req.id, owner_id=target.owner_id, target_item_id=target.id, offered_item_id=offered.id, status=status, note=note)
            db.add(s); db.flush(); c = Conversation(swap_id=s.id); db.add(c); db.flush()
            db.add(Message(conversation_id=c.id, sender_id=req.id, body=note))
            if reply: db.add(Message(conversation_id=c.id, sender_id=target.owner_id, body=reply))
            if status == "completed": offered.status = target.status = "swapped"
            made["swaps"] += 1
        db.commit()
    except Exception:
        db.rollback(); raise
    finally: db.close()
    print(f"Seed complete. Created {made}; removed {fixed} invalid legacy swap(s). Safe to re-run.")
    print("Demo login: aarav@zwyp.demo / zwyp1234")
if __name__ == "__main__": main()