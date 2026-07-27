import type { Page } from '@playwright/test';

export async function seedFrontendSession(page: Page) {
  await page.addInitScript(() => {
    const user = {
      id: 'e2e-user',
      name: 'E2E Owner',
      email: 'e2e.owner@example.test',
      phone: '',
    };
    localStorage.setItem('kepin_session', JSON.stringify(user));
    localStorage.setItem(
      'kepin_users',
      JSON.stringify([{ ...user, password: 'e2e-password' }]),
    );
  });
}
