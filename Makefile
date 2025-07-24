# Makefile for ALPR Backend (local dev)

VENV_DIR=venv
PYTHON=$(VENV_DIR)/bin/python
PIP=$(VENV_DIR)/bin/pip
ACTIVATE=. $(VENV_DIR)/bin/activate

# Setup virtualenv and install dependencies
setup:
	python -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Start Docker-based Postgres DB
db-up:
	docker run --name alpr-postgres \
		-e POSTGRES_USER=user \
		-e POSTGRES_PASSWORD=pass \
		-e POSTGRES_DB=alpr \
		-p 5432:5432 \
		-d postgres:14

# Stop and remove DB container
db-down:
	docker rm -f alpr-postgres

# Create DB tables from models
migrate:
	$(ACTIVATE); \
	python -c "from database import Base, engine; import models; Base.metadata.create_all(bind=engine)"

# Import CSV plate registry
import:
	$(ACTIVATE); \
	PYTHONPATH=. python scripts/import_plate_registry.py

# Run FastAPI dev server
run:
	$(ACTIVATE); \
	uvicorn main:app --reload

# Clean Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
