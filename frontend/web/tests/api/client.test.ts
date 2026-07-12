import { describe, expect, it, vi, afterEach } from "vitest";

import { apiPost } from "@/adapters/api/client";

describe("apiPost", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sendet Content-Type application/json bei POST-Body", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ prueflauf_id: "p1" }), {
        status: 201,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await apiPost("/prueflaeufe", { produktkodierung: "123" });

    expect(fetchMock).toHaveBeenCalledOnce();
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect((init.headers as Record<string, string>)["Content-Type"]).toBe("application/json");
    expect(init.body).toBe(JSON.stringify({ produktkodierung: "123" }));
  });
});
