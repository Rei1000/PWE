import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/adapters/api/client";
import * as prueflaeufeApi from "@/adapters/api/prueflaeufe";
import { FotoNachweisAnzeige } from "@/components/FotoNachweisAnzeige";
import { FotoNachweisUpload } from "@/components/FotoNachweisUpload";
import { SchrittNachweise } from "@/components/SchrittNachweise";

vi.mock("@/adapters/api/prueflaeufe", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/prueflaeufe")>(
    "@/adapters/api/prueflaeufe",
  );
  return {
    ...actual,
    erfasseFotoNachweis: vi.fn(),
    fetchNachweisDatei: vi.fn(),
  };
});

afterEach(() => {
  cleanup();
  vi.mocked(prueflaeufeApi.erfasseFotoNachweis).mockReset();
  vi.mocked(prueflaeufeApi.fetchNachweisDatei).mockReset();
  vi.restoreAllMocks();
});

function wrap(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(createElement(QueryClientProvider, { client }, ui));
}

describe("FotoNachweisUpload", () => {
  it("zeigt Client-Fehler bei ungültigem MIME", async () => {
    wrap(createElement(FotoNachweisUpload, { prueflaufId: "p1", schrittId: "s1" }));

    const input = screen.getByLabelText("Foto-Nachweis") as HTMLInputElement;
    const file = new File(["x"], "bad.gif", { type: "image/gif" });
    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByRole("alert").textContent).toContain("JPEG");
    expect(prueflaeufeApi.erfasseFotoNachweis).not.toHaveBeenCalled();
  });

  it("lädt Foto nach Bestätigung hoch", async () => {
    vi.mocked(prueflaeufeApi.erfasseFotoNachweis).mockResolvedValue({
      nachweis_id: "n1",
      art: "foto",
      datei_id: "d1",
      mime_type: "image/jpeg",
      groesse_bytes: 4,
    });

    const createObjectURL = vi.fn(() => "blob:preview");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL });

    wrap(createElement(FotoNachweisUpload, { prueflaufId: "p1", schrittId: "s1" }));

    const input = screen.getByLabelText("Foto-Nachweis") as HTMLInputElement;
    const file = new File([new Uint8Array([1, 2, 3, 4])], "foto.jpg", { type: "image/jpeg" });
    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByTestId("foto-upload-vorschau")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /Foto hochladen/ }));

    await waitFor(() =>
      expect(prueflaeufeApi.erfasseFotoNachweis).toHaveBeenCalledWith("p1", "s1", file),
    );
  });

  it("zeigt ApiError bei 413", async () => {
    vi.mocked(prueflaeufeApi.erfasseFotoNachweis).mockRejectedValue(
      new ApiError("Die Datei ist zu groß.", 413, "datei_zu_gross"),
    );

    wrap(createElement(FotoNachweisUpload, { prueflaufId: "p1", schrittId: "s1" }));

    const input = screen.getByLabelText("Foto-Nachweis") as HTMLInputElement;
    const file = new File([new Uint8Array([1, 2, 3])], "foto.jpg", { type: "image/jpeg" });
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Foto hochladen/ }));

    await waitFor(() => expect(screen.getByRole("alert").textContent).toContain("5 MiB"));
  });
});

describe("FotoNachweisAnzeige", () => {
  it("zeigt Bild nach Blob-Download", async () => {
    const blob = new Blob([new Uint8Array([1, 2])], { type: "image/png" });
    vi.mocked(prueflaeufeApi.fetchNachweisDatei).mockResolvedValue(blob);

    const createObjectURL = vi.fn(() => "blob:anzeige");
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL: vi.fn() });

    wrap(
      createElement(FotoNachweisAnzeige, {
        prueflaufId: "p1",
        nachweisId: "n1",
        dateiname: "foto.png",
      }),
    );

    await waitFor(() => expect(screen.getByTestId("foto-nachweis-bild")).toBeTruthy());
    expect(prueflaeufeApi.fetchNachweisDatei).toHaveBeenCalledWith("p1", "n1");
  });
});

describe("SchrittNachweise", () => {
  it("rendert kompakten Messwert und Foto-Anzeige", async () => {
    vi.mocked(prueflaeufeApi.fetchNachweisDatei).mockResolvedValue(
      new Blob([new Uint8Array([1])], { type: "image/jpeg" }),
    );
    vi.stubGlobal("URL", { ...URL, createObjectURL: vi.fn(() => "blob:x"), revokeObjectURL: vi.fn() });

    wrap(
      createElement(SchrittNachweise, {
        prueflaufId: "p1",
        nachweise: [
          {
            nachweis_id: "n-m",
            art: "messwert",
            erfasst_am: "2026-01-01T00:00:00Z",
            payload: { spannung: 230 },
            ist_automatisch: false,
          },
          {
            nachweis_id: "n-f",
            art: "foto",
            erfasst_am: "2026-01-01T00:00:01Z",
            payload: { datei_id: "d1", mime_type: "image/jpeg", groesse_bytes: 1 },
            ist_automatisch: false,
          },
        ],
      }),
    );

    expect(screen.getByText(/Messwert: spannung=230/)).toBeTruthy();
    await waitFor(() => expect(screen.getByTestId("foto-nachweis-bild")).toBeTruthy());
  });
});

describe("Foto-Nachweis Upload-Flow", () => {
  it("durchläuft Auswahl, Vorschau, Upload und Anzeige", async () => {
    vi.mocked(prueflaeufeApi.erfasseFotoNachweis).mockResolvedValue({
      nachweis_id: "n-foto",
      art: "foto",
      datei_id: "d1",
      mime_type: "image/jpeg",
      groesse_bytes: 4,
    });
    vi.mocked(prueflaeufeApi.fetchNachweisDatei).mockResolvedValue(
      new Blob([new Uint8Array([1, 2, 3, 4])], { type: "image/jpeg" }),
    );

    let blobCounter = 0;
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL: vi.fn(() => `blob:mock-${++blobCounter}`),
      revokeObjectURL: vi.fn(),
    });

    const { unmount } = wrap(createElement(FotoNachweisUpload, { prueflaufId: "p1", schrittId: "s1" }));

    const file = new File([new Uint8Array([1, 2, 3, 4])], "foto.jpg", { type: "image/jpeg" });
    fireEvent.change(screen.getByLabelText("Foto-Nachweis"), { target: { files: [file] } });
    expect(screen.getByTestId("foto-upload-vorschau")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: /Foto hochladen/ }));
    await waitFor(() => expect(prueflaeufeApi.erfasseFotoNachweis).toHaveBeenCalledOnce());

    unmount();
    cleanup();

    wrap(
      createElement(SchrittNachweise, {
        prueflaufId: "p1",
        nachweise: [
          {
            nachweis_id: "n-foto",
            art: "foto",
            erfasst_am: "2026-01-01T00:00:00Z",
            payload: {
              datei_id: "d1",
              mime_type: "image/jpeg",
              groesse_bytes: 4,
              dateiname: "foto.jpg",
            },
            ist_automatisch: false,
          },
        ],
      }),
    );

    await waitFor(() => expect(screen.getByTestId("foto-nachweis-bild")).toBeTruthy());
    expect(prueflaeufeApi.fetchNachweisDatei).toHaveBeenCalledWith("p1", "n-foto");
  });
});
