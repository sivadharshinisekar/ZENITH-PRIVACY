import { API_BASE } from "./config";
import { getToken } from "./session";

export type AccountRow = {
  id: number;
  service_name: string;
  sender_email: string;
  email_used: string;
  detected_at: string;
};

export type AccountsResponse = {
  items: AccountRow[];
  total: number;
  page: number;
  page_size: number;
};

async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string | null } = {},
): Promise<T> {
  const token = options.token ?? getToken();
  const headers: HeadersInit = {
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function exchangeGoogleCode(code: string, redirectUri: string) {
  return apiFetch<{ access_token: string; user_email: string }>("/auth/google", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, redirect_uri: redirectUri }),
    token: null,
  });
}

export async function scanEmails() {
  return apiFetch<{ scanned_messages: number; accounts_found: number }>("/scan-emails", {
    method: "POST",
  });
}

export async function fetchAccounts(params?: { q?: string; page?: number }) {
  const sp = new URLSearchParams();
  if (params?.q) sp.set("q", params.q);
  if (params?.page) sp.set("page", String(params.page));
  const qs = sp.toString();
  return apiFetch<AccountsResponse>(`/accounts${qs ? `?${qs}` : ""}`);
}
