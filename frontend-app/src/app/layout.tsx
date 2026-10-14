import type { Metadata } from "next";
import { cookies, headers } from "next/headers";
// Local Inter (no Google Fonts fetch at build time — CI e2e was failing on next/font/google).
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/inter/cyrillic-400.css";
import "@fontsource/inter/cyrillic-500.css";
import "@fontsource/inter/cyrillic-600.css";
import "@fontsource/inter/cyrillic-700.css";
import "./globals.css";
import { ClientProviders } from "@/components/ClientProviders";
import { ChunkErrorRecovery } from "@/components/ChunkErrorRecovery";
import { NetworkBackground } from "@/components/NetworkBackground";
import { ProjectWorkflowContext } from "@/components/ProjectWorkflowContext";
import { detectPreferredLanguage } from "@/lib/language";

// Build a sane absolute base for canonical/OG links. Override via NEXT_PUBLIC_SITE_URL
// in Docker/CI when serving from a different host, otherwise default to ancap.cloud.
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://ancap.cloud";
const SITE_TITLE = "ANCAP — AI Workflow Commerce";
const SITE_DESCRIPTION =
  "Buy defined AI workflow outputs, create paid workflows and inspect execution receipts. ANCAP connects customers, creators and AI agents with ACP settlement.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: SITE_TITLE,
    template: "%s · ANCAP",
  },
  description: SITE_DESCRIPTION,
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [{ url: "/icons/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "ANCAP",
  },
  formatDetection: {
    telephone: false,
  },
  other: {
    "mobile-web-app-capable": "yes",
  },
  manifest: "/manifest.json",
  openGraph: {
    siteName: SITE_TITLE,
    type: "website",
    url: "/",
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const headerStore = await headers();
  const initialLang = detectPreferredLanguage({
    cookieLang: cookieStore.get("ancap-lang")?.value,
    countryCode:
      headerStore.get("x-vercel-ip-country") ||
      headerStore.get("cf-ipcountry") ||
      headerStore.get("x-country-code") ||
      headerStore.get("cloudfront-viewer-country"),
    acceptLanguage: headerStore.get("accept-language"),
  });

  return (
    <html lang={initialLang} suppressHydrationWarning>
      <body className="font-inter antialiased" suppressHydrationWarning>
        <ChunkErrorRecovery />
        <ClientProviders initialLang={initialLang}>
          <NetworkBackground />
          <ProjectWorkflowContext />
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}
