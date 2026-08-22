import { katalogConflictMessage, katalogDomainMessage, katalogErrorMessage } from "@/lib/katalogErrors";
import { ApiError } from "@/adapters/api/client";
import { describe, expect, it } from "vitest";

describe("katalogConflictMessage", () => {
  it("liefert fachliche Meldung für kommando_in_verwendung", () => {
    const msg = katalogConflictMessage(new ApiError("x", 409, "kommando_in_verwendung"));
    expect(msg).toMatch(/offenen Entwurf/);
  });

  it("liefert null für andere Fehler", () => {
    expect(katalogConflictMessage(new ApiError("x", 404))).toBeNull();
  });
});

describe("katalogDomainMessage", () => {
  it("mappt entwurf_nicht_gefunden", () => {
    expect(katalogDomainMessage(new ApiError("x", 404, "entwurf_nicht_gefunden"))).toMatch(
      /Entwurf nicht gefunden/,
    );
  });

  it("mappt automatisierung_doppelt_zugewiesen", () => {
    expect(
      katalogDomainMessage(new ApiError("x", 409, "automatisierung_doppelt_zugewiesen")),
    ).toMatch(/entfernen/);
  });
});

describe("katalogErrorMessage", () => {
  it("bevorzugt Domain-Mapping", () => {
    expect(katalogErrorMessage(new ApiError("raw", 404, "entwurf_nicht_gefunden"))).toMatch(
      /Entwurf nicht gefunden/,
    );
  });
});
