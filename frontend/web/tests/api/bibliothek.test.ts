import { afterEach, describe, expect, it, vi } from "vitest";
import { ZodError } from "zod";

import { ApiError } from "@/adapters/api/client";
import {
  createKommando,
  createRoutine,
  createVorlage,
  deleteKommando,
  deleteVorlage,
  listKommandos,
  listRoutinen,
  listVorlagen,
  updateKommando,
} from "@/adapters/api/bibliothek";
import {
  kommandoDetailSchema,
  routineDetailSchema,
} from "@/adapters/api/schemas/bibliothek";

describe("bibliothek adapter", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("listKommandos parst Liste", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            kommandos: [{ kommando_id: "k1", bezeichnung: "Messgerät" }],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const items = await listKommandos();
    expect(items).toHaveLength(1);
    expect(items[0]?.kommando_id).toBe("k1");
  });

  it("createKommando sendet POST", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ kommando_id: "k2", bezeichnung: "Neu" }), {
        status: 201,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await createKommando({ bezeichnung: "Neu", kommandocode: "*IDN?" });
    expect(result.kommando_id).toBe("k2");
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/katalog/bibliothek/kommandos");
    expect(init.method).toBe("POST");
  });

  it("updateKommando parst Detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({ kommando_id: "k1", bezeichnung: "A", kommandocode: "C" }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const detail = await updateKommando("k1", { bezeichnung: "A", kommandocode: "C" });
    expect(kommandoDetailSchema.parse(detail).kommandocode).toBe("C");
  });

  it("deleteKommando wirft ApiError bei 409", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "In Verwendung", code: "kommando_in_verwendung" }), {
          status: 409,
        }),
      ),
    );

    await expect(deleteKommando("k1")).rejects.toBeInstanceOf(ApiError);
  });

  it("listRoutinen parst Liste", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            routinen: [{ routine_id: "r1", bezeichnung: "R1", anzahl_aktionen: 2 }],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const items = await listRoutinen();
    expect(items[0]?.anzahl_aktionen).toBe(2);
  });

  it("createRoutine parst Detail mit Aktionen", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            routine_id: "r1",
            bezeichnung: "R",
            aktionen: [{ position: 1, kommando_id: "k1" }],
          }),
          { status: 201, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const routine = await createRoutine({ bezeichnung: "R", kommando_ids: ["k1"] });
    expect(routineDetailSchema.parse(routine).aktionen).toHaveLength(1);
  });

  it("listVorlagen parst Liste", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({ vorlagen: [{ vorlage_id: "v1", bezeichnung: "V1" }] }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const items = await listVorlagen();
    expect(items[0]?.vorlage_id).toBe("v1");
  });

  it("createVorlage sendet POST", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ vorlage_id: "v2", bezeichnung: "Neu" }), {
          status: 201,
          headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const result = await createVorlage({ bezeichnung: "Neu", beschreibung: "Text" });
    expect(result.vorlage_id).toBe("v2");
    expect(result.bezeichnung).toBe("Neu");
  });

  it("deleteVorlage wirft ApiError bei 409", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "In Verwendung", code: "vorlage_in_verwendung" }), {
          status: 409,
        }),
      ),
    );

    await expect(deleteVorlage("v1")).rejects.toMatchObject({ code: "vorlage_in_verwendung" });
  });

  it("lehnt ungültige Antworten per Zod ab", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ kommandos: [{ fehlt: true }] }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(listKommandos()).rejects.toBeInstanceOf(ZodError);
  });
});
