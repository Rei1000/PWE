const STORAGE_PREFIX = "pwe-benutzer-profile:";

export function loadBenutzerProfileIds(benutzerId: string): string[] {
  try {
    const raw = sessionStorage.getItem(`${STORAGE_PREFIX}${benutzerId}`);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((id) => typeof id === "string") : [];
  } catch {
    return [];
  }
}

export function saveBenutzerProfileIds(benutzerId: string, profilIds: string[]): void {
  sessionStorage.setItem(`${STORAGE_PREFIX}${benutzerId}`, JSON.stringify(profilIds));
}
