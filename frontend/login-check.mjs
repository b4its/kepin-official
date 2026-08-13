import { chromium } from '@playwright/test';

const url = process.env.WEB_URL || 'http://localhost:5173';

const browser = await chromium.launch();
const page = await browser.newPage();

const logs = [];
page.on('console', (m) => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', (e) => logs.push(`[pageerror] ${e.message}`));
page.on('requestfailed', (r) => logs.push(`[requestfailed] ${r.url()} :: ${r.failure()?.errorText}`));

await page.goto(`${url}/auth/login`, { waitUntil: 'networkidle' });

await page.fill('#email', 'budi@tokomaju.com');
await page.fill('#password', 'budi123');
await page.click('button[type="submit"]');

await page.waitForTimeout(6000);

console.log('URL setelah login:', page.url());
console.log('--- logs ---');
console.log(logs.join('\n'));
await browser.close();