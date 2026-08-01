import { test, expect } from '@playwright/test';
import { DEMO_OWNER } from '../../helpers/ids';

const TENANT = DEMO_OWNER.tenant;

test.describe('Owner Audit Trail', () => {
  test('object type filter narrows audit events', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/audit`);
    await page.waitForLoadState('networkidle');
    const chip = page.getByRole('button', { name: /bank account/i });
    await expect(chip).toBeVisible();
    await chip.click();
    await expect(page.getByText('bank_account', { exact: true }).first()).toBeVisible();
    expect(errors).toEqual([]);
  });
});
