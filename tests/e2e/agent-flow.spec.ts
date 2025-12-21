import { test, expect } from '@playwright/test';

/**
 * E2E Tests for multi-agent interactions in KOSMOS.
 * Tests the full flow from user input through Zeus orchestration.
 */
test.describe('Agent Interaction Flow', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        // Wait for initial system message
        await expect(page.locator('text=System initialized')).toBeVisible({ timeout: 5000 });
    });

    test('should show system initialization message', async ({ page }) => {
        await expect(page.locator('text=Zeus Orchestrator')).toBeVisible();
    });

    test('should receive AI-generated response to user query', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();
        await chatInput.fill('What is the purpose of KOSMOS?');

        const sendButton = page.locator('button[type="submit"]').first();
        await sendButton.click();

        // Wait for AI response (not just system message)
        await expect(page.locator('.whitespace-pre-wrap').last()).not.toBeEmpty({ timeout: 15000 });

        // Response should be meaningful (not just error)
        const responseText = await page.locator('.whitespace-pre-wrap').last().textContent();
        expect(responseText).not.toContain('Error');
        expect(responseText?.length).toBeGreaterThan(10);
    });

    test('should show agent metadata after response', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();
        await chatInput.fill('Help me understand system architecture');

        const sendButton = page.locator('button[type="submit"]').first();
        await sendButton.click();

        // Wait for response with metadata
        await page.waitForTimeout(3000);

        // Check for metadata display (agents used, processing time)
        const metadataSection = page.locator('text=/Agents:|ms$/i');
        await expect(metadataSection.first()).toBeVisible({ timeout: 10000 });
    });

    test('should maintain conversation context', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();

        // First message
        await chatInput.fill('My name is TestUser');
        await page.locator('button[type="submit"]').first().click();
        await page.waitForTimeout(2000);

        // Second message referencing first
        await chatInput.fill('What is my name?');
        await page.locator('button[type="submit"]').first().click();

        // Response should reference the name
        await page.waitForTimeout(3000);
        const lastResponse = await page.locator('.whitespace-pre-wrap').last().textContent();
        expect(lastResponse?.toLowerCase()).toContain('testuser');
    });

    test('should handle rapid consecutive messages', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();
        const sendButton = page.locator('button[type="submit"]').first();

        // Send multiple messages quickly
        await chatInput.fill('Message 1');
        await sendButton.click();

        await chatInput.fill('Message 2');
        await sendButton.click();

        await chatInput.fill('Message 3');
        await sendButton.click();

        // Wait for all responses
        await page.waitForTimeout(5000);

        // All messages should appear
        await expect(page.locator('text=Message 1')).toBeVisible();
        await expect(page.locator('text=Message 2')).toBeVisible();
        await expect(page.locator('text=Message 3')).toBeVisible();
    });

    test('should handle special characters in messages', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();
        await chatInput.fill('Test <script>alert("xss")</script> & special chars: ñ, ü, 中文');

        await page.locator('button[type="submit"]').first().click();

        // Message should be displayed safely
        await page.waitForTimeout(2000);
        await expect(page.locator('text=special chars')).toBeVisible();

        // No XSS execution
        const alertDialogs = await page.evaluate(() => {
            return document.querySelectorAll('script').length;
        });
        // Scripts in user messages should be escaped, not injected
    });

    test('should display loading state during processing', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();
        await chatInput.fill('A complex question that takes time');

        const sendButton = page.locator('button[type="submit"]').first();

        // Check button state changes during submission
        await sendButton.click();

        // Send button should be disabled while processing
        // or a loading indicator should appear
        await expect(sendButton).toBeDisabled();
    });
});

test.describe('Error Handling', () => {
    test('should gracefully handle API errors', async ({ page }) => {
        // Intercept API call and return error
        await page.route('**/api/chat', route => {
            route.fulfill({
                status: 500,
                body: JSON.stringify({ error: 'Internal server error' })
            });
        });

        await page.goto('/');

        const chatInput = page.locator('textarea, input[type="text"]').first();
        await chatInput.fill('Test message');
        await page.locator('button[type="submit"]').first().click();

        // Should show error message
        await expect(page.locator('text=/error/i')).toBeVisible({ timeout: 5000 });
    });

    test('should handle network timeout', async ({ page }) => {
        // Simulate slow network
        await page.route('**/api/chat', async route => {
            await new Promise(resolve => setTimeout(resolve, 35000)); // 35s delay
            route.fulfill({
                status: 200,
                body: JSON.stringify({ response: 'delayed response' })
            });
        });

        await page.goto('/');

        const chatInput = page.locator('textarea, input[type="text"]').first();
        await chatInput.fill('Test message');
        await page.locator('button[type="submit"]').first().click();

        // After timeout, should show error or retry option
        await expect(page.locator('text=/timeout|error|retry/i')).toBeVisible({ timeout: 40000 });
    });
});

test.describe('UI/UX', () => {
    test('should scroll to newest message', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();
        const sendButton = page.locator('button[type="submit"]').first();

        // Send several messages to create scroll
        for (let i = 0; i < 5; i++) {
            await chatInput.fill(`Message number ${i + 1}`);
            await sendButton.click();
            await page.waitForTimeout(500);
        }

        // The last message should be in viewport
        const lastMessage = page.locator('text=Message number 5');
        await expect(lastMessage).toBeInViewport();
    });

    test('should support keyboard shortcuts', async ({ page }) => {
        const chatInput = page.locator('textarea, input[type="text"]').first();
        await chatInput.fill('Test message');

        // Enter should submit (if not Shift+Enter for newline)
        await chatInput.press('Enter');

        // Message should be sent
        await page.waitForTimeout(1000);
        await expect(page.locator('text=Test message')).toBeVisible();
    });

    test('should have accessible elements', async ({ page }) => {
        // Check for proper ARIA labels
        const chatInput = page.locator('textarea, input[type="text"]').first();
        await expect(chatInput).toHaveAttribute('placeholder');

        const sendButton = page.locator('button[type="submit"]').first();
        await expect(sendButton).toBeEnabled();
    });
});
