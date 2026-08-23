/** Auth-API — Gate 8.1a (Session-Cookie). */

import { z } from "zod";

import { apiFetch, apiGet, apiPost } from "@/adapters/api/client";

export const meSchema = z.object({
  benutzer_id: z.string(),
  login: z.string(),
  anzeigename: z.string(),
  status: z.string(),
  rollen: z.array(z.string()),
});

export type MeResponse = z.infer<typeof meSchema>;

const loginResponseSchema = meSchema
  .omit({ status: true })
  .extend({ csrf_token: z.string() });

export async function login(loginName: string, passwort: string): Promise<MeResponse> {
  const data = await apiPost<unknown>("/auth/login", {
    login: loginName,
    passwort,
  });
  const parsed = loginResponseSchema.parse(data);
  return {
    benutzer_id: parsed.benutzer_id,
    login: parsed.login,
    anzeigename: parsed.anzeigename,
    status: "aktiv",
    rollen: parsed.rollen,
  };
}

export async function logout(): Promise<void> {
  await apiFetch<void>("/auth/logout", { method: "POST" });
}

export async function fetchMe(): Promise<MeResponse> {
  const data = await apiGet<unknown>("/auth/me");
  return meSchema.parse(data);
}
