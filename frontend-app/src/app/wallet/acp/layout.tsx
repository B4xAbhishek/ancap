import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "ACP Wallet",
  description:
    "Receive and send native ACP, review network activity and manage wallet security.",
  alternates: { canonical: "/wallet/acp" },
  robots: { index: false, follow: false },
};
export default function WalletLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
