import { describe, expect, it } from "vitest";

import { ApiError } from "@/adapters/api/client";
import { prueflaufErrorMessage } from "@/lib/prueflaufErrors";

describe("prueflaufErrorMessage", () => {
  it("mappt ungueltiger_dateityp", () => {
    const msg = prueflaufErrorMessage(
      new ApiError("Der Dateityp wird nicht unterstützt.", 415, "ungueltiger_dateityp"),
    );
    expect(msg).toContain("JPEG");
  });

  it("mappt datei_zu_gross", () => {
    const msg = prueflaufErrorMessage(
      new ApiError("Die Datei ist zu groß.", 413, "datei_zu_gross"),
    );
    expect(msg).toContain("5 MiB");
  });

  it("mappt datei_speicherung_fehlgeschlagen", () => {
    const msg = prueflaufErrorMessage(
      new ApiError("Die Datei konnte nicht gespeichert werden.", 503, "datei_speicherung_fehlgeschlagen"),
    );
    expect(msg).toContain("gespeichert");
  });

  it("gibt null für Nicht-ApiError zurück", () => {
    expect(prueflaufErrorMessage(new Error("x"))).toBeNull();
  });
});
