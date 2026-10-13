import Link from "next/link";
import { Navigation } from "@/components/Navigation";

export const metadata = {
  title: "sACP Docs",
  description: "Stable ACP — USD-targeted, ACP-collateralized commerce stablecoin.",
};

export default function SacpDocsOverviewPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="container" style={{ padding: "48px 24px 72px" }}>
        <section style={{ padding: "24px 0 32px" }}>
          <div className="card">
            <div className="card-header">
              <div>
                <div className="section-num" style={{ marginBottom: 10 }}>
                  sACP
                </div>
                <h1 style={{ fontSize: "clamp(1.8rem, 4vw, 2.8rem)", fontWeight: 800, margin: 0 }}>
                  Stable ACP
                </h1>
              </div>
              <span className="badge badge-active">Foundation</span>
            </div>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.75, marginTop: 16, maxWidth: 900 }}>
              sACP is ANCAP&apos;s commerce stablecoin: USD-targeted and ACP-collateralized on BNB Smart Chain.
              It is not the same as ACP (accounting unit) or wACP (1 ACP ↔ 10 wACP wrap), and it is not a guaranteed
              fiat redemption product.
            </p>
          </div>
        </section>

        <section className="responsive-grid responsive-grid-2" style={{ gap: 16 }}>
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Read next</h3>
            <ul style={{ margin: 0, paddingLeft: 18, lineHeight: 1.9 }}>
              <li>
                <Link href="/docs/sacp/reserve">Reserve / collateral model</Link>
              </li>
              <li>
                <Link href="/docs/sacp/risks">Risk disclosures</Link>
              </li>
              <li>
                <Link href="/docs/wacp">Compare with wACP</Link>
              </li>
              <li>
                <a href="https://github.com/ancapcloud/ancap/blob/master/docs/STABLECOIN_SACP_SPEC.md">
                  Spec (STABLECOIN_SACP_SPEC.md)
                </a>
              </li>
            </ul>
          </div>

          <div className="card">
            <h3 style={{ marginTop: 0 }}>Public API</h3>
            <ul style={{ margin: 0, paddingLeft: 18, lineHeight: 1.9, color: "var(--text-muted)" }}>
              <li>
                <code>/api/v1/sacp/status</code>
              </li>
              <li>
                <code>/api/v1/sacp/reserve-proof</code>
              </li>
              <li>Exchange catalog asset: <code>sacp_bsc</code></li>
              <li>Contract source: <code>contracts/bridge-bsc/src/SACP.sol</code></li>
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}
