"""
Web Search MCP Server for KOSMOS.
Provides web search and content fetching capabilities.
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import quote_plus, urlparse
import json
from fastmcp import FastMCP

logger = logging.getLogger("mcp-web-search")

# Optional imports for real implementations
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    logger.warning("httpx not installed - web requests will be mocked")

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    logger.warning("beautifulsoup4 not installed - HTML parsing limited")


class WebSearchServer:
    """
    MCP Server for web search and content retrieval.
    Supports multiple search providers and web scraping.
    """

    def __init__(self):
        self.name = "kosmos-web-search"
        self.mcp = FastMCP(self.name)

        # API keys from environment
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")

        # HTTP client
        self._client: Optional["httpx.AsyncClient"] = None

        logger.info("Web Search MCP initialized")

        # Register tools
        self.mcp.tool()(self.web_search)
        self.mcp.tool()(self.fetch_url)
        self.mcp.tool()(self.extract_text)
        self.mcp.tool()(self.get_links)
        self.mcp.tool()(self.summarize_page)

    @property
    def client(self) -> "httpx.AsyncClient":
        """Get or create HTTP client."""
        if not HAS_HTTPX:
            raise RuntimeError("httpx not installed")
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "KOSMOS-Bot/1.0 (AI Research Assistant)"
                }
            )
        return self._client

    def _get_search_provider(self) -> str:
        """Determine available search provider."""
        if self.brave_api_key:
            return "brave"
        if self.serper_api_key:
            return "serper"
        if self.google_api_key and self.google_cse_id:
            return "google"
        return "mock"

    async def _brave_search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search using Brave Search API."""
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.brave_api_key,
        }
        params = {
            "q": query,
            "count": num_results,
        }

        response = await self.client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "source": "brave",
            })

        return results

    async def _serper_search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search using Serper API."""
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "q": query,
            "num": num_results,
        }

        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": "serper",
            })

        return results

    async def _google_search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": min(num_results, 10),
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": "google",
            })

        return results

    def _mock_search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Mock search for testing without API keys."""
        logger.warning("Using mock search - no API keys configured")
        return [
            {
                "title": f"Mock Result 1 for: {query}",
                "url": f"https://example.com/search?q={quote_plus(query)}&result=1",
                "snippet": f"This is a mock search result for '{query}'. Configure BRAVE_API_KEY, SERPER_API_KEY, or GOOGLE_API_KEY for real results.",
                "source": "mock",
            },
            {
                "title": f"Mock Result 2 for: {query}",
                "url": f"https://example.com/search?q={quote_plus(query)}&result=2",
                "snippet": f"Another mock result. To enable real web search, set the appropriate API key environment variable.",
                "source": "mock",
            },
        ][:num_results]

    def web_search(
        self,
        query: str,
        num_results: int = 10,
        provider: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search the web for information.

        Args:
            query: Search query string
            num_results: Number of results to return (max 10)
            provider: Force specific provider (brave, serper, google)

        Returns:
            List of search results with title, url, snippet
        """
        num_results = min(num_results, 10)
        search_provider = provider or self._get_search_provider()

        logger.info(f"Web search: '{query}' via {search_provider}")

        if search_provider == "mock" or not HAS_HTTPX:
            return self._mock_search(query, num_results)

        # Run async search in sync context
        async def do_search():
            if search_provider == "brave":
                return await self._brave_search(query, num_results)
            elif search_provider == "serper":
                return await self._serper_search(query, num_results)
            elif search_provider == "google":
                return await self._google_search(query, num_results)
            else:
                return self._mock_search(query, num_results)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, do_search())
                    return future.result()
            else:
                return loop.run_until_complete(do_search())
        except Exception as e:
            logger.error(f"Search error: {e}")
            return self._mock_search(query, num_results)

    def fetch_url(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch content from a URL.

        Args:
            url: URL to fetch
            headers: Optional custom headers

        Returns:
            Response data including content, status, headers
        """
        logger.info(f"Fetching URL: {url}")

        if not HAS_HTTPX:
            return {
                "url": url,
                "status": 0,
                "error": "httpx not installed",
                "content": "",
            }

        async def do_fetch():
            req_headers = headers or {}
            response = await self.client.get(url, headers=req_headers)

            content_type = response.headers.get("content-type", "")

            # Handle different content types
            if "application/json" in content_type:
                try:
                    content = response.json()
                except:
                    content = response.text
            else:
                content = response.text

            return {
                "url": str(response.url),
                "status": response.status_code,
                "content_type": content_type,
                "content": content,
                "headers": dict(response.headers),
            }

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, do_fetch())
                    return future.result()
            else:
                return loop.run_until_complete(do_fetch())
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return {
                "url": url,
                "status": 0,
                "error": str(e),
                "content": "",
            }

    def extract_text(
        self,
        html: str,
        selector: Optional[str] = None,
    ) -> str:
        """
        Extract text content from HTML.

        Args:
            html: HTML content string
            selector: Optional CSS selector to target

        Returns:
            Extracted text content
        """
        if not HAS_BS4:
            # Basic text extraction without BeautifulSoup
            import re
            # Remove script and style elements
            text = re.sub(r'<script[^>]*>.*?</script>',
                          '', html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '',
                          text, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', text)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        if selector:
            elements = soup.select(selector)
            text = " ".join(el.get_text(separator=" ", strip=True)
                            for el in elements)
        else:
            text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        import re
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def get_links(
        self,
        html: str,
        base_url: Optional[str] = None,
        filter_pattern: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Extract links from HTML content.

        Args:
            html: HTML content string
            base_url: Base URL for resolving relative links
            filter_pattern: Pattern to filter links

        Returns:
            List of links with text and href
        """
        import re
        from urllib.parse import urljoin

        links = []

        if HAS_BS4:
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)

                if base_url:
                    href = urljoin(base_url, href)

                if filter_pattern and not re.search(filter_pattern, href):
                    continue

                links.append({
                    "text": text,
                    "href": href,
                })
        else:
            # Basic extraction without BeautifulSoup
            pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'
            for match in re.finditer(pattern, html, re.IGNORECASE):
                href, text = match.groups()

                if base_url:
                    href = urljoin(base_url, href)

                if filter_pattern and not re.search(filter_pattern, href):
                    continue

                links.append({
                    "text": text.strip(),
                    "href": href,
                })

        return links

    def summarize_page(
        self,
        url: str,
        max_length: int = 1000,
    ) -> Dict[str, Any]:
        """
        Fetch and summarize a web page.

        Args:
            url: URL to summarize
            max_length: Maximum text length to return

        Returns:
            Page summary with title, text, links
        """
        logger.info(f"Summarizing page: {url}")

        # Fetch the page
        response = self.fetch_url(url)

        if response.get("error"):
            return {
                "url": url,
                "error": response["error"],
            }

        html = response.get("content", "")
        if not isinstance(html, str):
            return {
                "url": url,
                "content_type": response.get("content_type"),
                "data": html,
            }

        # Extract text
        text = self.extract_text(html)
        if len(text) > max_length:
            text = text[:max_length] + "..."

        # Extract title
        title = ""
        if HAS_BS4:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)
        else:
            import re
            match = re.search(
                r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            if match:
                title = match.group(1).strip()

        # Get main links (limit to 10)
        links = self.get_links(html, base_url=url)[:10]

        return {
            "url": url,
            "title": title,
            "text": text,
            "links": links,
            "fetched_at": datetime.utcnow().isoformat(),
        }

    def run(self):
        """Start the MCP server."""
        self.mcp.run()


if __name__ == "__main__":
    server = WebSearchServer()
    server.run()
