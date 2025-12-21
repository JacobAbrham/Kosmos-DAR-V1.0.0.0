"""
Memory MCP Server for KOSMOS.
Provides persistent key-value and semantic memory storage.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
from fastmcp import FastMCP

logger = logging.getLogger("mcp-memory")


class MemoryServer:
    """
    MCP Server for memory operations.
    Provides key-value storage, conversation history, and semantic search.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.name = "kosmos-memory"
        self.mcp = FastMCP(self.name)
        self.storage_path = Path(storage_path or "/tmp/kosmos-memory")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory stores (persisted to disk)
        self._kv_store: Dict[str, Any] = {}
        self._conversations: Dict[str, List[Dict]] = {}
        self._entities: Dict[str, Dict] = {}

        # Load existing data
        self._load_state()

        logger.info(f"Memory MCP initialized. Storage: {self.storage_path}")

        # Register tools
        self.mcp.tool()(self.store_value)
        self.mcp.tool()(self.retrieve_value)
        self.mcp.tool()(self.delete_value)
        self.mcp.tool()(self.list_keys)
        self.mcp.tool()(self.store_conversation)
        self.mcp.tool()(self.get_conversation_history)
        self.mcp.tool()(self.store_entity)
        self.mcp.tool()(self.get_entity)
        self.mcp.tool()(self.search_entities)
        self.mcp.tool()(self.clear_namespace)

    def _load_state(self) -> None:
        """Load persisted state from disk."""
        kv_file = self.storage_path / "kv_store.json"
        conv_file = self.storage_path / "conversations.json"
        entity_file = self.storage_path / "entities.json"

        if kv_file.exists():
            self._kv_store = json.loads(kv_file.read_text())
        if conv_file.exists():
            self._conversations = json.loads(conv_file.read_text())
        if entity_file.exists():
            self._entities = json.loads(entity_file.read_text())

    def _save_state(self) -> None:
        """Persist state to disk."""
        kv_file = self.storage_path / "kv_store.json"
        conv_file = self.storage_path / "conversations.json"
        entity_file = self.storage_path / "entities.json"

        kv_file.write_text(json.dumps(self._kv_store, indent=2))
        conv_file.write_text(json.dumps(self._conversations, indent=2))
        entity_file.write_text(json.dumps(self._entities, indent=2))

    def _make_key(self, namespace: str, key: str) -> str:
        """Create namespaced key."""
        return f"{namespace}:{key}"

    # Key-Value Operations

    def store_value(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        ttl_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Store a value with a key.

        Args:
            key: Unique key for the value
            value: Value to store (JSON-serializable)
            namespace: Namespace for grouping (default: "default")
            ttl_seconds: Time-to-live in seconds (optional)

        Returns:
            Storage confirmation
        """
        full_key = self._make_key(namespace, key)

        entry = {
            "value": value,
            "created": datetime.utcnow().isoformat(),
            "namespace": namespace,
        }

        if ttl_seconds:
            entry["expires"] = (
                datetime.utcnow().timestamp() + ttl_seconds
            )

        self._kv_store[full_key] = entry
        self._save_state()

        logger.info(f"Stored value: {full_key}")

        return {
            "key": key,
            "namespace": namespace,
            "stored": True,
        }

    def retrieve_value(
        self,
        key: str,
        namespace: str = "default",
    ) -> Optional[Any]:
        """
        Retrieve a value by key.

        Args:
            key: Key to retrieve
            namespace: Namespace (default: "default")

        Returns:
            Stored value or None
        """
        full_key = self._make_key(namespace, key)
        entry = self._kv_store.get(full_key)

        if not entry:
            return None

        # Check TTL
        if "expires" in entry:
            if datetime.utcnow().timestamp() > entry["expires"]:
                del self._kv_store[full_key]
                self._save_state()
                return None

        logger.info(f"Retrieved value: {full_key}")
        return entry["value"]

    def delete_value(
        self,
        key: str,
        namespace: str = "default",
    ) -> Dict[str, Any]:
        """
        Delete a value by key.

        Args:
            key: Key to delete
            namespace: Namespace (default: "default")

        Returns:
            Deletion confirmation
        """
        full_key = self._make_key(namespace, key)

        if full_key in self._kv_store:
            del self._kv_store[full_key]
            self._save_state()
            return {"deleted": True, "key": key}

        return {"deleted": False, "key": key, "reason": "not_found"}

    def list_keys(
        self,
        namespace: str = "default",
        pattern: Optional[str] = None,
    ) -> List[str]:
        """
        List all keys in a namespace.

        Args:
            namespace: Namespace to list
            pattern: Optional pattern to filter keys

        Returns:
            List of keys
        """
        prefix = f"{namespace}:"
        keys = []

        for full_key in self._kv_store:
            if full_key.startswith(prefix):
                key = full_key[len(prefix):]
                if pattern is None or pattern in key:
                    keys.append(key)

        return keys

    # Conversation Operations

    def store_conversation(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Store a conversation message.

        Args:
            conversation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata

        Returns:
            Storage confirmation
        """
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        message = {
            "id": hashlib.sha256(
                f"{conversation_id}{datetime.utcnow().isoformat()}{content}".encode()
            ).hexdigest()[:16],
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self._conversations[conversation_id].append(message)
        self._save_state()

        logger.info(f"Stored conversation message: {conversation_id}")

        return {
            "message_id": message["id"],
            "conversation_id": conversation_id,
            "stored": True,
        }

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        since: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get conversation history.

        Args:
            conversation_id: Conversation to retrieve
            limit: Maximum messages to return
            since: ISO timestamp to filter from

        Returns:
            List of messages
        """
        messages = self._conversations.get(conversation_id, [])

        if since:
            messages = [
                m for m in messages
                if m["timestamp"] >= since
            ]

        if limit:
            messages = messages[-limit:]

        return messages

    # Entity Operations (for knowledge graph-like storage)

    def store_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: Dict[str, Any],
        relations: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Store an entity with properties and relations.

        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity (person, concept, etc.)
            properties: Entity properties
            relations: List of relations to other entities

        Returns:
            Storage confirmation
        """
        self._entities[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "properties": properties,
            "relations": relations or [],
            "created": datetime.utcnow().isoformat(),
            "updated": datetime.utcnow().isoformat(),
        }

        self._save_state()
        logger.info(f"Stored entity: {entity_id}")

        return {
            "entity_id": entity_id,
            "type": entity_type,
            "stored": True,
        }

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """
        Get an entity by ID.

        Args:
            entity_id: Entity to retrieve

        Returns:
            Entity data or None
        """
        return self._entities.get(entity_id)

    def search_entities(
        self,
        entity_type: Optional[str] = None,
        property_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Search entities by type and properties.

        Args:
            entity_type: Filter by entity type
            property_filter: Property key-value filters
            limit: Maximum results

        Returns:
            List of matching entities
        """
        results = []

        for entity in self._entities.values():
            if entity_type and entity["type"] != entity_type:
                continue

            if property_filter:
                match = all(
                    entity["properties"].get(k) == v
                    for k, v in property_filter.items()
                )
                if not match:
                    continue

            results.append(entity)

            if len(results) >= limit:
                break

        return results

    def clear_namespace(self, namespace: str) -> Dict[str, Any]:
        """
        Clear all keys in a namespace.

        Args:
            namespace: Namespace to clear

        Returns:
            Deletion summary
        """
        prefix = f"{namespace}:"
        keys_to_delete = [
            k for k in self._kv_store if k.startswith(prefix)
        ]

        for key in keys_to_delete:
            del self._kv_store[key]

        self._save_state()

        return {
            "namespace": namespace,
            "deleted_count": len(keys_to_delete),
        }

    def run(self):
        """Start the MCP server."""
        self.mcp.run()


if __name__ == "__main__":
    server = MemoryServer()
    server.run()
