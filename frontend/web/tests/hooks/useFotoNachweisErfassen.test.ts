import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as prueflaeufeApi from "@/adapters/api/prueflaeufe";
import { useFotoNachweisErfassen } from "@/hooks/useFotoNachweisErfassen";
import { prueflaufQueryKey } from "@/lib/queryClient";

vi.mock("@/adapters/api/prueflaeufe", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/prueflaeufe")>(
    "@/adapters/api/prueflaeufe",
  );
  return {
    ...actual,
    erfasseFotoNachweis: vi.fn(),
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
  return { Wrapper, invalidateSpy };
}

describe("useFotoNachweisErfassen", () => {
  afterEach(() => {
    vi.mocked(prueflaeufeApi.erfasseFotoNachweis).mockReset();
  });

  it("invalidiert prueflaufQueryKey nach Erfolg", async () => {
    vi.mocked(prueflaeufeApi.erfasseFotoNachweis).mockResolvedValue({
      nachweis_id: "n1",
      art: "foto",
      datei_id: "d1",
      mime_type: "image/jpeg",
      groesse_bytes: 10,
    });

    const file = new File(["x"], "f.jpg", { type: "image/jpeg" });
    const { Wrapper, invalidateSpy } = createWrapper();
    const { result } = renderHook(() => useFotoNachweisErfassen("pid", "sid"), {
      wrapper: Wrapper,
    });

    result.current.mutate(file);
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: prueflaufQueryKey("pid") });
  });
});
