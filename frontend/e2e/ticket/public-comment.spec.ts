import { expect, test } from "@playwright/test";

test("employee can add a public comment to a ticket", async ({ page }) => {
  await page.goto("/login");

  await page.getByLabel("Email").fill("employee1@example.com");
  await page.getByLabel("Password").fill("password123");
  await page.getByRole("button", { name: "Sign In" }).click();

  await expect(page).toHaveURL("/");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

  await page.getByRole("main").getByRole("link", { name: "Create Ticket" }).click();

  await expect(page).toHaveURL("/tickets/new");
  await expect(page.getByRole("heading", { name: "Create Ticket" })).toBeVisible();

  const ticketTitle = `Playwright comment ticket ${Date.now()}`;
  const ticketDescription =
    "This ticket is used to verify public comment creation through Playwright.";
  const commentBody = "This is a Playwright public comment.";

  await page.getByLabel("Title").fill(ticketTitle);
  await page.getByLabel("Description").fill(ticketDescription);
  await page.getByLabel("Priority").selectOption("medium");

  await page.getByRole("button", { name: "Create Ticket" }).click();

  await expect(page).toHaveURL(/\/tickets\/\d+$/);
  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();

  await page.getByLabel("Public Comment").fill(commentBody);
  await page.getByRole("button", { name: "Add Comment" }).click();

  await expect(page.getByText(commentBody)).toBeVisible();

  await page.reload();

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();
  await expect(page.getByText(commentBody)).toBeVisible();
});