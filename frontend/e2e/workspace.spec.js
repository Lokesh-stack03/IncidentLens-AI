import { test, expect } from "@playwright/test";
import { resolve } from "node:path";

test("complete local investigation and document workflow", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByText("Backend connected")).toBeVisible();
  await page.getByRole("button", { name: /^Integrations/ }).click();
  await page.getByRole("button", { name: "Add integration" }).click();
  await page.getByLabel("Name", { exact: true }).fill("Local health API");
  await page.getByLabel("API URL").fill("http://127.0.0.1:8010/api/v1/health");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("Saved successfully.")).toBeVisible();
  await page.getByRole("button", { name: "Run check" }).click();
  await expect(
    page.getByText("Local health API responded successfully."),
  ).toBeVisible();

  await page.getByRole("button", { name: "Edit Local health API" }).click();
  await page
    .getByLabel("API URL")
    .fill("http://127.0.0.1:8010/api/v1/not-found");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("Saved successfully.")).toBeVisible();
  await page.getByRole("button", { name: "Run check" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "An incident was created",
  );
  await page.getByRole("button", { name: /^Incidents/ }).click();
  await page
    .getByRole("button", { name: "API request failed", exact: true })
    .click();
  await page.getByLabel("Incident status").selectOption("INVESTIGATING");
  await expect(page.getByLabel("Incident status")).toBeEnabled();
  await page.getByRole("button", { name: "Analyze with Gemini" }).click();
  await expect(page.getByRole("dialog").getByRole("alert")).toContainText(
    "GEMINI_API_KEY",
  );
  await page.getByLabel("Incident status").selectOption("RESOLVED");
  await expect(page.getByLabel("Incident status")).toBeEnabled();
  await page.getByRole("button", { name: "Close incident" }).click();
  await expect(page.getByText("RESOLVED", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: "Report incident" }).click();
  await page
    .getByLabel("Title", { exact: true })
    .fill("Simulated manual report");
  await page
    .getByLabel("Error message")
    .fill("Simulated HTTP 500 for a class demonstration");
  await page.getByLabel("HTTP status (optional)").fill("500");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Simulated manual report", exact: true }),
  ).toBeVisible();
  await page.getByLabel("Filter by status").selectOption("OPEN");
  await expect(
    page.getByRole("button", { name: "API request failed", exact: true }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Simulated manual report", exact: true })
    .click();
  page.once("dialog", (dialog) => dialog.accept());
  await page
    .getByRole("button", { name: "Delete incident", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByLabel("Filter by status").selectOption("ALL");

  await page.getByRole("button", { name: /^Knowledge base/ }).click();
  await page.getByLabel("Upload PDF").setInputFiles(resolve("../sample.pdf"));
  await expect(page.getByText(/pages processed into/)).toBeVisible({
    timeout: 90000,
  });
  await page.getByLabel("Search document content").fill("API request timeout");
  await page.getByRole("button", { name: "Search", exact: true }).click();
  await expect(page.locator(".result").first()).toBeVisible({ timeout: 30000 });
  await expect(page.locator(".result").first()).toContainText("sample.pdf");
  await expect(page.locator(".result").first()).toContainText("Page");
  await page.screenshot({
    path: "test-results/knowledge-desktop.png",
    fullPage: true,
  });
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Delete sample.pdf" }).click();
  await expect(
    page.getByText("Your uploaded PDFs will appear here."),
  ).toBeVisible();

  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Overview" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.screenshot({
    path: "test-results/overview-mobile.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: /^Incidents/ }).click();
  await page
    .getByRole("button", { name: "API request failed", exact: true })
    .click();
  page.once("dialog", (dialog) => dialog.accept());
  await page
    .getByRole("button", { name: "Delete incident", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.getByRole("button", { name: /^Integrations/ }).click();
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Delete Local health API" }).click();
  await expect(page.getByText("Connect your first API")).toBeVisible();
  expect(errors).toEqual([]);
});
