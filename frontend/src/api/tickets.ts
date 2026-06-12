import { apiFetch } from "./client";
import type { TicketCreateRequest, TicketRead, TicketStatus } from "../types";

export async function getTickets(): Promise<TicketRead[]> {
  return apiFetch<TicketRead[]>("/tickets", {
    method: "GET",
  });
}

export async function getTicketById(ticketId: string): Promise<TicketRead> {
  return apiFetch<TicketRead>(`/tickets/${ticketId}`, {
    method: "GET",
  });
}

export async function createTicket(payload: TicketCreateRequest): Promise<TicketRead> {
  return apiFetch<TicketRead>("/tickets", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function assignTicket(
  ticketId: string,
  assignedToUserId: number
): Promise<TicketRead> {
  return apiFetch<TicketRead>(`/tickets/${ticketId}/assign`, {
    method: "POST",
    body: JSON.stringify({
      assigned_to_user_id: assignedToUserId,
    }),
  });
}

export async function transitionTicket(
  ticketId: string,
  toStatus: TicketStatus
): Promise<TicketRead> {
  return apiFetch<TicketRead>(`/tickets/${ticketId}/transition`, {
    method: "POST",
    body: JSON.stringify({
      to_status: toStatus,
    }),
  });
}