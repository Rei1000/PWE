import { afterEach, describe, expect, it, vi } from "vitest";
import { ZodError } from "zod";

import { ApiError } from "@/adapters/api/client";
import {
  assignAutomatisierung,
  createEntwurf,
  createSchritt,
  deleteSchritt,
  getEntwurf,
  reorderSchritte,
  updateSchritt,
  veroeffentlichen,
} from "@/adapters/api/katalog";
import {
  entwurfAnlegenRequestSchema,
  entwurfDetailResponseSchema,
} from "@/adapters/api/schemas/katalog";

const PD_ID = "pd-1";
const SCHRIITT = {
  schritt_id: "s1",
  vorlage_id: "v1",
  ist_pflicht: true,
  reihenfolge: 1,
  sollvorgaben: { spannung: { min: 220, max: 240 } },
  kommando_id: null,
  routine_id: null,
};

describe("entwurf adapter", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("createEntwurf erlaubt leeren Entwurf", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ produktdefinition_id: PD_ID, produktkodierung: "1234567890" }),
        { status: 201, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await createEntwurf({ produktkodierung: "1234567890" });
    expect(result.produktdefinition_id).toBe(PD_ID);
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(String(init.body))).toEqual({
      produktkodierung: "1234567890",
      prozedur_schritte: [],
      sollbestueckung: [],
    });
  });

  it("entwurfAnlegenRequestSchema default prozedur_schritte []", () => {
    expect(entwurfAnlegenRequestSchema.parse({ produktkodierung: "1234567890" })).toEqual({
      produktkodierung: "1234567890",
      prozedur_schritte: [],
      sollbestueckung: [],
    });
  });

  it("getEntwurf parst Detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            produktdefinition_id: PD_ID,
            produktkodierung: "1234567890",
            sollbestueckung: [],
            prozedur_schritte: [SCHRIITT],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const entwurf = await getEntwurf(PD_ID);
    expect(entwurfDetailResponseSchema.parse(entwurf).prozedur_schritte).toHaveLength(1);
  });

  it("createSchritt sendet POST", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(SCHRIITT), {
        status: 201,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await createSchritt(PD_ID, {
      schritt_id: "s1",
      vorlage_id: "v1",
      ist_pflicht: true,
      sollvorgaben: {},
    });
    expect(result.schritt_id).toBe("s1");
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain(`/katalog/entwuerfe/${PD_ID}/schritte`);
    expect(init.method).toBe("POST");
  });

  it("updateSchritt sendet PUT", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ...SCHRIITT, ist_pflicht: false }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await updateSchritt(PD_ID, "s1", {
      vorlage_id: "v1",
      ist_pflicht: false,
      sollvorgaben: {},
    });
    expect(result.ist_pflicht).toBe(false);
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain("/schritte/s1");
  });

  it("deleteSchritt sendet DELETE", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await deleteSchritt(PD_ID, "s1");
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/schritte/s1");
    expect(init.method).toBe("DELETE");
  });

  it("reorderSchritte sendet vollständige Permutation", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          produktdefinition_id: PD_ID,
          produktkodierung: "1234567890",
          sollbestueckung: [],
          prozedur_schritte: [
            { ...SCHRIITT, schritt_id: "s2", reihenfolge: 1 },
            { ...SCHRIITT, schritt_id: "s1", reihenfolge: 2 },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const entwurf = await reorderSchritte(PD_ID, { schritt_ids: ["s2", "s1"] });
    expect(entwurf.prozedur_schritte.map((s) => s.schritt_id)).toEqual(["s2", "s1"]);
  });

  it("assignAutomatisierung Kommando", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          produktdefinition_id: PD_ID,
          schritt_id: "s1",
          kommando_id: "k1",
          routine_id: null,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await assignAutomatisierung(PD_ID, "s1", { kommando_id: "k1" });
    expect(result.kommando_id).toBe("k1");
  });

  it("assignAutomatisierung entfernen", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          produktdefinition_id: PD_ID,
          schritt_id: "s1",
          kommando_id: null,
          routine_id: null,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await assignAutomatisierung(PD_ID, "s1", {
      kommando_id: null,
      routine_id: null,
    });
    expect(result.kommando_id).toBeNull();
  });

  it("veroeffentlichen parst Version", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            version_id: "ver-1",
            produktdefinition_id: PD_ID,
            produktkodierung: "1234567890",
          }),
          { status: 201, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const version = await veroeffentlichen(PD_ID);
    expect(version.version_id).toBe("ver-1");
  });

  it("wirft ApiError bei 404", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Nicht gefunden", code: "entwurf_nicht_gefunden" }), {
          status: 404,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(getEntwurf("x")).rejects.toBeInstanceOf(ApiError);
  });

  it("wirft ApiError bei 409", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({ detail: "Duplikat", code: "schritt_id_bereits_vorhanden" }),
          { status: 409, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    await expect(
      createSchritt(PD_ID, {
        schritt_id: "s1",
        vorlage_id: "v1",
        ist_pflicht: true,
        sollvorgaben: {},
      }),
    ).rejects.toBeInstanceOf(ApiError);
  });

  it("wirft ZodError bei ungültiger Serverantwort", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ foo: "bar" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(getEntwurf(PD_ID)).rejects.toBeInstanceOf(ZodError);
  });
});
