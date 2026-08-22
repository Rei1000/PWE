import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/adapters/api/client";
import { EntwurfSchrittAutomatisierung } from "@/components/katalog/EntwurfSchrittAutomatisierung";
import { katalogEntwurfKey } from "@/lib/katalogQueryKeys";

const mutateAsync = vi.fn();

vi.mock("@/hooks/katalog/useKommandos", () => ({
  useKommandosQuery: () => ({
    data: [{ kommando_id: "k1", bezeichnung: "Kommando A" }],
  }),
}));

vi.mock("@/hooks/katalog/useRoutinen", () => ({
  useRoutinenQuery: () => ({
    data: [{ routine_id: "r1", bezeichnung: "Routine A", anzahl_aktionen: 1 }],
  }),
}));

vi.mock("@/hooks/katalog/useEntwurf", () => ({
  useAutomatisierungZuweisenMutation: () => ({
    mutateAsync,
    isPending: false,
    error: null,
  }),
}));

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const invalidateSpy = vi.spyOn(client, "invalidateQueries");
  function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  }
  const view = render(ui, { wrapper: Wrapper });
  return { ...view, invalidateSpy };
}

vi.mock("@/hooks/katalog/useKommandos", () => ({
  useKommandosQuery: () => ({
    data: [{ kommando_id: "k1", bezeichnung: "Kommando A" }],
  }),
}));

vi.mock("@/hooks/katalog/useRoutinen", () => ({
  useRoutinenQuery: () => ({
    data: [{ routine_id: "r1", bezeichnung: "Routine A", anzahl_aktionen: 1 }],
  }),
}));

vi.mock("@/hooks/katalog/useEntwurf", () => ({
  useAutomatisierungZuweisenMutation: () => ({
    mutateAsync,
    isPending: false,
    error: null,
  }),
}));

const baseSchritt = {
  schritt_id: "s1",
  vorlage_id: "v1",
  ist_pflicht: true,
  reihenfolge: 1,
  sollvorgaben: {},
  kommando_id: null,
  routine_id: null,
};

describe("EntwurfSchrittAutomatisierung", () => {
  afterEach(() => {
    mutateAsync.mockReset();
  });

  it("weist Kommando direkt zu", async () => {
    mutateAsync.mockResolvedValue({});
    const { getByLabelText, getAllByRole } = renderWithQuery(
      <EntwurfSchrittAutomatisierung produktdefinitionId="pd-1" schritt={baseSchritt} />,
    );

    fireEvent.change(getByLabelText("Externes Kommando"), { target: { value: "k1" } });
    fireEvent.click(getAllByRole("button", { name: "Zuweisen" })[0]!);

    await waitFor(() =>
      expect(mutateAsync).toHaveBeenCalledWith({ kommando_id: "k1" }),
    );
  });

  it("entfernt Automatisierung explizit", async () => {
    mutateAsync.mockResolvedValue({});
    const { getByRole } = renderWithQuery(
      <EntwurfSchrittAutomatisierung
        produktdefinitionId="pd-1"
        schritt={{ ...baseSchritt, kommando_id: "k1" }}
      />,
    );

    fireEvent.click(getByRole("button", { name: /Automatisierung entfernen/i }));
    await waitFor(() =>
      expect(mutateAsync).toHaveBeenCalledWith({ kommando_id: null, routine_id: null }),
    );
  });

  it("zeigt Confirm bei Wechsel und sendet remove vor assign", async () => {
    mutateAsync.mockResolvedValue({});
    const { getByLabelText, getByTestId, getByRole } = renderWithQuery(
      <EntwurfSchrittAutomatisierung
        produktdefinitionId="pd-1"
        schritt={{ ...baseSchritt, kommando_id: "k1" }}
      />,
    );

    fireEvent.change(getByLabelText("Routine"), { target: { value: "r1" } });
    fireEvent.click(getByTestId("assign-routine"));
    fireEvent.click(getByRole("button", { name: "Wechseln" }));

    await waitFor(() => expect(mutateAsync).toHaveBeenCalledTimes(2));
    expect(mutateAsync.mock.calls[0]?.[0]).toEqual({ kommando_id: null, routine_id: null });
    expect(mutateAsync.mock.calls[1]?.[0]).toEqual({ routine_id: "r1" });
  });

  it("sendet kein assign wenn remove beim Wechsel fehlschlägt", async () => {
    mutateAsync.mockRejectedValueOnce(new ApiError("Remove fehlgeschlagen", 409));
    const { getByLabelText, getByTestId, getByRole } = renderWithQuery(
      <EntwurfSchrittAutomatisierung
        produktdefinitionId="pd-1"
        schritt={{ ...baseSchritt, kommando_id: "k1" }}
      />,
    );

    fireEvent.change(getByLabelText("Routine"), { target: { value: "r1" } });
    fireEvent.click(getByTestId("assign-routine"));
    fireEvent.click(getByRole("button", { name: "Wechseln" }));

    await waitFor(() => expect(mutateAsync).toHaveBeenCalledTimes(1));
    expect(mutateAsync.mock.calls[0]?.[0]).toEqual({ kommando_id: null, routine_id: null });
  });

  it("invalidiert Entwurf wenn assign nach erfolgreichem remove fehlschlägt", async () => {
    mutateAsync
      .mockResolvedValueOnce({})
      .mockRejectedValueOnce(new ApiError("Assign fehlgeschlagen", 409));
    const { getByLabelText, getByTestId, getByRole, invalidateSpy } = renderWithQuery(
      <EntwurfSchrittAutomatisierung
        produktdefinitionId="pd-1"
        schritt={{ ...baseSchritt, kommando_id: "k1" }}
      />,
    );

    fireEvent.change(getByLabelText("Routine"), { target: { value: "r1" } });
    fireEvent.click(getByTestId("assign-routine"));
    fireEvent.click(getByRole("button", { name: "Wechseln" }));

    await waitFor(() => expect(mutateAsync).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: katalogEntwurfKey("pd-1") }),
    );
  });
});
