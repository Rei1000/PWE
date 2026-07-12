import { z } from "zod";

/** UI-Formular — rein Transport/UX, keine Domain-Regeln. */

export const refreshIntervalSchema = z.object({
  intervalSeconds: z.coerce.number().int().min(5).max(120),
});

export type RefreshIntervalForm = z.infer<typeof refreshIntervalSchema>;

export const startPrueflaufFormSchema = z.object({
  produktkodierung: z.string().min(1, "Produktkodierung erforderlich"),
  pruefobjekt_kennung: z.string().min(1, "Prüfobjekt-Kennung erforderlich"),
  pruefer_id: z.string().min(1, "Prüfer-ID erforderlich"),
});

export type StartPrueflaufForm = z.infer<typeof startPrueflaufFormSchema>;

export const komponenteFormSchema = z.object({
  komponenten_typ: z.string().min(1),
  seriennummer: z.string().min(1),
});

export type KomponenteForm = z.infer<typeof komponenteFormSchema>;

export const nachweisFormSchema = z.object({
  messwert: z.coerce.number({ invalid_type_error: "Zahl erforderlich" }),
});

export type NachweisForm = z.infer<typeof nachweisFormSchema>;
