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

test("agent can add an internal comment and employee cannot see it", async ({ page }) => {
  const ticketTitle = `Playwright internal comment ticket ${Date.now()}`;
  const ticketDescription =
    "This ticket is used to verify internal comment visibility rules.";
  const internalComment = "This is a Playwright internal comment.";

  // Employee creates the ticket
  await login(page, "employee1@example.com", "password123");
  await createTicketAsEmployee(page, ticketTitle, ticketDescription);

  const ticketUrl = page.url();

  await logout(page);

  // Agent adds an internal comment
  await login(page, "agent1@example.com", "password123");
  await page.goto(ticketUrl);

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();
  await expect(page.getByLabel("Mark as internal comment")).toBeVisible();

  const commentTextbox = page.getByRole("textbox", { name: /^Comment$/ });
  const internalCheckbox = page.getByLabel("Mark as internal comment");
  const commentsSection = page
    .locator("section")
    .filter({ has: page.getByRole("heading", { name: "Comments" }) });

  await commentTextbox.fill(internalComment);
  await internalCheckbox.check();
  await page.getByRole("button", { name: "Add Comment" }).click();

  // Wait for successful submit to complete
  await expect(commentTextbox).toHaveValue("");
  await expect(internalCheckbox).not.toBeChecked();

  // Assert against the Comments section, not the form
  await expect(commentsSection.getByText(internalComment)).toBeVisible();
  await expect(commentsSection.getByText(/^Internal Comment$/)).toBeVisible();

  await logout(page);

  // Employee revisits the same ticket and should NOT see the internal comment
  await login(page, "employee1@example.com", "password123");
  await page.goto(ticketUrl);

  await expect(page.getByRole("heading", { name: ticketTitle })).toBeVisible();

  // Employee should not see the internal comment text
  await expect(commentsSection.getByText(internalComment)).toHaveCount(0);

  // Employee should not see the internal-comment checkbox
  await expect(page.getByLabel("Mark as internal comment")).toHaveCount(0);
});
``