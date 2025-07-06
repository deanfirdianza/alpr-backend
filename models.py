from sqlalchemy import Column, Integer, String, DateTime, Date
from database import Base
from datetime import datetime

class PlateRegistry(Base):
    __tablename__ = "plate_registry"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True)
    expired_at = Column(Date)
    tax_status = Column(String)
    last_checked = Column(DateTime, default=datetime.utcnow)

class ScanHistory(Base):
    __tablename__ = "scan_history"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence = Column(String)