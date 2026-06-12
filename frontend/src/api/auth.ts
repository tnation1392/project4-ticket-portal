import { apiFetch } from "./client";
import type { LoginResponse, UserRead } from "../types";

export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getCurrentUser(): Promise<UserRead> {
  return apiFetch<UserRead>("/auth/me", {
    method: "GET",
  });
}
