const API_BASE_URL = "http://127.0.0.1:8000";

export function getAuthToken(): string | null {
  return localStorage.getItem("access_token");
}

export function setAuthToken(token: string): void {
  localStorage.setItem("access_token", token);
}

export function clearAuthToken(): void {
  localStorage.removeItem("access_token");
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = "Request failed";

    try {
      const errorBody = await response.json();
      errorMessage = errorBody.detail || errorMessage;
    } catch {
      // ignore JSON parsing issues for error body
    }

    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}