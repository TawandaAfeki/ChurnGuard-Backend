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

def get_active_alerts_for_user(db: Session, user_id: int):
    return (
        db.query(models.Alert)
        .filter(
            models.Alert.user_id == user_id,
            models.Alert.status == "active"
        )
        .order_by(models.Alert.priority.desc(), models.Alert.created_at.desc())
        .all()
    )

def get_customers_dashboard(db: Session, company_id: int):
    return db.execute("""
        SELECT
            c.id,
            c.name,
            c.email,
            c.mrr,
            c.contract_end_date,
            c.status,

            hs.score AS health_score,
            hs.risk_level,

            cm.last_login_at,
            cm.support_tickets_count,
            cm.features_used,
            cm.payment_status

        FROM customers c

        LEFT JOIN LATERAL (
            SELECT *
            FROM health_scores
            WHERE client_id = c.id
            ORDER BY calculated_at DESC
            LIMIT 1
        ) hs ON true

        LEFT JOIN LATERAL (
            SELECT *
            FROM customer_metrics
            WHERE client_id = c.id
            ORDER BY metric_date DESC
            LIMIT 1
        ) cm ON true

        WHERE c.company_id = :company_id
        ORDER BY c.name;
    """, {"company_id": company_id}).mappings().all()


