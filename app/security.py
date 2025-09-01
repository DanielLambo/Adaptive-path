# app/security.py
"""
API Security and Authentication

This module provides a simple bearer token authentication scheme for securing API endpoints.

Note: This is a basic security implementation suitable for internal testing.
For production, this should be replaced with a robust OAuth2 or LTI 1.3 implementation.
"""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# Environment variable for the static bearer token
API_TOKEN = os.getenv("API_STATIC_TOKEN", "a-secure-static-token")

# Define the header scheme
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def check_bearer_token(token: str = Depends(api_key_header)):
    """
    Dependency to validate the bearer token.

    The token should be provided in the 'Authorization' header like:
    Authorization: Bearer <your-token>
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )

    # Split "Bearer <token>"
    try:
        scheme, _, value = token.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer'.",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format.",
        )

    if value != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token",
        )

    return True
