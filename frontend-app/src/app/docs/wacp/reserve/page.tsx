import { Navigation } from "@/components/Navigation";

export const metadata = {
  title: "wACP Reserve",
  description: "Reserve proof model and backing invariant for wACP.",
};

export default function WacpReserveDocsPage() {
  return (
    <>
      <div className="min-h-screen">
        <Navigation />
        <main className="container" style={{ padding: "48px 24px 72px" }}>
          <div className="card">
            <div className="card-header">
              <h1 style={{ margin: 0, fontWeight: 800 }}>wACP reserve model</h1>
              <span className="badge badge-info">No reserve proof = no liquidity</span>
            </div>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.75 }}>
              Canonical invariant: <code>minted_wACP_on_BSC &lt;= locked_or_custodied_ACP_reserve - operational_buffer</code>.
              ACP has 8 decimals. wACP on BSC has 18 decimals. Conversion target (pad × wrap 1 ACP ↔ 10 wACP):{" "}
              <code>wacp_wei = acp_smallest_unit * 10^11</code>.
            </p>
            <ul style={{ lineHeight: 1.9, color: "var(--text-muted)" }}>
              <li>Healthy: backing ratio &gt;= 1.0</li>
              <li>Degraded: ratio near threshold or telemetry stale</li>
              <li>Critical: minted supply exceeds reserve-equivalent backing</li>
            </ul>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.75 }}>
              Public reserve proof should be exposed via <code>/api/v1/wacp/reserve-proof</code> and linked from wallet / bridge surfaces.
            </p>
          </div>
        </main>
      </div>
    </>
  );
}
