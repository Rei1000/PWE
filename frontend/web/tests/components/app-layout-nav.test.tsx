import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { AppLayout } from "@/components/layout/AppLayout";

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    Outlet: () => <p>Inhalt</p>,
  };
});

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: vi.fn(),
  useInvalidateSession: () => () => undefined,
}));

vi.mock("@/adapters/api/auth", () => ({
  logout: vi.fn(),
}));

import { useCurrentUser } from "@/hooks/useAuth";

function renderLayout() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <AppLayout />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("AppLayout Navigation", () => {
  it("zeigt Verwaltung für Administrator", () => {
    vi.mocked(useCurrentUser).mockReturnValue({
      data: {
        benutzer_id: "a1",
        login: "admin",
        anzeigename: "Admin",
        status: "aktiv",
        rollen: ["administrator"],
        passwortwechsel_erforderlich: false,
      },
      isLoading: false,
      isError: false,
    } as never);
    renderLayout();
    expect(screen.getByRole("link", { name: "Verwaltung" })).toBeTruthy();
  });

  it("blendet Verwaltung für Prüfer aus", () => {
    vi.mocked(useCurrentUser).mockReturnValue({
      data: {
        benutzer_id: "p1",
        login: "pruefer",
        anzeigename: "Prüfer",
        status: "aktiv",
        rollen: ["pruefer"],
        passwortwechsel_erforderlich: false,
      },
      isLoading: false,
      isError: false,
    } as never);
    renderLayout();
    expect(screen.queryByRole("link", { name: "Verwaltung" })).toBeNull();
  });
});
