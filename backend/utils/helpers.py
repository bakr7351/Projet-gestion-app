import re


# RFC 5322 simplified — rejects most invalid formats
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def is_valid_email(email: str) -> bool:
    """Return True if email matches RFC 5322 simplified pattern."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def is_strong_password(password: str) -> bool:
    """Return True if password is at least 8 characters."""
    return isinstance(password, str) and len(password) >= 8


def success_response(msg: str, data: dict = None) -> dict:
    resp = {"success": True, "message": msg}
    if data:
        resp.update(data)
    return resp


def error_response(msg: str) -> dict:
    return {"success": False, "message": msg}
