import { expect, test } from "@playwright/test";

test("employee can log in and create a ticket", async ({ page }) => {
  await page.goto("/login");

  await page.getByLabel("Email").fill("employee1@example.com");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign In" }).click();

  await expect(page).toHaveURL("/");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

  await page.getByRole("main").getByRole("link", { name: "Create Ticket" }).click();

  await expect(page).toHaveURL("/tickets/new");
  await expect(page.getByRole("heading", { name: "Create Ticket" })).toBeVisible();

  await page.getByLabel("Title").fill("Playwright created ticket");
  await page
    .getByLabel("Description")
    .fill("This ticket was created by the first Playwright end-to-end test.");

  await page.getByLabel("Priority").selectOption("high");

  await page.getByRole("button", { name: "Create Ticket" }).click();

  await expect(page).toHaveURL(/\/tickets\/\d+$/);
  await expect(
    page.getByRole("heading", { name: "Playwright created ticket" })
  ).toBeVisible();
  await expect(
    page.getByText("This ticket was created by the first Playwright end-to-end test.")
  ).toBeVisible();
});