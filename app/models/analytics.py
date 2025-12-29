from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/revenue-at-risk")
def revenue_at_risk(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            SUM(mrr * churn_probability) AS expected_mrr_loss,
            SUM(mrr) AS total_mrr
        FROM analytics_latest_churn
    """)
    result = db.execute(query).fetchone()

    return {
        "expected_mrr_loss": round(result.expected_mrr_loss or 0, 2),
        "total_mrr": round(result.total_mrr or 0, 2),
        "risk_ratio": round(
            (result.expected_mrr_loss / result.total_mrr) if result.total_mrr else 0,
            2
        )
    }
