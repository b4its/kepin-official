import { test, expect } from '@playwright/test';
import { loginApi } from '../fixtures/api.fixture';
import { DEMO_OWNER, DEMO_ADMIN, DEMO_EMPLOYEE, uniqueId } from '../helpers/ids';

const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1';

test.describe('Tenant Isolation', () => {
  test('resource created in tenant A is not accessible from tenant B', async () => {
    const ownerA = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const ownerB = await loginApi(apiURL, DEMO_ADMIN.email, DEMO_ADMIN.password);

    const createRes = await ownerA.api.post('/tenants/toko-maju/customers', {
      data: { name: `Isolation-${uniqueId()}`, email: '', phone: '', address: '' },
    });
    expect(createRes.ok()).toBeTruthy();
    const customer = await createRes.json();
    const customerId = customer.id || customer.items?.[0]?.id;

    const crossRes = await ownerB.api.get(`/tenants/warung-segar/customers/${customerId}`);
    expect([403, 404]).toContain(crossRes.status());

    await ownerA.api.dispose();
    await ownerB.api.dispose();
  });

  test('list from tenant B does not contain tenant A resources', async () => {
    const ownerA = await loginApi(apiURL, DEMO_OWNER.email, DEMO_OWNER.password);
    const ownerB = await loginApi(apiURL, DEMO_EMPLOYEE.email, DEMO_EMPLOYEE.password);

    const createRes = await ownerA.api.post('/tenants/toko-maju/customers', {
      data: { name: `Isolation-List-${uniqueId()}`, email: '', phone: '', address: '' },
    });
    expect(createRes.ok()).toBeTruthy();

    const listB = await ownerB.api.get('/tenants/warung-segar/customers');
    expect(listB.ok()).toBeTruthy();
    const bodyB = await listB.json();
    const items = bodyB.items || [];
    expect(items.some((c: any) => c.name?.includes('Isolation-List-'))).toBeFalsy();

    await ownerA.api.dispose();
    await ownerB.api.dispose();
  });
});
