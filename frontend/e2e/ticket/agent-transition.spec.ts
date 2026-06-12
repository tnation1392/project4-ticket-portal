import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";

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

test("agent can assign, triage, and move a ticket to in progress", async ({ page }) => {
  const ticketTitle = `Playwright transition ticket ${Date.now()}`;
  const ticketDescription =
    "This ticket is used to verify agent assignment and transition workflow.";

  // Employee creates the ticket
  await login(page, "employee1@example.com", "password123");
  await createTicketAsEmployee(page, ticketTitle, ticketDescription);

  const ticketUrl = page.url();

  // Verify ticket starts as new
  await expect(page.getByText("Status: new")).toBeVisible();

  await logout(page);

  // Agent opens the same ticket
  await login(page, "agent1@example.com", "password123");
  await page.goto(ticketUrl);

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();

  // Agent should be able to self-assign
  await expect(page.getByRole("button", { name: "Assign to Me" })).toBeVisible();
  await page.getByRole("button", { name: "Assign to Me" }).click();

  await expect(page.getByText(/This ticket is assigned to User/i)).toBeVisible();

  // Agent should be able to mark ticket triaged
  await expect(page.getByRole("button", { name: "Mark Triaged" })).toBeVisible();
  await page.getByRole("button", { name: "Mark Triaged" }).click();

  await expect(page.getByText("Status: triaged")).toBeVisible();

  // After triage, agent should be able to start work
  await expect(page.getByRole("button", { name: "Start Work" })).toBeVisible();
  await page.getByRole("button", { name: "Start Work" }).click();

  await expect(page.getByText("Status: in_progress")).toBeVisible();

  // Refresh to prove workflow state persisted
  await page.reload();

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();
  await expect(page.getByText("Status: in_progress")).toBeVisible();
  await expect(page.getByText(/This ticket is assigned to User/i)).toBeVisible();
});