import sys
import os
import csv
import time
from datetime import datetime
from database import SessionLocal  # assume get_db is a function that returns a database session
from models import PlateRegistry
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

BATCH_SIZE = 5000
CSV_PATH = "license-data.csv"  # default from config

def import_csv_to_db_in_batches(csv_path: str = CSV_PATH):
    start_time = time.time()
    db: Session = SessionLocal()
    batch = []
    total = 0

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            plate_number = row["license_plate"].strip().upper()
            expired_at = datetime.strptime(row["expired_at"], "%Y-%m-%d").date()

            plate = {
                "plate_number": plate_number,
                "expired_at": expired_at,
                "tax_status": "Tidak Teridentifikasi",
                "last_checked": None,
            }
            batch.append(plate)

            if len(batch) >= BATCH_SIZE:
                stmt = insert(PlateRegistry).values(batch)
                stmt = stmt.on_conflict_do_nothing(index_elements=["plate_number"])
                db.execute(stmt)
                db.commit()
                total += len(batch)
                print(f"Committed {total} records...")
                batch.clear()

        if batch:
            stmt = insert(PlateRegistry).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["plate_number"])
            db.execute(stmt)
            db.commit()
            total += len(batch)
            print(f"Final commit of {len(batch)} records. Total: {total}")

    print(f"Import completed in {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    import_csv_to_db_in_batches()