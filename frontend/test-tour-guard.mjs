import { chromium } from '@playwright/test';

const url = process.env.WEB_URL || 'https://kepin.oryphem.com';

const browser = await chromium.launch();
const results = [];

async function scenario(name, setupFn, assertFn) {
  const context = await browser.newContext();
  const page = await context.newPage();
  const unauthorized = [];
  const navigations = [];
  page.on('response', (r) => { if (r.status() === 401) unauthorized.push(r.url()); });
  page.on('framenavigated', (f) => { if (f === page.mainFrame()) navigations.push(f.url()); });
  try {
    await setupFn(page);
    await assertFn(page, { unauthorized, navigations });
    results.push(`PASS ${name}`);
  } catch (err) {
    results.push(`FAIL ${name} :: ${err.message}`);
  } finally {
    await context.close();
  }
}

// ── S1: tanpa login & tanpa slug — state tur tersimpan di langkah workspace ──
await scenario(
  'S1 unauth tanpa slug, state tur → dashboard',
  async (page) => {
    await page.addInitScript(() => {
      localStorage.setItem('kepin_tour_active', JSON.stringify({ page: '', step: 10 }));
      localStorage.removeItem('kepin_token');
      localStorage.removeItem('kepin_session');
      localStorage.removeItem('kepin_tenants');
    });
    await page.goto(`${url}/auth/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(4000);
  },
  async (page, { unauthorized }) => {
    if (!page.url().includes('/auth/login')) throw new Error(`URL berubah: ${page.url()}`);
    const state = await page.evaluate(() => localStorage.getItem('kepin_tour_active'));
    if (state !== null) throw new Error(`state tur tidak dibersihkan: ${state}`);
    if (unauthorized.length > 0) throw new Error(`ada 401: ${unauthorized.join(', ')}`);
  }
);

// ── S2: tanpa login tapi slug stale — skenario loop login ↔ /app/{slug} ──────
await scenario(
  'S2 unauth + slug stale (toko-maju), state tur → pos',
  async (page) => {
    await page.addInitScript(() => {
      localStorage.setItem('kepin_tour_active', JSON.stringify({ page: 'pos', step: 21 }));
      localStorage.setItem('kepin_tenants', JSON.stringify([{ slug: 'toko-maju', role: 'tenant_owner' }]));
      localStorage.removeItem('kepin_token');
      localStorage.removeItem('kepin_session');
    });
    await page.goto(`${url}/auth/login`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(5000);
  },
  async (page, { unauthorized, navigations }) => {
    if (unauthorized.length > 0) throw new Error(`server ditolak berulang (${unauthorized.length}x 401): ${unauthorized[0]}`);
    if (!page.url().includes('/auth/login')) throw new Error(`URL berubah ke: ${page.url()}`);
    if (navigations.some((n) => n.includes('/app/'))) throw new Error(`navigasi ke /app/ terjadi: ${navigations.join(' | ')}`);
    const state = await page.evaluate(() => localStorage.getItem('kepin_tour_active'));
    if (state !== null) throw new Error(`state tur tidak dibersihkan: ${state}`);
  }
);

// ── S3: login sebagai budi — state tur workspace harus lanjut normal ────────
await scenario(
  'S3 authed (budi/toko-maju), state tur → dashboard, popover muncul',
  async (page) => {
    await page.goto(`${url}/auth/login`, { waitUntil: 'networkidle' });
    await page.fill('#email', 'budi@tokomaju.com');
    await page.fill('#password', 'budi123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/app\/toko-maju/, { timeout: 20000 });
    await page.waitForTimeout(2000);
    await page.evaluate(() => {
      localStorage.setItem('kepin_tour_active', JSON.stringify({ page: '', step: 10 }));
    });
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(5000);
  },
  async (page, { unauthorized }) => {
    if (!page.url().includes('/app/toko-maju')) throw new Error(`URL: ${page.url()}`);
    if (unauthorized.length > 0) throw new Error(`ada 401: ${unauthorized.join(', ')}`);
    const popover = await page.locator('.driver-popover').count();
    if (popover === 0) throw new Error('popover driver.js tidak muncul');
    const state = await page.evaluate(() => localStorage.getItem('kepin_tour_active'));
    if (state === null) throw new Error('state tur hilang padahal masih authed');
  }
);

console.log(results.join('\n'));
const failed = results.filter((r) => r.startsWith('FAIL')).length;
console.log(failed === 0 ? '--- semua skenario PASS ---' : `--- ${failed} skenario GAGAL ---`);
await browser.close();
process.exit(failed === 0 ? 0 : 1);