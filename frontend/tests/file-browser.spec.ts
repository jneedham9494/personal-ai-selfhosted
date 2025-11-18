import { test, expect } from '@playwright/test';

test.describe('File Browser UI', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('should load the main interface', async ({ page }) => {
    // Check main title in chat panel (use exact to distinguish from welcome message)
    await expect(page.locator('.chat-header').getByRole('heading', { name: 'Personal AI Assistant' })).toBeVisible();

    // Check subtitle
    await expect(page.getByText('Powered by Qwen 2.5 Coder')).toBeVisible();

    // Check Note Viewer header
    await expect(page.getByRole('heading', { name: 'Note Viewer' })).toBeVisible();

    // Check hamburger menu exists
    await expect(page.getByLabel('Toggle file browser')).toBeVisible();
  });

  test('should display welcome content in MD viewer', async ({ page }) => {
    // Check welcome message is displayed
    await expect(page.getByRole('heading', { name: 'Welcome to Your Personal AI Assistant' })).toBeVisible();

    // Check quick start section
    await expect(page.getByText('Quick Start')).toBeVisible();

    // Check features section
    await expect(page.getByText('Goal Tracking')).toBeVisible();
    await expect(page.getByText('Habit Monitoring')).toBeVisible();
  });

  test('should open and close file browser sidebar', async ({ page }) => {
    const hamburgerBtn = page.getByLabel('Toggle file browser');
    const sidebar = page.locator('.file-sidebar');

    // Initially sidebar should be closed (off-screen)
    await expect(sidebar).not.toHaveClass(/open/);

    // Click hamburger to open
    await hamburgerBtn.click();
    await expect(sidebar).toHaveClass(/open/);

    // Should show "Your Vault" header
    await expect(page.getByRole('heading', { name: 'Your Vault' })).toBeVisible();

    // Click close button
    await page.locator('.close-sidebar-btn').click();
    await expect(sidebar).not.toHaveClass(/open/);
  });

  test('should display vault files in sidebar', async ({ page }) => {
    // Open sidebar
    await page.getByLabel('Toggle file browser').click();

    // Wait for files to load (they're fetched on mount)
    await page.waitForTimeout(1000);

    // Check that files are displayed
    const fileItems = page.locator('.file-item');
    const fileCount = await fileItems.count();

    // Should have 4 files
    expect(fileCount).toBe(4);

    // Check specific file names
    await expect(page.getByText('2025-Goals.md')).toBeVisible();
    await expect(page.getByText('2024-Review.md')).toBeVisible();
    await expect(page.getByText('Daily-Habits.md')).toBeVisible();
    await expect(page.getByText('XRPL-Learning.md')).toBeVisible();

    // Check folder names are displayed (use first() since multiple files have same folder)
    await expect(page.getByText('Projects', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Archive', { exact: true })).toBeVisible();
    await expect(page.getByText('Notes', { exact: true }).first()).toBeVisible();
  });

  test('should load file content when clicked', async ({ page }) => {
    // Open sidebar
    await page.getByLabel('Toggle file browser').click();
    await page.waitForTimeout(1000);

    // Click on 2025-Goals.md file
    await page.locator('.file-item').filter({ hasText: '2025-Goals.md' }).click();

    // Wait for file to load
    await page.waitForTimeout(500);

    // Check that content is displayed in MD viewer
    await expect(page.getByRole('heading', { name: '2025 Goals' })).toBeVisible();
    await expect(page.getByText('Learning Goals')).toBeVisible();
    await expect(page.getByText('Master XRPL development')).toBeVisible();

    // Check that sidebar is closed after selecting file
    const sidebar = page.locator('.file-sidebar');
    await expect(sidebar).not.toHaveClass(/open/);

    // Check current file is displayed in header
    await expect(page.locator('.current-file-name')).toContainText('2025-Goals.md');
  });

  test('should highlight active file', async ({ page }) => {
    // Open sidebar
    await page.getByLabel('Toggle file browser').click();
    await page.waitForTimeout(1000);

    // Click on a file
    const goalsFile = page.locator('.file-item').filter({ hasText: '2025-Goals.md' });
    await goalsFile.click();

    // Wait for file to load
    await page.waitForTimeout(500);

    // Open sidebar again
    await page.getByLabel('Toggle file browser').click();

    // Check that the clicked file has active class
    await expect(goalsFile).toHaveClass(/active/);
  });

  test('should render markdown content correctly', async ({ page }) => {
    // Open sidebar and click XRPL-Learning.md
    await page.getByLabel('Toggle file browser').click();
    await page.waitForTimeout(1000);

    await page.locator('.file-item').filter({ hasText: 'XRPL-Learning.md' }).click();
    await page.waitForTimeout(500);

    // Check markdown rendering
    await expect(page.getByRole('heading', { name: 'XRPL Learning Path' })).toBeVisible();

    // Check section headers are rendered
    await expect(page.getByRole('heading', { name: 'Resources' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Progress' })).toBeVisible();

    // Check for checkboxes (GFM task lists)
    const checkboxes = page.locator('input[type="checkbox"]');
    expect(await checkboxes.count()).toBeGreaterThan(0);
  });

  test('should load different files sequentially', async ({ page }) => {
    // Open sidebar
    await page.getByLabel('Toggle file browser').click();
    await page.waitForTimeout(1000);

    // Load first file
    await page.locator('.file-item').filter({ hasText: '2025-Goals.md' }).click();
    await page.waitForTimeout(500);
    await expect(page.getByRole('heading', { name: '2025 Goals' })).toBeVisible();

    // Open sidebar again and load different file
    await page.getByLabel('Toggle file browser').click();
    await page.locator('.file-item').filter({ hasText: 'Daily-Habits.md' }).click();
    await page.waitForTimeout(500);

    // Check new content is displayed
    await expect(page.getByRole('heading', { name: 'Daily Habits Tracker' })).toBeVisible();
    await expect(page.getByText('Morning Routine')).toBeVisible();

    // Check old content is not visible
    await expect(page.getByRole('heading', { name: '2025 Goals' })).not.toBeVisible();
  });

  test('should close sidebar when clicking overlay', async ({ page }) => {
    // Open sidebar
    await page.getByLabel('Toggle file browser').click();
    const sidebar = page.locator('.file-sidebar');
    await expect(sidebar).toHaveClass(/open/);

    // Click overlay
    await page.locator('.sidebar-overlay').click();

    // Sidebar should close
    await expect(sidebar).not.toHaveClass(/open/);
  });

  test('should display chat interface', async ({ page }) => {
    // Check chat input exists
    await expect(page.getByPlaceholder('Type a message... (Press Enter to send)')).toBeVisible();

    // Check send button exists
    await expect(page.getByRole('button', { name: 'Send' })).toBeVisible();

    // Check empty state message
    await expect(page.getByText('Start a conversation')).toBeVisible();
  });
});
