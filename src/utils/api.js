const STORAGE_KEY = "mindspace_auth_token";

export function getAuthToken() {
  return typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
}

export function setAuthToken(token) {
  if (typeof window !== "undefined") {
    localStorage.setItem(STORAGE_KEY, token);
  }
}

export function clearAuthToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export async function apiFetch(path, options = {}) {
  const token = getAuthToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(path, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    clearAuthToken();
    const error = new Error("Unauthorized");
    error.status = 401;
    throw error;
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "API request failed");
  }

  return res.json();
}
