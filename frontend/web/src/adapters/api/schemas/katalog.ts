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
  prozedur_schritte: z.array(prozedurSchrittEntwurfSchema).min(1),
  sollbestueckung: z.array(z.string()).default([]),
});

export const entwurfResponseSchema = z.object({
  produktdefinition_id: z.string(),
  produktkodierung: z.string(),
});

export const versionResponseSchema = z.object({
  version_id: z.string(),
  produktdefinition_id: z.string(),
  produktkodierung: z.string(),
});

export type EntwurfAnlegenRequest = z.infer<typeof entwurfAnlegenRequestSchema>;
export type EntwurfResponse = z.infer<typeof entwurfResponseSchema>;
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
