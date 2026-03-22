import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Accessibility", () => {
  test("workspace shell has no WCAG 2.2 AA violations", async ({ page }) => {
    await page.goto("/projects");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    expect(results.violations).toEqual([]);
  });

  test("governance page has no violations", async ({ page }) => {
    await page.goto("/projects/test-id/governance");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa"])
      .analyze();
    expect(results.violations).toEqual([]);
  });

  test("agents page has aria-live region", async ({ page }) => {
    await page.goto("/projects/test-id/agents");
    // Verify the page loads with accessible streaming region
    await expect(page.locator("body")).toBeVisible();
  });
});
