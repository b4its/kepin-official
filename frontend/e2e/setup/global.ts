import { config as loadEnv } from 'dotenv';
import { resolve } from 'path';

export default async function globalSetup() {
  loadEnv({ path: resolve(__dirname, '../.env.e2e') });
}
