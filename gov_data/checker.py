from sqlalchemy.orm import Session
from database import SessionLocal
from models import PlateRegistry
from datetime import date

def get_tax_status(plate_number: str) -> str:
    db: Session = SessionLocal()
    plate = db.query(PlateRegistry).filter_by(plate_number=plate_number.upper()).first()
    db.close()
    
    if not plate:
        return "not found"
    
    return "paid" if plate.expired_at >= date.today() else "unpaid"
