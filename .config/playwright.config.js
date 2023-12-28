import { defineConfig } from "@playwright/test";

const base = defineConfig({
	use: {
		screenshot: "only-on-failure",
		trace: "retain-on-failure",
		permissions: ["clipboard-read", "clipboard-write"],
		bypassCSP: true,
		launchOptions: {
			args: ["--disable-web-security"]
		}
	},
	expect: { timeout: 60000 },
	timeout: 90000,
	testMatch: /.*.spec.ts/,
	testDir: "..",
	workers: process.env.CI ? 1 : undefined
});

const normal = defineConfig(base, {
	globalSetup: "./playwright-setup.js"
});
normal.projects = undefined; // Explicitly unset this field due to https://github.com/microsoft/playwright/issues/28795

const lite = defineConfig(base, {
	webServer: {
		command: "pnpm --filter @gradio/app dev:lite",
		url: "http://localhost:9876/lite.html",
		reuseExistingServer: !process.env.CI
	}
});
lite.projects = undefined; // Explicitly unset this field due to https://github.com/microsoft/playwright/issues/28795

export default !!process.env.GRADIO_E2E_TEST_LITE ? lite : normal;
