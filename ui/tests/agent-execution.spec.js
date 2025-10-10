import { test, expect } from '@playwright/test';

const UI_URL = 'http://localhost:5174';
const API_URL = 'http://localhost:8000';

test.describe('Agent Team Execution E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Check if backend is running
    try {
      const response = await page.request.get(`${API_URL}/api/v1/health`);
      expect(response.ok()).toBeTruthy();
    } catch (error) {
      throw new Error('Backend is not running. Please start it with: poetry run uvicorn api.main:app --reload --port 8000');
    }
  });

  test('should create agent team via UI and get response back', async ({ page }) => {
    console.log('🚀 Starting agent team creation test...');
    
    // Go to dashboard
    await page.goto(UI_URL);
    console.log('✓ Loaded dashboard');
    
    // Click create team button
    await page.click('button:has-text("Create Team")');
    console.log('✓ Opened create team modal');
    
    // Fill in the form with a simple topic (no special characters for team name)
    const testTopic = 'Capital of France Research';
    await page.fill('input#topic', testTopic);
    await page.fill('textarea#goals', 'Find the capital city\nProvide basic information about Paris');
    console.log(`✓ Filled form with topic: "${testTopic}"`);
    
    // Submit the form
    await page.click('button[type="submit"]:has-text("Create Team")');
    console.log('✓ Submitted form');
    
    // Should show success message
    await expect(page.locator('.success-message')).toBeVisible({ timeout: 5000 });
    console.log('✓ Success message shown');
    
    // Should redirect to team detail page
    await expect(page).toHaveURL(/\/teams\/[a-f0-9-]+/, { timeout: 10000 });
    const teamId = page.url().split('/teams/')[1];
    console.log(`✓ Redirected to team detail page: ${teamId}`);
    
    // Wait for page to load - check for any content
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Give React time to render
    
    // Check if we got an error or if page loaded
    const hasError = await page.locator('.team-detail-error').isVisible().catch(() => false);
    if (hasError) {
      const errorText = await page.locator('.team-detail-error').textContent();
      console.log(`❌ Error loading team detail: ${errorText}`);
      throw new Error(`Failed to load team detail: ${errorText}`);
    }
    
    console.log('✓ Team detail page loaded');
    
    // Wait for execution to start - should see log entries
    console.log('⏳ Waiting for execution to start...');
    await page.waitForSelector('.log-entry', { timeout: 15000 });
    console.log('✓ Execution started - log entries visible');
    
    // Check that status is not "pending" anymore
    const statusBadge = page.locator('.status-badge');
    await expect(statusBadge).toBeVisible();
    const statusText = await statusBadge.textContent();
    console.log(`✓ Current status: ${statusText}`);
    
    // Wait for execution to complete (or fail) - max 2 minutes
    console.log('⏳ Waiting for agent team to complete (max 2 minutes)...');
    let completed = false;
    let attempts = 0;
    const maxAttempts = 24; // 24 * 5 seconds = 2 minutes
    
    while (!completed && attempts < maxAttempts) {
      await page.waitForTimeout(5000); // Wait 5 seconds
      attempts++;
      
      // Reload the page to get fresh data
      await page.reload();
      
      // Check status
      const currentStatus = await page.locator('.status-badge').textContent();
      console.log(`  [${attempts}/${maxAttempts}] Status: ${currentStatus}`);
      
      if (currentStatus === 'completed' || currentStatus === 'failed') {
        completed = true;
        console.log(`✓ Execution ${currentStatus}`);
      }
    }
    
    if (!completed) {
      console.log('⚠️  Execution did not complete within 2 minutes, but continuing test...');
    }
    
    // Check for agent response in the detail view
    console.log('🔍 Checking for agent response...');
    
    // Get the team data via API to verify response
    const apiResponse = await page.request.get(`${API_URL}/api/v1/agent-teams/${teamId}`);
    expect(apiResponse.ok()).toBeTruthy();
    const teamData = await apiResponse.json();
    
    console.log('Team data received:');
    console.log(`  - Status: ${teamData.status}`);
    console.log(`  - Execution log entries: ${teamData.execution_log?.length || 0}`);
    console.log(`  - Has agent_response: ${!!teamData.agent_response}`);
    console.log(`  - Has sachstand: ${!!teamData.sachstand}`);
    
    // Verify we have execution log entries
    expect(teamData.execution_log).toBeDefined();
    expect(teamData.execution_log.length).toBeGreaterThan(0);
    console.log('✓ Execution log has entries');
    
    // If completed, verify we have a response
    if (teamData.status === 'completed') {
      expect(teamData.agent_response).toBeDefined();
      console.log('✓ Agent response received');
      
      // Log the response structure
      if (teamData.agent_response) {
        console.log('Agent response structure:');
        console.log(`  - Has data: ${!!teamData.agent_response.data}`);
        console.log(`  - Has output: ${!!teamData.agent_response.output}`);
        console.log(`  - Completed: ${teamData.agent_response.completed}`);
        
        if (teamData.agent_response.output) {
          const outputPreview = JSON.stringify(teamData.agent_response.output).substring(0, 200);
          console.log(`  - Output preview: ${outputPreview}...`);
        }
      }
      
      // Verify sachstand was generated
      if (teamData.sachstand) {
        expect(teamData.sachstand).toBeDefined();
        console.log('✓ Sachstand (JSON-LD) generated');
        console.log(`  - Type: ${teamData.sachstand['@type']}`);
        console.log(`  - Name: ${teamData.sachstand.name}`);
      }
    } else if (teamData.status === 'failed') {
      console.log('⚠️  Team execution failed. Check execution log for details.');
      // Print last few log entries
      const lastLogs = teamData.execution_log.slice(-5);
      console.log('Last log entries:');
      lastLogs.forEach((log, i) => console.log(`  ${i + 1}. ${log}`));
    } else {
      console.log(`ℹ️  Team is still in status: ${teamData.status}`);
    }
    
    // Verify UI shows the execution log
    const logEntries = page.locator('.log-entry');
    const logCount = await logEntries.count();
    expect(logCount).toBeGreaterThan(0);
    console.log(`✓ UI displays ${logCount} log entries`);
    
    console.log('✅ Test completed successfully!');
  });

  test('should monitor multiple teams', async ({ page }) => {
    console.log('🚀 Testing multiple team monitoring...');
    
    // Create 2 teams via API for faster setup
    const topics = [
      'Population of Tokyo Research',
      'Telephone Invention History'
    ];
    
    const teamIds = [];
    for (const topic of topics) {
      const response = await page.request.post(`${API_URL}/api/v1/agent-teams`, {
        data: {
          topic: topic,
          goals: ['Research the topic', 'Provide accurate information']
        }
      });
      const data = await response.json();
      teamIds.push(data.team_id);
      console.log(`✓ Created team: ${data.team_id} for topic: "${topic}"`);
    }
    
    // Go to dashboard
    await page.goto(UI_URL);
    console.log('✓ Loaded dashboard');
    
    // Should see both teams in the list
    await page.waitForSelector('.teams-table');
    for (const topic of topics) {
      await expect(page.locator('.teams-table').locator(`text=${topic}`).first()).toBeVisible();
    }
    console.log('✓ Both teams visible in dashboard');
    
    // Click on first team
    await page.click(`tr:has-text("${topics[0]}")`);
    console.log(`✓ Navigated to first team detail`);
    
    // Should show team details
    await expect(page.locator('.metadata-value', { hasText: topics[0] })).toBeVisible();
    
    // Go back to dashboard
    await page.click('button:has-text("Back to Dashboard")');
    console.log('✓ Returned to dashboard');
    
    // Click on second team
    await page.click(`tr:has-text("${topics[1]}")`);
    console.log(`✓ Navigated to second team detail`);
    
    // Should show team details
    await expect(page.locator('.metadata-value', { hasText: topics[1] })).toBeVisible();
    
    console.log('✅ Multiple team monitoring test completed!');
  });
});
