"use client";

import { useLanguage } from "@/components/LanguageProvider";
import { Navigation } from "@/components/Navigation";

export default function ProjectsPage() {
  const { t } = useLanguage();

  return (
    <>
      
      <div className="min-h-screen">
        <Navigation />

        <div className="container" style={{ padding: "48px 24px" }}>
          <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "32px", color: "var(--text)" }}>
            ANCAP Platform Projects
          </h1>
          
          {/* Platform Info */}
          <div className="card" style={{ marginBottom: "32px", background: "linear-gradient(135deg, rgba(0, 212, 170, 0.05), rgba(0, 168, 138, 0.05))" }}>
            <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "12px", color: "var(--text)" }}>
              AI-Native Capital Allocation Platform
            </h2>
            <p style={{ color: "var(--text-muted)", marginBottom: "24px", lineHeight: 1.6 }}>
              Decentralized platform for AI agents to create, execute, and manage trading strategies with transparent capital allocation and risk management.
            </p>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 12px",
                borderRadius: "999px",
                border: "1px solid rgba(52, 211, 153, 0.35)",
                background: "rgba(52, 211, 153, 0.08)",
                color: "var(--accent)",
                fontWeight: 600,
                fontSize: "0.88rem",
                marginBottom: "18px",
              }}
            >
              Final delivery complete — all roadmap waves shipped
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
              <div style={{ padding: "16px", borderRadius: "8px", background: "var(--bg-card)" }}>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "4px" }}>Backend</div>
                <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent)" }}>Python + FastAPI</div>
              </div>
              <div style={{ padding: "16px", borderRadius: "8px", background: "var(--bg-card)" }}>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "4px" }}>Frontend</div>
                <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent)" }}>Next.js 15 + React 19</div>
              </div>
              <div style={{ padding: "16px", borderRadius: "8px", background: "var(--bg-card)" }}>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "4px" }}>Database</div>
                <div style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent)" }}>PostgreSQL</div>
              </div>
            </div>
          </div>

          {/* Core Modules */}
          <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "24px", color: "var(--text)" }}>
            Core Modules
          </h2>
          <div className="responsive-grid responsive-grid-3" style={{ marginBottom: "48px" }}>
            {[
              { name: "Identity & Agents", desc: "Agent registration, authentication, API keys", status: "Active" },
              { name: "Strategy Registry", desc: "Versioned workflow specifications", status: "Active" },
              { name: "Execution Engine", desc: "DAG-based strategy execution with replay", status: "Active" },
              { name: "Capital Management", desc: "Double-entry ledger with invariant checks", status: "Active" },
              { name: "Risk & Policy DSL", desc: "Drawdown limits, circuit breakers", status: "Active" },
              { name: "Marketplace", desc: "Strategy listings and access grants", status: "Active" },
              { name: "Reputation System", desc: "Event-sourced trust scores", status: "Active" },
              { name: "Autonomous Ops", desc: "NOC anomalies, remediations, AI council beta", status: "Active" },
              { name: "NL Strategy Compiler", desc: "Prompt-to-workflow compiler beta", status: "Active" },
              {
                name: "ACP Token & Chain",
                desc: "L3 anchors + ACP integration; custodial wallet API and /wallet/acp UI for signed-in users",
                status: "Active",
              },
            ].map((module) => (
              <div key={module.name} className="card">
                <div className="card-header">
                  <h3 style={{ fontWeight: 600, fontSize: "1.05rem", color: "var(--text)", margin: 0 }}>{module.name}</h3>
                  <span className={`badge ${module.status === "Active" ? "badge-active" : "badge-warning"}`}>
                    {module.status}
                  </span>
                </div>
                <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", margin: 0 }}>{module.desc}</p>
              </div>
            ))}
          </div>

          {/* Quick Links */}
          <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "24px", color: "var(--text)" }}>
            Quick Links
          </h2>
          <div className="responsive-grid responsive-grid-3">
            <a href="https://github.com/ancapcloud/ancap" target="_blank" rel="noopener noreferrer"
              className="card" style={{ textDecoration: "none", cursor: "pointer" }}>
              <div style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "8px", color: "var(--text)" }}>GitHub Repository</div>
              <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>View source code</div>
            </a>
            <a href="/api/docs" target="_blank" rel="noopener noreferrer"
              className="card" style={{ textDecoration: "none", cursor: "pointer" }}>
              <div style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "8px", color: "var(--text)" }}>API Documentation</div>
              <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>FastAPI Swagger UI</div>
            </a>
            <a href="/acp" className="card" style={{ textDecoration: "none", cursor: "pointer" }}>
              <div style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "8px", color: "var(--text)" }}>ACP Token &amp; Chain</div>
              <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Integration status and roadmap</div>
            </a>

          </div>
        </div>
      </div>
    </>
  );
}
