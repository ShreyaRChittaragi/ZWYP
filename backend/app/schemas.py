from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
class Cfg(BaseModel): model_config = ConfigDict(from_attributes=True)
class UserOut(Cfg):
    id: int; name: str; email: str; location: str; bio: str
class Register(BaseModel):
    name: str = Field(min_length=2, max_length=80); email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=6, max_length=72); location: str = ""
class Login(BaseModel): email: str; password: str
class ItemOut(Cfg):
    id: int; owner_id: int; title: str; description: str; category: str; condition: str
    location: str; wants: str; image_url: str; value_inr: int; status: str; owner: UserOut
class SwapIn(BaseModel):
    target_item_id: int; offered_item_id: int; note: str = Field(default="", max_length=500)
class SwapOut(Cfg):
    id: int; status: str; note: str; created_at: datetime; requester: UserOut; owner: UserOut
    target_item: ItemOut; offered_item: ItemOut
class MsgIn(BaseModel): body: str = Field(min_length=1, max_length=1000)
class MsgOut(Cfg):
    id: int; sender_id: int; body: str; created_at: datetime