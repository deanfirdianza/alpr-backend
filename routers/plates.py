from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import SessionLocal
from models import PlateRegistry

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/plates")
def get_plates(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str = "",
    tax_status: str = "",
    db: Session = Depends(get_db),
):
    query = db.query(PlateRegistry)

    # Apply search filter (plate number or registered owner)
    if search:
        query = query.filter(
            or_(
                PlateRegistry.plate_number.ilike(f"%{search}%"),
                PlateRegistry.registered_owner.ilike(f"%{search}%")
            )
        )

    # Filter by tax status if specified
    if tax_status:
        query = query.filter(PlateRegistry.tax_status.ilike(tax_status.lower()))

    # Get total count for pagination
    total = query.with_entities(func.count()).scalar()

    # Apply pagination
    results = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [r.__dict__ for r in results],
        "total": total
    }
