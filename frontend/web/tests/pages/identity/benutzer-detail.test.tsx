import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as identityApi from "@/adapters/api/identity";
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
  listProfile: vi.fn().mockResolvedValue([]),
  assignProfilZuBenutzer: vi.fn(),
  removeProfilVonBenutzer: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({
    data: {
      benutzer_id: "admin-1",
      login: "admin",
      anzeigename: "Administrator",
      status: "aktiv",
      rollen: ["administrator"],
      passwortwechsel_erforderlich: false,
    },
  }),
}));

const benutzerNeu = {
  benutzer_id: "u1",
  login: "neu",
  anzeigename: "Neuer Benutzer",
  status: "neu",
  rollen: ["pruefer"],
  passwortwechsel_erforderlich: true,
};

function renderDetail() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/verwaltung/benutzer/u1"]}>
        <Routes>
          <Route path="/verwaltung/benutzer/:benutzerId" element={<BenutzerDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("BenutzerDetailPage", () => {
  beforeEach(() => {
    vi.mocked(identityApi.getBenutzer).mockReset();
    vi.mocked(identityApi.aktivierenBenutzer).mockReset();
    vi.mocked(identityApi.setBenutzerRollen).mockReset();
  });

  it("aktiviert einen neuen Benutzer", async () => {
    vi.mocked(identityApi.getBenutzer).mockResolvedValue(benutzerNeu);
    vi.mocked(identityApi.aktivierenBenutzer).mockResolvedValue({
      ...benutzerNeu,
      status: "aktiv",
    });

    renderDetail();
    expect(await screen.findByText("Neuer Benutzer")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Aktivieren" }));

    await waitFor(() => {
      expect(identityApi.aktivierenBenutzer).toHaveBeenCalledWith("u1");
    });
  });

  it("speichert geänderte Rollen", async () => {
    vi.mocked(identityApi.getBenutzer).mockResolvedValue({
      ...benutzerNeu,
      status: "aktiv",
    });
    vi.mocked(identityApi.setBenutzerRollen).mockResolvedValue({
      ...benutzerNeu,
      status: "aktiv",
      rollen: ["pruefer", "qm"],
    });

    renderDetail();
    expect(await screen.findByText("Rollen")).toBeTruthy();
    fireEvent.click(screen.getByLabelText("QM"));
    fireEvent.click(screen.getByRole("button", { name: "Rollen speichern" }));

    await waitFor(() => {
      expect(identityApi.setBenutzerRollen).toHaveBeenCalledWith("u1", {
        rollen: ["pruefer", "qm"],
      });
    });
  });
});
