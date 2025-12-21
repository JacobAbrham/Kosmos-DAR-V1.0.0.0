import { test, expect } from '@playwright/test';

test.describe('Robust Governance Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should handle manual vote trigger via /vote command', async ({ page }) => {
    // 1. Trigger vote manually
    // Syntax: /vote <Title> <Cost>
    const chatInput = page.locator('input[type="text"], textarea').first();
    await chatInput.fill('/vote "New Feature Proposal" 75');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();

    // 2. Verify Voting UI appears
    // Look for specific elements that indicate voting is in progress or completed
    // The UI might transition quickly, so we look for the proposal card
    await expect(page.locator('text=New Feature Proposal')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('text=75')).toBeVisible();

    // 3. Wait for completion (polling happens in client, UI updates)
    // We expect a final status. The client polling logic we added waits up to 10s.
    // The UI likely displays "APPROVED", "REJECTED", or "APPROVED_WITH_REVIEW"
    const statusLocator = page.locator('text=/APPROVED|REJECTED/');
    await expect(statusLocator).toBeVisible({ timeout: 20000 });

    // 4. Verify Agent Participation
    // We expect to see the names of the Pentarchy members
    const agents = ['Zeus', 'Athena', 'Hephaestus', 'Hermes'];
    for (const agent of agents) {
        // Case insensitive check as UI might capitalize differently
        await expect(page.locator(`text=/${agent}/i`)).toBeVisible();
    }
  });
});
