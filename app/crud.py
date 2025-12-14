from sqlalchemy.orm import Session
from app import models, schemas, auth


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(
        models.User.email == email
    ).first()


def create_user(db: Session, user: schemas.UserCreate):
    # --------------------
    # 1. Find or create company (REQUIRED)
    # --------------------
    if not user.company_name:
        raise ValueError("company_name is required")

    company = db.query(models.Company).filter(
        models.Company.name == user.company_name
    ).first()

    if not company:
        company = models.Company(name=user.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    # --------------------
    # 2. Create user
    # --------------------
    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=auth.hash_password(user.password),
        company_id=company.id,   # ✅ ALWAYS SET
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


