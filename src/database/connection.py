"""
Database connection management for KOSMOS.
Provides async database connections and connection pooling.
"""

import os
import logging
from typing import Optional, Any, Dict
from contextlib import asynccontextmanager

logger = logging.getLogger("kosmos-db")

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER", "kosmos")
    password = os.getenv("POSTGRES_PASSWORD", "kosmos_dev_password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "kosmos_dev")
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"


class DatabaseConnection:
    """
    Async database connection wrapper.
    Supports both raw queries and ORM operations.
    """

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or DATABASE_URL
        self._pool = None
        self._engine = None

    async def connect(self):
        """Initialize database connection pool."""
        try:
            # Try asyncpg for async operations
            import asyncpg
            self._pool = await asyncpg.create_pool(
                self.database_url.replace("postgresql://", "postgres://"),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool established")
        except ImportError:
            logger.warning("asyncpg not available, falling back to sync mode")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self):
        """Close database connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed")

    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute query and fetch one result."""
        if not self._pool:
            await self.connect()

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetch_all(self, query: str, *args) -> list:
        """Execute query and fetch all results."""
        if not self._pool:
            await self.connect()

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def execute(self, query: str, *args) -> str:
        """Execute a query without returning results."""
        if not self._pool:
            await self.connect()

        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions."""
        if not self._pool:
            await self.connect()

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                yield conn


# Singleton instance
_database: Optional[DatabaseConnection] = None


async def get_database() -> DatabaseConnection:
    """Get or create the database connection singleton."""
    global _database
    if _database is None:
        _database = DatabaseConnection()
        await _database.connect()
    return _database


async def close_database():
    """Close the database connection."""
    global _database
    if _database:
        await _database.disconnect()
        _database = None
