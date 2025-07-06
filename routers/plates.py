from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
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
def get_plates(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    plates = db.query(PlateRegistry).offset(skip).limit(limit).all()
    return plates
