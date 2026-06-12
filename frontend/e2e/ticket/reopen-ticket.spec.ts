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

test("employee can reopen a resolved ticket", async ({ page }) => {
  const ticketTitle = `Playwright reopen ticket ${Date.now()}`;
  const ticketDescription =
    "This ticket is used to verify employee reopen workflow.";

  // Employee creates the ticket
  await login(page, "employee1@example.com", "password123");
  await createTicketAsEmployee(page, ticketTitle, ticketDescription);

  const ticketUrl = page.url();

  await expect(page.getByText(/^Status:\s*new$/)).toBeVisible();

  await logout(page);

  // Agent takes ticket through workflow to resolved
  await login(page, "agent1@example.com", "password123");
  await page.goto(ticketUrl);

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();

  // Assign to self
  await expect(page.getByRole("button", { name: "Assign to Me" })).toBeVisible();
  await page.getByRole("button", { name: "Assign to Me" }).click();
  await expect(page.getByText(/This ticket is assigned to User/i)).toBeVisible();

  // Triaged
  await expect(page.getByRole("button", { name: "Mark Triaged" })).toBeVisible();
  await page.getByRole("button", { name: "Mark Triaged" }).click();
  await expect(page.getByText(/^Status:\s*triaged$/)).toBeVisible();

  // In progress
  await expect(page.getByRole("button", { name: "Start Work" })).toBeVisible();
  await page.getByRole("button", { name: "Start Work" }).click();
  await expect(page.getByText(/^Status:\s*in_progress$/)).toBeVisible();

  // Resolve
  await expect(page.getByRole("button", { name: "Resolve Ticket" })).toBeVisible();
  await page.getByRole("button", { name: "Resolve Ticket" }).click();
  await expect(page.getByText(/^Status:\s*resolved$/)).toBeVisible();

  await logout(page);

  // Employee reopens the resolved ticket
  await login(page, "employee1@example.com", "password123");
  await page.goto(ticketUrl);

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();
  await expect(page.getByText(/^Status:\s*resolved$/)).toBeVisible();

  // Employee should see requester-side actions
  await expect(page.getByRole("button", { name: "Close Ticket" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Reopen Ticket" })).toBeVisible();

  await page.getByRole("button", { name: "Reopen Ticket" }).click();

  await expect(page.getByText(/^Status:\s*in_progress$/)).toBeVisible();

  // Refresh to prove persistence
  await page.reload();

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();
  await expect(page.getByText(/^Status:\s*in_progress$/)).toBeVisible();
});