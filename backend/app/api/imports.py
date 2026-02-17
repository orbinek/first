from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import uuid

from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.models.snapshot import PortfolioSnapshot
from app.models.position import SnapshotPosition
from app.services.hash_service import hash_file
from app.importer.xtb_pdf_importer import parse_xtb_pdf

router = APIRouter()


@router.post("/pdf")
async def import_pdf(file: UploadFile = File(...)):
    content = await file.read()
    file_hash = hash_file(content)

    db = SessionLocal()

    try:
        # 1. Prevent duplicate imports EARLY
        existing = (
            db.query(PortfolioSnapshot)
            .filter_by(source_file_hash=file_hash)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="This PDF has already been imported"
            )

        # 2. Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # 3. Parse PDF
        parsed = parse_xtb_pdf(tmp_path)

        # 4. Validate required metadata
        required_fields = ["snapshot_date", "account_currency"]
        missing = [f for f in required_fields if not parsed.get(f)]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required snapshot metadata: {', '.join(missing)}"
            )

        # 5. Create snapshot
        snapshot_id = str(uuid.uuid4())
        snapshot = PortfolioSnapshot(
            id=snapshot_id,
            snapshot_date=parsed["snapshot_date"],
            account_currency=parsed["account_currency"],
            reported_account_value=parsed.get("reported_account_value"),
            reported_cash=parsed.get("reported_cash"),
            source_file_hash=file_hash,
        )

        db.add(snapshot)
        db.flush()  # ensures FK availability

        # 6. Insert positions
        for pos in parsed["positions"]:
            db.add(SnapshotPosition(snapshot_id=snapshot_id, **pos))

        db.commit()

        return {
            "snapshot_id": snapshot_id,
            "positions_imported": len(parsed["positions"]),
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This PDF has already been imported"
        )

    finally:
        db.close()
