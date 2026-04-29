import { test, expect } from '@playwright/test';

const TEST_PASSWORD = 'Password123!';

async function signUp(page: any, email: string) {
  await page.goto('/signup');
  await page.fill('input[name="first_name"]', 'Test');
  await page.fill('input[name="last_name"]', 'User');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', TEST_PASSWORD);
  await page.fill('input[name="password_confirm"]', TEST_PASSWORD);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*dashboard/, { timeout: 15000 });
}

test.describe('Authentication Flow', () => {
  test('should allow a user to sign up', async ({ page }) => {
    const email = `signup-${Date.now()}@example.com`;
    await signUp(page, email);
    // Dashboard renders a welcome heading or the user email
    await expect(page.locator('text=Logged in as')).toBeVisible();
  });

  test('should allow a user to log out and log back in', async ({ page }) => {
    const email = `login-${Date.now()}@example.com`;

    // 1. Sign up
    await signUp(page, email);

    // 2. Log out (button text is "Logout" with an emoji prefix)
    await page.click('button:has-text("Logout")');
    await expect(page).toHaveURL(/.*login/, { timeout: 10000 });

    // 3. Log back in using the same email (LoginForm uses id="email" / id="password")
    await page.fill('#email', email);
    await page.fill('#password', TEST_PASSWORD);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 15000 });
  });
});

test.describe('Navigation & Component Integrity', () => {
  test('should open Command Palette with Ctrl+K', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('button[type="submit"]');
    await page.locator('body').click({ position: { x: 640, y: 50 } });
    await page.keyboard.press('Control+k');
    await expect(page.locator('input[placeholder="Search commands..."]')).toBeVisible({ timeout: 5000 });
  });

  test('should render all components in the library', async ({ page }) => {
    await page.goto('/debug/components');
    await expect(page.locator('h1')).toContainText('Component Library');

    await expect(page.locator('text=Skeleton Loading')).toBeVisible();
    await expect(page.locator('text=Smart Image')).toBeVisible();
    await expect(page.locator('text=Empty States')).toBeVisible();
    await expect(page.locator('text=Loading Spinners')).toBeVisible();
  });
});
