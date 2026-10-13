import Link from "next/link";
import { Navigation } from "@/components/Navigation";

export const metadata = {
  title: "ANCAP Dating — Legal",
  description: "18+ proximity dating and BLE mesh disclosures for ANCAP Dating.",
};

export default function DatingLegalPage() {
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <main className="mx-auto max-w-3xl px-4 py-10 prose prose-invert">
        <h1>ANCAP Dating — notice</h1>
        <p>
          ANCAP Dating is an <strong>18+</strong> proximity / mesh feature of the ANCAP Wallet. By creating a profile or
          enabling mesh you attest you are at least 18 years old.
        </p>
        <ul>
          <li>Not a guarantee of matches, safety, or continuous connectivity.</li>
          <li>Bluetooth mesh is visible to nearby radios; it is not strong anonymity.</li>
          <li>Access-point coordinates you publish may appear on <Link href="/dating">ancap.cloud/dating</Link>.</li>
          <li>Protocol inspiration: public-domain bitchat-style mesh messaging — ANCAP uses its own branded UUID/packets.</li>
          <li>Report abuse via in-app report or support channels; ANCAP may suspend accounts.</li>
        </ul>
        <p>
          Product page: <Link href="/dating">/dating</Link>. Spec:{" "}
          <a href="https://github.com/ancapcloud/ancap/blob/master/docs/mobile/ANCAP_DATING_MESH.md">
            docs/mobile/ANCAP_DATING_MESH.md
          </a>
          .
        </p>
      </main>
    </div>
  );
}
