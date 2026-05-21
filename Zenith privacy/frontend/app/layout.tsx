import type { Metadata } from "next";
import { IBM_Plex_Sans, Newsreader } from "next/font/google";
import "./globals.css";

const body = IBM_Plex_Sans({
  variable: "--font-zenith-body",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const display = Newsreader({
  variable: "--font-zenith-display",
  subsets: ["latin"],
  weight: ["500", "600"],
});

export const metadata: Metadata = {
  title: "Zenith Privacy",
  description: "Discover which services are linked to your Gmail inbox.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${body.variable} ${display.variable} h-full`}>
      <body className="min-h-full bg-[var(--zenith-bg)] font-sans text-[var(--zenith-fg)] antialiased">
        {children}
      </body>
    </html>
  );
}
