// file: playwright.config.js

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    // look for test files in the /e2e directory, relative to this configuration file
    testDir: './e2e',
    // run all tests in parallel
    fullyParallel: true,
    // reporter to use the container is ephemeral it will not save
    reporter: [
        ['list'],
        ['json', { outputFile: 'results.json' }],
    ],
    use: {
        viewport: { width: 2560, height: 1440 },
        deviceScaleFactor: 2,
        geolocation: { longitude: 12.492507, latitude: 41.889938 },
        permissions: ['geolocation'],
        // Docker.noble service name
        // base url to use in actions like await page.goto(/)
        // backend serves in port :8000
        baseURL: process.env.BASE_URL ?? 'http://127.0.0.1:5173',
        headless: true,
        // collect trace when retrying the failed test
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
    },
    // configure projects for major browsers
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],
    // run local dev server before starting the tests. no need for extra container for frontend
    webServer: {
        command: 'npm run dev -- --host 127.0.0.1 --port 5173',
        url: 'http://127.0.0.1:5173',
        reuseExistingServer: true,
    },
});
