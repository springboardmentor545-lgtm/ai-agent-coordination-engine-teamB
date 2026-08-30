from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from auth.security import decode_access_token

security_scheme = HTTPBearer()


def get_current_employee(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """
    FastAPI dependency: reads the Authorization: Bearer <token> header,
    verifies the JWT, and returns the trusted employee_id from inside it.
    Raises 401 if the token is missing, invalid, or expired.
    """
    token = credentials.credentials
    try:
        employee_id = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return employee_id