export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";

export function googleRedirectUri(): string {
  if (typeof window === "undefined") {
    return "";
  }
  return `${window.location.origin}/auth/callback`;
}
