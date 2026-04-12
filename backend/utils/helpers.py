import re

# Check valid email
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


# Check password strength
def is_strong_password(password):
    return len(password) >= 6


# Response message format
def success_message(msg):
    return {"success": True, "message": msg}


def error_message(msg):
    return {"success": False, "message": msg}