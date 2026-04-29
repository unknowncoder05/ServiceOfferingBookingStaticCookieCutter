import { test, expect } from '@playwright/test';

const TEST_PASSWORD = 'Password123!';

async function signUp(page: any) {
  const email = `items-${Date.now()}@example.com`;
  await page.goto('/signup');
  await page.fill('input[name="first_name"]', 'Items');
  await page.fill('input[name="last_name"]', 'Tester');
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', TEST_PASSWORD);
  await page.fill('input[name="password_confirm"]', TEST_PASSWORD);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*dashboard/, { timeout: 15000 });
}

test.describe('Items Management', () => {
  const itemName = `Item-${Date.now()}`;

  test.beforeEach(async ({ page }) => {
    await signUp(page);
  });

  test('should create, view, edit, and delete an item', async ({ page }) => {
    // 1. Navigate to Items
    await page.goto('/items');
    await expect(page.locator('h1')).toContainText('Items');

    // 2. Open create form and fill fields
    // ItemForm uses id="name" and id="description" (no name attribute)
    await page.click('button:has-text("Create Item")');
    await page.fill('#name', itemName);
    await page.fill('#description', 'A test item created by Playwright.');
    await page.click('button[type="submit"]');

    // 3. After submit, handleFormSuccess navigates back to /items list
    await expect(page.locator(`text=${itemName}`)).toBeVisible({ timeout: 10000 });

    // 4. View item detail via the "View" button in ItemCard
    await page.locator('button:has-text("View")').first().click();
    await expect(page.locator('h1')).toContainText(itemName);

    // 5. Edit item — detail view has an "Edit" button
    await page.click('button:has-text("Edit")');
    const nameInput = page.locator('#name');
    await nameInput.clear();
    await nameInput.fill(`${itemName}-edited`);
    await page.click('button[type="submit"]');

    // After edit, handleFormSuccess navigates back to the list
    await expect(page.locator('h1')).toContainText('Items');
    await expect(page.locator(`text=${itemName}-edited`)).toBeVisible({ timeout: 10000 });

    // 6. Delete item — ItemList.handleDelete uses window.confirm; accept it
    page.on('dialog', (dialog: any) => dialog.accept());
    await page.locator('button:has-text("Delete")').first().click();

    // Empty state renders "No items yet" in an h3 via EmptyState component
    await expect(page.locator('h3:has-text("No items yet")')).toBeVisible({ timeout: 10000 });
  });
});
