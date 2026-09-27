"""
Auth dependency for protected routes.

The frontend logs in via Supabase Auth (client-side) and sends the resulting
access token as `Authorization: Bearer <token>` on every request to our API.
This dependency asks Supabase to validate that token and returns the user id,
so route handlers can scope data (documents, chunks) to the current user.
"""
from fastapi import Header, HTTPException
from app.services.storage import get_client


async def get_current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing or malformed Authorization header")

    token = authorization.split(" ", 1)[1].strip()
    client = get_client()

    try:
        result = client.auth.get_user(token)
    except Exception as exc:
        raise HTTPException(401, f"Invalid or expired session: {exc!r}") from exc

    if not result or not result.user:
        raise HTTPException(401, "Invalid or expired session")

    return result.user.id
