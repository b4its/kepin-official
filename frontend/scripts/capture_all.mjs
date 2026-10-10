import { chromium } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const OUT_DIR = path.resolve('../documentation/dokumen/images');
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

const BASE_URL = 'http://72.61.213.112:3001';
const API_URL = 'http://72.61.213.112:8001';

console.log('Output directory:', OUT_DIR);

async function createBrowser() {
  const browser = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--ignore-certificate-errors', '--window-size=1440,900']
  });
  return browser;
}

async function setupPage(browser) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1.5,
    ignoreHTTPSErrors: true
  });
  const page = await context.newPage();

  // Intercept any API calls to api.kepin.oryphem.com and redirect them to backend port 8001
  await page.route('**://api.kepin.oryphem.com/**', async (route) => {
    const req = route.request();
    const newUrl = req.url().replace('https://api.kepin.oryphem.com', API_URL).replace('http://api.kepin.oryphem.com', API_URL);
    try {
      const response = await route.fetch({ url: newUrl });
      await route.fulfill({ response });
    } catch (err) {
      console.error('[Route Fetch Error]', err.message);
      await route.abort();
    }
  });

  return { context, page };
}

async function capture(page, name, waitMs = 1500) {
  if (waitMs > 0) {
    await page.waitForTimeout(waitMs);
  }
  const filePath = path.join(OUT_DIR, `${name}.png`);
  await page.screenshot({ path: filePath, fullPage: false });
  console.log(`[Captured] ${name}.png`);
}

async function run() {
  const browser = await createBrowser();

  // 1. PUBLIC MARKETING & AUTH PAGES
  console.log('\n--- 1. Marketing & Auth Pages ---');
  {
    const { context, page } = await setupPage(browser);

    // Landing Hero
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle', timeout: 20000 });
    await capture(page, '01_landing_hero', 1500);

    // Scroll to Fitur / Solusi
    const solusiEl = await page.$('#solusi, #fitur');
    if (solusiEl) {
      await solusiEl.scrollIntoViewIfNeeded();
      await capture(page, '02_landing_features', 1000);
    } else {
      await page.evaluate(() => window.scrollBy(0, 800));
      await capture(page, '02_landing_features', 1000);
    }

    // Scroll to Pricing
    const hargaEl = await page.$('#harga');
    if (hargaEl) {
      await hargaEl.scrollIntoViewIfNeeded();
      await capture(page, '03_landing_pricing', 1000);
    } else {
      await page.evaluate(() => window.scrollBy(0, 1600));
      await capture(page, '03_landing_pricing', 1000);
    }

    // Login page
    await page.goto(`${BASE_URL}/auth/login`, { waitUntil: 'networkidle' });
    await capture(page, '04_auth_login', 1000);

    // Register page
    await page.goto(`${BASE_URL}/auth/register`, { waitUntil: 'networkidle' });
    await capture(page, '05_auth_register', 1000);

    // Create Company page
    await page.goto(`${BASE_URL}/auth/create-company`, { waitUntil: 'networkidle' });
    await capture(page, '06_auth_create_company', 1000);

    // Join Company page
    await page.goto(`${BASE_URL}/auth/join-company`, { waitUntil: 'networkidle' });
    await capture(page, '07_auth_join_company', 1000);

    await context.close();
  }

  // 2. TENANT OWNER: budi@tokomaju.com
  console.log('\n--- 2. Tenant Owner: budi@tokomaju.com ---');
  {
    const { context, page } = await setupPage(browser);

    // Login
    await page.goto(`${BASE_URL}/auth/login`, { waitUntil: 'networkidle' });
    await page.fill('#email', 'budi@tokomaju.com');
    await page.fill('#password', 'budi123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/app/**', { timeout: 15000 });

    const tenantSlug = 'toko-maju';

    // Dashboard
    await page.goto(`${BASE_URL}/app/${tenantSlug}`, { waitUntil: 'networkidle' });
    await capture(page, '08_workspace_dashboard', 2000);

    // POS Kasir
    await page.goto(`${BASE_URL}/app/${tenantSlug}/pos`, { waitUntil: 'networkidle' });
    await capture(page, '09_pos_cashier', 2000);

    // Sales Invoices
    await page.goto(`${BASE_URL}/app/${tenantSlug}/sales/invoices`, { waitUntil: 'networkidle' });
    await capture(page, '10_sales_invoices', 1500);

    // Sales Customers
    await page.goto(`${BASE_URL}/app/${tenantSlug}/sales/customers`, { waitUntil: 'networkidle' });
    await capture(page, '11_sales_customers', 1500);

    // Purchasing Orders
    await page.goto(`${BASE_URL}/app/${tenantSlug}/purchasing/orders`, { waitUntil: 'networkidle' });
    await capture(page, '12_purchasing_orders', 1500);

    // Purchasing Payments
    await page.goto(`${BASE_URL}/app/${tenantSlug}/purchasing/payments`, { waitUntil: 'networkidle' });
    await capture(page, '13_purchasing_payments', 1500);

    // Purchasing Suppliers
    await page.goto(`${BASE_URL}/app/${tenantSlug}/purchasing/suppliers`, { waitUntil: 'networkidle' });
    await capture(page, '14_purchasing_suppliers', 1500);

    // Inventory Products
    await page.goto(`${BASE_URL}/app/${tenantSlug}/inventory/products`, { waitUntil: 'networkidle' });
    await capture(page, '15_inventory_products', 1500);

    // Inventory Movements
    await page.goto(`${BASE_URL}/app/${tenantSlug}/inventory/movements`, { waitUntil: 'networkidle' });
    await capture(page, '16_inventory_movements', 1500);

    // Accounting Chart of Accounts
    await page.goto(`${BASE_URL}/app/${tenantSlug}/accounting/chart-of-accounts`, { waitUntil: 'networkidle' });
    await capture(page, '17_accounting_chart_of_accounts', 1500);

    // Accounting Journals
    await page.goto(`${BASE_URL}/app/${tenantSlug}/accounting/journals`, { waitUntil: 'networkidle' });
    await capture(page, '18_accounting_journals', 1500);

    // Accounting Reconciliation
    await page.goto(`${BASE_URL}/app/${tenantSlug}/accounting/reconciliation`, { waitUntil: 'networkidle' });
    await capture(page, '19_accounting_reconciliation', 1500);

    // Reports Financial
    await page.goto(`${BASE_URL}/app/${tenantSlug}/reports`, { waitUntil: 'networkidle' });
    await capture(page, '20_reports_financial', 2000);

    // Reports Investor
    await page.goto(`${BASE_URL}/app/${tenantSlug}/reports/investor`, { waitUntil: 'networkidle' });
    await capture(page, '21_reports_investor', 1500);

    // Insights Analytics
    await page.goto(`${BASE_URL}/app/${tenantSlug}/insights`, { waitUntil: 'networkidle' });
    await capture(page, '22_insights_analytics', 2000);

    // Audit Trail
    await page.goto(`${BASE_URL}/app/${tenantSlug}/audit`, { waitUntil: 'networkidle' });
    await capture(page, '23_audit_trail', 1500);

    // Notifications
    await page.goto(`${BASE_URL}/app/${tenantSlug}/notifications`, { waitUntil: 'networkidle' });
    await capture(page, '24_notifications', 1500);

    // Tutorial
    await page.goto(`${BASE_URL}/app/${tenantSlug}/tutorial`, { waitUntil: 'networkidle' });
    await capture(page, '25_tutorial', 1500);

    // Transactions Manual
    await page.goto(`${BASE_URL}/app/${tenantSlug}/transactions`, { waitUntil: 'networkidle' });
    await capture(page, '26_manual_transactions', 1500);

    // Settings Organization
    await page.goto(`${BASE_URL}/app/${tenantSlug}/settings/organization`, { waitUntil: 'networkidle' });
    await capture(page, '27_settings_organization', 1500);

    // Settings Members
    await page.goto(`${BASE_URL}/app/${tenantSlug}/settings/members`, { waitUntil: 'networkidle' });
    await capture(page, '28_settings_members', 1500);

    // Settings Roles
    await page.goto(`${BASE_URL}/app/${tenantSlug}/settings/roles`, { waitUntil: 'networkidle' });
    await capture(page, '29_settings_roles', 1500);

    // Settings Branches
    await page.goto(`${BASE_URL}/app/${tenantSlug}/settings/branches`, { waitUntil: 'networkidle' });
    await capture(page, '30_settings_branches', 1500);

    // Settings Sidebar
    await page.goto(`${BASE_URL}/app/${tenantSlug}/settings/sidebar`, { waitUntil: 'networkidle' });
    await capture(page, '31_settings_sidebar', 1500);

    // Settings Security
    await page.goto(`${BASE_URL}/app/${tenantSlug}/settings/security`, { waitUntil: 'networkidle' });
    await capture(page, '32_settings_security', 1500);

    // Settings Billing
    await page.goto(`${BASE_URL}/app/${tenantSlug}/settings/billing`, { waitUntil: 'networkidle' });
    await capture(page, '33_settings_billing', 1500);

    await context.close();
  }

  // 3. EMPLOYEE: ani@tokomaju.com
  console.log('\n--- 3. Tenant Employee: ani@tokomaju.com ---');
  {
    const { context, page } = await setupPage(browser);

    await page.goto(`${BASE_URL}/auth/login`, { waitUntil: 'networkidle' });
    await page.fill('#email', 'ani@tokomaju.com');
    await page.fill('#password', 'ani12345');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/app/**', { timeout: 15000 });

    await capture(page, '34_employee_dashboard', 2000);
    await context.close();
  }

  // 4. SECOND TENANT: siti@warungsegar.com
  console.log('\n--- 4. Second Tenant: siti@warungsegar.com ---');
  {
    const { context, page } = await setupPage(browser);

    await page.goto(`${BASE_URL}/auth/login`, { waitUntil: 'networkidle' });
    await page.fill('#email', 'siti@warungsegar.com');
    await page.fill('#password', 'siti123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/app/**', { timeout: 15000 });

    await capture(page, '35_warung_segar_dashboard', 2000);

    // POS Warung Segar
    await page.goto(`${BASE_URL}/app/warung-segar/pos`, { waitUntil: 'networkidle' });
    await capture(page, '36_warung_segar_pos', 2000);

    await context.close();
  }

  // 5. PLATFORM ADMIN: admin@kepin.io
  console.log('\n--- 5. Platform Admin: admin@kepin.io ---');
  {
    const { context, page } = await setupPage(browser);

    await page.goto(`${BASE_URL}/auth/login`, { waitUntil: 'networkidle' });
    await page.fill('#email', 'admin@kepin.io');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/admin**', { timeout: 15000 });

    // Admin Dashboard
    await capture(page, '37_admin_dashboard', 2000);

    // Admin Tenants
    await page.goto(`${BASE_URL}/admin/tenants`, { waitUntil: 'networkidle' });
    await capture(page, '38_admin_tenants', 1500);

    // Admin Users
    await page.goto(`${BASE_URL}/admin/users`, { waitUntil: 'networkidle' });
    await capture(page, '39_admin_users', 1500);

    // Admin Subscriptions
    await page.goto(`${BASE_URL}/admin/subscriptions`, { waitUntil: 'networkidle' });
    await capture(page, '40_admin_subscriptions', 1500);

    // Admin Incidents
    await page.goto(`${BASE_URL}/admin/incidents`, { waitUntil: 'networkidle' });
    await capture(page, '41_admin_incidents', 1500);

    // Admin Audit
    await page.goto(`${BASE_URL}/admin/audit`, { waitUntil: 'networkidle' });
    await capture(page, '42_admin_audit', 1500);

    // Admin Security
    await page.goto(`${BASE_URL}/admin/security`, { waitUntil: 'networkidle' });
    await capture(page, '43_admin_security', 1500);

    await context.close();
  }

  await browser.close();
  console.log('\n✓ ALL SCREENSHOTS CAPTURED SUCCESSFULLY!');
}

run().catch((err) => {
  console.error('Fatal execution error:', err);
  process.exit(1);
});
