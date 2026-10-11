import Link from "next/link";

export default function LegalTeleportEarphonesRetiredPage() {
  return (
    <main style={{ maxWidth: 640, margin: "48px auto", padding: "0 24px", lineHeight: 1.7 }}>
      <h1 style={{ fontWeight: 800 }}>Teleport earphones retired</h1>
      <p style={{ color: "var(--text-muted)" }}>
        This medevac fiction SKU is no longer offered on the public launch surface.
      </p>
      <p>
        <Link href="/aeterna">AETERNA</Link>
        {" · "}
        <Link href="/legal">Legal hub</Link>
      </p>
    </main>
  );
}
