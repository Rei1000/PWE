import { apiDelete, apiGet, apiPost, apiPut } from "@/adapters/api/client";
import {
  kommandoCreateRequestSchema,
  kommandoCreateResponseSchema,
  kommandoDetailSchema,
  kommandoListeResponseSchema,
  kommandoUpdateRequestSchema,
  routineCreateRequestSchema,
  routineCreateResponseSchema,
  routineDetailSchema,
  routineListeResponseSchema,
  routineUpdateRequestSchema,
  vorlageCreateRequestSchema,
  vorlageCreateResponseSchema,
  vorlageDetailSchema,
  vorlageListeResponseSchema,
  vorlageUpdateRequestSchema,
  type KommandoCreateRequest,
  type KommandoDetail,
  type KommandoUpdateRequest,
  type RoutineCreateRequest,
  type RoutineDetail,
  type RoutineUpdateRequest,
  type VorlageCreateRequest,
  type VorlageDetail,
  type VorlageUpdateRequest,
} from "@/adapters/api/schemas/bibliothek";

const KOMMANDOS = "/katalog/bibliothek/kommandos";
const ROUTINEN = "/katalog/bibliothek/routinen";
const VORLAGEN = "/katalog/bibliothek/vorlagen";

export async function listKommandos() {
  const data = await apiGet<unknown>(KOMMANDOS);
  return kommandoListeResponseSchema.parse(data).kommandos;
}

export async function getKommando(kommandoId: string): Promise<KommandoDetail> {
  const data = await apiGet<unknown>(`${KOMMANDOS}/${kommandoId}`);
  return kommandoDetailSchema.parse(data);
}

export async function createKommando(body: KommandoCreateRequest) {
  const payload = kommandoCreateRequestSchema.parse(body);
  const data = await apiPost<unknown>(KOMMANDOS, payload);
  return kommandoCreateResponseSchema.parse(data);
}

export async function updateKommando(kommandoId: string, body: KommandoUpdateRequest) {
  const payload = kommandoUpdateRequestSchema.parse(body);
  const data = await apiPut<unknown>(`${KOMMANDOS}/${kommandoId}`, payload);
  return kommandoDetailSchema.parse(data);
}

export async function deleteKommando(kommandoId: string): Promise<void> {
  await apiDelete(`${KOMMANDOS}/${kommandoId}`);
}

export async function listRoutinen() {
  const data = await apiGet<unknown>(ROUTINEN);
  return routineListeResponseSchema.parse(data).routinen;
}

export async function getRoutine(routineId: string): Promise<RoutineDetail> {
  const data = await apiGet<unknown>(`${ROUTINEN}/${routineId}`);
  return routineDetailSchema.parse(data);
}

export async function createRoutine(body: RoutineCreateRequest): Promise<RoutineDetail> {
  const payload = routineCreateRequestSchema.parse(body);
  const data = await apiPost<unknown>(ROUTINEN, payload);
  return routineCreateResponseSchema.parse(data);
}

export async function updateRoutine(routineId: string, body: RoutineUpdateRequest): Promise<RoutineDetail> {
  const payload = routineUpdateRequestSchema.parse(body);
  const data = await apiPut<unknown>(`${ROUTINEN}/${routineId}`, payload);
  return routineDetailSchema.parse(data);
}

export async function deleteRoutine(routineId: string): Promise<void> {
  await apiDelete(`${ROUTINEN}/${routineId}`);
}

export async function listVorlagen() {
  const data = await apiGet<unknown>(VORLAGEN);
  return vorlageListeResponseSchema.parse(data).vorlagen;
}

export async function getVorlage(vorlageId: string): Promise<VorlageDetail> {
  const data = await apiGet<unknown>(`${VORLAGEN}/${vorlageId}`);
  return vorlageDetailSchema.parse(data);
}

export async function createVorlage(body: VorlageCreateRequest) {
  const payload = vorlageCreateRequestSchema.parse(body);
  const data = await apiPost<unknown>(VORLAGEN, payload);
  return vorlageCreateResponseSchema.parse(data);
}

export async function updateVorlage(vorlageId: string, body: VorlageUpdateRequest) {
  const payload = vorlageUpdateRequestSchema.parse(body);
  const data = await apiPut<unknown>(`${VORLAGEN}/${vorlageId}`, payload);
  return vorlageDetailSchema.parse(data);
}

export async function deleteVorlage(vorlageId: string): Promise<void> {
  await apiDelete(`${VORLAGEN}/${vorlageId}`);
}
