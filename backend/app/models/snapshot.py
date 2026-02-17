from sqlalchemy import Column, String, Date, Numeric
from app.core.database import Base

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(String, primary_key=True)
    snapshot_date = Column(Date, nullable=False)
    account_currency = Column(String, nullable=False)
    reported_account_value = Column(Numeric(18, 2))
    reported_cash = Column(Numeric(18, 2))
    source_file_hash = Column(String, unique=True, nullable=False)
