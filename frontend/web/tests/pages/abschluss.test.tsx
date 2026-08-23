import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/adapters/api/client";
import * as prueflaeufeApi from "@/adapters/api/prueflaeufe";
import * as pdfAktion from "@/lib/protokollPdfAktion";
import { AbschlussPage } from "@/pages/AbschlussPage";

vi.mock("@/adapters/api/prueflaeufe", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/prueflaeufe")>(
    "@/adapters/api/prueflaeufe",
  );
  return {
    ...actual,
    fetchProtokollPdf: vi.fn(),
  };
});

vi.mock("@/lib/protokollPdfAktion", async () => {
  const actual = await vi.importActual<typeof import("@/lib/protokollPdfAktion")>(
    "@/lib/protokollPdfAktion",
  );
  return {
    ...actual,
    openProtokollPdfInViewer: vi.fn(),
    downloadProtokollPdfBlob: vi.fn(),
  };
});

afterEach(() => {
  cleanup();
  vi.mocked(prueflaeufeApi.fetchProtokollPdf).mockReset();
  vi.mocked(pdfAktion.openProtokollPdfInViewer).mockReset();
  vi.mocked(pdfAktion.downloadProtokollPdfBlob).mockReset();
});

function wrap(ui: ReactNode, initialPath = "/prueflaeufe/lauf-12345678/abschluss") {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    createElement(
      QueryClientProvider,
      { client },
      createElement(
        MemoryRouter,
        { initialEntries: [initialPath] },
        createElement(
          Routes,
          null,
          createElement(Route, {
            path: "/prueflaeufe/:prueflaufId/abschluss",
            element: ui,
          }),
        ),
      ),
    ),
  );
}

describe("AbschlussPage Gate 8.4", () => {
  it("öffnet PDF im Viewer nach Klick auf Anzeigen & Drucken", async () => {
    const blob = new Blob([new Uint8Array([1, 2])], { type: "application/pdf" });
    vi.mocked(prueflaeufeApi.fetchProtokollPdf).mockResolvedValue(blob);

    wrap(createElement(AbschlussPage));

    fireEvent.click(screen.getByRole("button", { name: /Anzeigen & Drucken/i }));

    await waitFor(() => {
      expect(prueflaeufeApi.fetchProtokollPdf).toHaveBeenCalledWith("lauf-12345678");
      expect(pdfAktion.openProtokollPdfInViewer).toHaveBeenCalledWith(blob);
    });
    expect(pdfAktion.downloadProtokollPdfBlob).not.toHaveBeenCalled();
  });

  it("zeigt Fehler wenn PDF-Laden fehlschlägt", async () => {
    vi.mocked(prueflaeufeApi.fetchProtokollPdf).mockRejectedValue(
      new ApiError("Der Prüflauf wurde nicht gefunden.", 404, "prueflauf_nicht_gefunden"),
    );

    wrap(createElement(AbschlussPage));
    fireEvent.click(screen.getByRole("button", { name: /Anzeigen & Drucken/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert").textContent).toMatch(/nicht gefunden|Prüflauf/i);
    });
    expect(pdfAktion.openProtokollPdfInViewer).not.toHaveBeenCalled();
  });

  it("lässt Download unverändert über downloadProtokollPdfBlob laufen", async () => {
    const blob = new Blob([new Uint8Array([9])], { type: "application/pdf" });
    vi.mocked(prueflaeufeApi.fetchProtokollPdf).mockResolvedValue(blob);

    wrap(createElement(AbschlussPage));
    fireEvent.click(screen.getByRole("button", { name: /Protokoll-PDF herunterladen/i }));

    await waitFor(() => {
      expect(prueflaeufeApi.fetchProtokollPdf).toHaveBeenCalledWith("lauf-12345678");
      expect(pdfAktion.downloadProtokollPdfBlob).toHaveBeenCalledWith(
        blob,
        "protokoll-lauf-123.pdf",
      );
    });
    expect(pdfAktion.openProtokollPdfInViewer).not.toHaveBeenCalled();
  });
});
