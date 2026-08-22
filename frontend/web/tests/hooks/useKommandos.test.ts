import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as bibliothekApi from "@/adapters/api/bibliothek";
import { useCreateKommandoMutation } from "@/hooks/katalog/useKommandos";
import { katalogKommandosKey } from "@/lib/katalogQueryKeys";

vi.mock("@/adapters/api/bibliothek", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/bibliothek")>(
    "@/adapters/api/bibliothek",
  );
  return { ...actual, createKommando: vi.fn() };
});

function createWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const invalidateSpy = vi.spyOn(client, "invalidateQueries");
  function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client }, children);
  }
  return { Wrapper, invalidateSpy };
}

describe("useCreateKommandoMutation", () => {
  afterEach(() => {
    vi.mocked(bibliothekApi.createKommando).mockReset();
  });

  it("invalidiert Kommandos-Liste nach Erfolg", async () => {
    vi.mocked(bibliothekApi.createKommando).mockResolvedValue({
      kommando_id: "k1",
      bezeichnung: "Test",
    });

    const { Wrapper, invalidateSpy } = createWrapper();
    const { result } = renderHook(() => useCreateKommandoMutation(), { wrapper: Wrapper });

    result.current.mutate({ bezeichnung: "Test", kommandocode: "C" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: katalogKommandosKey });
  });
});
