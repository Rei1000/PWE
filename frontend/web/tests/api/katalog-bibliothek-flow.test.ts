import { afterEach, describe, expect, it, vi } from "vitest";

import {
  createKommando,
  createRoutine,
  createVorlage,
  listKommandos,
  listRoutinen,
  listVorlagen,
} from "@/adapters/api/bibliothek";

describe("katalog bibliothek flow", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("Kommando → Routine → Vorlage über HTTP-Adapter", async () => {
    const store = {
      kommandos: [] as Array<{ kommando_id: string; bezeichnung: string; kommandocode: string }>,
      routinen: [] as Array<{
        routine_id: string;
        bezeichnung: string;
        aktionen: Array<{ position: number; kommando_id: string }>;
      }>,
      vorlagen: [] as Array<{ vorlage_id: string; bezeichnung: string; beschreibung?: string | null }>,
    };

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        const body = init?.body ? JSON.parse(String(init.body)) : undefined;

        if (url.endsWith("/katalog/bibliothek/kommandos") && method === "POST") {
          const item = { kommando_id: "k1", bezeichnung: body.bezeichnung, kommandocode: body.kommandocode };
          store.kommandos.push(item);
          return new Response(JSON.stringify({ kommando_id: item.kommando_id, bezeichnung: item.bezeichnung }), {
            status: 201,
            headers: { "Content-Type": "application/json" },
          });
        }
        if (url.endsWith("/katalog/bibliothek/kommandos") && method === "GET") {
          return new Response(
            JSON.stringify({
              kommandos: store.kommandos.map(({ kommando_id, bezeichnung }) => ({ kommando_id, bezeichnung })),
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }
        if (url.endsWith("/katalog/bibliothek/routinen") && method === "POST") {
          const item = {
            routine_id: "r1",
            bezeichnung: body.bezeichnung,
            aktionen: body.kommando_ids.map((id: string, index: number) => ({
              position: index + 1,
              kommando_id: id,
            })),
          };
          store.routinen.push(item);
          return new Response(JSON.stringify(item), {
            status: 201,
            headers: { "Content-Type": "application/json" },
          });
        }
        if (url.endsWith("/katalog/bibliothek/routinen") && method === "GET") {
          return new Response(
            JSON.stringify({
              routinen: store.routinen.map((r) => ({
                routine_id: r.routine_id,
                bezeichnung: r.bezeichnung,
                anzahl_aktionen: r.aktionen.length,
              })),
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }
        if (url.endsWith("/katalog/bibliothek/vorlagen") && method === "POST") {
          const item = { vorlage_id: "v1", bezeichnung: body.bezeichnung };
          store.vorlagen.push({ ...item, beschreibung: body.beschreibung ?? null });
          return new Response(JSON.stringify(item), {
            status: 201,
            headers: { "Content-Type": "application/json" },
          });
        }
        if (url.endsWith("/katalog/bibliothek/vorlagen") && method === "GET") {
          return new Response(
            JSON.stringify({
              vorlagen: store.vorlagen.map(({ vorlage_id, bezeichnung }) => ({ vorlage_id, bezeichnung })),
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }

        return new Response("not found", { status: 404 });
      }),
    );

    await createKommando({ bezeichnung: "Messgerät", kommandocode: "*IDN?" });
    const kommandos = await listKommandos();
    expect(kommandos).toHaveLength(1);

    const routine = await createRoutine({ bezeichnung: "Standard", kommando_ids: ["k1"] });
    expect(routine.aktionen).toHaveLength(1);

    const routinen = await listRoutinen();
    expect(routinen[0]?.anzahl_aktionen).toBe(1);

    await createVorlage({ bezeichnung: "Spannung prüfen", beschreibung: "Laborschritt" });
    const vorlagen = await listVorlagen();
    expect(vorlagen).toHaveLength(1);
  });
});
