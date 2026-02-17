from fastapi import APIRouter, HTTPException
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.snapshot import PortfolioSnapshot
from app.models.position import SnapshotPosition

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("/latest/asset-class-allocation")
def latest_asset_class_allocation():
    db = SessionLocal()

    try:
        # 1. Get latest snapshot
        snapshot = (
            db.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.snapshot_date.desc())
            .first()
        )

        if not snapshot:
            raise HTTPException(status_code=404, detail="No snapshots found")

        # 2. Aggregate market value by asset class
        rows = (
            db.query(
                SnapshotPosition.asset_class,
                func.sum(SnapshotPosition.reported_market_value).label("total_value"),
            )
            .filter(SnapshotPosition.snapshot_id == snapshot.id)
            .group_by(SnapshotPosition.asset_class)
            .all()
        )

        total_value = sum(row.total_value for row in rows)

        if total_value == 0:
            raise HTTPException(status_code=400, detail="Portfolio value is zero")

        # 3. Convert to percentages
        result = [
            {
                "asset_class": row.asset_class,
                "value": round(float(row.total_value / total_value * 100), 2),
            }
            for row in rows
        ]

        return result

    finally:
        db.close()
