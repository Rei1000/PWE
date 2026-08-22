import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiDelete, apiPut } from "@/adapters/api/client";

describe("apiPut", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sendet PUT mit JSON-Body", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ kommando_id: "k1", bezeichnung: "X", kommandocode: "C" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await apiPut("/katalog/bibliothek/kommandos/k1", { bezeichnung: "X", kommandocode: "C" });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("PUT");
    expect(init.body).toBe(JSON.stringify({ bezeichnung: "X", kommandocode: "C" }));
  });

  it("wirft ApiError bei Fehlerantwort", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Nicht gefunden", code: "externes_kommando_nicht_gefunden" }), {
          status: 404,
        }),
      ),
    );

    await expect(apiPut("/x", {})).rejects.toMatchObject({
      status: 404,
      code: "externes_kommando_nicht_gefunden",
    } satisfies Partial<ApiError>);
  });
});

describe("apiDelete", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sendet DELETE und akzeptiert 204", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await apiDelete("/katalog/bibliothek/kommandos/k1");

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("DELETE");
  });

  it("wirft ApiError bei 409", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "In Verwendung", code: "kommando_in_verwendung" }), {
          status: 409,
        }),
      ),
    );

    await expect(apiDelete("/x")).rejects.toMatchObject({
      status: 409,
      code: "kommando_in_verwendung",
    });
  });
});
