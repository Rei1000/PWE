import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as qualApi from "@/adapters/api/identityQualification";
import {
  useCreateEinweisungMutation,
  useEinweisungenQuery,
  useWiderrufenEinweisungMutation,
} from "@/hooks/identity/useEinweisungen";

vi.mock("@/adapters/api/identityQualification", () => ({
  listEinweisungen: vi.fn(),
  createEinweisung: vi.fn(),
  widerrufenEinweisung: vi.fn(),
}));

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

describe("useEinweisungen", () => {
  beforeEach(() => {
    vi.mocked(qualApi.listEinweisungen).mockReset();
    vi.mocked(qualApi.createEinweisung).mockReset();
    vi.mocked(qualApi.widerrufenEinweisung).mockReset();
  });

  it("lädt Einweisungen für einen Benutzer", async () => {
    vi.mocked(qualApi.listEinweisungen).mockResolvedValue([
      {
        einweisung_id: "e1",
        benutzer_id: "u1",
        version_id: "v1",
        eingewiesen_durch: "admin",
        datum: "2026-01-01T00:00:00Z",
        status: "gueltig",
      },
    ]);

    const { result } = renderHook(() => useEinweisungenQuery("u1"), { wrapper: wrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
  });

  it("legt eine Einweisung an", async () => {
    vi.mocked(qualApi.createEinweisung).mockResolvedValue({
      einweisung_id: "e1",
      benutzer_id: "u1",
      version_id: "v1",
      eingewiesen_durch: "admin",
      datum: "2026-01-01T00:00:00Z",
      status: "gueltig",
    });

    const { result } = renderHook(() => useCreateEinweisungMutation("u1"), { wrapper: wrapper() });
    await result.current.mutateAsync({
      benutzer_id: "u1",
      version_id: "v1",
    });
    expect(qualApi.createEinweisung).toHaveBeenCalledWith({
      benutzer_id: "u1",
      version_id: "v1",
    });
  });

  it("widerruft eine Einweisung", async () => {
    vi.mocked(qualApi.widerrufenEinweisung).mockResolvedValue({
      einweisung_id: "e1",
      benutzer_id: "u1",
      version_id: "v1",
      eingewiesen_durch: "admin",
      datum: "2026-01-01T00:00:00Z",
      status: "widerrufen",
    });

    const { result } = renderHook(() => useWiderrufenEinweisungMutation("u1"), {
      wrapper: wrapper(),
    });
    await result.current.mutateAsync("e1");
    expect(qualApi.widerrufenEinweisung).toHaveBeenCalledWith("e1");
  });
});
