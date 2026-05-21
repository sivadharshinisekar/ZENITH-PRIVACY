"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { AccountRow } from "@/lib/api";
import { fetchAccounts, scanEmails } from "@/lib/api";
import { clearSession, getStoredEmail, getToken } from "@/lib/session";

export default function DashboardPage() {
  const router = useRouter();
  const [accounts, setAccounts] = useState<AccountRow[]>([]);
  const [filter, setFilter] = useState("");
  const [loadingList, setLoadingList] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanSummary, setScanSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const email = useMemo(() => getStoredEmail(), []);
  const filterRef = useRef(filter);
  filterRef.current = filter;

  const loadAccounts = useCallback(async () => {
    setLoadingList(true);
    setError(null);
    try {
      const q = filterRef.current.trim() || undefined;
      const res = await fetchAccounts({ q });
      setAccounts(res.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load accounts");
    } finally {
      setLoadingList(false);
    }
  }, []);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    void loadAccounts();
  }, [loadAccounts, router]);

  const handleScan = async () => {
    setScanning(true);
    setScanSummary(null);
    setError(null);
    try {
      const res = await scanEmails();
      setScanSummary(`Scanned ${res.scanned_messages} messages · ${res.accounts_found} signup signals processed`);
      await loadAccounts();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setScanning(false);
    }
  };

  const handleSignOut = () => {
    clearSession();
    router.replace("/login");
  };

  return (
    <div className="flex min-h-full flex-col bg-[var(--zenith-bg)]">
      <header className="border-b border-[var(--zenith-border)] bg-[var(--zenith-card)]/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--zenith-muted)]">Zenith Privacy</p>
            <h1 className="font-display text-xl font-semibold">Account radar</h1>
            {email ? <p className="text-sm text-[var(--zenith-muted)]">{email}</p> : null}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleScan}
              disabled={scanning}
              className="rounded-lg bg-[var(--zenith-accent)] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {scanning ? "Scanning inbox…" : "Scan my emails"}
            </button>
            <Link
              href="/"
              className="rounded-lg border border-[var(--zenith-border)] px-3 py-2 text-sm font-medium hover:bg-[var(--zenith-accent-soft)]"
            >
              Home
            </Link>
            <button
              type="button"
              onClick={handleSignOut}
              className="rounded-lg px-3 py-2 text-sm font-medium text-[var(--zenith-muted)] hover:text-[var(--zenith-fg)]"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-6 py-10">
        {scanSummary ? (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900 dark:border-emerald-900/40 dark:bg-emerald-950/30 dark:text-emerald-100">
            {scanSummary}
          </div>
        ) : null}
        {error ? (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900 dark:border-rose-900/40 dark:bg-rose-950/30 dark:text-rose-100">
            {error}
          </div>
        ) : null}

        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Detected services</h2>
            <p className="text-sm text-[var(--zenith-muted)]">
              Deduplicated by service name. Dates reflect the latest matching message we processed.
            </p>
          </div>
          <div className="flex w-full flex-col gap-2 md:w-80">
            <label className="flex flex-col text-xs font-medium text-[var(--zenith-muted)]">
              Filter by service
              <input
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") void loadAccounts();
                }}
                placeholder="e.g. Netflix"
                className="mt-1 rounded-lg border border-[var(--zenith-border)] bg-[var(--zenith-card)] px-3 py-2 text-sm text-[var(--zenith-fg)]"
              />
            </label>
            <button
              type="button"
              onClick={() => void loadAccounts()}
              className="self-end rounded-lg border border-[var(--zenith-border)] px-3 py-1.5 text-xs font-semibold hover:bg-[var(--zenith-accent-soft)]"
            >
              Apply filter
            </button>
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-[var(--zenith-border)] bg-[var(--zenith-card)] shadow-sm">
          {loadingList ? (
            <div className="px-6 py-16 text-center text-sm text-[var(--zenith-muted)]">Loading your dashboard…</div>
          ) : accounts.length === 0 ? (
            <div className="space-y-3 px-6 py-16 text-center">
              <p className="font-medium">No accounts yet</p>
              <p className="text-sm text-[var(--zenith-muted)]">
                Run a scan to look for welcome and verification emails from the last few hundred messages.
              </p>
              <button
                type="button"
                onClick={handleScan}
                disabled={scanning}
                className="rounded-lg bg-[var(--zenith-accent)] px-4 py-2 text-sm font-semibold text-white hover:opacity-95 disabled:opacity-60"
              >
                {scanning ? "Scanning…" : "Scan my emails"}
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-[var(--zenith-border)] text-sm">
                <thead className="bg-[var(--zenith-accent-soft)]/40 text-left text-xs font-semibold uppercase tracking-wide text-[var(--zenith-muted)]">
                  <tr>
                    <th className="px-4 py-3">Service</th>
                    <th className="px-4 py-3">Sender</th>
                    <th className="px-4 py-3">Email used</th>
                    <th className="px-4 py-3">Detected</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--zenith-border)]">
                  {accounts.map((row) => (
                    <tr key={row.id} className="hover:bg-[var(--zenith-accent-soft)]/30">
                      <td className="px-4 py-3 font-medium">{row.service_name}</td>
                      <td className="px-4 py-3 text-[var(--zenith-muted)]">{row.sender_email}</td>
                      <td className="px-4 py-3 text-[var(--zenith-muted)]">{row.email_used}</td>
                      <td className="px-4 py-3 text-[var(--zenith-muted)]">{formatDate(row.detected_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function formatDate(iso: string) {
  try {
    return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso));
  } catch {
    return iso;
  }
}
