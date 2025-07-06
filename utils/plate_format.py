import re

def format_plate(plate_raw):
    match = re.match(r"^([A-Z]{1,2})(\d{1,4})([A-Z]{1,3})$", plate_raw)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return plate_raw
