"""FastAPI dependencies for authentication and CORS."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException, Request, status

from src.integrations.firebase.auth import verify_id_token


async def require_auth(request: Request) -> dict[str, Any]:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )
    token = auth_header[7:]
    return verify_id_token(token)


async def optional_auth(request: Request) -> Optional[dict[str, Any]]:
    try:
        return await require_auth(request)
    except HTTPException:
        return None
