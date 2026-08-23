import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as identityApi from "@/adapters/api/identity";
import * as qualApi from "@/adapters/api/identityQualification";
import { EinweisungenPage } from "@/pages/identity/EinweisungenPage";

vi.mock("@/adapters/api/identity", () => ({
  listBenutzer: vi.fn(),
}));

vi.mock("@/adapters/api/identityQualification", () => ({
  listEinweisungen: vi.fn(),
  createEinweisung: vi.fn(),
  widerrufenEinweisung: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useCurrentUser: () => ({
    data: {
      benutzer_id: "admin-1",
      rollen: ["pruefer"],
      passwortwechsel_erforderlich: false,
    },
  }),
}));

describe("EinweisungenPage", () => {
  beforeEach(() => {
    vi.mocked(identityApi.listBenutzer).mockResolvedValue([]);
    vi.mocked(qualApi.listEinweisungen).mockResolvedValue([]);
  });

  it("blendet Schreibaktionen für Prüfer aus", async () => {
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <Routes>
            <Route path="/" element={<EinweisungenPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );
    expect(await screen.findByText("Einweisungen")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Einweisung anlegen" })).toBeNull();
  });
});
