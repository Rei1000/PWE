import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as qualApi from "@/adapters/api/identityQualification";
import { ProfilePage } from "@/pages/identity/ProfilePage";

vi.mock("@/adapters/api/identityQualification", () => ({
  listProfile: vi.fn(),
  createProfil: vi.fn(),
  updateProfil: vi.fn(),
  aktivierenProfil: vi.fn(),
  deaktivierenProfil: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({
    data: {
      benutzer_id: "admin-1",
      rollen: ["administrator"],
      passwortwechsel_erforderlich: false,
    },
  }),
}));

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <Routes>
          <Route path="/" element={<ProfilePage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("ProfilePage", () => {
  beforeEach(() => {
    vi.mocked(qualApi.listProfile).mockReset();
    vi.mocked(qualApi.deaktivierenProfil).mockReset();
    vi.mocked(qualApi.aktivierenProfil).mockReset();
  });

  it("deaktiviert ein aktives Profil", async () => {
    vi.mocked(qualApi.listProfile).mockResolvedValue([
      {
        profil_id: "p1",
        bezeichnung: "Montage",
        beschreibung: null,
        produktdefinition_ids: [],
        aktiv: true,
      },
    ]);
    vi.mocked(qualApi.deaktivierenProfil).mockResolvedValue({
      profil_id: "p1",
      bezeichnung: "Montage",
      beschreibung: null,
      produktdefinition_ids: [],
      aktiv: false,
    });

    renderPage();
    expect(await screen.findByText("Montage")).toBeTruthy();
    fireEvent.click(screen.getAllByRole("button", { name: "Deaktivieren" })[0]);
    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Deaktivieren" }).length).toBeGreaterThan(1);
    });
    fireEvent.click(screen.getAllByRole("button", { name: "Deaktivieren" })[1]);

    await waitFor(() => {
      expect(qualApi.deaktivierenProfil).toHaveBeenCalledWith("p1");
    });
  });
});
