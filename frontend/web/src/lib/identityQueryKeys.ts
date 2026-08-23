export const identityBenutzerKey = ["identity", "benutzer"] as const;
export const identityBenutzerDetailKey = (id: string) => ["identity", "benutzer", id] as const;
export const identityProfileKey = ["identity", "profile"] as const;
export const identityProfilDetailKey = (id: string) => ["identity", "profile", id] as const;
export const identityEinweisungenKey = (benutzerId: string, versionId?: string) =>
  ["identity", "einweisungen", benutzerId, versionId ?? ""] as const;
export const identityBenutzerProfileKey = (benutzerId: string) =>
  ["identity", "benutzer-profile", benutzerId] as const;
