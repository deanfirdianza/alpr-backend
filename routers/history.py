from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import SessionLocal
from datetime import datetime
from models import ScanHistory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    plate: str = "",
    date_from: str = "",
    date_to: str = "",
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    query = db.query(ScanHistory)

    # Filter by plate substring
    if plate:
        query = query.filter(ScanHistory.plate_number.ilike(f"%{plate}%"))

    # Filter by date range
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.filter(ScanHistory.timestamp >= dt_from)
        except ValueError:
            pass  # Ignore invalid date

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.filter(ScanHistory.timestamp <= dt_to)
        except ValueError:
            pass

    # Get total count before pagination
    total = query.with_entities(func.count()).scalar()

    # Apply pagination
    results = query.order_by(ScanHistory.timestamp.desc()) \
                   .offset((page - 1) * per_page) \
                   .limit(per_page) \
                   .all()

    # Return raw dicts (or define your Pydantic models if desired)
    return {
        "items": [r.__dict__ for r in results],
        "total": total
    }

