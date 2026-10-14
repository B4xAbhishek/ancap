import { fallbackWorkflowBundles, fallbackWorkflowTemplates, type WorkflowBundle, type WorkflowTemplate } from "@/lib/workflowStore";
import { getServerApiBase, serverApiFetch } from "@/lib/serverApi";
import { WorkflowsCatalog } from "./WorkflowsCatalog";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const API_BASE = getServerApiBase();

async function getWorkflowTemplates(): Promise<{ items: WorkflowTemplate[]; fallback: boolean }> {
  try {
    const res = await serverApiFetch(`${API_BASE}/workflow-store/templates`, {
      cache: "no-store",
    });

    if (!res.ok) {
      return { items: fallbackWorkflowTemplates, fallback: true };
    }

    const data = (await res.json()) as { items: WorkflowTemplate[] };
    return data.items?.length ? { items: data.items, fallback: false } : { items: fallbackWorkflowTemplates, fallback: true };
  } catch {
    return { items: fallbackWorkflowTemplates, fallback: true };
  }
}

async function getWorkflowBundles(): Promise<WorkflowBundle[]> {
  try {
    const res = await serverApiFetch(`${API_BASE}/workflow-store/bundles`, {
      cache: "no-store",
    });

    if (!res.ok) {
      return fallbackWorkflowBundles;
    }

    const data = (await res.json()) as { items: WorkflowBundle[] };
    return data.items?.length ? data.items : fallbackWorkflowBundles;
  } catch {
    return fallbackWorkflowBundles;
  }
}

export default async function WorkflowsPage() {
  const [workflows, bundles] = await Promise.all([getWorkflowTemplates(), getWorkflowBundles()]);
  return <WorkflowsCatalog workflows={workflows.items} bundles={bundles} isFallback={workflows.fallback} />;
}
