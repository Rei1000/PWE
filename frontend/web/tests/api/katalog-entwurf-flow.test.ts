import { afterEach, describe, expect, it, vi } from "vitest";

import {
  assignAutomatisierung,
  createEntwurf,
  createSchritt,
  getEntwurf,
  veroeffentlichen,
} from "@/adapters/api/katalog";

describe("katalog entwurf flow", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("Entwurf anlegen → Schritt → Automatisierung → Publish", async () => {
    const state = {
      produktdefinition_id: "pd-flow",
      produktkodierung: "1234567890",
      schritte: [] as Array<{
        schritt_id: string;
        vorlage_id: string;
        ist_pflicht: boolean;
        reihenfolge: number;
        sollvorgaben: Record<string, unknown>;
        kommando_id: string | null;
        routine_id: string | null;
      }>,
    };

    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo, init?: RequestInit) => {
        const url = String(input);
        const method = init?.method ?? "GET";
        const body = init?.body ? JSON.parse(String(init.body)) : undefined;

        if (url.endsWith("/katalog/entwuerfe") && method === "POST") {
          return new Response(
            JSON.stringify({
              produktdefinition_id: state.produktdefinition_id,
              produktkodierung: body.produktkodierung,
            }),
            { status: 201, headers: { "Content-Type": "application/json" } },
          );
        }

        if (url.includes("/schritte/reihenfolge")) {
          return new Response(
            JSON.stringify({
              produktdefinition_id: state.produktdefinition_id,
              produktkodierung: state.produktkodierung,
              sollbestueckung: [],
              prozedur_schritte: state.schritte,
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }

        if (url.endsWith("/schritte") && method === "POST") {
          const schritt = {
            schritt_id: body.schritt_id,
            vorlage_id: body.vorlage_id,
            ist_pflicht: body.ist_pflicht,
            reihenfolge: state.schritte.length + 1,
            sollvorgaben: body.sollvorgaben,
            kommando_id: null,
            routine_id: null,
          };
          state.schritte.push(schritt);
          return new Response(JSON.stringify(schritt), {
            status: 201,
            headers: { "Content-Type": "application/json" },
          });
        }

        if (url.includes("/automatisierung") && method === "PUT") {
          const schritt = state.schritte[0];
          if (!schritt) throw new Error("missing schritt");
          schritt.kommando_id = body.kommando_id ?? null;
          schritt.routine_id = body.routine_id ?? null;
          return new Response(
            JSON.stringify({
              produktdefinition_id: state.produktdefinition_id,
              schritt_id: schritt.schritt_id,
              kommando_id: schritt.kommando_id,
              routine_id: schritt.routine_id,
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }

        if (url.endsWith("/veroeffentlichen") && method === "POST") {
          return new Response(
            JSON.stringify({
              version_id: "ver-flow",
              produktdefinition_id: state.produktdefinition_id,
              produktkodierung: state.produktkodierung,
            }),
            { status: 201, headers: { "Content-Type": "application/json" } },
          );
        }

        if (url.includes("/katalog/entwuerfe/pd-flow") && method === "GET") {
          return new Response(
            JSON.stringify({
              produktdefinition_id: state.produktdefinition_id,
              produktkodierung: state.produktkodierung,
              sollbestueckung: [],
              prozedur_schritte: state.schritte,
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          );
        }

        return new Response("not found", { status: 404 });
      }),
    );

    const entwurf = await createEntwurf({ produktkodierung: "1234567890" });
    expect(entwurf.produktdefinition_id).toBe("pd-flow");

    await createSchritt(entwurf.produktdefinition_id, {
      schritt_id: "s1",
      vorlage_id: "v1",
      ist_pflicht: true,
      sollvorgaben: { spannung: { min: 220, max: 240 } },
    });

    const loaded = await getEntwurf(entwurf.produktdefinition_id);
    expect(loaded.prozedur_schritte[0]?.sollvorgaben).toEqual({ spannung: { min: 220, max: 240 } });

    await assignAutomatisierung(entwurf.produktdefinition_id, "s1", { kommando_id: "k1" });
    const withAuto = await getEntwurf(entwurf.produktdefinition_id);
    expect(withAuto.prozedur_schritte[0]?.kommando_id).toBe("k1");

    const version = await veroeffentlichen(entwurf.produktdefinition_id);
    expect(version.version_id).toBe("ver-flow");
  });
});
