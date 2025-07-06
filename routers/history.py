from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ScanHistory

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(ScanHistory).order_by(ScanHistory.timestamp.desc()).all()
