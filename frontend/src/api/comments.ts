import { apiFetch } from "./client";
import type {CommentCreateRequest, CommentRead} from "../types";

export async function getComments(ticketId: string): Promise<CommentRead[]> {
  return apiFetch<CommentRead[]>(`/tickets/${ticketId}/comments`, {
    method: "GET",
  });
}

export async function createComment(
  ticketId: string,
  payload: CommentCreateRequest
): Promise<CommentRead> {
  return apiFetch<CommentRead>(`/tickets/${ticketId}/comments`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
