import { z } from "zod";

/** Zod nur für API-Transportvalidierung — keine Domain-Regeln. */

export const healthResponseSchema = z.object({
  status: z.string(),
});

export type HealthResponse = z.infer<typeof healthResponseSchema>;
