export type EntwurfRecent = {
  produktdefinition_id: string;
  produktkodierung: string;
  zuletztGeoeffnet: string;
};

const STORAGE_KEY = "pwe.katalog.entwurf-recents";
const MAX_RECENTS = 8;

export function loadEntwurfRecents(): EntwurfRecent[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter(
        (item): item is EntwurfRecent =>
          typeof item === "object" &&
          item !== null &&
          typeof (item as EntwurfRecent).produktdefinition_id === "string" &&
          typeof (item as EntwurfRecent).produktkodierung === "string" &&
          typeof (item as EntwurfRecent).zuletztGeoeffnet === "string",
      )
      .slice(0, MAX_RECENTS);
  } catch {
    return [];
  }
}

export function rememberEntwurfRecent(entry: Pick<EntwurfRecent, "produktdefinition_id" | "produktkodierung">) {
  if (typeof localStorage === "undefined") return;
  const now = new Date().toISOString();
  const next: EntwurfRecent = {
    produktdefinition_id: entry.produktdefinition_id,
    produktkodierung: entry.produktkodierung,
    zuletztGeoeffnet: now,
  };
  const without = loadEntwurfRecents().filter(
    (item) => item.produktdefinition_id !== next.produktdefinition_id,
  );
  const merged = [next, ...without].slice(0, MAX_RECENTS);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
}

export function clearEntwurfRecentsForTests() {
  if (typeof localStorage !== "undefined") {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export { MAX_RECENTS };
