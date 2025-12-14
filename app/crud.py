from sqlalchemy.orm import Session
from app import models, schemas, auth

def create_user(db: Session, user: schemas.UserCreate):
    # 1. Find or create company
    company = None
    if user.company_name:
        company = db.query(models.Company).filter(
            models.Company.name == user.company_name
        ).first()

        if not company:
            company = models.Company(name=user.company_name)
            db.add(company)
            db.commit()
            db.refresh(company)

    # 2. Create user
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=auth.hash_password(user.password),
        company_id=company.id if company else None
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


