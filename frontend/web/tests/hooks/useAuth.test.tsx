import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as authApi from "@/adapters/api/auth";
import { ApiError } from "@/adapters/api/client";
import { RequireAuth, RequireNoForceChange } from "@/hooks/useAuth";

vi.mock("@/adapters/api/auth", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/auth")>("@/adapters/api/auth");
  return { ...actual, fetchMe: vi.fn() };
});

function renderForceChangeGuard() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route element={<RequireAuth />}>
            <Route path="/passwort-aendern" element={<p>Passwort-Dialog</p>} />
            <Route element={<RequireNoForceChange />}>
              <Route index element={<p>Start</p>} />
            </Route>
          </Route>
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("RequireNoForceChange", () => {
  beforeEach(() => {
    vi.mocked(authApi.fetchMe).mockReset();
  });

  it("leitet bei passwortwechsel_erforderlich zum Passwortdialog um", async () => {
    vi.mocked(authApi.fetchMe).mockResolvedValue({
      benutzer_id: "u1",
      login: "user",
      anzeigename: "User",
      status: "aktiv",
      rollen: ["pruefer"],
      passwortwechsel_erforderlich: true,
    });
    renderForceChangeGuard();
    expect(await screen.findByText("Passwort-Dialog")).toBeTruthy();
    expect(screen.queryByText("Start")).toBeNull();
  });

  it("lässt Start zu ohne Passwortzwang", async () => {
    vi.mocked(authApi.fetchMe).mockResolvedValue({
      benutzer_id: "u1",
      login: "user",
      anzeigename: "User",
      status: "aktiv",
      rollen: ["pruefer"],
      passwortwechsel_erforderlich: false,
    });
    renderForceChangeGuard();
    expect(await screen.findByText("Start")).toBeTruthy();
  });
});

describe("RequireAuth", () => {
  it("leitet ohne Session zur Login-Seite um", async () => {
    vi.mocked(authApi.fetchMe).mockRejectedValue(new ApiError("Nicht angemeldet", 401));
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    render(
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
    expect(await screen.findByText("Login-Seite")).toBeTruthy();
  });
});
