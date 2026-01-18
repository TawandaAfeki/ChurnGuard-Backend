from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Clients(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # USER-ENTERED DATA (Settings / Add Customer)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    mrr = Column(Numeric(10, 2), nullable=False)
    contract_end = Column(Date, nullable=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    company = relationship("Company")
