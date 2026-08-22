import { fireEvent, render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SollvorgabenEditor } from "@/components/katalog/SollvorgabenEditor";

describe("SollvorgabenEditor", () => {
  it("fügt Zeile hinzu und serialisiert Min/Max", () => {
    const onChange = vi.fn();
    const { getByRole, getByLabelText } = render(<SollvorgabenEditor value={{}} onChange={onChange} />);

    fireEvent.click(getByRole("button", { name: /Zeile hinzufügen/i }));
    fireEvent.change(getByLabelText("Feldname"), { target: { value: "spannung" } });
    fireEvent.change(getByLabelText("Min (optional)"), { target: { value: "220" } });
    fireEvent.change(getByLabelText("Max (optional)"), { target: { value: "240" } });

    expect(onChange).toHaveBeenCalled();
    const last = onChange.mock.calls.at(-1)?.[0] as Record<string, { min?: number; max?: number }>;
    expect(last).toEqual({ spannung: { min: 220, max: 240 } });
  });

  it("meldet doppelte Feldnamen", () => {
    const onChange = vi.fn();
    const { getByRole, getAllByLabelText, getByText } = render(
      <SollvorgabenEditor value={{}} onChange={onChange} />,
    );

    fireEvent.click(getByRole("button", { name: /Zeile hinzufügen/i }));
    fireEvent.click(getByRole("button", { name: /Zeile hinzufügen/i }));
    const fields = getAllByLabelText("Feldname");
    fireEvent.change(fields[0]!, { target: { value: "a" } });
    fireEvent.change(fields[1]!, { target: { value: "a" } });

    expect(getByText(/Doppelte Feldnamen/i)).toBeTruthy();
  });
});
