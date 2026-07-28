import re

def validate_phone(phone: str) -> bool:
    # Basic regex for phone numbers (adjust as needed)
    pattern = re.compile(r'^\+?[\d\s\-\$\$]{10,}$')
    return bool(phone and pattern.match(phone))

def validate_email(email: str) -> bool:
    pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    return bool(email and pattern.match(email))