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

exit venv
>>> deactivate

install req
>>>pip install -r requirements.txt

---
ps1

.\setup.ps1 setup       # Setup venv + install pip requirements
.\setup.ps1 db-up       # Start Docker DB
.\setup.ps1 migrate     # Create tables
.\setup.ps1 import      # Import license-data.csv
.\setup.ps1 run         # Start FastAPI app
.\setup.ps1 db-down     # Stop and remove DB
.\setup.ps1 clean       # Remove __pycache__ folders
