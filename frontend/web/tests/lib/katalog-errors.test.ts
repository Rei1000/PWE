import { katalogConflictMessage } from "@/lib/katalogErrors";
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
