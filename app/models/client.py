from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Client(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    mrr = Column(Numeric(10, 2))
    health_score = Column(Integer)
    risk_level = Column(String)
    last_active = Column(Date)
    contract_end = Column(Date)
    actions = Column(String)
    
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    company = relationship("Company")

