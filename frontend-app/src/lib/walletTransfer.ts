/** Native ACP uses eight decimal places. Never use floating point for a send limit. */
const SCALE = 100_000_000n;
export const DEFAULT_ACP_FEE = "0.00000100";
export const isAcpAddress = (value: string) =>
  /^acp1[a-z0-9]{20,100}$/.test(value.trim());

export function acpUnits(
  value: string | null | undefined,
  floor = false,
): bigint | null {
  if (
    typeof value !== "string" ||
    !/^\d{1,18}(\.\d{1,18})?$/.test(value.trim())
  )
    return null;
  const [whole, fraction = ""] = value.trim().split(".");
  if (!floor && /[1-9]/.test(fraction.slice(8))) return null;
  return BigInt(whole) * SCALE + BigInt(fraction.slice(0, 8).padEnd(8, "0"));
}

export function acpFromUnits(value: bigint): string {
  const fraction = (value % SCALE)
    .toString()
    .padStart(8, "0")
    .replace(/0+$/, "");
  return `${value / SCALE}${fraction ? "." + fraction : ""}`;
}

export function transferCheck(
  address: string,
  amount: string,
  fee: string,
  available: string | null,
) {
  const balance = acpUnits(available, true),
    value = acpUnits(amount),
    feeUnits = acpUnits(fee);
  const error = !isAcpAddress(address)
    ? "address"
    : value === null || value <= 0n
      ? "amount"
      : feeUnits === null || feeUnits < acpUnits(DEFAULT_ACP_FEE)!
        ? "fee"
        : balance === null
          ? "unavailable"
          : value + feeUnits > balance
            ? "balance"
            : null;
  return {
    error,
    total:
      value !== null && feeUnits !== null
        ? acpFromUnits(value + feeUnits)
        : null,
  };
}

export function maximumSend(available: string | null, fee: string): string {
  const balance = acpUnits(available, true),
    feeUnits = acpUnits(fee);
  return balance !== null && feeUnits !== null && balance > feeUnits
    ? acpFromUnits(balance - feeUnits)
    : "";
}

export function parseBulkTransfers(text: string, available: string | null) {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  if (!lines.length || lines.length > 20) throw new Error("rows");
  const seen = new Set<string>();
  let total = 0n;
  const rows = lines.map((line) => {
    const parts = line.split(/\s+/);
    if (parts.length !== 2 || seen.has(parts[0])) throw new Error("rows");
    const [address, amount] = parts;
    const check = transferCheck(address, amount, DEFAULT_ACP_FEE, available);
    if (check.error) throw new Error(check.error);
    seen.add(address);
    total += acpUnits(check.total)!;
    return { address, amount };
  });
  const balance = acpUnits(available, true);
  if (balance === null || total > balance) throw new Error("balance");
  return { rows, total: acpFromUnits(total) };
}
