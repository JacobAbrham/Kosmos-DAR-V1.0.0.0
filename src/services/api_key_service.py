"""
API Key Service for KOSMOS.
Manages API keys for programmatic access.
"""
import os
import secrets
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class APIKey:
    """API Key data model."""
    id: str
    name: str
    key_hash: str
    prefix: str  # First 8 chars for identification
    owner_id: str
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class APIKeyCreate(BaseModel):
    """API key creation request."""
    name: str
    scopes: List[str] = ["chat:read", "chat:write"]
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    """API key creation response (includes full key only once)."""
    id: str
    name: str
    prefix: str
    key: str  # Full key - only shown once
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None


class APIKeyInfo(BaseModel):
    """API key info (without full key)."""
    id: str
    name: str
    prefix: str
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool


class APIKeyService:
    """
    Service for managing API keys.
    In production, this would use a database.
    """

    def __init__(self):
        self._keys: Dict[str, APIKey] = {}  # In-memory storage for MVP
        self._key_prefix = os.getenv("API_KEY_PREFIX", "kos")

    def _generate_key(self) -> tuple[str, str]:
        """Generate a new API key and its hash."""
        # Generate 32 random bytes (256 bits)
        random_bytes = secrets.token_bytes(32)

        # Create key with prefix: kos_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        key = f"{self._key_prefix}_{secrets.token_urlsafe(32)}"

        # Hash for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        return key, key_hash

    def _hash_key(self, key: str) -> str:
        """Hash an API key for comparison."""
        return hashlib.sha256(key.encode()).hexdigest()

    def create_key(
        self,
        owner_id: str,
        name: str,
        scopes: List[str],
        expires_in_days: Optional[int] = None,
    ) -> APIKeyResponse:
        """Create a new API key."""
        key, key_hash = self._generate_key()
        prefix = key[:12]  # kos_xxxxxxx
        key_id = secrets.token_urlsafe(16)

        now = datetime.now(timezone.utc)
        expires_at = None
        if expires_in_days:
            from datetime import timedelta
            expires_at = now + timedelta(days=expires_in_days)

        api_key = APIKey(
            id=key_id,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            owner_id=owner_id,
            scopes=scopes,
            created_at=now,
            expires_at=expires_at,
        )

        self._keys[key_hash] = api_key

        logger.info(f"Created API key {prefix}... for user {owner_id}")

        return APIKeyResponse(
            id=key_id,
            name=name,
            prefix=prefix,
            key=key,  # Only returned once
            scopes=scopes,
            created_at=now,
            expires_at=expires_at,
        )

    def validate_key(self, key: str) -> Optional[APIKey]:
        """Validate an API key and return its data if valid."""
        key_hash = self._hash_key(key)

        api_key = self._keys.get(key_hash)
        if api_key is None:
            return None

        # Check if active
        if not api_key.is_active:
            logger.warning(f"Inactive API key used: {api_key.prefix}")
            return None

        # Check expiration
        if api_key.expires_at and datetime.now(timezone.utc) > api_key.expires_at:
            logger.warning(f"Expired API key used: {api_key.prefix}")
            return None

        # Update last used
        api_key.last_used_at = datetime.now(timezone.utc)

        return api_key

    def list_keys(self, owner_id: str) -> List[APIKeyInfo]:
        """List all API keys for an owner."""
        keys = []
        for api_key in self._keys.values():
            if api_key.owner_id == owner_id:
                keys.append(APIKeyInfo(
                    id=api_key.id,
                    name=api_key.name,
                    prefix=api_key.prefix,
                    scopes=api_key.scopes,
                    created_at=api_key.created_at,
                    expires_at=api_key.expires_at,
                    last_used_at=api_key.last_used_at,
                    is_active=api_key.is_active,
                ))
        return keys

    def revoke_key(self, key_id: str, owner_id: str) -> bool:
        """Revoke an API key."""
        for api_key in self._keys.values():
            if api_key.id == key_id and api_key.owner_id == owner_id:
                api_key.is_active = False
                logger.info(f"Revoked API key {api_key.prefix}")
                return True
        return False

    def has_scope(self, api_key: APIKey, scope: str) -> bool:
        """Check if API key has a specific scope."""
        # Support wildcard scopes
        if "*" in api_key.scopes:
            return True

        # Check exact match
        if scope in api_key.scopes:
            return True

        # Check prefix match (e.g., "chat:*" matches "chat:read")
        scope_prefix = scope.split(":")[0]
        if f"{scope_prefix}:*" in api_key.scopes:
            return True

        return False


# Global API key service instance
_api_key_service: Optional[APIKeyService] = None


def get_api_key_service() -> APIKeyService:
    """Get or create the global API key service."""
    global _api_key_service
    if _api_key_service is None:
        _api_key_service = APIKeyService()
    return _api_key_service
