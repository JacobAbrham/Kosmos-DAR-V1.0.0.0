import { test, expect } from '@playwright/test';

test.describe('Pentarchy Voting Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should trigger voting for medium-cost task', async ({ page }) => {
    // Send a message that requires Pentarchy voting (cost $50-100)
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Please deploy a new feature that costs $75');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Should show voting UI
    await expect(page.locator('text=/voting|pentarchy/i')).toBeVisible({ timeout: 10000 });
  });

  test('should display all 5 agent votes', async ({ page }) => {
    // Trigger voting
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Deploy feature costing $80');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for voting to complete
    await page.waitForTimeout(3000);
    
    // Should show votes from 5 agents
    const expectedAgents = ['Zeus', 'Hermes', 'Athena', 'Hephaestus', 'Nur'];
    
    for (const agent of expectedAgents) {
      await expect(page.locator(`text=${agent}`)).toBeVisible();
    }
  });

  test('should show vote approval/rejection', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Task costing $60');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for voting
    await page.waitForTimeout(3000);
    
    // Should show approval or rejection indicator
    const voteResult = page.locator('text=/approved|rejected|passed|failed/i').first();
    await expect(voteResult).toBeVisible({ timeout: 5000 });
  });

  test('should bypass voting for low-cost task', async ({ page }) => {
    // Task under $50 should auto-approve
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Send an email (costs $5)');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Should NOT show voting UI
    await page.waitForTimeout(2000);
    
    // Verify no voting interface appeared
    const votingUI = page.locator('text=/pentarchy vote|voting in progress/i');
    await expect(votingUI).not.toBeVisible();
  });

  test('should auto-reject high-cost task', async ({ page }) => {
    // Task over $100 should auto-reject
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Deploy infrastructure costing $150');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Should show rejection
    await expect(page.locator('text=/rejected|denied|exceeded/i')).toBeVisible({ timeout: 5000 });
  });

  test('should show vote reasoning', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Feature deployment $70');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for voting
    await page.waitForTimeout(3000);
    
    // Should display reasoning for each vote
    await expect(page.locator('text=/reason|rationale|because/i')).toBeVisible({ timeout: 5000 });
  });

  test('should display vote count', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Task $85');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Should show vote tally (e.g., "3/5 approved")
    await expect(page.locator('text=/[0-9]\/5|votes/i')).toBeVisible({ timeout: 5000 });
  });

  test('should handle voting timeout', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Task requiring vote $75');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait longer than voting timeout
    await page.waitForTimeout(15000);
    
    // Should show timeout message or default result
    const result = page.locator('text=/timeout|completed|result/i').first();
    await expect(result).toBeVisible();
  });

  test('should show real-time vote updates', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Deploy service $65');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Votes should appear progressively (0/5 → 1/5 → ... → 5/5)
    // Check initial state
    await expect(page.locator('text=/0\/5|voting/i')).toBeVisible({ timeout: 2000 });
    
    // Eventually should reach 5/5
    await expect(page.locator('text=/5\/5|complete/i')).toBeVisible({ timeout: 10000 });
  });

  test('should allow vote result appeal/details', async ({ page }) => {
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Task $90');
    
    const sendButton = page.locator('button[type="submit"]').first();
    await sendButton.click();
    
    // Wait for voting to complete
    await page.waitForTimeout(4000);
    
    // Should have option to view details or expand
    const detailsButton = page.locator('button:has-text("Details")').or(
      page.locator('button:has-text("View")')
    ).first();
    
    if (await detailsButton.isVisible()) {
      await detailsButton.click();
      
      // Should show expanded vote information
      await expect(page.locator('text=/reasoning|justification/i')).toBeVisible();
    }
  });
});
