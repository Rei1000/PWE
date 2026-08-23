/** Identity Qualification API — Profile & Einweisungen (Gate 8.1c1). */

import { apiDelete, apiGet, apiPost, apiPut } from "@/adapters/api/client";
import {
  einweisungSchema,
  profilSchema,
  type Einweisung,
  type EinweisungAnlegenRequest,
  type Profil,
  type ProfilAnlegenRequest,
  type ProfilAktualisierenRequest,
} from "@/adapters/api/schemas/identity";
import { z } from "zod";

const PROFILE = "/identity/profile";
const EINWEISUNGEN = "/identity/einweisungen";

const profilListeSchema = z.array(profilSchema);
const einweisungListeSchema = z.array(einweisungSchema);

export async function listProfile(): Promise<Profil[]> {
  const data = await apiGet<unknown>(PROFILE);
  return profilListeSchema.parse(data);
}

export async function getProfil(profilId: string): Promise<Profil> {
  const data = await apiGet<unknown>(`${PROFILE}/${profilId}`);
  return profilSchema.parse(data);
}

export async function createProfil(body: ProfilAnlegenRequest): Promise<Profil> {
  const data = await apiPost<unknown>(PROFILE, body);
  return profilSchema.parse(data);
}

export async function updateProfil(
  profilId: string,
  body: ProfilAktualisierenRequest,
): Promise<Profil> {
  const data = await apiPut<unknown>(`${PROFILE}/${profilId}`, body);
  return profilSchema.parse(data);
}

export async function aktivierenProfil(profilId: string): Promise<Profil> {
  const data = await apiPost<unknown>(`${PROFILE}/${profilId}/aktivieren`, {});
  return profilSchema.parse(data);
}

export async function deaktivierenProfil(profilId: string): Promise<Profil> {
  const data = await apiPost<unknown>(`${PROFILE}/${profilId}/deaktivieren`, {});
  return profilSchema.parse(data);
}

export async function assignProfilZuBenutzer(
  profilId: string,
  benutzerId: string,
): Promise<void> {
  await apiPut<unknown>(`${PROFILE}/${profilId}/benutzer/${benutzerId}`, {});
}

export async function removeProfilVonBenutzer(
  profilId: string,
  benutzerId: string,
): Promise<void> {
  await apiDelete(`${PROFILE}/${profilId}/benutzer/${benutzerId}`);
}

export async function listEinweisungen(
  benutzerId: string,
  versionId?: string,
): Promise<Einweisung[]> {
  const params = new URLSearchParams({ benutzer_id: benutzerId });
  if (versionId) {
    params.set("version_id", versionId);
  }
  const data = await apiGet<unknown>(`${EINWEISUNGEN}?${params.toString()}`);
  return einweisungListeSchema.parse(data);
}

export async function createEinweisung(body: EinweisungAnlegenRequest): Promise<Einweisung> {
  const data = await apiPost<unknown>(EINWEISUNGEN, body);
  return einweisungSchema.parse(data);
}

export async function widerrufenEinweisung(einweisungId: string): Promise<Einweisung> {
  const data = await apiPost<unknown>(`${EINWEISUNGEN}/${einweisungId}/widerrufen`, {});
  return einweisungSchema.parse(data);
}
