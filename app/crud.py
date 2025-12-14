from app import models
from app.auth import hash_password

def create_user(db, user):
    # Find existing company
    company = db.query(models.Company).filter(
        models.Company.name == user.company_name
    ).first()

    # Create company if it doesn't exist
    if not company:
        company = models.Company(name=user.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    # Create user
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



