import { test, expect } from '@playwright/test';
import { loginApi } from '../../fixtures/api.fixture';
import { DEMO_EMPLOYEE, DEMO_OWNER, uniqueId } from '../../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';
const TENANT = DEMO_EMPLOYEE.tenant;

test.describe('Employee Auth & Context', () => {
  test('employee can open tenant workspace', async ({ page }) => {
    await page.goto(`/app/${TENANT}`);
    await expect(page).toHaveURL(/\/app\/toko-maju/);
  });
});

test.describe('Employee Product & Inventory', () => {
  test('products page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/inventory/products`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('stock movements page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/inventory/movements`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('get products endpoint returns data', async ({ request }) => {
    const res = await request.get(`/tenants/${TENANT}/products`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
  });

  test('create product via API is forbidden for employee', async () => {
    const { api } = await loginApi(apiURL, DEMO_EMPLOYEE.email, DEMO_EMPLOYEE.password);
    const sku = `SKU-E2E-${uniqueId()}`;
    const res = await api.post(`/tenants/${TENANT}/products`, {
      data: { sku, name: 'E2E Employee Product', category: 'Test', unit: 'pcs', price: 5000, cost: 2500, stock: 5, minStock: 1, status: 'active' },
    });
    expect(res.status()).toBe(403);
    await api.dispose();
  });

  test('create product with owner token works for reference', async () => {
    const { api } = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const sku = `SKU-EMPREF-${uniqueId()}`;
    const res = await api.post(`/tenants/${TENANT}/products`, {
      data: { sku, name: 'E2E Owner Creates for Employee Test', category: 'Test', unit: 'pcs', price: 5000, cost: 2500, stock: 5, minStock: 1, status: 'active' },
    });
    expect(res.status()).toBe(201);
    await api.dispose();
  });
});

test.describe('Employee Sales-Read Only', () => {
  test('invoices page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/sales/invoices`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('customers page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/sales/customers`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('get customers endpoint returns data for employee', async ({ request }) => {
    const res = await request.get(`/tenants/${TENANT}/customers`);
    expect(res.status()).toBe(200);
  });
});

test.describe('Employee Purchasing-Read Only', () => {
  test('purchase orders page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/purchasing/orders`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('suppliers page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/purchasing/suppliers`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });
});

test.describe('Employee Notifications & Audit', () => {
  test('notifications page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/notifications`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });

  test('audit page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('response', (res) => { if (res.status() >= 500) errors.push(`${res.status()} ${res.url()}`); });
    await page.goto(`/app/${TENANT}/audit`);
    await page.waitForLoadState('networkidle');
    expect(errors).toEqual([]);
  });
});
