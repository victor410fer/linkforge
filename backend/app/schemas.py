from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import pydantic

# Compatibility helper for Pydantic v1/v2
if pydantic.__version__.startswith('2'):
    model_config = {'from_attributes': True}
else:
    model_config = {'orm_mode': True}

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    is_pro: bool
    created_at: datetime
    class Config:
        orm_mode = True
    # For v2 compatibility (ignored in v1)
    model_config = model_config

class LinkCreate(BaseModel):
    url: str
    custom_slug: Optional[str] = None

class LinkOut(BaseModel):
    id: int
    slug: str
    original_url: str
    clicks: int
    created_at: datetime
    class Config:
        orm_mode = True
    model_config = model_config

class LinkDetail(LinkOut):
    short_url: str

class SubscribeRequest(BaseModel):
    plan: str
