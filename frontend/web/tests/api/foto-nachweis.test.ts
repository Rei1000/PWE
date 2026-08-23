import { afterEach, describe, expect, it, vi } from "vitest";
import { ZodError } from "zod";

import { ApiError } from "@/adapters/api/client";
import { erfasseFotoNachweis, fetchNachweisDatei } from "@/adapters/api/prueflaeufe";
import { fotoNachweisResponseSchema } from "@/adapters/api/schemas/prueflaeufe";

describe("fotoNachweisResponseSchema", () => {
  it("parst Upload-Response", () => {
    const data = fotoNachweisResponseSchema.parse({
      nachweis_id: "n1",
      art: "foto",
      datei_id: "d1",
      mime_type: "image/jpeg",
      groesse_bytes: 1234,
      dateiname: "foto.jpg",
    });
    expect(data.art).toBe("foto");
    expect(data.mime_type).toBe("image/jpeg");
  });

  it("lehnt falsche art ab", () => {
    expect(() =>
      fotoNachweisResponseSchema.parse({
        nachweis_id: "n1",
        art: "messwert",
        datei_id: "d1",
        mime_type: "image/jpeg",
        groesse_bytes: 1,
      }),
    ).toThrow(ZodError);
  });
});

describe("erfasseFotoNachweis adapter", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sendet multipart/form-data ohne JSON Content-Type", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          nachweis_id: "n1",
          art: "foto",
          datei_id: "d1",
          mime_type: "image/jpeg",
          groesse_bytes: 4,
        }),
        { status: 201, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const file = new File([new Uint8Array([0xff, 0xd8, 0xff, 0x00])], "foto.jpg", {
      type: "image/jpeg",
    });
    const result = await erfasseFotoNachweis("p1", "schritt-a", file);

    expect(result.nachweis_id).toBe("n1");
    expect(fetchMock).toHaveBeenCalledOnce();
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect(init.body).toBeInstanceOf(FormData);
    expect((init.headers as Record<string, string>)["Content-Type"]).toBeUndefined();
    expect((init.headers as Record<string, string>).Accept).toBe("application/json");
  });

  it("wirft ApiError bei 415", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Der Dateityp wird nicht unterstützt.", code: "ungueltiger_dateityp" }), {
        status: 415,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const file = new File(["x"], "foto.gif", { type: "image/gif" });
    await expect(erfasseFotoNachweis("p1", "s1", file)).rejects.toMatchObject({
      name: "ApiError",
      status: 415,
      code: "ungueltiger_dateityp",
    } satisfies Partial<ApiError>);
  });
});

describe("fetchNachweisDatei adapter", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("lädt Bild-Blob", async () => {
    const blob = new Blob([new Uint8Array([1, 2, 3])], { type: "image/png" });
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(blob, { status: 200, headers: { "Content-Type": "image/png" } }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchNachweisDatei("p1", "n1");
    expect(result.type).toBe("image/png");
    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/prueflaeufe/p1/nachweise/n1/datei");
    expect((init.headers as Record<string, string>).Accept).toContain("image/png");
  });
});
