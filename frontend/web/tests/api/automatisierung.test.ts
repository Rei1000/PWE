import { afterEach, describe, expect, it, vi } from "vitest";
import { ZodError } from "zod";

import { ApiError } from "@/adapters/api/client";
import { automatisierungAusfuehren } from "@/adapters/api/prueflaeufe";
import {
  automatisierungAusfuehrenResponseSchema,
  prueflaufDetailSchema,
} from "@/adapters/api/schemas/prueflaeufe";

describe("automatisierung schemas", () => {
  it("parst Erfolg bei fehlgeschlagen=false", () => {
    const data = automatisierungAusfuehrenResponseSchema.parse({
      ausfuehrung_id: "a1",
      fehlgeschlagen: false,
      ausgefuehrte_aktionen: 2,
      abgebrochen_bei_aktion_position: null,
      fehlerart: null,
      nachweise: [{ nachweis_id: "n1", art: "rohantwort" }],
    });
    expect(data.fehlgeschlagen).toBe(false);
  });

  it("parst fachlichen Fehlschlag bei fehlgeschlagen=true (kein ApiError)", () => {
    const data = automatisierungAusfuehrenResponseSchema.parse({
      ausfuehrung_id: "a2",
      fehlgeschlagen: true,
      ausgefuehrte_aktionen: 0,
      abgebrochen_bei_aktion_position: 1,
      fehlerart: "keine_geraeteantwort",
      nachweise: [],
    });
    expect(data.fehlgeschlagen).toBe(true);
    expect(data.fehlerart).toBe("keine_geraeteantwort");
  });

  it("lehnt ungültige fehlerart ab", () => {
    expect(() =>
      automatisierungAusfuehrenResponseSchema.parse({
        ausfuehrung_id: "a3",
        fehlgeschlagen: true,
        ausgefuehrte_aktionen: 0,
        abgebrochen_bei_aktion_position: null,
        fehlerart: "timeout",
        nachweise: [],
      }),
    ).toThrow(ZodError);
  });

  it("parst Read-Model-Flags für Automatisierung", () => {
    const detail = prueflaufDetailSchema.parse({
      prueflauf_id: "p1",
      version_id: "v1",
      produktkodierung: "1234567890",
      pruefobjekt_kennung: "GER-1",
      pruefer_id: "pruefer-1",
      status: "in_bearbeitung",
      gestartet_am: "2026-01-01T12:00:00Z",
      schritte: [
        {
          schritt_id: "schritt-a",
          vorlage_id: "vorlage-a",
          ist_pflicht: true,
          reihenfolge: 1,
          sollvorgaben: {},
          nachweise: [],
          hat_automatisierung: true,
          kann_automatisierung_ausfuehren: true,
          automatisierung_bezeichnung: "Spannung",
        },
      ],
      sollbestueckung: [],
      erfasste_komponenten: [],
    });
    expect(detail.schritte[0].hat_automatisierung).toBe(true);
    expect(detail.schritte[0].kann_automatisierung_ausfuehren).toBe(true);
  });
});

describe("automatisierungAusfuehren adapter", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("ruft Zielendpoint und liefert HTTP-200-Ergebnis inkl. fehlgeschlagen=true", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          ausfuehrung_id: "exec-1",
          fehlgeschlagen: true,
          ausgefuehrte_aktionen: 0,
          abgebrochen_bei_aktion_position: 1,
          fehlerart: "geraetefehlschlag",
          nachweise: [{ nachweis_id: "n1", art: "rohantwort" }],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await automatisierungAusfuehren("pid", "sid");

    expect(result.fehlgeschlagen).toBe(true);
    expect(result).not.toBeInstanceOf(ApiError);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/prueflaeufe/pid/schritte/sid/automatisierung/ausfuehren");
    expect(url).not.toContain("/kommandos/");
    expect(init.method).toBe("POST");
    expect(init.body).toBe("{}");
  });

  it("wirft ApiError bei 4xx", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Keine Automatisierung", code: "keine_automatisierung_am_schritt" }), {
          status: 409,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(automatisierungAusfuehren("pid", "sid")).rejects.toBeInstanceOf(ApiError);
  });

  it("scheitert an Zod bei ungültigem Response-Body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ falsch: true }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(automatisierungAusfuehren("pid", "sid")).rejects.toThrow(ZodError);
  });
});
