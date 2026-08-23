import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as authApi from "@/adapters/api/auth";
import { PasswortAendernPage } from "@/pages/PasswortAendernPage";

vi.mock("@/adapters/api/auth", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/auth")>("@/adapters/api/auth");
  return {
    ...actual,
    changePassword: vi.fn(),
    fetchMe: vi.fn(),
  };
});

function renderPasswort(force = false) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  vi.mocked(authApi.fetchMe).mockResolvedValue({
    benutzer_id: "u1",
    login: "user",
    anzeigename: "User",
    status: "aktiv",
    rollen: ["pruefer"],
    passwortwechsel_erforderlich: force,
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/passwort-aendern"]}>
        <Routes>
          <Route path="/passwort-aendern" element={<PasswortAendernPage />} />
          <Route path="/login" element={<p>Login</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("PasswortAendernPage", () => {
  beforeEach(() => {
    vi.mocked(authApi.changePassword).mockReset();
  });

  it("ändert das Passwort und leitet zur Login-Seite um", async () => {
    vi.mocked(authApi.changePassword).mockResolvedValue();
    renderPasswort(false);

    fireEvent.change(screen.getByLabelText("Aktuelles Passwort"), {
      target: { value: "alt" },
    });
    fireEvent.change(screen.getByLabelText("Neues Passwort"), {
      target: { value: "neu" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Passwort speichern" }));

    await waitFor(() => {
      expect(authApi.changePassword).toHaveBeenCalledWith("alt", "neu");
    });
    expect(await screen.findByText("Login")).toBeTruthy();
  });

  it("zeigt keinen Abbrechen-Button bei erzwungenem Passwortwechsel", async () => {
    renderPasswort(true);
    expect(await screen.findByText("Passwort ändern erforderlich")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Abbrechen" })).toBeNull();
  });
});
