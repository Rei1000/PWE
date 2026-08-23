import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as identityApi from "@/adapters/api/identity";
import * as qualApi from "@/adapters/api/identityQualification";
import { BenutzerDetailPage } from "@/pages/identity/BenutzerDetailPage";

vi.mock("@/adapters/api/identity", () => ({
  getBenutzer: vi.fn(),
  aktivierenBenutzer: vi.fn(),
  sperrenBenutzer: vi.fn(),
  entsperrenBenutzer: vi.fn(),
  archivierenBenutzer: vi.fn(),
  wiederherstellenBenutzer: vi.fn(),
  setBenutzerRollen: vi.fn(),
  resetBenutzerPasswort: vi.fn(),
}));

vi.mock("@/adapters/api/identityQualification", () => ({
  listProfile: vi.fn(),
  assignProfilZuBenutzer: vi.fn(),
  removeProfilVonBenutzer: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({
    data: {
      benutzer_id: "admin-1",
      rollen: ["abteilungsleiter"],
      passwortwechsel_erforderlich: false,
    },
  }),
}));

describe("Profilzuordnung", () => {
  beforeEach(() => {
    vi.mocked(identityApi.getBenutzer).mockResolvedValue({
      benutzer_id: "u1",
      login: "max",
      anzeigename: "Max",
      status: "aktiv",
      rollen: ["pruefer"],
      passwortwechsel_erforderlich: false,
    });
    vi.mocked(qualApi.listProfile).mockResolvedValue([
      {
        profil_id: "p1",
        bezeichnung: "Profil A",
        beschreibung: null,
        produktdefinition_ids: [],
        aktiv: true,
      },
    ]);
    vi.mocked(qualApi.assignProfilZuBenutzer).mockResolvedValue();
  });

  it("weist ein Profil einem Benutzer zu", async () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={["/verwaltung/benutzer/u1"]}>
          <Routes>
            <Route path="/verwaltung/benutzer/:benutzerId" element={<BenutzerDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(await screen.findByText("Berechtigungsprofile")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Profil zuweisen"), { target: { value: "p1" } });
    fireEvent.click(screen.getByRole("button", { name: "Zuweisen" }));

    await waitFor(() => {
      expect(qualApi.assignProfilZuBenutzer).toHaveBeenCalledWith("p1", "u1");
    });
    expect(await screen.findByText("Profil A")).toBeTruthy();
  });
});
