"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { exchangeGoogleCode } from "@/lib/api";
import { googleRedirectUri } from "@/lib/config";
import { setSession } from "@/lib/session";

function CallbackContent() {
  const params = useSearchParams();
  const router = useRouter();
  const [message, setMessage] = useState("Completing sign-in…");

  useEffect(() => {
    const code = params.get("code");
    const error = params.get("error");
    if (error) {
      setMessage(`Google returned an error: ${error}`);
      return;
    }
    if (!code) {
      setMessage("Missing authorization code. Start again from the login page.");
      return;
    }

    const redirect = "http://localhost:3000/auth/callback";
    if (!redirect) {
      setMessage("Unable to resolve redirect URI.");
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const res = await exchangeGoogleCode(code, redirect);
        if (cancelled) return;
        setSession(res.access_token, res.user_email);
        router.replace("/dashboard");
      } catch (e) {
        if (!cancelled) {
          setMessage(e instanceof Error ? e.message : "Authentication failed");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [params, router]);

  return (
    <div className="mx-auto flex max-w-lg flex-col gap-4 px-6 py-24 text-center">
      <h1 className="font-display text-2xl font-semibold">Finishing Google sign-in</h1>
      <p className="text-sm text-[var(--zenith-muted)]">{message}</p>
      <Link href="/login" className="text-sm font-medium text-[var(--zenith-accent)] hover:underline">
        Return to login
      </Link>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="px-6 py-24 text-center text-sm text-[var(--zenith-muted)]">Preparing secure redirect…</div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
