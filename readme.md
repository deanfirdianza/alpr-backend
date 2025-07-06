Run Docker to setup DB

>>> docker run --name alpr-postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=alpr -p 5432:5432 -d postgres:14


Once DB is running, run this in Python:

python
>>> from database import Base, engine
>>> import models
>>> Base.metadata.create_all(bind=engine)
>>> exit()

run venv
source venv/bin/activate

Put license-data.csv on root

Run this
uvicorn main:app --reload

Check it live on
http://127.0.0.1:8000/docs#/

migrate data using
PYTHONPATH=. python scripts/import_plate_registry.py
