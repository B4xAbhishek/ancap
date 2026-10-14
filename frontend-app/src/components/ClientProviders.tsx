"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { Language, isSupportedLanguage } from "@/locales/translations";
import { LanguageProvider } from "./LanguageProvider";
import { AuthProvider } from "./AuthProvider";
import { WalletProvider } from "./WalletProvider";
import { ThemeProvider } from "./ThemeProvider";
import { CookieConsent } from "./CookieConsent";
import { FloatingNewsWidget } from "./FloatingNewsWidget";
import { FloatingEarthSupportWidget } from "./FloatingEarthSupportWidget";

function ServiceWorkerRegister() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;
    let cancelled = false;
    (async () => {
      try {
        // Drop legacy cache bags that stored HTML / Next chunks (ancap-v1/v2).
        if ("caches" in window) {
          const keys = await caches.keys();
          await Promise.all(
            keys
              .filter((k) => k === "ancap-v1" || k === "ancap-v2" || k.startsWith("ancap-v"))
              .map((k) => caches.delete(k))
          );
        }
        if (cancelled) return;
        const reg = await navigator.serviceWorker.register("/sw.js");
        await reg.update();
      } catch {
        /* ignore registration failures */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);
  return null;
}

export function ClientProviders({ children, initialLang }: { children: React.ReactNode; initialLang?: string }) {
  const resolvedInitialLang: Language = isSupportedLanguage(initialLang) ? initialLang : "en";
  const pathname = usePathname();

  return (
    <ThemeProvider>
      <AuthProvider>
        <WalletProvider>
          <LanguageProvider initialLang={resolvedInitialLang}>
            <ServiceWorkerRegister />
            {children}
            {pathname === "/feed" || pathname === "/dashboard" ? <FloatingNewsWidget /> : null}
            {pathname === "/stardust" ? <FloatingEarthSupportWidget /> : null}
            <CookieConsent />
          </LanguageProvider>
        </WalletProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
