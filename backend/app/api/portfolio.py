from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.snapshot import PortfolioSnapshot
from app.models.position import SnapshotPosition

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"]
)

@router.get("/dashboard")
def get_dashboard():
    db: Session = SessionLocal()

    snapshot = (
        db.query(PortfolioSnapshot)
        .order_by(PortfolioSnapshot.snapshot_date.desc())
        .first()
    )

    if not snapshot:
        return {"positions": []}

    positions = (
        db.query(SnapshotPosition)
        .filter(SnapshotPosition.snapshot_id == snapshot.id)
        .all()
    )

    total_value = sum(
        float(p.reported_market_value or 0) for p in positions
    )

    result = []
    for p in positions:
        value = float(p.reported_market_value or 0)
        result.append({
            "symbol": p.symbol,
            "name": p.name,
            "asset_class": p.asset_class,
            "sector": p.sector or "Unknown",
            "market_value": value,
            "weight": round(value / total_value * 100, 2) if total_value else 0,
        })

    db.close()
    return {
        "snapshot_date": snapshot.snapshot_date,
        "positions": result,
    }
