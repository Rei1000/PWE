import { z } from "zod";

export const prueflaufStartenRequestSchema = z.object({
  produktkodierung: z.string().min(1),
  pruefobjekt_kennung: z.string().min(1),
  pruefer_id: z.string().min(1),
});

export const prueflaufResponseSchema = z.object({
  prueflauf_id: z.string(),
  version_id: z.string(),
  produktkodierung: z.string(),
  pruefobjekt_kennung: z.string(),
  pruefer_id: z.string(),
  status: z.string(),
});

export const komponenteErfassenRequestSchema = z.object({
  komponenten_typ: z.string().min(1),
  seriennummer: z.string().min(1),
});

export const nachweisArtSchema = z.enum([
  "messwert",
  "foto",
  "kommentar",
  "manuelle_eingabe",
  "rohantwort",
  "extrahierter_wert",
  "ergaenzung",
  "komponentenerfassung",
]);

export const nachweisErfassenRequestSchema = z.object({
  art: nachweisArtSchema,
  payload: z.record(z.unknown()).default({}),
  ist_automatisch: z.boolean().default(false),
});

export const nachweisResponseSchema = z.object({
  nachweis_id: z.string(),
  art: z.string(),
});

export const abschlussResponseSchema = z.object({
  prueflauf_id: z.string(),
  status: z.string(),
  ist_gueltig: z.boolean(),
  snapshot_id: z.string(),
});

export const nachweisDetailSchema = z.object({
  nachweis_id: z.string(),
  art: z.string(),
  erfasst_am: z.string(),
  payload: z.record(z.unknown()),
  ist_automatisch: z.boolean(),
});

export const beurteilungSchema = z.object({
  ergebnis: z.string(),
  festgelegt_am: z.string(),
  kommentar: z.string().nullable().optional(),
});

export const schrittDurchfuehrungSchema = z.object({
  schritt_id: z.string(),
  vorlage_id: z.string(),
  ist_pflicht: z.boolean(),
  reihenfolge: z.number(),
  sollvorgaben: z.record(z.unknown()),
  nachweise: z.array(nachweisDetailSchema),
  beurteilung: beurteilungSchema.nullable().optional(),
  kann_nachweis_erfassen: z.boolean().default(false),
  kann_beurteilt_werden: z.boolean().default(false),
});

export const prueflaufDetailSchema = z.object({
  prueflauf_id: z.string(),
  version_id: z.string(),
  produktkodierung: z.string(),
  pruefobjekt_kennung: z.string(),
  pruefer_id: z.string(),
  status: z.string(),
  gestartet_am: z.string(),
  abgeschlossen_am: z.string().nullable().optional(),
  schritte: z.array(schrittDurchfuehrungSchema),
  sollbestueckung: z.array(z.string()),
  erfasste_komponenten: z.array(z.string()),
  ist_abgeschlossen: z.boolean().default(false),
  fehlende_komponenten: z.array(z.string()).default([]),
  kann_komponente_erfassen: z.boolean().default(false),
  kann_abgeschlossen_werden: z.boolean().default(false),
});

export type PrueflaufStartenRequest = z.infer<typeof prueflaufStartenRequestSchema>;
export type PrueflaufResponse = z.infer<typeof prueflaufResponseSchema>;
export type PrueflaufDetail = z.infer<typeof prueflaufDetailSchema>;
export type KomponenteErfassenRequest = z.infer<typeof komponenteErfassenRequestSchema>;
export type NachweisErfassenRequest = z.infer<typeof nachweisErfassenRequestSchema>;
export type AbschlussResponse = z.infer<typeof abschlussResponseSchema>;
