import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { EntwurfNeuPage } from "@/pages/katalog/EntwurfNeuPage";

const mutateAsync = vi.fn();

vi.mock("@/hooks/katalog/useEntwurf", () => ({
  useEntwurfAnlegenMutation: () => ({
    mutateAsync,
    isPending: false,
    error: null,
    reset: vi.fn(),
  }),
}));

const navigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return { ...actual, useNavigate: () => navigate };
});

describe("EntwurfNeuPage", () => {
  it("legt leeren Entwurf an und navigiert", async () => {
    mutateAsync.mockResolvedValue({
      produktdefinition_id: "pd-1",
      produktkodierung: "1234567890",
    });

    render(
      <MemoryRouter>
        <EntwurfNeuPage />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByLabelText("Produktkodierung"), {
      target: { value: "1234567890" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Entwurf anlegen/i }));

    await vi.waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith({
        produktkodierung: "1234567890",
        prozedur_schritte: [],
        sollbestueckung: [],
      });
      expect(navigate).toHaveBeenCalledWith("/katalog/entwuerfe/pd-1");
    });
  });
});
