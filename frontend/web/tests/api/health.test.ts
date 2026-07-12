import { describe, expect, it } from "vitest";

import { healthResponseSchema } from "@/adapters/api/schemas/health";
import { refreshIntervalSchema } from "@/forms/schemas";

describe("healthResponseSchema", () => {
  it("parst gültige API-Antwort", () => {
    expect(healthResponseSchema.parse({ status: "ok" })).toEqual({ status: "ok" });
  });

  it("lehnt ungültige Antwort ab", () => {
    expect(() => healthResponseSchema.parse({})).toThrow();
  });
});

describe("refreshIntervalSchema", () => {
  it("validiert Transport-Intervall", () => {
    expect(refreshIntervalSchema.parse({ intervalSeconds: 30 })).toEqual({
      intervalSeconds: 30,
    });
  });

  it("lehnt Werte außerhalb 5–120 ab", () => {
    expect(() => refreshIntervalSchema.parse({ intervalSeconds: 3 })).toThrow();
  });
});
