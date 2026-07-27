export function uniqueId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export function uniqueEmail(): string {
  return `e2e.${uniqueId()}@test.example`;
}

export const DEMO_OWNER = {
  email: 'budi@tokomaju.com',
  password: 'budi123',
  tenant: 'toko-maju',
};

export const DEMO_EMPLOYEE = {
  email: 'ani@tokomaju.com',
  password: 'ani123',
  tenant: 'toko-maju',
};

export const DEMO_ADMIN = {
  email: 'admin@kepin.io',
  password: 'admin123',
};
