"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Navigation } from "@/components/Navigation";
import { useAuth } from "@/components/AuthProvider";
import { useLanguage } from "@/components/LanguageProvider";
import { apiFetch } from "@/lib/api";
import { workflowOpsCopy } from "@/locales/workflowOps";
import {
  downloadWorkflowJson,
  parseWorkflowCsv,
  quoteWorkflowPlan,
  resultSummary,
} from "@/lib/workflowOps";

type DocumentInput = { name: string; content: string };
type Project = {
  id: string;
  owner_user_id: string;
  members: Record<string, string>;
  name: string;
  context: { text?: string; documents?: DocumentInput[] };
  retention_days: number;
};
type Connection = {
  id: string;
  name: string;
  kind: string;
  config: Record<string, string>;
  credential_stored: boolean;
  allow_delivery: boolean;
};
type Definition = {
  name: string;
  project_id: string;
  steps: { slug: string; inputs: Record<string, unknown> }[];
  inputs: Record<string, unknown>;
  coin_ids: string[];
  require_review: boolean;
  connection_ids: string[];
  provider_connection_id: string | null;
  test_cases: { name: string; required_text: string[] }[];
};
type Automation = {
  id: string;
  owner_user_id: string;
  project_id: string;
  name: string;
  versions: { version: number; definition: Definition; hash: string }[];
  published_version: number | null;
  enabled: boolean;
  interval_minutes: number;
  monthly_budget_acp: string;
  spent_acp: string;
};
type Operation = {
  id: string;
  automation_id: string | null;
  kind: string;
  state: string;
  cost_acp: string;
  progress: {
    cursor?: number;
    output?: unknown;
    items?: {
      run_id: string;
      output: unknown;
      quality: unknown;
      row: number;
      step: number;
    }[];
    quality?: unknown;
    deliveries?: { connection_id: string; state: string; message?: string }[];
    error?: string;
  };
};
type CatalogItem = {
  slug: string;
  title: string;
  price: { amount: string; currency: string };
};
type Workspace = {
  user_id: string;
  is_operator: boolean;
  projects: Project[];
  connections: Connection[];
  automations: Automation[];
  runs: Operation[];
};
const emptyWorkspace: Workspace = {
  user_id: "",
  is_operator: false,
  projects: [],
  connections: [],
  automations: [],
  runs: [],
};
const field =
  "w-full min-w-0 rounded-xl border border-[var(--border)] bg-[var(--bg)] px-3 py-2.5 text-sm text-[var(--text)]";
const button =
  "rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold disabled:opacity-40";
const panel =
  "rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 sm:p-7";

export function WorkflowStudio() {
  const { lang } = useLanguage();
  const c = workflowOpsCopy[lang];
  const { isAuthenticated, isLoading } = useAuth();
  const [tab, setTab] = useState("trial"),
    [data, setData] = useState<Workspace>(emptyWorkspace),
    [catalog, setCatalog] = useState<CatalogItem[]>([]),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState("");
  const [projectId, setProjectId] = useState(""),
    [projectName, setProjectName] = useState(""),
    [context, setContext] = useState(""),
    [documents, setDocuments] = useState<DocumentInput[]>([]),
    [retention, setRetention] = useState(30),
    [inviteEmail, setInviteEmail] = useState(""),
    [inviteRole, setInviteRole] = useState("viewer");
  const [connectionName, setConnectionName] = useState(""),
    [kind, setKind] = useState("webhook"),
    [target, setTarget] = useState(""),
    [targetRange, setTargetRange] = useState("Sheet1!A:D"),
    [credential, setCredential] = useState(""),
    [deliveryConsent, setDeliveryConsent] = useState(false);
  const [automationId, setAutomationId] = useState(""),
    [autoName, setAutoName] = useState(""),
    [steps, setSteps] = useState<string[]>(["token-listing-pack"]),
    [stepInputs, setStepInputs] = useState<Record<string, unknown>[]>([{}]),
    [extraInputs, setExtraInputs] = useState<Record<string, unknown>>({}),
    [task, setTask] = useState(""),
    [assets, setAssets] = useState(""),
    [requiredText, setRequiredText] = useState(""),
    [requireReview, setRequireReview] = useState(true),
    [connectionIds, setConnectionIds] = useState<string[]>([]),
    [providerId, setProviderId] = useState(""),
    [version, setVersion] = useState(1);
  const [interval, setIntervalMinutes] = useState(1440),
    [budget, setBudget] = useState(""),
    [maxCost, setMaxCost] = useState(""),
    [spendConsent, setSpendConsent] = useState(false),
    [batchRows, setBatchRows] = useState<Record<string, string>[]>([]),
    [trialName, setTrialName] = useState(""),
    [trialDescription, setTrialDescription] = useState(""),
    [reviewNote, setReviewNote] = useState(""),
    [edited, setEdited] = useState(""),
    [economics, setEconomics] = useState<Record<string, unknown> | null>(null);
  const project = data.projects.find((p) => p.id === projectId);
  const automation = data.automations.find((a) => a.id === automationId);
  const isOwner = !automation || automation.owner_user_id === data.user_id;
  const canEditProject =
    !project ||
    project.owner_user_id === data.user_id ||
    project.members?.[data.user_id] === "editor";
  const estimate = quoteWorkflowPlan(
    steps.map(
      (slug) => catalog.find((t) => t.slug === slug)?.price.amount || "invalid",
    ),
    Math.max(1, batchRows.length),
  );
  const load = useCallback(async () => {
    if (isAuthenticated) setData(await apiFetch("/workflow-ops"));
  }, [isAuthenticated]);
  useEffect(() => {
    Promise.all([
      apiFetch("/workflow-store/templates"),
      apiFetch("/workflow-ops/capabilities"),
    ])
      .then(([templates, cap]) => {
        setCatalog(
          templates.items.filter((x: CatalogItem) =>
            cap.workflow_slugs.includes(x.slug),
          ),
        );
      })
      .catch((e) => setNotice(String(e.message)));
  }, []);
  useEffect(() => {
    if (!isAuthenticated) {
      setData(emptyWorkspace);
      return;
    }
    void load().catch((e) => setNotice(e.message));
    const timer = window.setInterval(() => void load().catch(() => {}), 10000);
    return () => clearInterval(timer);
  }, [isAuthenticated, load]);
  async function action(job: () => Promise<unknown>) {
    setBusy(true);
    setNotice("");
    try {
      await job();
      await load();
      setNotice(c.done);
    } catch (e) {
      setNotice(`${c.error}: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setBusy(false);
    }
  }
  const request = (path: string, body: unknown, method = "POST") =>
    apiFetch(`/workflow-ops${path}`, { method, body: JSON.stringify(body) });
  function selectProject(id: string) {
    setProjectId(id);
    const p = data.projects.find((x) => x.id === id);
    setProjectName(p?.name || "");
    setContext(p?.context.text || "");
    setDocuments(p?.context.documents || []);
    setRetention(p?.retention_days || 30);
  }
  function applyDefinition(d: Definition, id = "") {
    setAutomationId(id);
    setAutoName(d.name);
    selectProject(d.project_id);
    setSteps(d.steps.map((s) => s.slug));
    setStepInputs(d.steps.map((s) => s.inputs || {}));
    setExtraInputs(d.inputs || {});
    setTask(String(d.inputs?.task_description || ""));
    setAssets(d.coin_ids.join(", "));
    setRequireReview(d.require_review);
    setConnectionIds(id ? d.connection_ids : []);
    setProviderId(id ? d.provider_connection_id || "" : "");
    setRequiredText(d.test_cases.flatMap((t) => t.required_text).join(", "));
    setSpendConsent(false);
  }
  function selectAutomation(a: Automation) {
    applyDefinition(a.versions[a.versions.length - 1].definition, a.id);
    setVersion(
      a.published_version || a.versions[a.versions.length - 1].version,
    );
    setBudget(a.monthly_budget_acp === "0" ? "" : a.monthly_budget_acp);
    setIntervalMinutes(a.interval_minutes);
    setTab("builder");
  }
  const definition = (): Definition => ({
    name: autoName,
    project_id: projectId,
    steps: steps.map((slug, i) => ({ slug, inputs: stepInputs[i] || {} })),
    inputs: {
      ...extraInputs,
      project_name: project?.name || projectName,
      task_description: task,
      language: lang,
    },
    coin_ids: assets
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
    require_review: requireReview,
    connection_ids: connectionIds,
    provider_connection_id: providerId || null,
    test_cases: requiredText.trim()
      ? [
          {
            name: "Required text",
            required_text: requiredText
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
          },
        ]
      : [],
  });
  async function uploadDocuments(files: FileList | null) {
    if (!files) return;
    const next = [...documents];
    for (const f of Array.from(files)) {
      if (f.size > 64000 || !/^.*\.(txt|md|csv)$/i.test(f.name))
        throw new Error("TXT/MD/CSV, maximum 64 KB per file");
      const content = await f.text();
      if (content.length > 16000)
        throw new Error("Document exceeds 16000 characters");
      next.push({ name: f.name, content });
    }
    if (next.length > 10) throw new Error("Maximum 10 documents");
    setDocuments(next);
  }
  async function queue(mode: "manual" | "test" | "batch") {
    await request(`/automations/${automationId}/runs`, {
      idempotency_key: crypto.randomUUID(),
      max_cost_acp: maxCost,
      kind: mode,
      inputs: {},
      rows: mode === "batch" ? batchRows : [],
    });
    setSpendConsent(false);
    setTab("runs");
  }
  function label(text: string, control: React.ReactNode) {
    return (
      <label className="block space-y-2 text-sm">
        <span className="font-medium">{text}</span>
        {control}
      </label>
    );
  }
  const tabs = [
    "trial",
    "projects",
    "connections",
    "builder",
    "runs",
    ...(data.is_operator ? ["economics"] : []),
  ];
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <Navigation />
      <main className="mx-auto max-w-6xl px-4 py-10 sm:py-14">
        <header className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-[var(--accent)]">
            ANCAP
          </p>
          <h1 className="mt-3 text-3xl font-semibold sm:text-5xl">{c.title}</h1>
          <p className="mt-4 leading-7 text-[var(--text-muted)]">{c.lead}</p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link href="/ai/workflows" className={button}>
              {c.steps}
            </Link>
            <Link href="/docs/workflow-operations" className={button}>
              {c.config}
            </Link>
            <button
              className={button}
              onClick={() =>
                action(async () =>
                  downloadWorkflowJson(
                    "ancap-private-profile.json",
                    await apiFetch("/workflow-ops/private-profile"),
                  ),
                )
              }
              disabled={!isAuthenticated || busy}
            >
              {c.privateProfile}
            </button>
          </div>
          <p className="mt-3 text-xs leading-6 text-[var(--text-muted)]">
            {c.privateNote}
          </p>
        </header>
        <nav aria-label={c.title} className="my-8 flex flex-wrap gap-2">
          {tabs.map((t) => (
            <button
              key={t}
              aria-pressed={tab === t}
              className={`${button} ${tab === t ? "bg-[var(--accent)] text-slate-950" : ""}`}
              onClick={() => {
                setTab(t);
                if (t === "economics")
                  void action(async () =>
                    setEconomics(
                      await apiFetch("/workflow-ops/admin/economics"),
                    ),
                  );
              }}
            >
              {c[t as keyof typeof c]}
            </button>
          ))}
        </nav>
        {notice && (
          <p
            role="status"
            className="mb-5 break-words rounded-xl border border-[var(--border)] p-4"
          >
            {notice}
          </p>
        )}
        {!isLoading && !isAuthenticated && (
          <div className="mb-6 rounded-xl border border-[var(--border)] p-5">
            <Link
              href="/login?next=%2Fai%2Fstudio"
              className="font-semibold text-[var(--accent)]"
            >
              {c.login} →
            </Link>
          </div>
        )}
        {tab === "trial" && (
          <section className={`${panel} max-w-3xl`}>
            <h2 className="text-2xl font-semibold">{c.trial}</h2>
            <p className="my-4 text-sm leading-7 text-[var(--text-muted)]">
              {c.trialNote}
            </p>
            <div className="space-y-4">
              {label(
                c.trialName,
                <input
                  className={field}
                  value={trialName}
                  onChange={(e) => setTrialName(e.target.value)}
                  maxLength={120}
                />,
              )}
              {label(
                c.trialDescription,
                <textarea
                  className={field}
                  value={trialDescription}
                  onChange={(e) => setTrialDescription(e.target.value)}
                  maxLength={2000}
                  rows={5}
                />,
              )}
              <button
                className={button}
                disabled={
                  !isAuthenticated ||
                  busy ||
                  trialName.length < 2 ||
                  trialDescription.length < 10
                }
                onClick={() =>
                  action(async () => {
                    await request("/trial", {
                      project_name: trialName,
                      description: trialDescription,
                      language: lang,
                    });
                    setTab("runs");
                  })
                }
              >
                {c.runTrial}
              </button>
            </div>
          </section>
        )}
        {tab === "projects" && (
          <div className="grid gap-6 lg:grid-cols-[1fr_2fr]">
            <section className={panel}>
              <h2 className="mb-4 text-xl font-semibold">{c.projects}</h2>
              <button className={button} onClick={() => selectProject("")}>
                {c.create}
              </button>
              <ul className="mt-4 space-y-3">
                {data.projects.map((p) => (
                  <li key={p.id}>
                    <button
                      className="text-left text-[var(--accent)]"
                      onClick={() => selectProject(p.id)}
                    >
                      {p.name}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
            <section className={panel}>
              <div className="space-y-4">
                {label(
                  c.name,
                  <input
                    className={field}
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    maxLength={120}
                    disabled={!canEditProject}
                  />,
                )}
                {label(
                  c.context,
                  <textarea
                    className={field}
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    rows={6}
                    maxLength={16000}
                    disabled={!canEditProject}
                  />,
                )}
                {label(
                  c.docs,
                  <input
                    className={field}
                    type="file"
                    accept=".txt,.md,.csv"
                    multiple
                    disabled={!canEditProject}
                    onChange={(e) =>
                      void action(() => uploadDocuments(e.target.files))
                    }
                  />,
                )}
                <ul className="space-y-2">
                  {documents.map((d, i) => (
                    <li
                      key={`${d.name}-${i}`}
                      className="flex items-center justify-between gap-3 text-sm"
                    >
                      <span className="break-all">{d.name}</span>
                      <button
                        className={button}
                        disabled={!canEditProject}
                        onClick={() =>
                          setDocuments((ds) => ds.filter((_, j) => j !== i))
                        }
                      >
                        {c.remove}
                      </button>
                    </li>
                  ))}
                </ul>
                {label(
                  c.retention,
                  <input
                    className={field}
                    type="number"
                    value={retention}
                    min={1}
                    max={365}
                    disabled={!canEditProject}
                    onChange={(e) => setRetention(Number(e.target.value))}
                  />,
                )}
                <div className="flex flex-wrap gap-3">
                  <button
                    className={button}
                    disabled={
                      busy ||
                      !isAuthenticated ||
                      !projectName ||
                      !canEditProject
                    }
                    onClick={() =>
                      action(async () => {
                        const p = await request(
                          projectId ? `/projects/${projectId}` : "/projects",
                          {
                            name: projectName,
                            context,
                            documents,
                            retention_days: retention,
                          },
                          projectId ? "PUT" : "POST",
                        );
                        setProjectId(p.id);
                      })
                    }
                  >
                    {c.save}
                  </button>
                  {project?.owner_user_id === data.user_id && (
                    <button
                      className={button}
                      disabled={busy}
                      onClick={() =>
                        action(async () => {
                          await apiFetch(
                            `/workflow-ops/projects/${projectId}`,
                            { method: "DELETE" },
                          );
                          selectProject("");
                        })
                      }
                    >
                      {c.delete}
                    </button>
                  )}
                </div>
                {project?.owner_user_id === data.user_id && (
                  <fieldset className="space-y-3 border-t border-[var(--border)] pt-5">
                    <legend className="pt-5 font-semibold">{c.share}</legend>
                    {label(
                      c.invite,
                      <input
                        className={field}
                        type="email"
                        value={inviteEmail}
                        onChange={(e) => setInviteEmail(e.target.value)}
                      />,
                    )}
                    {label(
                      c.role,
                      <select
                        className={field}
                        value={inviteRole}
                        onChange={(e) => setInviteRole(e.target.value)}
                      >
                        <option value="viewer">{c.viewer}</option>
                        <option value="editor">{c.editor}</option>
                        <option value="remove">{c.remove}</option>
                      </select>,
                    )}
                    <button
                      className={button}
                      disabled={busy || !inviteEmail}
                      onClick={() =>
                        action(() =>
                          request(`/projects/${projectId}/members`, {
                            email: inviteEmail,
                            role: inviteRole,
                          }),
                        )
                      }
                    >
                      {c.share}
                    </button>
                  </fieldset>
                )}
              </div>
            </section>
          </div>
        )}
        {tab === "connections" && (
          <div className="grid gap-6 lg:grid-cols-2">
            <section className={panel}>
              <h2 className="mb-5 text-xl font-semibold">{c.connections}</h2>
              <div className="space-y-4">
                {label(
                  c.name,
                  <input
                    className={field}
                    value={connectionName}
                    maxLength={120}
                    onChange={(e) => setConnectionName(e.target.value)}
                  />,
                )}
                {label(
                  c.integrations,
                  <select
                    className={field}
                    value={kind}
                    onChange={(e) => {
                      setKind(e.target.value);
                      setTarget(
                        e.target.value === "anthropic"
                          ? "claude-sonnet-4-6"
                          : "",
                      );
                      setCredential("");
                      setDeliveryConsent(false);
                    }}
                  >
                    {[
                      "webhook",
                      "telegram",
                      "google_sheets",
                      "hubspot",
                      "anthropic",
                    ].map((k) => (
                      <option key={k} value={k}>
                        {
                          (
                            {
                              webhook: "HTTPS webhook",
                              telegram: "Telegram",
                              google_sheets: "Google Sheets",
                              hubspot: "HubSpot notes",
                              anthropic: "Anthropic BYOK",
                            } as Record<string, string>
                          )[k]
                        }
                      </option>
                    ))}
                  </select>,
                )}
                {kind !== "hubspot" &&
                  label(
                    (
                      {
                        webhook: "HTTPS URL",
                        telegram: "Telegram chat ID",
                        google_sheets: "Spreadsheet ID",
                        anthropic: "Model",
                      } as Record<string, string>
                    )[kind],
                    <input
                      className={field}
                      value={target}
                      onChange={(e) => setTarget(e.target.value)}
                    />,
                  )}
                {kind === "google_sheets" &&
                  label(
                    c.config,
                    <input
                      className={field}
                      value={targetRange}
                      onChange={(e) => setTargetRange(e.target.value)}
                    />,
                  )}
                {label(
                  c.creds,
                  <input
                    className={field}
                    type="password"
                    autoComplete="off"
                    value={credential}
                    onChange={(e) => setCredential(e.target.value)}
                  />,
                )}
                {kind !== "anthropic" && (
                  <label className="flex items-start gap-3 text-sm">
                    <input
                      type="checkbox"
                      checked={deliveryConsent}
                      onChange={(e) => setDeliveryConsent(e.target.checked)}
                    />
                    {c.consent}
                  </label>
                )}
                <p className="text-xs leading-6 text-[var(--text-muted)]">
                  {c.byokNote}
                </p>
                <button
                  className={button}
                  disabled={
                    busy ||
                    !isAuthenticated ||
                    !connectionName ||
                    !credential ||
                    (kind !== "anthropic" && !deliveryConsent)
                  }
                  onClick={() =>
                    action(async () => {
                      const config =
                        kind === "webhook"
                          ? { url: target }
                          : kind === "telegram"
                            ? { chat_id: target }
                            : kind === "google_sheets"
                              ? { spreadsheet_id: target, range: targetRange }
                              : kind === "anthropic"
                                ? { model: target }
                                : {};
                      await request("/connections", {
                        name: connectionName,
                        kind,
                        config,
                        secret: credential,
                        allow_delivery: deliveryConsent,
                      });
                      setCredential("");
                    })
                  }
                >
                  {c.save}
                </button>
              </div>
            </section>
            <section className={panel}>
              <ul className="space-y-5">
                {data.connections.map((connection) => (
                  <li
                    key={connection.id}
                    className="border-b border-[var(--border)] pb-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <span>
                        {connection.name} · {connection.kind}
                      </span>
                      <button
                        className={button}
                        disabled={busy}
                        onClick={() =>
                          action(() =>
                            apiFetch(
                              `/workflow-ops/connections/${connection.id}`,
                              { method: "DELETE" },
                            ),
                          )
                        }
                      >
                        {c.delete}
                      </button>
                    </div>
                    <p className="mt-3 text-xs text-[var(--text-muted)]">
                      {c.connectionNote}
                    </p>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        )}
        {tab === "builder" && (
          <div className="space-y-6">
            <section className={panel}>
              <div className="flex flex-wrap items-center gap-3">
                <button
                  className={button}
                  onClick={() => {
                    setAutomationId("");
                    setAutoName("");
                    setSteps(["token-listing-pack"]);
                    setStepInputs([{}]);
                    setExtraInputs({});
                    setTask("");
                    setConnectionIds([]);
                    setProviderId("");
                    setSpendConsent(false);
                  }}
                >
                  {c.builder} +
                </button>
                {data.automations.map((a) => (
                  <button
                    key={a.id}
                    className={button}
                    aria-pressed={a.id === automationId}
                    onClick={() => selectAutomation(a)}
                  >
                    {a.name}
                  </button>
                ))}
              </div>
            </section>
            <section className={panel}>
              <div className="grid gap-4 sm:grid-cols-2">
                {label(
                  c.autoName,
                  <input
                    className={field}
                    value={autoName}
                    maxLength={120}
                    onChange={(e) => setAutoName(e.target.value)}
                    disabled={!isOwner}
                  />,
                )}
                {label(
                  c.project,
                  <select
                    className={field}
                    value={projectId}
                    onChange={(e) => selectProject(e.target.value)}
                    disabled={!!automationId}
                  >
                    <option value="">{c.selectProject}</option>
                    {data.projects.map((p) => (
                      <option value={p.id} key={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>,
                )}
              </div>
              <h3 className="mb-3 mt-6 font-semibold">{c.steps}</h3>
              <ol className="space-y-3">
                {steps.map((slug, i) => (
                  <li
                    key={i}
                    className="flex flex-wrap items-center gap-3 rounded-xl border border-[var(--border)] p-3"
                  >
                    <span className="text-sm">{i + 1} →</span>
                    <select
                      aria-label={`${c.steps} ${i + 1}`}
                      className={`${field} flex-1`}
                      value={slug}
                      disabled={!isOwner}
                      onChange={(e) =>
                        setSteps((s) =>
                          s.map((v, j) => (j === i ? e.target.value : v)),
                        )
                      }
                    >
                      {catalog.map((t) => (
                        <option key={t.slug} value={t.slug}>
                          {t.title} · {t.price.amount} {t.price.currency}
                        </option>
                      ))}
                    </select>
                    <button
                      className={button}
                      aria-label={`↑ ${i + 1}`}
                      disabled={!isOwner || i === 0}
                      onClick={() => {
                        setStepInputs((values) => {
                          const n = [...values];
                          [n[i - 1], n[i]] = [n[i], n[i - 1]];
                          return n;
                        });
                        setSteps((s) => {
                          const n = [...s];
                          [n[i - 1], n[i]] = [n[i], n[i - 1]];
                          return n;
                        });
                      }}
                    >
                      ↑
                    </button>
                    <button
                      className={button}
                      disabled={!isOwner || steps.length === 1}
                      onClick={() => {
                        setStepInputs((s) => s.filter((_, j) => j !== i));
                        setSteps((s) => s.filter((_, j) => j !== i));
                      }}
                    >
                      {c.remove}
                    </button>
                  </li>
                ))}
              </ol>
              <button
                className={`${button} mt-3`}
                disabled={!isOwner || steps.length >= 5}
                onClick={() => {
                  setSteps((s) => [...s, "token-listing-pack"]);
                  setStepInputs((s) => [...s, {}]);
                }}
              >
                {c.addStep}
              </button>
              <div className="mt-5 space-y-4">
                {label(
                  c.inputs,
                  <textarea
                    className={field}
                    rows={4}
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    maxLength={12000}
                    disabled={!isOwner}
                  />,
                )}
                {label(
                  c.assets,
                  <input
                    className={field}
                    placeholder="bitcoin, ethereum"
                    value={assets}
                    onChange={(e) => setAssets(e.target.value)}
                    disabled={!isOwner}
                  />,
                )}
                {label(
                  c.quality,
                  <input
                    className={field}
                    placeholder="Required text, required phrase"
                    value={requiredText}
                    onChange={(e) => setRequiredText(e.target.value)}
                    disabled={!isOwner}
                  />,
                )}
                <p className="text-xs leading-6 text-[var(--text-muted)]">
                  {c.qualityNote}
                </p>
                <label className="flex items-center gap-3 text-sm">
                  <input
                    type="checkbox"
                    checked={requireReview}
                    onChange={(e) => setRequireReview(e.target.checked)}
                    disabled={!isOwner}
                  />
                  {c.review}
                </label>
                <fieldset>
                  <legend className="mb-2 text-sm font-medium">
                    {c.delivery}
                  </legend>
                  <div className="flex flex-wrap gap-4">
                    {data.connections
                      .filter(
                        (conn) =>
                          conn.kind !== "anthropic" && conn.allow_delivery,
                      )
                      .map((conn) => (
                        <label
                          key={conn.id}
                          className="flex items-center gap-2 text-sm"
                        >
                          <input
                            type="checkbox"
                            checked={connectionIds.includes(conn.id)}
                            disabled={!isOwner}
                            onChange={(e) =>
                              setConnectionIds((ids) =>
                                e.target.checked
                                  ? [...ids, conn.id]
                                  : ids.filter((id) => id !== conn.id),
                              )
                            }
                          />
                          {conn.name}
                        </label>
                      ))}
                  </div>
                </fieldset>
                {label(
                  c.provider,
                  <select
                    className={field}
                    value={providerId}
                    disabled={!isOwner}
                    onChange={(e) => setProviderId(e.target.value)}
                  >
                    <option value="">ANCAP</option>
                    {data.connections
                      .filter((conn) => conn.kind === "anthropic")
                      .map((conn) => (
                        <option key={conn.id} value={conn.id}>
                          {conn.name}
                        </option>
                      ))}
                  </select>,
                )}
                {providerId && (
                  <p className="text-xs leading-6">{c.byokNote}</p>
                )}
                <div className="flex flex-wrap gap-3">
                  <button
                    className={button}
                    disabled={
                      busy ||
                      !isAuthenticated ||
                      !isOwner ||
                      !autoName ||
                      !projectId
                    }
                    onClick={() =>
                      action(async () => {
                        const a = await request(
                          automationId
                            ? `/automations/${automationId}/versions`
                            : "/automations",
                          definition(),
                        );
                        setAutomationId(a.id);
                        setVersion(a.versions[a.versions.length - 1].version);
                      })
                    }
                  >
                    {c.save}
                  </button>
                  {automation && (
                    <>
                      <select
                        aria-label={c.version}
                        className={`${field} w-28`}
                        value={version}
                        onChange={(e) => setVersion(Number(e.target.value))}
                      >
                        {automation.versions.map((v) => (
                          <option value={v.version} key={v.version}>
                            {c.version} {v.version}
                          </option>
                        ))}
                      </select>
                      <button
                        className={button}
                        disabled={busy || !isOwner}
                        onClick={() =>
                          action(() =>
                            request(`/automations/${automationId}/publish`, {
                              version,
                            }),
                          )
                        }
                      >
                        {c.publish} / {c.rollback}
                      </button>
                      <button
                        className={button}
                        onClick={() =>
                          action(async () =>
                            downloadWorkflowJson(
                              "ancap-workflow-plan.json",
                              await apiFetch(
                                `/workflow-ops/automations/${automationId}/export`,
                              ),
                            ),
                          )
                        }
                      >
                        {c.export}
                      </button>
                    </>
                  )}
                </div>
                {label(
                  c.loadPlan,
                  <input
                    className={field}
                    type="file"
                    accept=".json"
                    onChange={(e) =>
                      void action(async () => {
                        const f = e.target.files?.[0];
                        if (!f || f.size > 200000)
                          throw new Error("Plan exceeds limit");
                        const plan = JSON.parse(await f.text());
                        if (plan.format !== "ancap-workflow-plan/v1")
                          throw new Error("Unsupported plan");
                        applyDefinition({
                          ...plan.definition,
                          project_id: projectId,
                          connection_ids: [],
                          provider_connection_id: null,
                          require_review: true,
                        });
                      })
                    }
                  />,
                )}
              </div>
            </section>
            {automation && isOwner && (
              <section className={panel}>
                <h2 className="mb-4 text-xl font-semibold">{c.schedule}</h2>
                <p className="mb-5 text-sm leading-7 text-[var(--text-muted)]">
                  {c.scheduleNote}
                </p>
                <div className="grid gap-4 sm:grid-cols-2">
                  {label(
                    c.interval,
                    <input
                      className={field}
                      type="number"
                      value={interval}
                      min={60}
                      max={43200}
                      onChange={(e) =>
                        setIntervalMinutes(Number(e.target.value))
                      }
                    />,
                  )}
                  {label(
                    c.budget,
                    <input
                      className={field}
                      type="number"
                      min="0.01"
                      max="210000000"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                    />,
                  )}
                </div>
                <p className="my-4 text-sm">
                  {c.progress}: {automation.spent_acp} ACP ·{" "}
                  {automation.enabled ? c.enabled : c.paused}
                </p>
                <button
                  className={button}
                  disabled={busy || !budget || !automation.published_version}
                  onClick={() =>
                    action(() =>
                      request(
                        `/automations/${automationId}/schedule`,
                        {
                          enabled: !automation.enabled,
                          interval_minutes: interval,
                          monthly_budget_acp: budget,
                        },
                        "PUT",
                      ),
                    )
                  }
                >
                  {automation.enabled ? c.pause : c.enabled}
                </button>
              </section>
            )}
            {automation && isOwner && (
              <section className={panel}>
                <h2 className="mb-5 text-xl font-semibold">{c.run}</h2>
                <p className="mb-4 text-sm">
                  {c.estimated}: {estimate ?? "—"} ACP ·{" "}
                  {batchRows.length || 1} {c.rows}
                </p>
                <div className="space-y-4">
                  {label(
                    c.maxCost,
                    <input
                      className={field}
                      type="number"
                      value={maxCost}
                      min="0.01"
                      max="210000000"
                      onChange={(e) => {
                        setMaxCost(e.target.value);
                        setSpendConsent(false);
                      }}
                    />,
                  )}
                  {label(
                    c.batch,
                    <input
                      className={field}
                      type="file"
                      accept=".csv"
                      onChange={(e) =>
                        void action(async () => {
                          const f = e.target.files?.[0];
                          if (f) setBatchRows(parseWorkflowCsv(await f.text()));
                          setSpendConsent(false);
                        })
                      }
                    />,
                  )}
                  {batchRows.length > 0 && (
                    <button className={button} onClick={() => setBatchRows([])}>
                      {c.remove} CSV ({batchRows.length})
                    </button>
                  )}
                  <label className="flex items-start gap-3 text-sm leading-6">
                    <input
                      type="checkbox"
                      checked={spendConsent}
                      onChange={(e) => setSpendConsent(e.target.checked)}
                    />
                    {c.confirmSpend}
                  </label>
                  <div className="flex flex-wrap gap-3">
                    <button
                      className={button}
                      disabled={
                        busy ||
                        !spendConsent ||
                        !maxCost ||
                        !automation.published_version
                      }
                      onClick={() =>
                        action(() =>
                          queue(batchRows.length ? "batch" : "manual"),
                        )
                      }
                    >
                      {batchRows.length ? c.batch : c.run}
                    </button>
                    <button
                      className={button}
                      disabled={busy || !spendConsent || !maxCost}
                      onClick={() => action(() => queue("test"))}
                    >
                      {c.test}
                    </button>
                    <a
                      className={button}
                      href="/workflow-integrations/ancap-workflow-example.py"
                      download
                    >
                      {c.downloadSdk}
                    </a>
                    <a
                      className={button}
                      href="/workflow-integrations/ancap-workflow-n8n.json"
                      download
                    >
                      {c.downloadN8n}
                    </a>
                  </div>
                </div>
              </section>
            )}
          </div>
        )}
        {tab === "runs" && (
          <section className="space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-2xl font-semibold">{c.runs}</h2>
              <button
                className={button}
                disabled={busy || !isAuthenticated}
                onClick={() => action(load)}
              >
                {c.refresh}
              </button>
            </div>
            {data.runs.map((run) => (
              <article key={run.id} className={panel}>
                <header className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold">
                      {c.progress}:{" "}
                      {c[run.state as keyof typeof c] || run.state}
                    </p>
                    <p className="mt-2 break-all text-xs text-[var(--text-muted)]">
                      {run.id} · {run.kind} · {run.cost_acp} ACP
                    </p>
                  </div>
                  <button
                    className={button}
                    onClick={() =>
                      downloadWorkflowJson(
                        `ancap-operation-${run.id}.json`,
                        run,
                      )
                    }
                  >
                    {c.export}
                  </button>
                </header>
                {run.progress.error && (
                  <p role="alert" className="mt-4 text-sm">
                    {run.progress.error}
                  </p>
                )}
                {run.progress.output != null && (
                  <p className="mt-5 whitespace-pre-wrap break-words text-sm">
                    {resultSummary(run.progress.output)}
                  </p>
                )}
                {run.progress.quality != null && (
                  <details className="mt-4">
                    <summary>{c.quality}</summary>
                    <pre className="mt-3 whitespace-pre-wrap break-all text-xs">
                      {JSON.stringify(run.progress.quality, null, 2)}
                    </pre>
                  </details>
                )}
                {run.progress.items?.map((item, i) => (
                  <section
                    key={item.run_id}
                    className="mt-5 border-t border-[var(--border)] pt-4"
                  >
                    <h3 className="font-semibold">
                      {c.output} {i + 1}
                    </h3>
                    <p className="mt-3 whitespace-pre-wrap break-words text-sm">
                      {resultSummary(item.output)}
                    </p>
                    <details className="mt-3">
                      <summary className="cursor-pointer text-sm">
                        {c.quality} / {c.output}
                      </summary>
                      <pre className="mt-3 whitespace-pre-wrap break-all text-xs">
                        {JSON.stringify(
                          { output: item.output, quality: item.quality },
                          null,
                          2,
                        )}
                      </pre>
                    </details>
                  </section>
                ))}
                {run.state === "queued" && (
                  <button
                    className={`${button} mt-4`}
                    disabled={busy}
                    onClick={() =>
                      action(() => request(`/runs/${run.id}/cancel`, {}))
                    }
                  >
                    {c.cancel}
                  </button>
                )}
                {run.state === "awaiting_review" && (
                  <div className="mt-5 space-y-4">
                    {label(
                      c.note,
                      <textarea
                        className={field}
                        value={reviewNote}
                        onChange={(e) => setReviewNote(e.target.value)}
                        rows={2}
                      />,
                    )}
                    {label(
                      c.edited,
                      <textarea
                        className={field}
                        value={edited}
                        onChange={(e) => setEdited(e.target.value)}
                        rows={3}
                      />,
                    )}
                    <div className="flex flex-wrap gap-3">
                      {["approve", "reject"].map((decision) => (
                        <button
                          className={button}
                          key={decision}
                          disabled={busy}
                          onClick={() =>
                            action(async () => {
                              await request(`/runs/${run.id}/review`, {
                                decision,
                                note: reviewNote,
                                edited_output: edited
                                  ? JSON.parse(edited)
                                  : null,
                              });
                              setEdited("");
                              setReviewNote("");
                            })
                          }
                        >
                          {decision === "approve" ? c.approve : c.reject}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {run.progress.deliveries?.map((d) => (
                  <div key={d.connection_id} className="mt-4 text-sm">
                    <p>
                      {c.delivery}:{" "}
                      {d.state === "delivered"
                        ? c.delivered
                        : c.deliveryUnknown}
                    </p>
                    {d.state !== "delivered" && run.state === "completed" && (
                      <button
                        className={`${button} mt-2`}
                        disabled={busy}
                        onClick={() =>
                          action(() =>
                            request(`/runs/${run.id}/retry-delivery`, {
                              connection_id: d.connection_id,
                              confirm_retry: true,
                            }),
                          )
                        }
                      >
                        {c.retryDelivery}
                      </button>
                    )}
                  </div>
                ))}
              </article>
            ))}
          </section>
        )}
        {tab === "economics" && data.is_operator && (
          <section className={panel}>
            <h2 className="text-2xl font-semibold">{c.economics}</h2>
            <p className="my-5 text-sm leading-7 text-[var(--text-muted)]">
              {c.economicsNote}
            </p>
            {economics && (
              <dl className="grid gap-5 sm:grid-cols-3">
                {[
                  [c.paidRuns, economics.paid_operations],
                  [c.paidUsers, economics.paid_users],
                  [c.repeatUsers, economics.repeat_users],
                  [c.capturedCredits, economics.captured_platform_credits_acp],
                  [c.trial, economics.trial_operations],
                  [c.test, economics.test_operations],
                ].map(([name, value], i) => (
                  <div key={i} className="border-t border-[var(--border)] pt-4">
                    <dt className="text-sm text-[var(--text-muted)]">
                      {String(name)}
                    </dt>
                    <dd className="mt-2 break-all text-xl font-semibold">
                      {String(value)}
                    </dd>
                  </div>
                ))}
              </dl>
            )}
          </section>
        )}
      </main>
    </div>
  );
}
