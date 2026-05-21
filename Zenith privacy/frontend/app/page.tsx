import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b border-[var(--zenith-border)] bg-[var(--zenith-card)]/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <span className="font-display text-xl font-semibold tracking-tight">Zenith Privacy</span>
          <Link
            href="/login"
            className="rounded-lg bg-[var(--zenith-accent)] px-4 py-2 text-sm font-medium text-white shadow-sm hover:opacity-95"
          >
            Sign in
          </Link>
        </div>
      </header>
      <main className="mx-auto flex max-w-5xl flex-1 flex-col gap-10 px-6 py-16">
        <section className="max-w-2xl space-y-4">
          <p className="text-sm font-medium uppercase tracking-wide text-[var(--zenith-accent)]">
            Inbox intelligence
          </p>
          <h1 className="font-display text-4xl font-semibold leading-tight text-balance md:text-5xl">
            See which online accounts echo through your Gmail
          </h1>
          <p className="text-lg leading-relaxed text-[var(--zenith-muted)]">
            Connect Google securely, scan recent messages for common signup patterns, and review a concise list of
            services—without storing full email bodies.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-lg bg-[var(--zenith-accent)] px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:opacity-95"
            >
              Continue with Google
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-lg border border-[var(--zenith-border)] bg-[var(--zenith-card)] px-5 py-2.5 text-sm font-semibold hover:bg-[var(--zenith-accent-soft)]"
            >
              Open dashboard
            </Link>
          </div>
        </section>
        <section className="grid gap-4 md:grid-cols-3">
          {[
            {
              title: "Read-only Gmail",
              body: "OAuth scopes are limited to metadata and snippets needed for detection—not full archives.",
            },
            {
              title: "Pattern-based signals",
              body: "Heuristics flag welcome and verification emails so you can audit signups quickly.",
            },
            {
              title: "Encrypted tokens",
              body: "Refresh tokens are encrypted at rest; only derived account rows are shown in the UI.",
            },
          ].map((card) => (
            <article
              key={card.title}
              className="rounded-2xl border border-[var(--zenith-border)] bg-[var(--zenith-card)] p-5 shadow-sm"
            >
              <h2 className="font-display text-lg font-semibold">{card.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-[var(--zenith-muted)]">{card.body}</p>
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}
