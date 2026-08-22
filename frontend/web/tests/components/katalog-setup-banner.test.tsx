import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { KatalogSetupBanner } from "@/components/katalog/KatalogSetupBanner";

describe("KatalogSetupBanner", () => {
  it("zeigt Labor-/Setup-Kennzeichnung", () => {
    render(<KatalogSetupBanner />);
    const banner = screen.getByTestId("katalog-setup-banner");
    expect(banner.textContent).toContain("Katalog-Setup / Laborbetrieb");
    expect(screen.getByText(/ohne Authentifizierung/i)).toBeDefined();
  });
});
