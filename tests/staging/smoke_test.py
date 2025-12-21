#!/usr/bin/env python3
"""
KOSMOS Staging Smoke Tests
Run after deployment to verify core functionality
"""
import asyncio
import sys
import time
from dataclasses import dataclass
from typing import Optional

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    import subprocess
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "httpx", "-q"])
    import httpx


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration_ms: float


class StagingSmokeTests:
    """Smoke tests for staging environment"""

    def __init__(self, api_url: str = "http://localhost:8001"):
        self.api_url = api_url.rstrip("/")
        self.results: list[TestResult] = []

    async def run_all(self) -> bool:
        """Run all smoke tests"""
        print("🧪 KOSMOS Staging Smoke Tests")
        print("=" * 50)
        print(f"Target: {self.api_url}")
        print("=" * 50)
        print()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Core health tests
            await self._test(client, "Health Check", self._test_health)
            await self._test(client, "Ready Check", self._test_ready)
            await self._test(client, "Metrics Endpoint", self._test_metrics)
            await self._test(client, "API Documentation", self._test_docs)

            # API functionality tests
            await self._test(client, "Agents List", self._test_agents)
            await self._test(client, "Chat Message", self._test_chat)
            await self._test(client, "MCP Servers", self._test_mcp)
            await self._test(client, "Voting Stats", self._test_votes)

        # Print summary
        self._print_summary()

        return all(r.passed for r in self.results)

    async def _test(self, client: httpx.AsyncClient, name: str, test_func):
        """Run a single test with timing"""
        print(f"🔍 {name}...", end=" ", flush=True)
        start = time.time()

        try:
            await test_func(client)
            duration = (time.time() - start) * 1000
            self.results.append(TestResult(name, True, "OK", duration))
            print(f"✅ ({duration:.0f}ms)")
        except AssertionError as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult(name, False, str(e), duration))
            print(f"❌ {e}")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.results.append(TestResult(
                name, False, f"Error: {e}", duration))
            print(f"❌ {e}")

    async def _test_health(self, client: httpx.AsyncClient):
        """Test health endpoint"""
        response = await client.get(f"{self.api_url}/health")
        assert response.status_code == 200, f"Status {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Status: {data.get('status')}"

    async def _test_ready(self, client: httpx.AsyncClient):
        """Test readiness endpoint"""
        response = await client.get(f"{self.api_url}/ready")
        assert response.status_code == 200, f"Status {response.status_code}"

    async def _test_metrics(self, client: httpx.AsyncClient):
        """Test Prometheus metrics endpoint"""
        response = await client.get(f"{self.api_url}/metrics")
        assert response.status_code == 200, f"Status {response.status_code}"
        assert "kosmos_" in response.text or "python_" in response.text, "No metrics found"

    async def _test_docs(self, client: httpx.AsyncClient):
        """Test OpenAPI documentation"""
        response = await client.get(f"{self.api_url}/docs")
        assert response.status_code == 200, f"Status {response.status_code}"
        assert "swagger" in response.text.lower(
        ) or "openapi" in response.text.lower(), "No API docs"

    async def _test_agents(self, client: httpx.AsyncClient):
        """Test agents list endpoint"""
        response = await client.get(f"{self.api_url}/api/v1/agents")
        assert response.status_code == 200, f"Status {response.status_code}"
        agents = response.json()
        assert isinstance(agents, list), "Expected list of agents"
        assert len(
            agents) >= 5, f"Expected at least 5 agents, got {len(agents)}"

    async def _test_chat(self, client: httpx.AsyncClient):
        """Test chat message endpoint"""
        response = await client.post(
            f"{self.api_url}/api/v1/chat/message",
            json={
                "message": "Staging test message",
                "conversation_id": f"staging-test-{int(time.time())}"
            }
        )
        assert response.status_code == 200, f"Status {response.status_code}"
        data = response.json()
        assert "response" in data or "message" in data, "No response in chat"

    async def _test_mcp(self, client: httpx.AsyncClient):
        """Test MCP servers endpoint"""
        response = await client.get(f"{self.api_url}/api/v1/mcp/servers")
        assert response.status_code == 200, f"Status {response.status_code}"

    async def _test_votes(self, client: httpx.AsyncClient):
        """Test voting stats endpoint"""
        response = await client.get(f"{self.api_url}/api/v1/votes/stats")
        assert response.status_code == 200, f"Status {response.status_code}"

    def _print_summary(self):
        """Print test summary"""
        print()
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total_time = sum(r.duration_ms for r in self.results)

        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(
                f"  {status} {result.name}: {result.message} ({result.duration_ms:.0f}ms)")

        print("=" * 50)
        print(f"Passed: {passed}/{len(self.results)}")
        print(f"Failed: {failed}/{len(self.results)}")
        print(f"Total Time: {total_time:.0f}ms")
        print("=" * 50)

        if failed == 0:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Please review.")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="KOSMOS Staging Smoke Tests")
    parser.add_argument(
        "--url", default="http://localhost:8001", help="API URL")
    parser.add_argument("--wait", type=int, default=0,
                        help="Wait seconds before running")
    args = parser.parse_args()

    if args.wait > 0:
        print(f"⏳ Waiting {args.wait} seconds for services to start...")
        await asyncio.sleep(args.wait)

    tests = StagingSmokeTests(args.url)
    success = await tests.run_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
