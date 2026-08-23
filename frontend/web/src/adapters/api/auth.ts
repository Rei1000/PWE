/** Auth-API — Gate 8.1a (Session-Cookie). */

import { z } from "zod";

import { apiFetch, apiGet, apiPost } from "@/adapters/api/client";

export const meSchema = z.object({
  benutzer_id: z.string(),
  login: z.string(),
  anzeigename: z.string(),
  status: z.string(),
  rollen: z.array(z.string()),
  passwortwechsel_erforderlich: z.boolean().default(false),
});

export type MeResponse = z.infer<typeof meSchema>;

export async function login(loginName: string, passwort: string): Promise<void> {
  await apiPost<unknown>("/auth/login", {
    login: loginName,
    passwort,
  });
}

export async function logout(): Promise<void> {
  await apiFetch<void>("/auth/logout", { method: "POST" });
}

export async function fetchMe(): Promise<MeResponse> {
  const data = await apiGet<unknown>("/auth/me");
  return meSchema.parse(data);
}

export async function changePassword(
  altesPasswort: string,
  neuesPasswort: string,
): Promise<void> {
  await apiPost<unknown>("/auth/passwort", {
    altes_passwort: altesPasswort,
    neues_passwort: neuesPasswort,
  });
}
