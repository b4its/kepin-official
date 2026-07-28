import { defineConfig, devices } from '@playwright/test';
import { config as loadEnv } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

loadEnv({ path: resolve(__dirname, '.env.e2e') });

const webURL = process.env.E2E_WEB_URL ?? 'http://127.0.0.1:5173';
const apiURL = process.env.E2E_API_URL ?? 'http://127.0.0.1:8000/api/v1/';

export default defineConfig({
  testDir: './e2e',
  outputDir: './test-results/artifacts',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  globalSetup: resolve(__dirname, 'e2e/setup/global.ts'),
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
  ],
  use: {
    baseURL: webURL,
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
    locale: 'id-ID',
    timezoneId: 'Asia/Jakarta',
    colorScheme: 'light',
    ignoreHTTPSErrors: false,
  },
  projects: [
    {
      name: 'api',
      testMatch: /api\/.*\.spec\.ts/,
      use: { baseURL: apiURL },
    },
    {
      name: 'chrome-public',
      testMatch: /public\/.*\.spec\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
    {
      name: 'chrome-admin',
      testMatch: /admin\/.*\.spec\.ts/,
      dependencies: ['setup-admin'],
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        storageState: 'e2e/.auth/admin.json',
      },
    },
    {
      name: 'setup-admin',
      testMatch: /setup\/auth\.setup\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
    {
      name: 'chrome-tenant-owner',
      testMatch: /client\/owner\/.*\.spec\.ts/,
      dependencies: ['setup-owner'],
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        storageState: 'e2e/.auth/tenant-owner.json',
      },
    },
    {
      name: 'setup-owner',
      testMatch: /setup\/auth-owner\.setup\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
    {
      name: 'chrome-tenant-employee',
      testMatch: /client\/employee\/.*\.spec\.ts/,
      dependencies: ['setup-employee'],
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        storageState: 'e2e/.auth/tenant-employee.json',
      },
    },
    {
      name: 'setup-employee',
      testMatch: /setup\/auth-employee\.setup\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
    {
      name: 'chrome-no-organization',
      testMatch: /client\/no-organization\/.*\.spec\.ts/,
      dependencies: ['setup-no-org'],
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
        storageState: 'e2e/.auth/no-org.json',
      },
    },
    {
      name: 'setup-no-org',
      testMatch: /setup\/auth-no-org\.setup\.ts/,
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',
      },
    },
  ],
});
