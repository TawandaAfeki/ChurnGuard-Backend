from app import models
from app.auth import hash_password

def create_user(db, user):
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

    db_user = models.User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),
        company_id=company.id
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user



