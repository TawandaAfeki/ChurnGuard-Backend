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
    email: Optional[EmailStr] = None
    mrr: float
    contract_start_date: Optional[date] = None
    contract_end: Optional[date] = None


class ClientOut(ClientCreate):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

from datetime import datetime

class AlertOut(BaseModel):
    id: str
    alert_type: str
    priority: str
    title: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True

class CustomerDashboardOut(BaseModel):
    id: int
    name: str
    email: str | None
    mrr: float
    contract_end_date: date | None
    status: str

    health_score: int | None
    risk_level: str | None

    last_login_at: datetime | None
    support_tickets_count: int | None
    features_used: int | None
    payment_status: str | None
