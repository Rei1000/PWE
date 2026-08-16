import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as prueflaeufeApi from "@/adapters/api/prueflaeufe";
import { useAutomatisierungAusfuehren } from "@/hooks/useAutomatisierungAusfuehren";
import { prueflaufQueryKey } from "@/lib/queryClient";

vi.mock("@/adapters/api/prueflaeufe", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/prueflaeufe")>(
    "@/adapters/api/prueflaeufe",
  );
  return {
    ...actual,
    automatisierungAusfuehren: vi.fn(),
  };
});

function createWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const invalidateSpy = vi.spyOn(client, "invalidateQueries");
  function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  }
  return { Wrapper, client, invalidateSpy };
}

describe("useAutomatisierungAusfuehren", () => {
  afterEach(() => {
    vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockReset();
  });

  it("setzt retry: false und invalidiert nach HTTP 200", async () => {
    vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockResolvedValue({
      ausfuehrung_id: "e1",
      fehlgeschlagen: true,
      ausgefuehrte_aktionen: 0,
      abgebrochen_bei_aktion_position: 1,
      fehlerart: "keine_geraeteantwort",
      nachweise: [],
    });

    const { Wrapper, invalidateSpy } = createWrapper();
    const { result } = renderHook(() => useAutomatisierungAusfuehren("pid", "sid"), {
      wrapper: Wrapper,
    });

    expect(result.current).toMatchObject({});
    result.current.mutate();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.fehlgeschlagen).toBe(true);
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: prueflaufQueryKey("pid") });
  });

  it("invalidiert auch bei Netzwerkfehler ohne erneute Ausführung", async () => {
    vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockRejectedValue(
      new TypeError("Failed to fetch"),
    );

    const { Wrapper, invalidateSpy } = createWrapper();
    const { result } = renderHook(() => useAutomatisierungAusfuehren("pid", "sid"), {
      wrapper: Wrapper,
    });

    result.current.mutate();
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: prueflaufQueryKey("pid") });
    expect(prueflaeufeApi.automatisierungAusfuehren).toHaveBeenCalledTimes(1);
  });
});
