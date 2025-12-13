from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, ARRAY, TIMESTAMP
from .database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company_name = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    email = Column(String)
    mrr = Column(Numeric(10,2))
    health_score = Column(Integer)
    risk_level = Column(String)
    last_active = Column(Date)
    contract_end = Column(Date)
    actions = Column(ARRAY(String))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
