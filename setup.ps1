# setup.ps1 — ALPR Backend Automation Script (Windows)

# ========== Config ==========
$VenvPath = "venv"
$PythonExe = "$VenvPath\Scripts\python.exe"
$PipExe = "$VenvPath\Scripts\pip.exe"
$ActivateCmd = "$VenvPath\Scripts\Activate.ps1"

# ========== Helper ==========
function Check-Command {
    param($cmd)
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "$cmd is not installed or not in PATH"
        exit 1
    }
}

# ========== Commands ==========
function Setup-Venv {
    if (-not (Test-Path $VenvPath)) {
        python -m venv $VenvPath
    }
    & $PipExe install --upgrade pip
    & $PipExe install -r requirements.txt
}

function Start-DB {
    docker run --name alpr-postgres `
        -e POSTGRES_USER=user `
        -e POSTGRES_PASSWORD=pass `
        -e POSTGRES_DB=alpr `
        -p 5432:5432 `
        -d postgres:14
}

function Stop-DB {
    docker rm -f alpr-postgres
}

function Migrate-DB {
    & $PythonExe -c "from database import Base, engine; import models; Base.metadata.create_all(bind=engine)"
}

function Import-CSV {
    $env:PYTHONPATH = "."
    & $PythonExe scripts/import_plate_registry.py
}

function Run-App {
    & "$VenvPath\Scripts\uvicorn.exe" main:app --reload
}

function Clean-Pycache {
    Get-ChildItem -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force
}

# ========== Main ==========
param (
    [string]$task = ""
)

switch ($task) {
    "setup" { Setup-Venv }
    "db-up" { Start-DB }
    "db-down" { Stop-DB }
    "migrate" { Migrate-DB }
    "import" { Import-CSV }
    "run" { Run-App }
    "clean" { Clean-Pycache }
    default {
        Write-Host "Usage: .\setup.ps1 [setup|db-up|db-down|migrate|import|run|clean]"
    }
}
