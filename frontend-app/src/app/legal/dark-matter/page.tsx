import Link from "next/link";

export default function LegalDarkMatterRetiredPage() {
  return (
    <main style={{ maxWidth: 640, margin: "48px auto", padding: "0 24px", lineHeight: 1.7 }}>
      <h1 style={{ fontWeight: 800 }}>Dark matter desk retired</h1>
      <p style={{ color: "var(--text-muted)" }}>
        The symbolic dark-matter auction is no longer offered on the public launch surface.
      </p>
      <p>
        <Link href="/legal">Legal hub</Link>
        {" · "}
        <Link href="/">Home</Link>
      </p>
    </main>
  );
}
