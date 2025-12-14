from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas, auth


def get_user_by_email(db: Session, email: str):
    return (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )


def create_user(db: Session, user: schemas.UserCreate):
    # --------------------
    # 1. Find or create company (REQUIRED)
    # --------------------
    if not user.company_name:
        raise ValueError("company_name is required")

    company = (
        db.query(models.Company)
        .filter(models.Company.name == user.company_name)
        .first()
    )

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

def generate_alerts_for_company(db: Session, company_id: int):
    db.execute(text("""
        INSERT INTO alerts (
            user_id,
            client_id,
            alert_type,
            priority,
            title,
            description
        )
        SELECT
            u.id,
            c.id,
            'high_risk',
            'high',
            'Customer at high risk',
            'Health score below 40'
        FROM customers c
        JOIN users u ON u.company_id = c.company_id
        JOIN health_scores hs ON hs.client_id = c.id
        WHERE c.company_id = :company_id
          AND hs.score < 40
          AND NOT EXISTS (
              SELECT 1 FROM alerts a
              WHERE a.client_id = c.id
                AND a.alert_type = 'high_risk'
                AND a.status = 'active'
          )
    """), {"company_id": company_id})

    db.commit()


def get_active_alerts_for_user(db: Session, user_id: int):
    return (
        db.query(models.Alert)
        .filter(
            models.Alert.user_id == user_id,
            models.Alert.status == "active",
        )
        .order_by(
            models.Alert.priority.desc(),
            models.Alert.created_at.desc(),
        )
        .all()
    )


def get_customers_dashboard(db: Session, company_id: int):
    result = db.execute(
        text("""
            SELECT
                c.id,
                c.name,
                c.email,
                c.mrr,
                c.contract_end AS contract_end_date,
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
        """),
        {"company_id": company_id},
    )

    return result.mappings().all()

def get_churn_trend(db: Session, company_id: int):
    result = db.execute(
        text("""
            SELECT
                date_trunc('month', hs.calculated_at) AS month,
                COUNT(*) FILTER (WHERE hs.risk_level = 'high')   AS high,
                COUNT(*) FILTER (WHERE hs.risk_level = 'medium') AS medium,
                COUNT(*) FILTER (WHERE hs.risk_level = 'low')    AS low
            FROM health_scores hs
            JOIN customers c ON c.id = hs.client_id
            WHERE c.company_id = :company_id
            GROUP BY month
            ORDER BY month
        """),
        {"company_id": company_id},
    )

    return result.mappings().all()

