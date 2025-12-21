from typing import Dict, List
from .server import BaseMCPServer


class SimpleMemoryServer(BaseMCPServer):
    """
    A simple in-memory key-value store MCP server.
    """

    def __init__(self):
        super().__init__("kosmos-memory")
        self.memory_store: Dict[str, str] = {}

        # Register tools explicitly
        self.mcp.tool()(self.read_memory)
        self.mcp.tool()(self.write_memory)
        self.mcp.tool()(self.list_memories)
        self.mcp.tool()(self.delete_memory)

    def read_memory(self, key: str) -> str:
        """Read a value from memory by key."""
        return self.memory_store.get(key, "Key not found")

    def write_memory(self, key: str, value: str) -> str:
        """Write a value to memory."""
        self.memory_store[key] = value
        return f"Stored '{value}' at '{key}'"

    def list_memories(self) -> List[str]:
        """List all keys in memory."""
        return list(self.memory_store.keys())

    def delete_memory(self, key: str) -> str:
        """Delete a key from memory."""
        if key in self.memory_store:
            del self.memory_store[key]
            return f"Deleted '{key}'"
        return "Key not found"


if __name__ == "__main__":
    server = SimpleMemoryServer()
    server.run()
