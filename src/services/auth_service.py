"""
Authentication Service for KOSMOS.
Provides JWT-based authentication and authorization.
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from passlib.context import CryptContext
import jwt
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
JWT_SECRET = os.getenv("JWT_SECRET", "kosmos-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
JWT_REFRESH_DAYS = int(os.getenv("JWT_REFRESH_DAYS", "7"))


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"
    AGENT = "agent"
    READONLY = "readonly"


class Permission(str, Enum):
    """System permissions."""
    # Chat permissions
    CHAT_READ = "chat:read"
    CHAT_WRITE = "chat:write"

    # Vote permissions
    VOTE_READ = "vote:read"
    VOTE_INITIATE = "vote:initiate"
    VOTE_PARTICIPATE = "vote:participate"

    # Agent permissions
    AGENT_VIEW = "agent:view"
    AGENT_MANAGE = "agent:manage"
    AGENT_EXECUTE = "agent:execute"

    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_AUDIT = "admin:audit"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: list(Permission),  # All permissions
    UserRole.OPERATOR: [
        Permission.CHAT_READ, Permission.CHAT_WRITE,
        Permission.VOTE_READ, Permission.VOTE_INITIATE, Permission.VOTE_PARTICIPATE,
        Permission.AGENT_VIEW, Permission.AGENT_MANAGE, Permission.AGENT_EXECUTE,
        Permission.ADMIN_AUDIT,
    ],
    UserRole.USER: [
        Permission.CHAT_READ, Permission.CHAT_WRITE,
        Permission.VOTE_READ, Permission.VOTE_PARTICIPATE,
        Permission.AGENT_VIEW,
    ],
    UserRole.AGENT: [
        Permission.CHAT_READ, Permission.CHAT_WRITE,
        Permission.VOTE_READ, Permission.VOTE_PARTICIPATE,
        Permission.AGENT_EXECUTE,
    ],
    UserRole.READONLY: [
        Permission.CHAT_READ,
        Permission.VOTE_READ,
        Permission.AGENT_VIEW,
    ],
}


@dataclass
class TokenPayload:
    """JWT token payload."""
    sub: str  # User ID
    email: str
    roles: List[str]
    permissions: List[str]
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"


class UserCreate(BaseModel):
    """User registration schema."""
    email: EmailStr
    password: str
    name: str
    roles: List[UserRole] = [UserRole.USER]


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthService:
    """Authentication and authorization service."""

    def __init__(self):
        self.secret = JWT_SECRET
        self.algorithm = JWT_ALGORITHM

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_permissions_for_roles(self, roles: List[UserRole]) -> List[str]:
        """Get all permissions for given roles."""
        permissions = set()
        for role in roles:
            if role in ROLE_PERMISSIONS:
                permissions.update(ROLE_PERMISSIONS[role])
        return [p.value for p in permissions]

    def create_access_token(
        self,
        user_id: str,
        email: str,
        roles: List[str],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(hours=JWT_EXPIRATION_HOURS)

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        # Get permissions for roles
        role_enums = [UserRole(r) for r in roles if r in [
            e.value for e in UserRole]]
        permissions = self.get_permissions_for_roles(role_enums)

        payload = {
            "sub": user_id,
            "email": email,
            "roles": roles,
            "permissions": permissions,
            "exp": expire,
            "iat": now,
            "type": "access",
        }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT refresh token."""
        if expires_delta is None:
            expires_delta = timedelta(days=JWT_REFRESH_DAYS)

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def create_tokens(
        self,
        user_id: str,
        email: str,
        roles: List[str],
    ) -> TokenResponse:
        """Create access and refresh tokens."""
        access_token = self.create_access_token(user_id, email, roles)
        refresh_token = self.create_refresh_token(user_id, email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=JWT_EXPIRATION_HOURS * 3600,
        )

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def has_permission(self, token_payload: Dict[str, Any], permission: Permission) -> bool:
        """Check if token has a specific permission."""
        permissions = token_payload.get("permissions", [])
        return permission.value in permissions

    def has_role(self, token_payload: Dict[str, Any], role: UserRole) -> bool:
        """Check if token has a specific role."""
        roles = token_payload.get("roles", [])
        return role.value in roles


# Global auth service instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or create the global auth service."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
