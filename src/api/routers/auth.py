"""
Authentication Router for KOSMOS API.
Handles user registration, login, and API key management.
"""
import uuid
import logging
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from src.services.auth_service import (
    get_auth_service,
    AuthService,
    UserCreate,
    UserLogin,
    TokenResponse,
    UserRole,
)
from src.services.api_key_service import (
    get_api_key_service,
    APIKeyService,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyInfo,
)
from src.api.auth_deps import get_current_user, require_permission
from src.services.auth_service import Permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user store for MVP (use database in production)
_users_db = {}


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user."""
    # Check if user exists
    if user_data.email in _users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = auth_service.hash_password(user_data.password)

    _users_db[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": hashed_password,
        "roles": [r.value for r in user_data.roles],
        "created_at": datetime.now(timezone.utc),
    }

    logger.info(f"User registered: {user_data.email}")

    # Generate tokens
    return auth_service.create_tokens(
        user_id=user_id,
        email=user_data.email,
        roles=[r.value for r in user_data.roles],
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login and get access tokens."""
    user = _users_db.get(credentials.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not auth_service.verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    logger.info(f"User logged in: {credentials.email}")

    return auth_service.create_tokens(
        user_id=user["id"],
        email=user["email"],
        roles=user["roles"],
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh access token using refresh token."""
    payload = auth_service.decode_token(refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Get user to verify still exists and get current roles
    user = _users_db.get(payload.get("email"))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return auth_service.create_tokens(
        user_id=user["id"],
        email=user["email"],
        roles=user["roles"],
    )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
):
    """Get current user information."""
    return {
        "user_id": current_user.get("sub"),
        "email": current_user.get("email"),
        "roles": current_user.get("roles"),
        "permissions": current_user.get("permissions"),
    }


# API Key Management

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: dict = Depends(get_current_user),
    api_key_service: APIKeyService = Depends(get_api_key_service),
):
    """Create a new API key for the current user."""
    return api_key_service.create_key(
        owner_id=current_user.get("sub"),
        name=key_data.name,
        scopes=key_data.scopes,
        expires_in_days=key_data.expires_in_days,
    )


@router.get("/api-keys", response_model=List[APIKeyInfo])
async def list_api_keys(
    current_user: dict = Depends(get_current_user),
    api_key_service: APIKeyService = Depends(get_api_key_service),
):
    """List all API keys for the current user."""
    return api_key_service.list_keys(current_user.get("sub"))


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user),
    api_key_service: APIKeyService = Depends(get_api_key_service),
):
    """Revoke an API key."""
    success = api_key_service.revoke_key(key_id, current_user.get("sub"))

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return {"message": "API key revoked"}
