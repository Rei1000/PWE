import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { RoutineEditorPage } from "@/pages/katalog/RoutineEditorPage";

const kommandosMock = vi.fn();
const routineQueryMock = vi.fn();
const createMutationMock = vi.fn();
const updateMutationMock = vi.fn();

vi.mock("@/hooks/katalog/useKommandos", () => ({
  useKommandosQuery: () => kommandosMock(),
}));

vi.mock("@/hooks/katalog/useRoutinen", () => ({
  useRoutineQuery: (id?: string) => routineQueryMock(id),
  useCreateRoutineMutation: () => createMutationMock(),
  useUpdateRoutineMutation: () => updateMutationMock(),
}));

function renderEditor(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/katalog/routinen/neu" element={<RoutineEditorPage />} />
        <Route path="/katalog/routinen/:routineId" element={<RoutineEditorPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("RoutineEditorPage", () => {
  it("zeigt Fallback für unbekannte Kommando-ID beim Laden", () => {
    kommandosMock.mockReturnValue({ data: [] });
    routineQueryMock.mockReturnValue({
      data: {
        routine_id: "r1",
        bezeichnung: "R",
        aktionen: [{ position: 1, kommando_id: "k-missing" }],
      },
      isLoading: false,
      error: null,
    });
    createMutationMock.mockReturnValue({ mutateAsync: vi.fn(), isPending: false, error: null, reset: vi.fn() });
    updateMutationMock.mockReturnValue({ mutateAsync: vi.fn(), isPending: false, error: null, reset: vi.fn() });

    renderEditor("/katalog/routinen/r1");

    expect(screen.getByText(/Unbekannt \(k-missing\)/)).toBeDefined();
  });

  it("rendert Hoch/Runter-Steuerung nach Hinzufügen", () => {
    kommandosMock.mockReturnValue({
      data: [{ kommando_id: "k1", bezeichnung: "Kommando A" }],
    });
    routineQueryMock.mockReturnValue({ data: undefined, isLoading: false, error: null });
    createMutationMock.mockReturnValue({ mutateAsync: vi.fn(), isPending: false, error: null, reset: vi.fn() });
    updateMutationMock.mockReturnValue({ mutateAsync: vi.fn(), isPending: false, error: null, reset: vi.fn() });

    renderEditor("/katalog/routinen/neu");

    const select = screen.getAllByLabelText("Kommando auswählen")[0]!;
    fireEvent.change(select, { target: { value: "k1" } });
    fireEvent.click(screen.getAllByRole("button", { name: /Hinzufügen/i })[0]!);

    expect(screen.getAllByLabelText("Nach oben")[0]).toBeDefined();
    expect(screen.getAllByLabelText("Nach unten")[0]).toBeDefined();
    expect(screen.getAllByText("Kommando A").length).toBeGreaterThan(0);
  });
});
