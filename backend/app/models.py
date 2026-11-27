from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
now = lambda: datetime.utcnow()
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(80), default="")
    bio: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(40), index=True)
    condition: Mapped[str] = mapped_column(String(30))
    location: Mapped[str] = mapped_column(String(80), index=True)
    wants: Mapped[str] = mapped_column(String(200))
    image_url: Mapped[str] = mapped_column(String(300), default="")
    value_inr: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="available")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    owner: Mapped[User] = relationship()
class SwapRequest(Base):
    __tablename__ = "swap_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    target_item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    offered_item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now, onupdate=now)
    requester: Mapped[User] = relationship(foreign_keys=[requester_id])
    owner: Mapped[User] = relationship(foreign_keys=[owner_id])
    target_item: Mapped[Item] = relationship(foreign_keys=[target_item_id])
    offered_item: Mapped[Item] = relationship(foreign_keys=[offered_item_id])
class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    swap_id: Mapped[int] = mapped_column(ForeignKey("swap_requests.id"), unique=True)
    swap: Mapped[SwapRequest] = relationship()
class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
