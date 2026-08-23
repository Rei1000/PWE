import { z } from "zod";

export const benutzerSchema = z.object({
  benutzer_id: z.string(),
  login: z.string(),
  anzeigename: z.string(),
  status: z.string(),
  rollen: z.array(z.string()),
  passwortwechsel_erforderlich: z.boolean(),
});

export type Benutzer = z.infer<typeof benutzerSchema>;

export const benutzerListeSchema = z.object({
  benutzer: z.array(benutzerSchema),
});

export const benutzerAnlegenSchema = z.object({
  login: z.string().min(1, "Login erforderlich"),
  anzeigename: z.string().min(1, "Anzeigename erforderlich"),
  passwort: z.string().min(1, "Passwort erforderlich"),
  rollen: z.array(z.string()).min(1, "Mindestens eine Rolle"),
});

export type BenutzerAnlegenRequest = z.infer<typeof benutzerAnlegenSchema>;

export const benutzerRollenSchema = z.object({
  rollen: z.array(z.string()).min(1, "Mindestens eine Rolle"),
});

export const passwortResetSchema = z.object({
  neues_passwort: z.string().min(1, "Passwort erforderlich"),
});

export const passwortAendernSchema = z.object({
  altes_passwort: z.string().min(1, "Altes Passwort erforderlich"),
  neues_passwort: z.string().min(1, "Neues Passwort erforderlich"),
});

export type PasswortAendernRequest = z.infer<typeof passwortAendernSchema>;

export const profilSchema = z.object({
  profil_id: z.string(),
  bezeichnung: z.string(),
  beschreibung: z.string().nullable().optional(),
  produktdefinition_ids: z.array(z.string()),
  aktiv: z.boolean(),
});

export type Profil = z.infer<typeof profilSchema>;

export const profilAnlegenSchema = z.object({
  bezeichnung: z.string().min(1, "Bezeichnung erforderlich"),
  beschreibung: z.string().optional(),
  produktdefinition_ids: z.array(z.string()).optional(),
});

export type ProfilAnlegenRequest = z.infer<typeof profilAnlegenSchema>;

export const profilAktualisierenSchema = profilAnlegenSchema;

export type ProfilAktualisierenRequest = z.infer<typeof profilAktualisierenSchema>;

export const einweisungSchema = z.object({
  einweisung_id: z.string(),
  benutzer_id: z.string(),
  version_id: z.string(),
  eingewiesen_durch: z.string(),
  datum: z.string(),
  status: z.string(),
  gueltig_bis: z.string().nullable().optional(),
  bemerkung: z.string().nullable().optional(),
  herkunft_einweisung_id: z.string().nullable().optional(),
  uebernommen_bei_publish: z.boolean().optional(),
});

export type Einweisung = z.infer<typeof einweisungSchema>;

export const einweisungAnlegenSchema = z.object({
  benutzer_id: z.string().min(1),
  version_id: z.string().min(1),
  gueltig_bis: z.string().optional(),
  bemerkung: z.string().optional(),
});

export type EinweisungAnlegenRequest = z.infer<typeof einweisungAnlegenSchema>;
