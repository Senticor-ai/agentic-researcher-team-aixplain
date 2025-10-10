import { test, expect } from '@playwright/test';

const UI_URL = 'http://localhost:5174';
const API_URL = 'http://localhost:8000';

test.describe('OSINT Agent Team Monitor E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Check if backend is running
    try {
      const response = await page.request.get(`${API_URL}/api/v1/health`);
      expect(response.ok()).toBeTruthy();
    } catch (error) {
      throw new Error('Backend is not running. Please start it with: poetry run uvicorn api.main:app --reload --port 8000');
    }
  });

  test('should load dashboard and show create team button', async ({ page }) => {
    await page.goto(UI_URL);
    
    // Check page title
    await expect(page.locator('h1')).toContainText('OSINT Agent Team Monitor');
    
    // Check dashboard header
    await expect(page.locator('h2')).toContainText('Agent Teams');
    
    // Check create button exists
    await expect(page.locator('button:has-text("Create Team")')).toBeVisible();
  });

  test('should create a new agent team', async ({ page }) => {
    await page.goto(UI_URL);
    
    // Click create team button
    await page.click('button:has-text("Create Team")');
    
    // Modal should appear
    await expect(page.locator('h2:has-text("Create Agent Team")')).toBeVisible();
    
    // Fill in the form
    const testTopic = `E2E Test ${Date.now()}`;
    await page.fill('input#topic', testTopic);
    await page.fill('textarea#goals', 'Test goal 1\nTest goal 2\nTest goal 3');
    
    // Submit the form
    await page.click('button:has-text("Create Team")');
    
    // Should show success message
    await expect(page.locator('.success-message')).toBeVisible({ timeout: 5000 });
    
    // Should redirect to team detail page
    await expect(page).toHaveURL(/\/teams\/[a-f0-9-]+/, { timeout: 10000 });
    
    // Team detail page should show the topic
    await expect(page.locator('text=' + testTopic)).toBeVisible();
  });

  test('should display team list', async ({ page }) => {
    // Create a team first via API
    const testTopic = `List Test ${Date.now()}`;
    const createResponse = await page.request.post(`${API_URL}/api/v1/agent-teams`, {
      data: {
        topic: testTopic,
        goals: ['List test goal']
      }
    });
    expect(createResponse.ok()).toBeTruthy();
    
    // Go to dashboard
    await page.goto(UI_URL);
    
    // Wait for teams to load
    await page.waitForSelector('.teams-table', { timeout: 5000 });
    
    // Should see our team in the list
    await expect(page.locator(`text=${testTopic}`)).toBeVisible();
  });

  test('should navigate to team detail from dashboard', async ({ page }) => {
    // Create a team first via API
    const testTopic = `Nav Test ${Date.now()}`;
    const createResponse = await page.request.post(`${API_URL}/api/v1/agent-teams`, {
      data: {
        topic: testTopic,
        goals: ['Navigation test goal']
      }
    });
    const teamData = await createResponse.json();
    const teamId = teamData.team_id;
    
    // Go to dashboard
    await page.goto(UI_URL);
    
    // Wait for teams to load
    await page.waitForSelector('.teams-table');
    
    // Click on the team row
    await page.click(`tr:has-text("${testTopic}")`);
    
    // Should navigate to team detail
    await expect(page).toHaveURL(`/teams/${teamId}`);
    
    // Should show team details
    await expect(page.locator(`text=${testTopic}`)).toBeVisible();
    await expect(page.locator('h3:has-text("Execution Log")')).toBeVisible();
    await expect(page.locator('h3:has-text("Extracted Entities")')).toBeVisible();
    await expect(page.locator('h3:has-text("JSON-LD Sachstand")')).toBeVisible();
  });

  test('should show error when backend is unreachable', async ({ page, context }) => {
    // Block API requests to simulate backend down
    await context.route(`${API_URL}/**`, route => route.abort());
    
    await page.goto(UI_URL);
    
    // Should show error message
    await expect(page.locator('.error-message')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Failed to load agent teams')).toBeVisible();
  });

  test('should handle create team form validation', async ({ page }) => {
    await page.goto(UI_URL);
    
    // Click create team button
    await page.click('button:has-text("Create Team")');
    
    // Try to submit without filling topic
    await page.click('button[type="submit"]:has-text("Create Team")');
    
    // HTML5 validation should prevent submission
    const topicInput = page.locator('input#topic');
    await expect(topicInput).toHaveAttribute('required', '');
  });
});
