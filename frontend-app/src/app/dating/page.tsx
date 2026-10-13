import Link from "next/link";
import { Navigation } from "@/components/Navigation";

export const metadata = {
  title: "ANCAP Dating",
  description: "Proximity dating with bitchat-inspired BLE mesh and public access-point map. 18+.",
};

type AccessPoint = {
  id: string;
  title: string;
  description: string | null;
  lat: number;
  lon: number;
  ble_service_hint: string;
  status: string;
};

async function loadAccessPoints(): Promise<AccessPoint[]> {
  const base = process.env.ANCAP_SERVER_API_URL || process.env.NEXT_PUBLIC_API_BASE || "https://api.ancap.cloud/v1";
  try {
    const res = await fetch(`${base.replace(/\/$/, "")}/dating/access-points?limit=100`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return [];
    return (await res.json()) as AccessPoint[];
  } catch {
    return [];
  }
}

export default async function DatingPage() {
  const points = await loadAccessPoints();

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <main className="mx-auto max-w-3xl px-4 py-10">
        <p className="text-sm uppercase tracking-[0.2em] text-rose-300/80">Proximity · Mesh · 18+</p>
        <h1 className="mt-2 text-3xl font-semibold">ANCAP Dating</h1>
        <p className="mt-3 text-sm leading-7 text-white/68">
          Decentralized proximity dating for the ANCAP Wallet. Nearby phones advertise as{" "}
          <strong>ANCAP Dating</strong> over Bluetooth mesh (bitchat-inspired — no internet required for nearby chat).
          When online, access points appear on this map catalog.
        </p>
        <p className="mt-3 text-sm leading-7 text-white/55">
          Open the <strong>Dating</strong> tab in the mobile wallet to scan devices, create a rendezvous point, or mesh-chat.
          Legal: <Link href="/legal/dating" className="underline">/legal/dating</Link>. Spec:{" "}
          <a
            href="https://github.com/ancapcloud/ancap/blob/master/docs/mobile/ANCAP_DATING_MESH.md"
            className="underline"
            target="_blank"
            rel="noreferrer"
          >
            ANCAP_DATING_MESH.md
          </a>
          .
        </p>

        <section className="mt-10">
          <h2 className="text-lg font-semibold">Access points</h2>
          <p className="mt-1 text-sm text-white/50">
            Published rendezvous pins (BLE service hint shared with nearby scanners).
          </p>
          <ul className="mt-4 space-y-3">
            {points.map((p) => (
              <li key={p.id} className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3">
                <div className="font-medium text-white">{p.title}</div>
                {p.description ? <p className="mt-1 text-sm text-white/60">{p.description}</p> : null}
                <p className="mt-2 text-xs text-white/45">
                  {p.lat.toFixed(5)}, {p.lon.toFixed(5)} · {p.ble_service_hint}
                </p>
                <a
                  className="mt-2 inline-block text-xs text-emerald-300/90 underline"
                  href={`https://www.openstreetmap.org/?mlat=${p.lat}&mlon=${p.lon}#map=16/${p.lat}/${p.lon}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open map
                </a>
              </li>
            ))}
            {!points.length ? (
              <li className="text-sm text-white/45">
                No published access points yet. Create one from the mobile Dating tab (requires 18+ profile).
              </li>
            ) : null}
          </ul>
        </section>
      </main>
    </div>
  );
}
