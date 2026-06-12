import { expect, Page, test } from "@playwright/test";

async function login(page: Page, email: string, password: string) {
  await page.goto("/login");

  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign In" }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
}

async function logout(page: Page) {
  await page.getByRole("button", { name: "Logout" }).click();
  await expect(page).toHaveURL(/\/login$/);
}

async function createTicketAsEmployee(
  page: Page,
  title: string,
  description: string
) {
  await page.getByRole("main").getByRole("link", { name: "Create Ticket" }).click();

  await expect(page).toHaveURL(/\/tickets\/new$/);
  await expect(page.getByRole("heading", { name: "Create Ticket" })).toBeVisible();

  await page.getByLabel("Title").fill(title);
  await page.getByLabel("Description").fill(description);
  await page.getByLabel("Priority").selectOption("medium");

  await page.getByRole("button", { name: "Create Ticket" }).click();

  await expect(page).toHaveURL(/\/tickets\/\d+$/);
  await expect(page.getByRole("heading", { name: title })).toBeVisible();
}

test("agent can self-assign an unassigned ticket", async ({ page }) => {
  const ticketTitle = `Playwright self-assign ticket ${Date.now()}`;
  const ticketDescription =
    "This ticket is used to verify agent self-assignment through Playwright.";

  // Employee creates the ticket
  await login(page, "employee1@example.com", "password123");
  await createTicketAsEmployee(page, ticketTitle, ticketDescription);

  // Capture the detail page URL so the agent can revisit it
  const ticketUrl = page.url();

  // Log out employee
  await logout(page);

  // Log in as agent
  await login(page, "agent1@example.com", "password123");

  // Open the same ticket
  await page.goto(ticketUrl);

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();

  // The assignment button should be visible for agent on an unassigned ticket
  await expect(page.getByRole("button", { name: "Assign to Me" })).toBeVisible();

  await page.getByRole("button", { name: "Assign to Me" }).click();

  // After assignment, the button should disappear and assignment text should update
  await expect(page.getByRole("button", { name: "Assign to Me" })).toBeHidden();

  await expect(page.getByText(/This ticket is assigned to User/i)).toBeVisible();

  // Refresh to prove persistence, not just local UI state
  await page.reload();

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();
  await expect(page.getByText(/This ticket is assigned to User/i)).toBeVisible();
});