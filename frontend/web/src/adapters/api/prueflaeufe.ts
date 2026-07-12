import { apiFetchBlob, apiGet, apiPost } from "@/adapters/api/client";
import {
  abschlussResponseSchema,
  prueflaufDetailSchema,
  prueflaufResponseSchema,
  type AbschlussResponse,
  type KomponenteErfassenRequest,
  type NachweisErfassenRequest,
  type PrueflaufDetail,
  type PrueflaufResponse,
  type PrueflaufStartenRequest,
} from "@/adapters/api/schemas/prueflaeufe";

export async function startPrueflauf(body: PrueflaufStartenRequest): Promise<PrueflaufResponse> {
  const data = await apiPost<unknown>("/prueflaeufe", body);
  return prueflaufResponseSchema.parse(data);
}

export async function fetchPrueflauf(prueflaufId: string): Promise<PrueflaufDetail> {
  const data = await apiGet<unknown>(`/prueflaeufe/${prueflaufId}`);
  return prueflaufDetailSchema.parse(data);
}

export async function erfasseKomponente(
  prueflaufId: string,
  body: KomponenteErfassenRequest,
): Promise<void> {
  await apiPost(`/prueflaeufe/${prueflaufId}/komponenten`, body);
}

export async function erfasseNachweis(
  prueflaufId: string,
  schrittId: string,
  body: NachweisErfassenRequest,
): Promise<void> {
  await apiPost(`/prueflaeufe/${prueflaufId}/schritte/${schrittId}/nachweise`, body);
}

export async function beurteileSchritt(prueflaufId: string, schrittId: string): Promise<void> {
  await apiPost(`/prueflaeufe/${prueflaufId}/schritte/${schrittId}/beurteilung`);
}

export async function schliessePrueflaufAb(prueflaufId: string): Promise<AbschlussResponse> {
  const data = await apiPost<unknown>(`/prueflaeufe/${prueflaufId}/abschluss`);
  return abschlussResponseSchema.parse(data);
}

export async function fetchProtokollPdf(prueflaufId: string): Promise<Blob> {
  return apiFetchBlob(`/prueflaeufe/${prueflaufId}/protokoll/pdf`);
}
