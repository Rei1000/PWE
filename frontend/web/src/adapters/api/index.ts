export { ApiError, apiFetch, apiFetchBlob, apiGet, apiPost, getApiBaseUrl } from "@/adapters/api/client";
export { fetchHealth } from "@/adapters/api/health";
export { createEntwurf, seedDemoKatalog, veroeffentlichen } from "@/adapters/api/katalog";
export {
  beurteileSchritt,
  erfasseKomponente,
  erfasseNachweis,
  fetchProtokollPdf,
  fetchPrueflauf,
  schliessePrueflaufAb,
  startPrueflauf,
} from "@/adapters/api/prueflaeufe";
export { healthResponseSchema, type HealthResponse } from "@/adapters/api/schemas/health";
export {
  DEMO_KATALOG_ENTWURF,
  type EntwurfAnlegenRequest,
  type EntwurfResponse,
  type VersionResponse,
} from "@/adapters/api/schemas/katalog";
export {
  type AbschlussResponse,
  type PrueflaufDetail,
  type PrueflaufResponse,
  type PrueflaufStartenRequest,
} from "@/adapters/api/schemas/prueflaeufe";
