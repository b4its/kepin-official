import { chromium } from '@playwright/test';

const base = process.env.WEB_URL || 'http://localhost:5173';

const browser = await chromium.launch();
const page = await browser.newPage();

const logs = [];
page.on('console', (m) => logs.push(`[console.${m.type()}] ${m.text()}`));
page.on('pageerror', (e) => logs.push(`[pageerror] ${e.message}`));
page.on('requestfailed', (r) => logs.push(`[requestfailed] ${r.url()} :: ${r.failure()?.errorText}`));

await page.goto(`${base}/auth/login`, { waitUntil: 'networkidle' });
await page.fill('#email', 'budi@tokomaju.com');
await page.fill('#password', 'budi123');
await page.click('button[type="submit"]');

await page.waitForURL('**/app/**', { timeout: 15000 }).catch(() => {});
await page.waitForTimeout(8000);

const title = await page.title();
const bodySnippet = (await page.locator('body').innerText()).slice(0, 300).replace(/\n+/g, ' | ');
console.log('FINAL URL :', page.url());
console.log('BODY      :', bodySnippet);
console.log('--- console/errors ---');
console.log(logs.join('\n') || '(tidak ada error)');
await browser.close();