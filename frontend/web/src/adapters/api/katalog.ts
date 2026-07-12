import { apiPost } from "@/adapters/api/client";
import {
  entwurfAnlegenRequestSchema,
  entwurfResponseSchema,
  versionResponseSchema,
  type EntwurfAnlegenRequest,
  type EntwurfResponse,
  type VersionResponse,
} from "@/adapters/api/schemas/katalog";

export async function createEntwurf(body: EntwurfAnlegenRequest): Promise<EntwurfResponse> {
  const payload = entwurfAnlegenRequestSchema.parse(body);
  const data = await apiPost<unknown>("/katalog/entwuerfe", payload);
  return entwurfResponseSchema.parse(data);
}

export async function veroeffentlichen(produktdefinitionId: string): Promise<VersionResponse> {
  const data = await apiPost<unknown>(`/katalog/entwuerfe/${produktdefinitionId}/veroeffentlichen`);
  return versionResponseSchema.parse(data);
}

export async function seedDemoKatalog(body: EntwurfAnlegenRequest): Promise<VersionResponse> {
  const entwurf = await createEntwurf(body);
  return veroeffentlichen(entwurf.produktdefinition_id);
}
