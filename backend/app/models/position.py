from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey
from app.core.database import Base

class SnapshotPosition(Base):
    __tablename__ = "snapshot_positions"

    id = Column(String, primary_key=True)
    snapshot_id = Column(String, ForeignKey("portfolio_snapshots.id"), nullable=False)
    symbol = Column(String, nullable=False)
    isin = Column(String)
    name = Column(String)
    asset_class = Column(String)
    quantity = Column(Numeric(18, 6))
    reported_market_value = Column(Numeric(18, 2))
    currency = Column(String)
    is_fractional = Column(Boolean, default=False)
    sector = Column(String, nullable=True)

