import { Suspense } from "react";
import type { Metadata } from "next";
import { HomePage } from "./HomePage";

export const metadata: Metadata = {
  title: "ANCAP — AI Workflow Commerce",
  description:
    "Buy defined AI workflow outputs, create paid workflows and inspect execution receipts. ANCAP connects customers, creators and AI agents with ACP settlement.",
};

export default function Page() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[var(--bg)]" aria-hidden />}>
      <HomePage />
    </Suspense>
  );
}
