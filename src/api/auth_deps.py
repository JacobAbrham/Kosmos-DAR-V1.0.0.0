"""
FastAPI Authentication Dependencies.
Provides JWT authentication middleware and dependencies.
"""
import logging
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.services.auth_service import (
    get_auth_service,
    AuthService,
    Permission,
    UserRole,
)

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Dependency to get the current authenticated user.
    Raises 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = auth_service.decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[dict]:
    """
    Dependency to optionally get the current user.
    Returns None if not authenticated.
    """
    if credentials is None:
        return None

    payload = auth_service.decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        return None

    return payload


def require_permission(permission: Permission):
    """
    Dependency factory to require a specific permission.
    Usage: @app.get("/admin", dependencies=[Depends(require_permission(Permission.ADMIN_USERS))])
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        if not auth_service.has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required",
            )
        return current_user

    return permission_checker


def require_role(role: UserRole):
    """
    Dependency factory to require a specific role.
    Usage: @app.get("/admin", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    async def role_checker(
        current_user: dict = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        if not auth_service.has_role(current_user, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role denied: {role.value} required",
            )
        return current_user

    return role_checker


def require_any_role(roles: List[UserRole]):
    """
    Dependency factory to require any of the specified roles.
    """
    async def role_checker(
        current_user: dict = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service),
    ):
        for role in roles:
            if auth_service.has_role(current_user, role):
                return current_user

        role_names = [r.value for r in roles]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of these roles required: {role_names}",
        )

    return role_checker
