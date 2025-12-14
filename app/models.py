from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    ForeignKey,
    Text,
    TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from .database import Base


# --------------------
# Company
# --------------------
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# --------------------
# User
# --------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# --------------------
# Customer
# --------------------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    name = Column(String, nullable=False)
    email = Column(String)
    mrr = Column(Numeric(10, 2))
    contract_end = Column(Date)
    status = Column(String)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# --------------------
# Alert
# --------------------
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    client_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))

    alert_type = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="active")

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

