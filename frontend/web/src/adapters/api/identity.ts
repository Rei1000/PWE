/** Identity Admin API — Benutzerverwaltung (Gate 8.1c1). */

import { apiGet, apiPost, apiPut } from "@/adapters/api/client";
import {
  benutzerListeSchema,
  benutzerRollenSchema,
  benutzerSchema,
  type Benutzer,
  type BenutzerAnlegenRequest,
  passwortResetSchema,
} from "@/adapters/api/schemas/identity";
import type { z } from "zod";

type BenutzerRollenRequest = z.infer<typeof benutzerRollenSchema>;

const BENUTZER = "/identity/benutzer";

export async function listBenutzer(): Promise<Benutzer[]> {
  const data = await apiGet<unknown>(BENUTZER);
  return benutzerListeSchema.parse(data).benutzer;
}

export async function getBenutzer(benutzerId: string): Promise<Benutzer> {
  const data = await apiGet<unknown>(`${BENUTZER}/${benutzerId}`);
  return benutzerSchema.parse(data);
}

export async function createBenutzer(body: BenutzerAnlegenRequest): Promise<Benutzer> {
  const data = await apiPost<unknown>(BENUTZER, body);
  return benutzerSchema.parse(data);
}

export async function aktivierenBenutzer(benutzerId: string): Promise<Benutzer> {
  const data = await apiPost<unknown>(`${BENUTZER}/${benutzerId}/aktivieren`, {});
  return benutzerSchema.parse(data);
}

export async function sperrenBenutzer(benutzerId: string): Promise<Benutzer> {
  const data = await apiPost<unknown>(`${BENUTZER}/${benutzerId}/sperren`, {});
  return benutzerSchema.parse(data);
}

export async function entsperrenBenutzer(benutzerId: string): Promise<Benutzer> {
  const data = await apiPost<unknown>(`${BENUTZER}/${benutzerId}/entsperren`, {});
  return benutzerSchema.parse(data);
}

export async function archivierenBenutzer(benutzerId: string): Promise<Benutzer> {
  const data = await apiPost<unknown>(`${BENUTZER}/${benutzerId}/archivieren`, {});
  return benutzerSchema.parse(data);
}

export async function wiederherstellenBenutzer(benutzerId: string): Promise<Benutzer> {
  const data = await apiPost<unknown>(`${BENUTZER}/${benutzerId}/wiederherstellen`, {});
  return benutzerSchema.parse(data);
}

export async function setBenutzerRollen(
  benutzerId: string,
  body: BenutzerRollenRequest,
): Promise<Benutzer> {
  const data = await apiPut<unknown>(`${BENUTZER}/${benutzerId}/rollen`, body);
  return benutzerSchema.parse(data);
}

export async function resetBenutzerPasswort(
  benutzerId: string,
  neuesPasswort: string,
): Promise<Benutzer> {
  const body = passwortResetSchema.parse({ neues_passwort: neuesPasswort });
  const data = await apiPost<unknown>(`${BENUTZER}/${benutzerId}/passwort`, body);
  return benutzerSchema.parse(data);
}
