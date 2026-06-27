import { apiFetch } from "@/adapters/api/client";
import { healthResponseSchema, type HealthResponse } from "@/adapters/api/schemas/health";

export async function fetchHealth(): Promise<HealthResponse> {
  const data = await apiFetch<unknown>("/health");
  return healthResponseSchema.parse(data);
}
