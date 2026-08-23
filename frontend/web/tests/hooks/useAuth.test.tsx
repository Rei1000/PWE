import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as authApi from "@/adapters/api/auth";
import { ApiError } from "@/adapters/api/client";
import { RequireAuth } from "@/hooks/useAuth";

vi.mock("@/adapters/api/auth", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/auth")>("@/adapters/api/auth");
  return {
    ...actual,
    fetchMe: vi.fn(),
    logout: vi.fn(),
  };
});

function renderProtected() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/secure"]}>
        <Routes>
          <Route path="/login" element={<p>Login-Seite</p>} />
          <Route element={<RequireAuth />}>
            <Route path="/secure" element={<p>Geschützt</p>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("RequireAuth", () => {
  beforeEach(() => {
    vi.mocked(authApi.fetchMe).mockReset();
  });

  it("leitet ohne Session zur Login-Seite um", async () => {
    vi.mocked(authApi.fetchMe).mockRejectedValue(new ApiError("Nicht angemeldet", 401));
    renderProtected();
    expect(await screen.findByText("Login-Seite")).toBeTruthy();
  });

  it("zeigt geschützte Route bei gültiger Session", async () => {
    vi.mocked(authApi.fetchMe).mockResolvedValue({
      benutzer_id: "u1",
      login: "admin",
      anzeigename: "Administrator",
      status: "aktiv",
      rollen: ["administrator"],
    });
    renderProtected();
    expect(await screen.findByText("Geschützt")).toBeTruthy();
    await waitFor(() => {
      expect(authApi.fetchMe).toHaveBeenCalled();
    });
  });
});
