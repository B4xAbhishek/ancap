export function parseWorkflowCsv(raw: string): Record<string, string>[] {
  if (new TextEncoder().encode(raw).length > 64000)
    throw new Error("CSV exceeds 64 KB");
  const rows: string[][] = [];
  let row: string[] = [],
    field = "",
    quoted = false;
  const text = raw.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') {
        field += '"';
        i++;
      } else if (quoted) quoted = false;
      else if (field === "") quoted = true;
      else throw new Error("Invalid CSV quote");
    } else if (c === "," && !quoted) {
      row.push(field);
      field = "";
    } else if ((c === "\n" || c === "\r") && !quoted) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      if (row.some(Boolean)) rows.push(row);
      row = [];
      field = "";
    } else field += c;
  }
  if (quoted) throw new Error("Unclosed CSV quote");
  row.push(field);
  if (row.some(Boolean)) rows.push(row);
  if (rows.length < 2 || rows.length > 21)
    throw new Error("CSV requires headers and 1–20 rows");
  const headers = rows[0].map((h) => h.trim());
  if (
    headers.length > 30 ||
    headers.some(
      (h) =>
        !/^[a-zA-Z][a-zA-Z0-9_]{0,63}$/.test(h) ||
        ["constructor", "prototype"].includes(h),
    ) ||
    new Set(headers).size !== headers.length
  )
    throw new Error("Use unique input names as CSV headers");
  return rows.slice(1).map((values) => {
    if (values.length !== headers.length || values.some((v) => v.length > 2000))
      throw new Error("Invalid CSV row length");
    return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
  });
}

export function quoteWorkflowPlan(amounts: string[], rows = 1): string | null {
  if (!amounts.length || !Number.isInteger(rows) || rows < 1 || rows > 20)
    return null;
  let total = 0n;
  for (const amount of amounts) {
    if (!/^\d{1,18}(\.\d{1,18})?$/.test(amount)) return null;
    const [whole, fraction = ""] = amount.split(".");
    total += BigInt(whole) * 10n ** 18n + BigInt(fraction.padEnd(18, "0"));
  }
  total *= BigInt(rows);
  const fraction = (total % 10n ** 18n)
    .toString()
    .padStart(18, "0")
    .replace(/0+$/, "");
  return `${total / 10n ** 18n}${fraction ? "." + fraction : ""}`;
}

export function downloadWorkflowJson(name: string, value: unknown) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function resultSummary(value: unknown): string {
  if (!value || typeof value !== "object") return String(value ?? "");
  const item = value as Record<string, unknown>;
  const deliverable = item.deliverable as Record<string, unknown> | undefined;
  return String(
    deliverable?.summary ||
      deliverable?.raw_text ||
      item.summary ||
      item.note ||
      "",
  );
}
