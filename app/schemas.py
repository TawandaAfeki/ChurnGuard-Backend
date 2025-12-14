from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    company_name: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    company_id: int

    class Config:
        from_attributes = True

class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr]
    mrr: Optional[float]
    health_score: Optional[int]
    risk_level: Optional[str]
    last_active: Optional[date]
    contract_end: Optional[date]
    actions: Optional[List[str]] = []

class ClientOut(ClientCreate):
    id: int
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

