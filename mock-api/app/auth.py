import os

from fastapi import Header, HTTPException

EXPECTED_TOKEN = os.getenv("MOCK_API_TOKEN", "techcorp-mock-token-2025")

def verify_token(authorization: str | None = Header(default=None)):
    if authorization != f"Bearer {EXPECTED_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "message": "Missing or invalid authorization token"},
        )