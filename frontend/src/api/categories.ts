import { apiFetch } from "./client";
import type { CategoryRead } from "../types";

export async function getCategories(): Promise<CategoryRead[]> {
  return apiFetch<CategoryRead[]>("/categories", {
    method: "GET",
  });
}