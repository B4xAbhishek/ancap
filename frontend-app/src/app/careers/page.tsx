import type { Metadata } from "next";
import Link from "next/link";
import { Navigation } from "@/components/Navigation";
import { SiteLegalFooter } from "@/components/legal/LegalViews";

export const metadata: Metadata = {
  title: "Fundraising Advisor / Investor Relations — Careers | ANCAP",
  description:
    "ANCAP is hiring a Fundraising Advisor / Investor Relations Specialist for an AI & Web3 startup. Help raise capital, shape IR, and connect us with serious investors.",
};

export default function CareersPage() {
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />

      <main>
        <section
          className="relative overflow-hidden"
          style={{
            minHeight: "58vh",
            display: "flex",
            alignItems: "flex-end",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <div
            aria-hidden
            style={{
              position: "absolute",
              inset: 0,
              background:
                "radial-gradient(ellipse at 18% 15%, color-mix(in srgb, #34d399 18%, transparent), transparent 52%), linear-gradient(165deg, #061018 0%, var(--bg) 58%, color-mix(in srgb, #0b2a22 35%, var(--bg)) 100%)",
            }}
          />
          <div className="container" style={{ position: "relative", zIndex: 1, padding: "88px 24px 48px" }}>
            <p className="section-num" style={{ letterSpacing: "0.18em" }}>
              CAREERS · OPEN ROLE
            </p>
            <h1
              style={{
                fontFamily: "var(--font-display, Georgia, 'Times New Roman', serif)",
                fontSize: "clamp(2rem, 4.4vw, 3.4rem)",
                fontWeight: 700,
                letterSpacing: "-0.02em",
                lineHeight: 1.08,
                maxWidth: 920,
                margin: "12px 0 16px",
              }}
            >
              Fundraising Advisor / Investor Relations Specialist
            </h1>
            <p style={{ color: "var(--text-muted)", maxWidth: 720, lineHeight: 1.7, fontSize: "1.05rem" }}>
              AI &amp; Web3 startup · Remote-friendly · ACP-first platform
            </p>
          </div>
        </section>

        <section className="container" style={{ padding: "40px 24px 72px", maxWidth: 820 }}>
          <p style={{ color: "var(--text-muted)", lineHeight: 1.75, marginBottom: 28 }}>
            ANCAP builds paid AI workflows settled in ACP, with a live chain, wACP on BSC (1 ACP ↔ 10
            wACP), a mobile wallet, and an agent economy. We are looking for a fundraising and IR
            partner who can open serious capital conversations without overselling the product.
          </p>

          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 12 }}>Description</h2>
          <p style={{ color: "var(--text-muted)", lineHeight: 1.75, marginBottom: 20 }}>
            You will help ANCAP attract and structure financing: map investor targets, prepare clean
            IR materials, run intro and follow-up cycles, and keep messaging honest about what is
            live versus what is still on the roadmap. This is an advisory / specialist seat — not a
            guarantee of a closed round, and not a securities offering by ANCAP through this page.
          </p>

          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 12 }}>What you will do</h2>
          <ul style={{ color: "var(--text-muted)", lineHeight: 1.8, paddingLeft: 22, marginBottom: 24 }}>
            <li>Build and refresh a concise investor narrative for an AI + Web3 workflow platform</li>
            <li>Identify funds, angels, and strategic partners that fit our stage and thesis</li>
            <li>Coordinate decks, data rooms, and Q&amp;A with founders / product leads</li>
            <li>Own CRM hygiene for investor outreach and warm intros</li>
            <li>Advise on timing, terms language, and IR cadence (updates, milestones, proof)</li>
          </ul>

          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 12 }}>What we look for</h2>
          <ul style={{ color: "var(--text-muted)", lineHeight: 1.8, paddingLeft: 22, marginBottom: 24 }}>
            <li>Prior fundraising or IR work in AI, crypto, or deep-tech startups</li>
            <li>Clear written English; comfortable explaining technical products to capital allocators</li>
            <li>Existing network or a proven process for earning warm intros (not cold spam)</li>
            <li>Discipline around compliance: no fake traction, no guaranteed-return language</li>
          </ul>

          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: 12 }}>How to apply</h2>
          <p style={{ color: "var(--text-muted)", lineHeight: 1.75, marginBottom: 28 }}>
            Send a short note (who you have helped raise for, what stage, and how you work) to{" "}
            <a href="mailto:support@ancap.cloud?subject=Fundraising%20Advisor%20/%20IR" className="text-emerald-300 hover:text-emerald-200">
              support@ancap.cloud
            </a>
            . Include links to a deck you shaped or a public company you advised, if available.
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
            <a href="mailto:support@ancap.cloud?subject=Fundraising%20Advisor%20/%20IR" className="btn">
              Apply by email
            </a>
            <Link href="/" className="btn btn-ghost">
              Back to ANCAP
            </Link>
          </div>
        </section>
      </main>

      <SiteLegalFooter />
    </div>
  );
}
