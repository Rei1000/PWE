import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as authApi from "@/adapters/api/auth";
import { LoginPage } from "@/pages/LoginPage";

vi.mock("@/adapters/api/auth", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/auth")>("@/adapters/api/auth");
  return {
    ...actual,
    login: vi.fn(),
    fetchMe: vi.fn(),
    logout: vi.fn(),
  };
});

function renderLogin() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<p>Start</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    vi.mocked(authApi.login).mockReset();
  });

  it("meldet an und navigiert zur Startseite", async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      benutzer_id: "u1",
      login: "admin",
      anzeigename: "Administrator",
      status: "aktiv",
      rollen: ["administrator"],
    });
    renderLogin();
    fireEvent.change(screen.getByLabelText("Login"), { target: { value: "admin" } });
    fireEvent.change(screen.getByLabelText("Passwort"), {
      target: { value: "admin-change-me" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Anmelden" }));
    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith("admin", "admin-change-me");
    });
    expect(await screen.findByText("Start")).toBeTruthy();
  });
});
