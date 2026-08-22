import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ConfirmDialog } from "@/components/katalog/ConfirmDialog";

describe("ConfirmDialog", () => {
  it("ruft onConfirm bei Bestätigung auf", () => {
    const onConfirm = vi.fn();
    const onCancel = vi.fn();
    render(
      <ConfirmDialog
        open
        title="Löschen?"
        description="Wirklich löschen?"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Löschen" }));
    expect(onConfirm).toHaveBeenCalledOnce();
  });
});
