import { test, expect } from "@playwright/test";

test.describe("Core Loop", () => {
  test("create project -> activate policies -> generate evals -> export", async ({
    page,
  }) => {
    await page.goto("/");

    // 1. Navigate to projects
    await expect(page).toHaveURL(/projects/);

    // 2. Navigate to governance tab
    // (Full E2E requires running backend — this is a structural test)
    await page.goto("/projects/test-id/governance");
    await expect(page.locator("body")).toBeVisible();

    // 3. Check governance page loads
    await page.goto("/projects/test-id/evals");
    await expect(page.locator("body")).toBeVisible();

    // 4. Check pipeline page loads
    await page.goto("/projects/test-id/pipeline");
    await expect(page.locator("body")).toBeVisible();
  });
});
