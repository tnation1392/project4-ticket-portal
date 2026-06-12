export type UserRole = "employee" | "agent" | "admin";

export interface UserRead {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserRead;
}

export type TicketStatus =
  | "new"
  | "triaged"
  | "in_progress"
  | "waiting_for_customer"
  | "resolved"
  | "closed";

export type TicketPriority = "low" | "medium" | "high" | "urgent";

export interface CategoryRead {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TicketRead {
  id: number;
  title: string;
  description: string;
  category_id: number;
  priority: TicketPriority;
  status: TicketStatus;
  created_by_user_id: number;
  assigned_to_user_id: number | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  closed_at: string | null;
}

export interface TicketCreateRequest {
  title: string;
  description: string;
  category_id: number;
  priority: TicketPriority;
}

export interface CommentRead {
  id: number;
  ticket_id: number;
  author_user_id: number;
  body: string;
  is_internal: boolean;
  created_at: string;
}

export interface CommentCreateRequest {
  body: string;
  is_internal: boolean;
}