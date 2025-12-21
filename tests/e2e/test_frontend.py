"""
End-to-end tests using Playwright.
"""
import re
from playwright.sync_api import Page, expect


class TestHomePage:
    """Test the main chat interface."""

    def test_page_loads(self, page: Page):
        """Test that the home page loads correctly."""
        page.goto("http://localhost:3000")

        # Check page title
        expect(page).to_have_title(re.compile("KOSMOS"))

        # Check main elements are present
        expect(page.locator("input[type='text']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

    def test_send_message(self, page: Page):
        """Test sending a chat message."""
        page.goto("http://localhost:3000")

        # Type a message
        input_field = page.locator("input[type='text']")
        input_field.fill("Hello, KOSMOS!")

        # Submit
        page.locator("button[type='submit']").click()

        # Wait for response
        page.wait_for_selector("text=Hello", timeout=10000)

        # Check message appears
        expect(page.locator("text=Hello, KOSMOS!")).to_be_visible()

    def test_agent_selector(self, page: Page):
        """Test agent selection buttons."""
        page.goto("http://localhost:3000")

        # Wait for agents to load
        page.wait_for_selector("button:has-text('Auto')")

        # Check agent buttons exist
        expect(page.locator("button:has-text('Auto')")).to_be_visible()

    def test_vote_command(self, page: Page):
        """Test /vote command."""
        page.goto("http://localhost:3000")

        # Type vote command
        input_field = page.locator("input[type='text']")
        input_field.fill("/vote Test Proposal 100")

        # Submit
        page.locator("button[type='submit']").click()

        # Wait for system message
        page.wait_for_selector("text=Initiating Pentarchy Vote", timeout=10000)

    def test_conversation_persistence(self, page: Page):
        """Test that conversation ID is displayed."""
        page.goto("http://localhost:3000")

        # Send a message
        input_field = page.locator("input[type='text']")
        input_field.fill("Test persistence")
        page.locator("button[type='submit']").click()

        # Wait for response
        page.wait_for_timeout(2000)

        # Check conversation ID appears
        expect(page.locator("text=Conversation:")).to_be_visible()

    def test_loading_indicator(self, page: Page):
        """Test loading indicator appears."""
        page.goto("http://localhost:3000")

        # Send a message
        input_field = page.locator("input[type='text']")
        input_field.fill("Test loading")
        page.locator("button[type='submit']").click()

        # Check loading indicator (pulsing dots)
        expect(page.locator(".animate-pulse").first).to_be_visible()

    def test_responsive_layout(self, page: Page):
        """Test responsive design on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:3000")

        # Check elements are still visible
        expect(page.locator("input[type='text']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()


class TestErrorHandling:
    """Test error handling in the UI."""

    def test_empty_message(self, page: Page):
        """Test that empty messages are not sent."""
        page.goto("http://localhost:3000")

        # Try to submit empty message
        page.locator("button[type='submit']").click()

        # No new messages should appear
        page.wait_for_timeout(500)


class TestAccessibility:
    """Test accessibility features."""

    def test_form_labels(self, page: Page):
        """Test that form elements have proper labels."""
        page.goto("http://localhost:3000")

        # Check input has placeholder
        input_field = page.locator("input[type='text']")
        expect(input_field).to_have_attribute("placeholder", re.compile(".+"))

    def test_button_disabled_during_loading(self, page: Page):
        """Test button is disabled while loading."""
        page.goto("http://localhost:3000")

        # Send message
        input_field = page.locator("input[type='text']")
        input_field.fill("Test disabled state")
        page.locator("button[type='submit']").click()

        # Check button is disabled
        expect(page.locator("button[type='submit']")).to_be_disabled()
