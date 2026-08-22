import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as katalogApi from "@/adapters/api/katalog";
import { useSchrittAnlegenMutation } from "@/hooks/katalog/useEntwurf";
import { katalogEntwurfKey } from "@/lib/katalogQueryKeys";

vi.mock("@/adapters/api/katalog", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/katalog")>(
    "@/adapters/api/katalog",
  );
  return { ...actual, createSchritt: vi.fn() };
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

describe("useSchrittAnlegenMutation", () => {
  afterEach(() => {
    vi.mocked(katalogApi.createSchritt).mockReset();
  });

  it("invalidiert Entwurf nach Erfolg", async () => {
    vi.mocked(katalogApi.createSchritt).mockResolvedValue({
      schritt_id: "s1",
      vorlage_id: "v1",
      ist_pflicht: true,
      reihenfolge: 1,
      sollvorgaben: {},
      kommando_id: null,
      routine_id: null,
    });

    const { Wrapper, invalidateSpy } = createWrapper();
    const { result } = renderHook(() => useSchrittAnlegenMutation("pd-1"), { wrapper: Wrapper });

    result.current.mutate({
      schritt_id: "s1",
      vorlage_id: "v1",
      ist_pflicht: true,
      sollvorgaben: {},
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: katalogEntwurfKey("pd-1") });
  });
});
