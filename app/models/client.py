# app/models/client.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    name = Column(String, nullable=False)
    email = Column(String)
    mrr = Column(Float)
    health_score = Column(Integer)
    risk_level = Column(String)
    contract_end = Column(Date)

    company = relationship("Company")
