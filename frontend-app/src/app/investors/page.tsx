import type { Metadata } from "next";
import { InvestorOverview } from "./InvestorOverview";
export const metadata: Metadata = {
  title: "Investor overview — AI workflow commerce",
  description: "ANCAP's workflow commerce model, product evidence, expansion portfolio and funding milestones.",
};
export default function InvestorsPage() { return <InvestorOverview />; }
