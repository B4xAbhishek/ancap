import Link from "next/link";
import { Navigation } from "@/components/Navigation";

export const metadata = {
  title: "wACP PancakeSwap",
  description: "PancakeSwap V3 bootstrap liquidity and V2 reference market for wACP.",
};

const V2_POOL = "0xF391ca2bcBaB93Afa23326ebF1e35DB950841601";
const V3_POOL =
  process.env.NEXT_PUBLIC_WACP_V3_POOL?.trim().toLowerCase() ||
  "0xe626bd3ef516c4f784e5d5fb46e297d9c0d7f5e1";
const WACP = "0x349797E2f1A4FD722Af2dB181ab1C4ED7606F402";
const USDT = "0x55d398326f99059fF775485246999027B3197955";
const V3_POOL_URL =
  process.env.NEXT_PUBLIC_WACP_V3_POOL_URL?.trim() ||
  `https://pancakeswap.finance/liquidity/pool/bsc/${V3_POOL}`;

export default function WacpPancakeDocsPage() {
  return (
    <>
      <div className="min-h-screen">
        <Navigation />
        <main className="container" style={{ padding: "48px 24px 72px" }}>
          <div className="card">
            <div className="card-header">
              <h1 style={{ margin: 0, fontWeight: 800 }}>wACP → PancakeSwap</h1>
              <span className="badge badge-active">Playbook</span>
            </div>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.75 }}>
              New scarce liquidity targets <strong>PancakeSwap V3</strong> concentrated <code>wACP/USDT</code>.
              The existing <strong>V2</strong> pair remains a thin canonical reference market (smoke /{" "}
              <strong>checkout oracle</strong> until V3 depth passes quote smoke).
            </p>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.75 }}>
              Operator playbook (Stage A/B/C):{" "}
              <a
                href="https://github.com/ancapcloud/ancap/blob/master/docs/WACP_LIQUIDITY_V3_PLAYBOOK.md"
                target="_blank"
                rel="noreferrer"
              >
                WACP_LIQUIDITY_V3_PLAYBOOK.md
              </a>
            </p>

            <h2 style={{ marginTop: 24, fontWeight: 700 }}>V3 primary (bootstrap / shallow)</h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.75 }}>
              Live pool exists for discovery and small swaps. Depth is <strong>not</strong> deep-market
              infrastructure — large size uses{" "}
              <Link href="/buy-acp">OTC / Exchange</Link>. Platform checkout oracle stays on V2 until
              operator sets <code>WACP_ORACLE_USE_V3=true</code> after acceptable slippage smoke.
            </p>
            <div style={{ marginTop: 8, display: "grid", gap: 8, color: "var(--text-muted)" }}>
              <div>
                <strong style={{ color: "var(--text)" }}>Pool:</strong>{" "}
                <a href={V3_POOL_URL} target="_blank" rel="noreferrer">
                  open V3 pool (0.25%)
                </a>
              </div>
              <div>
                <strong style={{ color: "var(--text)" }}>Address:</strong> <code>{V3_POOL}</code>
              </div>
              <div>
                <strong style={{ color: "var(--text)" }}>Fee tier:</strong> 0.25% (2500)
              </div>
              <div>
                <strong style={{ color: "var(--text)" }}>GeckoTerminal:</strong>{" "}
                <a
                  href={`https://www.geckoterminal.com/bsc/pools/${V3_POOL}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  V3 pool chart
                </a>
              </div>
            </div>

            <h2 style={{ marginTop: 28, fontWeight: 700 }}>V2 reference (thin / oracle)</h2>
            <ol style={{ lineHeight: 1.9, color: "var(--text-muted)" }}>
              <li>wACP production contract verified on BSC explorer</li>
              <li>Reserve / bridge / risk / contracts docs published</li>
              <li>Public reserve proof: <code>/api/v1/wacp/reserve-proof</code></li>
              <li>V2 pair: <code>{V2_POOL}</code></li>
              <li>
                Initial liquidity bootstrap tx:{" "}
                <code>0x82458ec2b17e5aa58201a625169e493bb5ce8159487d66846906d9de69587503</code>
              </li>
            </ol>
            <div style={{ marginTop: 16, display: "grid", gap: 8, color: "var(--text-muted)" }}>
              <div>
                <strong style={{ color: "var(--text)" }}>V2 pool:</strong>{" "}
                <a
                  href={`https://pancakeswap.finance/liquidity/pool/bsc/${V2_POOL}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  open pool
                </a>
              </div>
              <div>
                <strong style={{ color: "var(--text)" }}>Swap:</strong>{" "}
                <a
                  href={`https://pancakeswap.finance/swap?inputCurrency=${USDT}&outputCurrency=${WACP}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  USDT → wACP
                </a>
              </div>
            </div>

            <h2 style={{ marginTop: 28, fontWeight: 700 }}>Profit path (not LP APR)</h2>
            <p style={{ color: "var(--text-muted)", lineHeight: 1.75 }}>
              Revenue is ACP spent on workflows, paid API, marketplace, and pay — fees land in the
              platform treasury. After non-zero fee income, recycle an approved tranche into this V3
              pool (human-signed). See{" "}
              <Link href="/buy-acp">Buy ACP → spend golden path</Link> and{" "}
              <Link href="/treasury">/treasury</Link>.
            </p>

            <p style={{ marginTop: 24, color: "var(--text-muted)", lineHeight: 1.75 }}>
              Large orders relative to active V3 depth should use{" "}
              <Link href="/buy-acp">OTC / exchange office routing</Link> instead of consuming the full
              concentrated band. wACP on BSC uses <strong>18 decimals</strong> on-chain.
            </p>
          </div>
        </main>
      </div>
    </>
  );
}
