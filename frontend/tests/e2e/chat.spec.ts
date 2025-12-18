import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load chat interface', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/KOSMOS/);
    
    // Check chat input exists
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await expect(chatInput).toBeVisible();
  });

  test('should send a message and receive response', async ({ page }) => {
    // Type message
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Hello Zeus, what can you help me with?');
    
    // Send message (look for send button)
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for response (should appear in chat history)
    await page.waitForSelector('text=Zeus', { timeout: 10000 });
    
    // Verify message appears in chat
    await expect(page.locator('text=Hello Zeus')).toBeVisible();
  });

  test('should display typing indicator while waiting', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Test message');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Look for typing indicator (ellipsis, spinner, etc.)
    // Adjust selector based on actual implementation
    const typingIndicator = page.locator('[data-testid="typing-indicator"]').first();
    await expect(typingIndicator).toBeVisible({ timeout: 5000 });
  });

  test('should handle empty message submission', async ({ page }) => {
    const sendButton = page.locator('button[type="submit"]').first();
    
    // Try to send without typing
    await sendButton.click();
    
    // Button should be disabled or no message sent
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await expect(chatInput).toBeFocused();
  });

  test('should show message history', async ({ page }) => {
    // Send first message
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('First message');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for response
    await page.waitForTimeout(2000);
    
    // Send second message
    await chatInput.fill('Second message');
    await sendButton.click();
    
    // Both messages should be visible
    await expect(page.locator('text=First message')).toBeVisible();
    await expect(page.locator('text=Second message')).toBeVisible();
  });

  test('should handle long messages', async ({ page }) => {
    const longMessage = 'A'.repeat(1000);
    
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill(longMessage);
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Should handle without crashing
    await page.waitForTimeout(2000);
  });

  test('should show agent indicator', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Hello');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for response with agent name
    await page.waitForSelector('text=Zeus', { timeout: 10000 });
    
    // Verify agent name is displayed
    const agentIndicator = page.locator('text=Zeus').first();
    await expect(agentIndicator).toBeVisible();
  });

  test('should handle rapid message sending', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    const sendButton = page.locator('button[type="submit"]').first();
    
    // Send multiple messages quickly
    for (let i = 1; i <= 3; i++) {
      await chatInput.fill(`Message ${i}`);
      await sendButton.click();
      await page.waitForTimeout(100);
    }
    
    // All messages should be queued/sent
    await expect(page.locator('text=Message 1')).toBeVisible();
    await expect(page.locator('text=Message 2')).toBeVisible();
    await expect(page.locator('text=Message 3')).toBeVisible();
  });

  test('should clear input after sending', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Test message');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Input should be cleared
    await expect(chatInput).toHaveValue('');
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate offline
    await page.context().setOffline(true);
    
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Test offline message');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Should show error message
    await expect(page.locator('text=/error|failed|offline/i')).toBeVisible({ timeout: 5000 });
    
    // Re-enable network
    await page.context().setOffline(false);
  });
});
