import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as identityApi from "@/adapters/api/identity";
import { BenutzerPage } from "@/pages/identity/BenutzerPage";

vi.mock("@/adapters/api/identity", () => ({
  listBenutzer: vi.fn(),
  createBenutzer: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({
    data: adminUser,
  }),
}));

const adminUser = {
  benutzer_id: "admin-1",
  login: "admin",
  anzeigename: "Administrator",
  status: "aktiv",
  rollen: ["administrator"],
  passwortwechsel_erforderlich: false,
};

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/verwaltung/benutzer"]}>
        <Routes>
          <Route path="/verwaltung/benutzer" element={<BenutzerPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("BenutzerPage", () => {
  beforeEach(() => {
    vi.mocked(identityApi.listBenutzer).mockReset();
  });

  it("zeigt die Benutzerliste mit Status", async () => {
    vi.mocked(identityApi.listBenutzer).mockResolvedValue([
      {
        benutzer_id: "u1",
        login: "max",
        anzeigename: "Max Mustermann",
        status: "aktiv",
        rollen: ["pruefer"],
        passwortwechsel_erforderlich: false,
      },
      {
        benutzer_id: "u2",
        login: "anna",
        anzeigename: "Anna Admin",
        status: "gesperrt",
        rollen: ["qm"],
        passwortwechsel_erforderlich: true,
      },
    ]);

    renderPage();
    expect(await screen.findByText("Max Mustermann")).toBeTruthy();
    expect(screen.getByText("Gesperrt")).toBeTruthy();
    expect(screen.getByText("Aktiv")).toBeTruthy();
  });
});
