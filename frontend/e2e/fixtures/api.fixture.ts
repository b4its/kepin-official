import { expect, request, type APIRequestContext } from '@playwright/test';

export async function loginApi(
  apiURL: string,
  email: string,
  password: string,
): Promise<{ api: APIRequestContext; token: string; userId: string }> {
  const anonymous = await request.newContext({ baseURL: apiURL });
  const response = await anonymous.post('/auth/login', {
    data: { email, password },
  });
  expect(response.status()).toBe(200);
  const body = await response.json();
  await anonymous.dispose();

  const api = await request.newContext({
    baseURL: apiURL,
    extraHTTPHeaders: {
      Authorization: `Bearer ${body.access_token}`,
      'Content-Type': 'application/json',
    },
  });

  return { api, token: body.access_token, userId: body.user.id };
}
