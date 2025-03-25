from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class PortfolioCreate(BaseModel):
    title: str
    description: Optional[str] = None

class PortfolioResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
