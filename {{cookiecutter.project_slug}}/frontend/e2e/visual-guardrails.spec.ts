import fs from 'node:fs/promises';
import path from 'node:path';
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from '@playwright/test';

const screenshotDir = path.join(process.cwd(), 'artifacts', 'pm-execution-screenshots');

async function setTheme(page: any, theme: 'light' | 'dark') {
  await page.addInitScript((value: 'light' | 'dark') => {
    window.localStorage.setItem('theme', value);
  }, theme);
}

for (const theme of ['light', 'dark'] as const) {
  test(`login shell renders in ${theme} mode`, async ({ page }) => {
    await setTheme(page, theme);
    await page.goto('/login', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('form').first()).toBeVisible();

    const htmlClass = (await page.locator('html').getAttribute('class')) || '';
    if (theme === 'dark') {
      expect(htmlClass).toContain('dark');
    } else {
      expect(htmlClass).not.toContain('dark');
    }

    const loginA11y = await new AxeBuilder({ page }).analyze();
    expect(loginA11y.violations).toEqual([]);

    await fs.mkdir(screenshotDir, { recursive: true });
    await page.screenshot({
      path: path.join(screenshotDir, `login-${theme}.png`),
      fullPage: true,
    });
  });
}
