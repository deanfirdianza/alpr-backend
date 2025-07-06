import csv
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models import PlateRegistry
import config

def run_import():
    db: Session = SessionLocal()
    with open(config.CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            plate_number = row["license_plate"].strip().upper()
            expired_at = datetime.strptime(row["expired_at"], "%Y-%m-%d").date()

            db_plate = PlateRegistry(
                plate_number=plate_number,
                expired_at=expired_at,
                tax_status="unknown",  # Can be updated during scan
                last_checked=None
            )

            db.merge(db_plate)  # Upsert logic
    db.commit()
    db.close()
    print("✅ Imported CSV to plate_registry")

if __name__ == "__main__":
    run_import()
