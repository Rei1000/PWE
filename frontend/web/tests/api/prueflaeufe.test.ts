import { describe, expect, it } from "vitest";

import {
  DEMO_KATALOG_ENTWURF,
  entwurfResponseSchema,
  versionResponseSchema,
} from "@/adapters/api/schemas/katalog";
import {
  prueflaufDetailSchema,
  prueflaufResponseSchema,
} from "@/adapters/api/schemas/prueflaeufe";

describe("katalog schemas", () => {
  it("parst Entwurf-Response", () => {
    expect(
      entwurfResponseSchema.parse({
        produktdefinition_id: "pd-1",
        produktkodierung: "1234567890",
      }),
    ).toMatchObject({ produktkodierung: "1234567890" });
  });

  it("Demo-Katalog ist valide", () => {
    expect(DEMO_KATALOG_ENTWURF.prozedur_schritte).toHaveLength(1);
  });
});

describe("prueflaeufe schemas", () => {
  it("parst Prüflauf-Start-Response", () => {
    expect(
      prueflaufResponseSchema.parse({
        prueflauf_id: "p1",
        version_id: "v1",
        produktkodierung: "1234567890",
        pruefobjekt_kennung: "GER-1",
        pruefer_id: "pruefer-1",
        status: "gestartet",
      }),
    ).toMatchObject({ status: "gestartet" });
  });

  it("parst Prüflauf-Detail mit Schritten", () => {
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
          sollvorgaben: { spannung: { min: 220, max: 240 } },
          nachweise: [],
        },
      ],
      sollbestueckung: ["mainboard"],
      erfasste_komponenten: [],
    });
    expect(detail.schritte[0].schritt_id).toBe("schritt-a");
  });

  it("parst Version-Response", () => {
    expect(
      versionResponseSchema.parse({
        version_id: "v1",
        produktdefinition_id: "pd-1",
        produktkodierung: "1234567890",
      }),
    ).toMatchObject({ version_id: "v1" });
  });
});
