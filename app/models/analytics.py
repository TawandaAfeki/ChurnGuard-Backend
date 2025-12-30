from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/revenue-at-risk")
def revenue_at_risk(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT
            SUM(mrr * churn_probability) AS expected_mrr_loss,
            SUM(mrr) AS total_mrr
        FROM analytics_latest_churn
    """)).fetchone()

    return {
        "expected_mrr_loss": round(result.expected_mrr_loss or 0, 2),
        "total_mrr": round(result.total_mrr or 0, 2),
        "risk_ratio": round(
            (result.expected_mrr_loss / result.total_mrr) if result.total_mrr else 0,
            2
        )
    }


@router.get("/risk-momentum")
def risk_momentum(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT
            c.id,
            c.name,
            r.delta_churn
        FROM analytics_risk_momentum r
        JOIN customers c ON c.id = r.client_id
        ORDER BY r.delta_churn DESC
    """)).fetchall()

    return [
  {
    "customer": row.name,
    "trend": (
      "deteriorating" if row.delta_churn > 0.1
      else "improving" if row.delta_churn < -0.1
      else "stable"
    ),
    "delta": round(row.delta_churn, 2),
    "revenue_at_risk": round(row.mrr * row.churn_probability, 2)
  }
  for row in rows
]



@router.post("/simulate-churn")
def simulate_churn(
    client_id: int,
    login_delta: int = 0,
    ticket_delta: int = 0,
    payment_fix: bool = False,
    db: Session = Depends(get_db)
):
    row = db.execute(text("""
        SELECT churn_probability::float
        FROM analytics_latest_churn
        WHERE client_id = :client_id
    """), {"client_id": client_id}).fetchone()

    churn = row.churn_probability

    churn -= login_delta * 0.02
    churn += ticket_delta * 0.03
    if payment_fix:
        churn -= 0.15

    churn = max(0, min(1, churn))

    return {
        "current": row.churn_probability,
        "simulated": round(churn, 2),
        "impact": round(row.churn_probability - churn, 2)
    }
