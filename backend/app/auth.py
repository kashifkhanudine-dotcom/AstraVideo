from __future__ import annotations

from fastapi import Header, HTTPException

from .config import settings


async def get_current_user(authorization: str | None = Header(default=None)) -> dict[str, str]:
    if not settings.require_auth:
        return {"uid": "demo-user", "email": "demo@astravideo.local"}

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        import firebase_admin
        from firebase_admin import auth

        if not firebase_admin._apps:
            firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id or None})
        decoded = auth.verify_id_token(token)
        return {"uid": decoded["uid"], "email": decoded.get("email", "")}
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid Firebase token") from exc
