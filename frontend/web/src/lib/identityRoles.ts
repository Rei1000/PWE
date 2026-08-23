import type { MeResponse } from "@/adapters/api/auth";

export const SYSTEM_ROLLE = {
  ADMINISTRATOR: "administrator",
  QM: "qm",
  ABTEILUNGSLEITER: "abteilungsleiter",
  PRUEFER: "pruefer",
} as const;

export type SystemRolle = (typeof SYSTEM_ROLLE)[keyof typeof SYSTEM_ROLLE];

export const ALLE_ROLLEN: SystemRolle[] = [
  SYSTEM_ROLLE.ADMINISTRATOR,
  SYSTEM_ROLLE.QM,
  SYSTEM_ROLLE.ABTEILUNGSLEITER,
  SYSTEM_ROLLE.PRUEFER,
];

export function hatRolle(user: MeResponse | undefined, rolle: SystemRolle): boolean {
  return user?.rollen.includes(rolle) ?? false;
}

export function hatEineRolle(user: MeResponse | undefined, rollen: SystemRolle[]): boolean {
  return rollen.some((r) => hatRolle(user, r));
}

/** Identity Read: Admin, QM, Abteilungsleiter — nicht Prüfer (ADR-0025). */
export function darfIdentityLesen(user: MeResponse | undefined): boolean {
  return hatEineRolle(user, [
    SYSTEM_ROLLE.ADMINISTRATOR,
    SYSTEM_ROLLE.QM,
    SYSTEM_ROLLE.ABTEILUNGSLEITER,
  ]);
}

export function istAdministrator(user: MeResponse | undefined): boolean {
  return hatRolle(user, SYSTEM_ROLLE.ADMINISTRATOR);
}

export function darfProfileSchreiben(user: MeResponse | undefined): boolean {
  return hatEineRolle(user, [SYSTEM_ROLLE.ADMINISTRATOR, SYSTEM_ROLLE.QM]);
}

export function darfEinweisungSchreiben(user: MeResponse | undefined): boolean {
  return hatEineRolle(user, [SYSTEM_ROLLE.ADMINISTRATOR, SYSTEM_ROLLE.ABTEILUNGSLEITER]);
}

export function darfProfilZuordnung(user: MeResponse | undefined): boolean {
  return hatEineRolle(user, [SYSTEM_ROLLE.ADMINISTRATOR, SYSTEM_ROLLE.ABTEILUNGSLEITER]);
}
