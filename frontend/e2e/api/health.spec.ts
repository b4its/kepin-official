import { test, expect } from '@playwright/test';

test.describe('Health', () => {
  test('live endpoint returns ok', async ({ request }) => {
    const res = await request.get('health/live');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.status).toBe('ok');
  });

  test('ready endpoint returns ok', async ({ request }) => {
    const res = await request.get('health/ready');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.status).toBe('ok');
  });

  test('startup endpoint returns ok', async ({ request }) => {
    const res = await request.get('health/startup');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.status).toBe('ok');
  });
});
