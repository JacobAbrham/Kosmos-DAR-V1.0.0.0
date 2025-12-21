"""
Filesystem MCP Server for KOSMOS.
Provides secure file operations within allowed directories.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastmcp import FastMCP

logger = logging.getLogger("mcp-filesystem")

# Default allowed directories (configurable via env)
ALLOWED_PATHS = [
    os.getenv("KOSMOS_DATA_DIR", "/tmp/kosmos-data"),
    os.getenv("KOSMOS_UPLOADS_DIR", "/tmp/kosmos-uploads"),
]


class FilesystemServer:
    """
    MCP Server for filesystem operations.
    Provides read, write, list, and search capabilities.
    """

    def __init__(self, allowed_paths: Optional[List[str]] = None):
        self.name = "kosmos-filesystem"
        self.mcp = FastMCP(self.name)
        self.allowed_paths = [Path(p)
                              for p in (allowed_paths or ALLOWED_PATHS)]

        # Ensure directories exist
        for path in self.allowed_paths:
            path.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Filesystem MCP initialized. Allowed paths: {self.allowed_paths}")

        # Register tools
        self.mcp.tool()(self.read_file)
        self.mcp.tool()(self.write_file)
        self.mcp.tool()(self.list_directory)
        self.mcp.tool()(self.search_files)
        self.mcp.tool()(self.delete_file)
        self.mcp.tool()(self.get_file_info)

    def _validate_path(self, file_path: str) -> Path:
        """Validate that path is within allowed directories."""
        path = Path(file_path).resolve()

        for allowed in self.allowed_paths:
            try:
                path.relative_to(allowed.resolve())
                return path
            except ValueError:
                continue

        raise PermissionError(
            f"Access denied: {file_path} is outside allowed directories")

    def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        Read contents of a file.

        Args:
            file_path: Path to the file
            encoding: File encoding (default: utf-8)

        Returns:
            File contents as string
        """
        path = self._validate_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise IsADirectoryError(f"Not a file: {file_path}")

        logger.info(f"Reading file: {path}")
        return path.read_text(encoding=encoding)

    def write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> Dict[str, Any]:
        """
        Write content to a file.

        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding (default: utf-8)
            create_dirs: Create parent directories if needed

        Returns:
            Dict with file info
        """
        path = self._validate_path(file_path)

        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Writing to file: {path}")
        path.write_text(content, encoding=encoding)

        return {
            "path": str(path),
            "size": path.stat().st_size,
            "created": True,
        }

    def list_directory(
        self,
        directory_path: str,
        pattern: str = "*",
        recursive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List contents of a directory.

        Args:
            directory_path: Path to directory
            pattern: Glob pattern for filtering (default: *)
            recursive: Include subdirectories

        Returns:
            List of file/directory info dicts
        """
        path = self._validate_path(directory_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        logger.info(f"Listing directory: {path}")

        results = []
        glob_func = path.rglob if recursive else path.glob

        for item in glob_func(pattern):
            stat = item.stat()
            results.append({
                "name": item.name,
                "path": str(item),
                "is_file": item.is_file(),
                "is_dir": item.is_dir(),
                "size": stat.st_size if item.is_file() else 0,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })

        return results

    def search_files(
        self,
        directory_path: str,
        query: str,
        file_pattern: str = "*.txt",
    ) -> List[Dict[str, Any]]:
        """
        Search for files containing specific text.

        Args:
            directory_path: Directory to search in
            query: Text to search for
            file_pattern: File pattern to search (default: *.txt)

        Returns:
            List of matching files with context
        """
        path = self._validate_path(directory_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        logger.info(f"Searching in {path} for '{query}'")

        results = []
        for file_path in path.rglob(file_pattern):
            if not file_path.is_file():
                continue

            try:
                content = file_path.read_text()
                if query.lower() in content.lower():
                    # Find matching lines
                    lines = content.split('\n')
                    matches = [
                        {"line": i + 1, "text": line.strip()}
                        for i, line in enumerate(lines)
                        if query.lower() in line.lower()
                    ][:5]  # Limit to 5 matches per file

                    results.append({
                        "path": str(file_path),
                        "matches": matches,
                    })
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")

        return results

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file.

        Args:
            file_path: Path to file to delete

        Returns:
            Confirmation dict
        """
        path = self._validate_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise IsADirectoryError(f"Not a file: {file_path}")

        logger.info(f"Deleting file: {path}")
        path.unlink()

        return {"deleted": str(path), "success": True}

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file.

        Args:
            file_path: Path to the file

        Returns:
            File information dict
        """
        path = self._validate_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = path.stat()

        return {
            "path": str(path),
            "name": path.name,
            "extension": path.suffix,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
        }

    def run(self):
        """Start the MCP server."""
        self.mcp.run()


if __name__ == "__main__":
    server = FilesystemServer()
    server.run()
