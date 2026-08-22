import { z } from "zod";

export const prozedurSchrittEntwurfSchema = z.object({
  schritt_id: z.string().min(1),
  vorlage_id: z.string().min(1),
  ist_pflicht: z.boolean(),
  reihenfolge: z.number().int(),
  sollvorgaben: z.record(z.unknown()).default({}),
});

export const entwurfAnlegenRequestSchema = z.object({
  produktkodierung: z.string().min(1),
  prozedur_schritte: z.array(prozedurSchrittEntwurfSchema).default([]),
  sollbestueckung: z.array(z.string()).default([]),
});

export const entwurfResponseSchema = z.object({
  produktdefinition_id: z.string(),
  produktkodierung: z.string(),
});

export const prozedurSchrittEntwurfResponseSchema = z.object({
  schritt_id: z.string(),
  vorlage_id: z.string(),
  ist_pflicht: z.boolean(),
  reihenfolge: z.number().int(),
  sollvorgaben: z.record(z.unknown()).default({}),
  kommando_id: z.string().nullable().optional(),
  routine_id: z.string().nullable().optional(),
});

export const entwurfDetailResponseSchema = z.object({
  produktdefinition_id: z.string(),
  produktkodierung: z.string(),
  sollbestueckung: z.array(z.string()).default([]),
  prozedur_schritte: z.array(prozedurSchrittEntwurfResponseSchema).default([]),
});

export const schrittAnlegenRequestSchema = z.object({
  schritt_id: z.string().min(1),
  vorlage_id: z.string().min(1),
  ist_pflicht: z.boolean(),
  sollvorgaben: z.record(z.unknown()).default({}),
});

export const schrittAktualisierenRequestSchema = z.object({
  vorlage_id: z.string().min(1),
  ist_pflicht: z.boolean(),
  sollvorgaben: z.record(z.unknown()).default({}),
});

export const reihenfolgeRequestSchema = z.object({
  schritt_ids: z.array(z.string().min(1)).min(1),
});

export const automatisierungZuweisenRequestSchema = z.object({
  kommando_id: z.string().nullable().optional(),
  routine_id: z.string().nullable().optional(),
});

export const automatisierungZuweisenResponseSchema = z.object({
  produktdefinition_id: z.string(),
  schritt_id: z.string(),
  kommando_id: z.string().nullable(),
  routine_id: z.string().nullable(),
});

export const versionResponseSchema = z.object({
  version_id: z.string(),
  produktdefinition_id: z.string(),
  produktkodierung: z.string(),
});

export type EntwurfAnlegenRequest = z.infer<typeof entwurfAnlegenRequestSchema>;
export type EntwurfResponse = z.infer<typeof entwurfResponseSchema>;
export type EntwurfDetailResponse = z.infer<typeof entwurfDetailResponseSchema>;
export type ProzedurSchrittEntwurfResponse = z.infer<typeof prozedurSchrittEntwurfResponseSchema>;
export type SchrittAnlegenRequest = z.infer<typeof schrittAnlegenRequestSchema>;
export type SchrittAktualisierenRequest = z.infer<typeof schrittAktualisierenRequestSchema>;
export type ReihenfolgeRequest = z.infer<typeof reihenfolgeRequestSchema>;
export type AutomatisierungZuweisenRequest = z.infer<typeof automatisierungZuweisenRequestSchema>;
export type AutomatisierungZuweisenResponse = z.infer<typeof automatisierungZuweisenResponseSchema>;
export type VersionResponse = z.infer<typeof versionResponseSchema>;

/** Demo-Katalog für Happy Path — Konfigurationsdaten, keine Fachlogik. */
export const DEMO_KATALOG_ENTWURF: EntwurfAnlegenRequest = {
  produktkodierung: "1234567890",
  prozedur_schritte: [
    {
      schritt_id: "schritt-a",
      vorlage_id: "vorlage-a",
      ist_pflicht: true,
      reihenfolge: 1,
      sollvorgaben: { spannung: { min: 220, max: 240 } },
    },
  ],
  sollbestueckung: ["mainboard"],
};
