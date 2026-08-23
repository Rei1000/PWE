import { apiFetchBlob, apiGet, apiPost, apiPostMultipart } from "@/adapters/api/client";
import {
  abschlussResponseSchema,
  automatisierungAusfuehrenResponseSchema,
  fotoNachweisResponseSchema,
  prueflaufDetailSchema,
  prueflaufResponseSchema,
  type AbschlussResponse,
  type AutomatisierungAusfuehrenResponse,
  type FotoNachweisResponse,
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

/** Gate 8.3b — Multipart-Foto-Nachweis (ADR-0022). */
export async function erfasseFotoNachweis(
  prueflaufId: string,
  schrittId: string,
  datei: File,
): Promise<FotoNachweisResponse> {
  const formData = new FormData();
  formData.append("datei", datei);
  const data = await apiPostMultipart<unknown>(
    `/prueflaeufe/${prueflaufId}/schritte/${schrittId}/nachweise/foto`,
    formData,
  );
  return fotoNachweisResponseSchema.parse(data);
}

/** Gate 8.3b — kontextgebundener Foto-Download. */
export async function fetchNachweisDatei(prueflaufId: string, nachweisId: string): Promise<Blob> {
  return apiFetchBlob(
    `/prueflaeufe/${prueflaufId}/nachweise/${nachweisId}/datei`,
    "image/jpeg, image/png, */*",
  );
}

export async function beurteileSchritt(prueflaufId: string, schrittId: string): Promise<void> {
  await apiPost(`/prueflaeufe/${prueflaufId}/schritte/${schrittId}/beurteilung`);
}

/** ADR-0016 — schrittzentrierte Automatisierung. Kein Legacy-Endpunkt. */
export async function automatisierungAusfuehren(
  prueflaufId: string,
  schrittId: string,
): Promise<AutomatisierungAusfuehrenResponse> {
  const data = await apiPost<unknown>(
    `/prueflaeufe/${prueflaufId}/schritte/${schrittId}/automatisierung/ausfuehren`,
    {},
  );
  return automatisierungAusfuehrenResponseSchema.parse(data);
}

export async function schliessePrueflaufAb(prueflaufId: string): Promise<AbschlussResponse> {
  const data = await apiPost<unknown>(`/prueflaeufe/${prueflaufId}/abschluss`);
  return abschlussResponseSchema.parse(data);
}

export async function fetchProtokollPdf(prueflaufId: string): Promise<Blob> {
  return apiFetchBlob(`/prueflaeufe/${prueflaufId}/protokoll/pdf`);
}
