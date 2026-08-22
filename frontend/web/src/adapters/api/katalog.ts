import { apiDelete, apiGet, apiPost, apiPut } from "@/adapters/api/client";
import {
  automatisierungZuweisenRequestSchema,
  automatisierungZuweisenResponseSchema,
  entwurfAnlegenRequestSchema,
  entwurfDetailResponseSchema,
  entwurfResponseSchema,
  prozedurSchrittEntwurfResponseSchema,
  reihenfolgeRequestSchema,
  schrittAktualisierenRequestSchema,
  schrittAnlegenRequestSchema,
  versionResponseSchema,
  type AutomatisierungZuweisenRequest,
  type AutomatisierungZuweisenResponse,
  type EntwurfAnlegenRequest,
  type EntwurfDetailResponse,
  type EntwurfResponse,
  type ReihenfolgeRequest,
  type SchrittAktualisierenRequest,
  type SchrittAnlegenRequest,
  type VersionResponse,
} from "@/adapters/api/schemas/katalog";

export async function createEntwurf(body: EntwurfAnlegenRequest): Promise<EntwurfResponse> {
  const payload = entwurfAnlegenRequestSchema.parse(body);
  const data = await apiPost<unknown>("/katalog/entwuerfe", payload);
  return entwurfResponseSchema.parse(data);
}

export async function getEntwurf(produktdefinitionId: string): Promise<EntwurfDetailResponse> {
  const data = await apiGet<unknown>(`/katalog/entwuerfe/${produktdefinitionId}`);
  return entwurfDetailResponseSchema.parse(data);
}

export async function createSchritt(
  produktdefinitionId: string,
  body: SchrittAnlegenRequest,
) {
  const payload = schrittAnlegenRequestSchema.parse(body);
  const data = await apiPost<unknown>(
    `/katalog/entwuerfe/${produktdefinitionId}/schritte`,
    payload,
  );
  return prozedurSchrittEntwurfResponseSchema.parse(data);
}

export async function updateSchritt(
  produktdefinitionId: string,
  schrittId: string,
  body: SchrittAktualisierenRequest,
) {
  const payload = schrittAktualisierenRequestSchema.parse(body);
  const data = await apiPut<unknown>(
    `/katalog/entwuerfe/${produktdefinitionId}/schritte/${schrittId}`,
    payload,
  );
  return prozedurSchrittEntwurfResponseSchema.parse(data);
}

export async function deleteSchritt(produktdefinitionId: string, schrittId: string): Promise<void> {
  await apiDelete(`/katalog/entwuerfe/${produktdefinitionId}/schritte/${schrittId}`);
}

export async function reorderSchritte(
  produktdefinitionId: string,
  body: ReihenfolgeRequest,
): Promise<EntwurfDetailResponse> {
  const payload = reihenfolgeRequestSchema.parse(body);
  const data = await apiPut<unknown>(
    `/katalog/entwuerfe/${produktdefinitionId}/schritte/reihenfolge`,
    payload,
  );
  return entwurfDetailResponseSchema.parse(data);
}

export async function assignAutomatisierung(
  produktdefinitionId: string,
  schrittId: string,
  body: AutomatisierungZuweisenRequest,
): Promise<AutomatisierungZuweisenResponse> {
  const payload = automatisierungZuweisenRequestSchema.parse(body);
  const data = await apiPut<unknown>(
    `/katalog/entwuerfe/${produktdefinitionId}/schritte/${schrittId}/automatisierung`,
    payload,
  );
  return automatisierungZuweisenResponseSchema.parse(data);
}

export async function veroeffentlichen(produktdefinitionId: string): Promise<VersionResponse> {
  const data = await apiPost<unknown>(`/katalog/entwuerfe/${produktdefinitionId}/veroeffentlichen`);
  return versionResponseSchema.parse(data);
}

export async function seedDemoKatalog(body: EntwurfAnlegenRequest): Promise<VersionResponse> {
  const entwurf = await createEntwurf(body);
  return veroeffentlichen(entwurf.produktdefinition_id);
}
