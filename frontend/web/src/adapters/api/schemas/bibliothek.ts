import { z } from "zod";

export const kommandoListenEintragSchema = z.object({
  kommando_id: z.string(),
  bezeichnung: z.string(),
});

export const kommandoListeResponseSchema = z.object({
  kommandos: z.array(kommandoListenEintragSchema),
});

export const kommandoDetailSchema = z.object({
  kommando_id: z.string(),
  bezeichnung: z.string(),
  kommandocode: z.string(),
});

export const kommandoCreateRequestSchema = z.object({
  bezeichnung: z.string().min(1),
  kommandocode: z.string().min(1),
});

export const kommandoUpdateRequestSchema = kommandoCreateRequestSchema;

export const kommandoCreateResponseSchema = z.object({
  kommando_id: z.string(),
  bezeichnung: z.string(),
});

export const routineAktionSchema = z.object({
  position: z.number().int(),
  kommando_id: z.string(),
});

export const routineListenEintragSchema = z.object({
  routine_id: z.string(),
  bezeichnung: z.string(),
  anzahl_aktionen: z.number().int(),
});

export const routineListeResponseSchema = z.object({
  routinen: z.array(routineListenEintragSchema),
});

export const routineDetailSchema = z.object({
  routine_id: z.string(),
  bezeichnung: z.string(),
  aktionen: z.array(routineAktionSchema),
});

export const routineCreateRequestSchema = z.object({
  bezeichnung: z.string().min(1),
  kommando_ids: z.array(z.string().min(1)),
});

export const routineUpdateRequestSchema = routineCreateRequestSchema;

export const routineCreateResponseSchema = routineDetailSchema;

export const vorlageListenEintragSchema = z.object({
  vorlage_id: z.string(),
  bezeichnung: z.string(),
});

export const vorlageListeResponseSchema = z.object({
  vorlagen: z.array(vorlageListenEintragSchema),
});

export const vorlageDetailSchema = z.object({
  vorlage_id: z.string(),
  bezeichnung: z.string(),
  beschreibung: z.string().nullable().optional(),
});

export const vorlageCreateRequestSchema = z.object({
  bezeichnung: z.string().min(1),
  beschreibung: z.string().nullable().optional(),
});

export const vorlageUpdateRequestSchema = vorlageCreateRequestSchema;

export const vorlageCreateResponseSchema = z.object({
  vorlage_id: z.string(),
  bezeichnung: z.string(),
});

export type KommandoListenEintrag = z.infer<typeof kommandoListenEintragSchema>;
export type KommandoDetail = z.infer<typeof kommandoDetailSchema>;
export type KommandoCreateRequest = z.infer<typeof kommandoCreateRequestSchema>;
export type KommandoUpdateRequest = z.infer<typeof kommandoUpdateRequestSchema>;

export type RoutineListenEintrag = z.infer<typeof routineListenEintragSchema>;
export type RoutineDetail = z.infer<typeof routineDetailSchema>;
export type RoutineCreateRequest = z.infer<typeof routineCreateRequestSchema>;
export type RoutineUpdateRequest = z.infer<typeof routineUpdateRequestSchema>;

export type VorlageListenEintrag = z.infer<typeof vorlageListenEintragSchema>;
export type VorlageDetail = z.infer<typeof vorlageDetailSchema>;
export type VorlageCreateRequest = z.infer<typeof vorlageCreateRequestSchema>;
export type VorlageUpdateRequest = z.infer<typeof vorlageUpdateRequestSchema>;
