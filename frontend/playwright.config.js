import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  timeout: 120000,
  use: {
    baseURL: "http://127.0.0.1:5174",
    channel: "chrome",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command: "node scripts/test-backend.mjs",
      url: "http://127.0.0.1:8010/api/v1/health",
      timeout: 120000,
    },
    {
      command: "npm run dev -- --port 5174 --strictPort",
      url: "http://127.0.0.1:5174",
      env: { API_TARGET: "http://127.0.0.1:8010" },
    },
  ],
});
