export type SollvorgabeRow = {
  feldname: string;
  min: string;
  max: string;
};

export function rowsFromSollvorgaben(record: Record<string, unknown>): SollvorgabeRow[] {
  return Object.entries(record).map(([feldname, value]) => {
    const obj = typeof value === "object" && value !== null ? (value as Record<string, unknown>) : {};
    return {
      feldname,
      min: obj.min !== undefined && obj.min !== null ? String(obj.min) : "",
      max: obj.max !== undefined && obj.max !== null ? String(obj.max) : "",
    };
  });
}

export function parseOptionalNumber(raw: string): number | undefined {
  const trimmed = raw.trim();
  if (!trimmed) return undefined;
  const parsed = Number(trimmed);
  if (!Number.isFinite(parsed)) return undefined;
  return parsed;
}

export function sollvorgabenFromRows(rows: SollvorgabeRow[]): Record<string, { min?: number; max?: number }> {
  const result: Record<string, { min?: number; max?: number }> = {};
  for (const row of rows) {
    const feldname = row.feldname.trim();
    if (!feldname) continue;
    const min = parseOptionalNumber(row.min);
    const max = parseOptionalNumber(row.max);
    const entry: { min?: number; max?: number } = {};
    if (min !== undefined) entry.min = min;
    if (max !== undefined) entry.max = max;
    result[feldname] = entry;
  }
  return result;
}

export function findDuplicateFeldnamen(rows: SollvorgabeRow[]): string[] {
  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const row of rows) {
    const name = row.feldname.trim();
    if (!name) continue;
    if (seen.has(name)) duplicates.add(name);
    seen.add(name);
  }
  return [...duplicates];
}

export function moveSchrittIds(ids: string[], index: number, direction: -1 | 1): string[] {
  const target = index + direction;
  if (target < 0 || target >= ids.length) return ids;
  const next = [...ids];
  const current = next[index];
  const swap = next[target];
  if (current === undefined || swap === undefined) return ids;
  next[index] = swap;
  next[target] = current;
  return next;
}

export function suggestSchrittId(): string {
  const suffix =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID().slice(0, 8)
      : String(Date.now()).slice(-8);
  return `schritt-${suffix}`;
}
