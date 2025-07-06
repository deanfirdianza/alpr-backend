from fastapi import APIRouter
from detector import run_single_scan
from gov_data.checker import get_tax_status

router = APIRouter()

@router.post("/scan")
def scan_plate():
    plate_data = run_single_scan()
    tax_status = get_tax_status(plate_data["plate_number"])
    return tax_status
