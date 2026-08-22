import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { KatalogHubPage } from "@/pages/katalog/KatalogHubPage";

describe("KatalogHubPage", () => {
  it("verlinkt alle Bibliotheksbereiche", () => {
    render(
      <MemoryRouter>
        <KatalogHubPage />
      </MemoryRouter>,
    );

    const links = screen.getAllByRole("link", { name: /Verwalten/i });
    expect(links).toHaveLength(3);
    expect(links[0]?.getAttribute("href")).toBe("/katalog/kommandos");
  });
});
