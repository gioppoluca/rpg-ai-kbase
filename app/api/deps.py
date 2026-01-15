from fastapi import Header, HTTPException

from app.core.config import settings


def require_api_key(authorization: str | None = Header(default=None)):
    """Optional simple bearer auth.

    If SETTINGS.api_key is set, requests must include:
      Authorization: Bearer <key>
    """
    if not settings.api_key:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid token")
