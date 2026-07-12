import { z } from "zod";

/** Zod nur für API-Transportvalidierung — keine Domain-Regeln. */

export const healthResponseSchema = z.object({
  status: z.string(),
});

export type HealthResponse = z.infer<typeof healthResponseSchema>;

export const refreshIntervalSchema = z.object({
  intervalSeconds: z.coerce.number().int().min(5).max(120),
});

export type RefreshIntervalForm = z.infer<typeof refreshIntervalSchema>;
