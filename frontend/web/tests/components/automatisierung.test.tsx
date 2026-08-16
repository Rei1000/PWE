import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement, type ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/adapters/api/client";
import * as prueflaeufeApi from "@/adapters/api/prueflaeufe";
import { AutomatisierungErgebnis } from "@/components/AutomatisierungErgebnis";
import { SchrittAutomatisierung } from "@/components/SchrittAutomatisierung";

vi.mock("@/adapters/api/prueflaeufe", async () => {
  const actual = await vi.importActual<typeof import("@/adapters/api/prueflaeufe")>(
    "@/adapters/api/prueflaeufe",
  );
  return {
    ...actual,
    automatisierungAusfuehren: vi.fn(),
  };
});

afterEach(() => {
  cleanup();
  vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockReset();
});

function wrap(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(createElement(QueryClientProvider, { client }, ui));
}

function expectDisabled(el: HTMLElement, disabled: boolean) {
  expect((el as HTMLButtonElement).disabled).toBe(disabled);
}

describe("AutomatisierungErgebnis", () => {
  it("zeigt Erfolg", () => {
    render(
      createElement(AutomatisierungErgebnis, {
        ergebnis: {
          ausfuehrung_id: "e1",
          fehlgeschlagen: false,
          ausgefuehrte_aktionen: 2,
          abgebrochen_bei_aktion_position: null,
          fehlerart: null,
          nachweise: [{ nachweis_id: "n1", art: "rohantwort" }],
        },
      }),
    );
    expect(screen.getByText("Automatisierung erfolgreich")).toBeTruthy();
    expect(screen.getByText(/2 Aktionen/)).toBeTruthy();
  });

  it("zeigt fachlichen Fehlschlag mit übersetzter Fehlerart", () => {
    render(
      createElement(AutomatisierungErgebnis, {
        ergebnis: {
          ausfuehrung_id: "e2",
          fehlgeschlagen: true,
          ausgefuehrte_aktionen: 0,
          abgebrochen_bei_aktion_position: 1,
          fehlerart: "keine_geraeteantwort",
          nachweise: [{ nachweis_id: "n1", art: "rohantwort" }],
        },
      }),
    );
    expect(screen.getByText("Automatisierung fehlgeschlagen")).toBeTruthy();
    expect(screen.getByText("Keine Geräteantwort")).toBeTruthy();
    expect(screen.getByText(/Abbruch bei Position 1/)).toBeTruthy();
    expect(screen.getByText(/Neue Nachweise/)).toBeTruthy();
  });
});

describe("SchrittAutomatisierung", () => {
  it("rendert nichts ohne hat_automatisierung", () => {
    const { container } = wrap(
      createElement(SchrittAutomatisierung, {
        prueflaufId: "p1",
        schrittId: "s1",
        hatAutomatisierung: false,
        kannAusfuehren: false,
      }),
    );
    expect(container.querySelector('[data-testid="schritt-automatisierung"]')).toBeNull();
  });

  it("deaktiviert Button wenn kann_automatisierung_ausfuehren=false", () => {
    wrap(
      createElement(SchrittAutomatisierung, {
        prueflaufId: "p1",
        schrittId: "s1",
        hatAutomatisierung: true,
        kannAusfuehren: false,
      }),
    );
    expectDisabled(screen.getByRole("button", { name: /Automatisierung ausführen/ }), true);
  });

  it("führt Mutation aus und zeigt Erfolg", async () => {
    vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockResolvedValue({
      ausfuehrung_id: "e1",
      fehlgeschlagen: false,
      ausgefuehrte_aktionen: 1,
      abgebrochen_bei_aktion_position: null,
      fehlerart: null,
      nachweise: [{ nachweis_id: "n1", art: "rohantwort" }],
    });

    wrap(
      createElement(SchrittAutomatisierung, {
        prueflaufId: "p1",
        schrittId: "s1",
        hatAutomatisierung: true,
        kannAusfuehren: true,
        bezeichnung: "Spannung",
      }),
    );

    fireEvent.click(screen.getByRole("button", { name: /Automatisierung ausführen/ }));

    await waitFor(() => {
      expect(screen.getByTestId("automatisierung-ergebnis")).toBeTruthy();
    });
    expect(screen.getByText("Automatisierung erfolgreich")).toBeTruthy();
    expect(prueflaeufeApi.automatisierungAusfuehren).toHaveBeenCalledTimes(1);
    expect(prueflaeufeApi.automatisierungAusfuehren).toHaveBeenCalledWith("p1", "s1");
  });

  it("zeigt fachlichen Fehlschlag bei HTTP 200", async () => {
    vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockResolvedValue({
      ausfuehrung_id: "e2",
      fehlgeschlagen: true,
      ausgefuehrte_aktionen: 0,
      abgebrochen_bei_aktion_position: 1,
      fehlerart: "ungueltige_antwort",
      nachweise: [],
    });

    wrap(
      createElement(SchrittAutomatisierung, {
        prueflaufId: "p1",
        schrittId: "s1",
        hatAutomatisierung: true,
        kannAusfuehren: true,
      }),
    );

    fireEvent.click(screen.getByRole("button", { name: /Automatisierung ausführen/ }));
    await waitFor(() => {
      expect(screen.getByText("Automatisierung fehlgeschlagen")).toBeTruthy();
    });
    expect(screen.getByText(/nicht ausgewertet/)).toBeTruthy();
  });

  it("zeigt ApiErrorAlert bei 4xx", async () => {
    vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockRejectedValue(
      new ApiError("Keine Automatisierung", 409, "keine_automatisierung_am_schritt"),
    );

    wrap(
      createElement(SchrittAutomatisierung, {
        prueflaufId: "p1",
        schrittId: "s1",
        hatAutomatisierung: true,
        kannAusfuehren: true,
      }),
    );

    fireEvent.click(screen.getByRole("button", { name: /Automatisierung ausführen/ }));
    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeTruthy();
    });
    expect(screen.getByText("Keine Automatisierung")).toBeTruthy();
    expect(screen.queryByTestId("automatisierung-ergebnis")).toBeNull();
  });

  it("verhindert Doppelklick während Pending", async () => {
    let resolveFn: (value: unknown) => void = () => undefined;
    vi.mocked(prueflaeufeApi.automatisierungAusfuehren).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveFn = resolve as (value: unknown) => void;
        }),
    );

    wrap(
      createElement(SchrittAutomatisierung, {
        prueflaufId: "p1",
        schrittId: "s1",
        hatAutomatisierung: true,
        kannAusfuehren: true,
      }),
    );

    const button = screen.getByRole("button", { name: /Automatisierung ausführen/ });
    fireEvent.click(button);
    await waitFor(() => expectDisabled(button, true));
    fireEvent.click(button);
    expect(prueflaeufeApi.automatisierungAusfuehren).toHaveBeenCalledTimes(1);
    resolveFn({
      ausfuehrung_id: "e1",
      fehlgeschlagen: false,
      ausgefuehrte_aktionen: 1,
      abgebrochen_bei_aktion_position: null,
      fehlerart: null,
      nachweise: [],
    });
  });
});
