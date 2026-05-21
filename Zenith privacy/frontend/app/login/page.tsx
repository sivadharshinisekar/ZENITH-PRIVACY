"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { GOOGLE_CLIENT_ID } from "@/lib/config";
import { buildGoogleAuthUrl } from "@/lib/google";
import { getToken } from "@/lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [missingConfig, setMissingConfig] = useState(false);

  useEffect(() => {
    if (getToken()) {
      router.replace("/dashboard");
    }
    if (!GOOGLE_CLIENT_ID) {
      setMissingConfig(true);
    }
  }, [router]);

  return (
    <div className="flex min-h-full flex-col bg-[var(--zenith-bg)]">
      <header className="border-b border-[var(--zenith-border)] bg-[var(--zenith-card)]/80 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <Link href="/" className="font-display text-lg font-semibold">
            Zenith Privacy
          </Link>
          <Link href="/" className="text-sm text-[var(--zenith-muted)] hover:text-[var(--zenith-fg)]">
            Back home
          </Link>
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center px-6 py-16">
        <div className="rounded-2xl border border-[var(--zenith-border)] bg-[var(--zenith-card)] p-8 shadow-lg">
          <h1 className="font-display text-2xl font-semibold">Sign in with Google</h1>
          <p className="mt-2 text-sm leading-relaxed text-[var(--zenith-muted)]">
            We request read-only Gmail access to scan recent messages for signup confirmations. Raw bodies are not
            stored on our servers.
          </p>
          {missingConfig ? (
            <p className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-100">
              Set <code className="font-mono text-xs">NEXT_PUBLIC_GOOGLE_CLIENT_ID</code> in{" "}
              <code className="font-mono text-xs">frontend/.env.local</code> to enable the button.
            </p>
          ) : null}
          <button
            type="button"
            disabled={missingConfig}
            onClick={() => {
              window.location.href = buildGoogleAuthUrl();
            }}
            className="mt-8 flex w-full items-center justify-center gap-2 rounded-xl border border-[var(--zenith-border)] bg-white px-4 py-3 text-sm font-semibold text-[var(--zenith-fg)] shadow-sm transition hover:bg-[var(--zenith-accent-soft)] disabled:cursor-not-allowed disabled:opacity-60 dark:bg-slate-900"
          >
            <GoogleMark />
            Login with Google
          </button>
        </div>
      </main>
    </div>
  );
}

function GoogleMark() {
  return (
    <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden>
      <path
        fill="#FFC107"
        d="M43.611 20.083H42V20H24v8h11.303C33.42 32.575 29.288 35 24 35c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"
      />
      <path
        fill="#FF3D00"
        d="m6.306 14.691 6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"
      />
      <path
        fill="#4CAF50"
        d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"
      />
      <path
        fill="#1976D2"
        d="M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 0 1-4.087 5.571l.003-.002 6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z"
      />
    </svg>
  );
}
