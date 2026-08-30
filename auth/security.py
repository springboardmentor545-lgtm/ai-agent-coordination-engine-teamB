import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from config.settings import JWT_SECRET

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 8


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(employee_id: str) -> str:
    """Create a signed JWT containing the employee_id, expiring in JWT_EXPIRY_HOURS."""
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    payload = {
        "employee_id": employee_id,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    Verify a JWT's signature and expiry, and return the employee_id inside it.
    Raises jwt.InvalidTokenError (or a subclass) if the token is invalid or expired.
    """
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload["employee_id"]