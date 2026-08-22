import { describe, expect, it } from "vitest";

import {
  findDuplicateFeldnamen,
  moveSchrittIds,
  parseOptionalNumber,
  rowsFromSollvorgaben,
  sollvorgabenFromRows,
} from "@/lib/entwurfEditor";

describe("entwurfEditor helpers", () => {
  it("parst und serialisiert Sollvorgaben", () => {
    const rows = rowsFromSollvorgaben({ spannung: { min: 220, max: 240 } });
    expect(rows).toHaveLength(1);
    const record = sollvorgabenFromRows(rows);
    expect(record).toEqual({ spannung: { min: 220, max: 240 } });
  });

  it("lässt leere Min/Max weg", () => {
    const record = sollvorgabenFromRows([{ feldname: "strom", min: "", max: "" }]);
    expect(record).toEqual({ strom: {} });
  });

  it("parst Zahlen", () => {
    expect(parseOptionalNumber("12.5")).toBe(12.5);
    expect(parseOptionalNumber("")).toBeUndefined();
    expect(parseOptionalNumber("abc")).toBeUndefined();
  });

  it("erkennt doppelte Feldnamen", () => {
    expect(
      findDuplicateFeldnamen([
        { feldname: "a", min: "", max: "" },
        { feldname: "a", min: "", max: "" },
      ]),
    ).toEqual(["a"]);
  });

  it("ignoriert leere Feldnamen", () => {
    expect(sollvorgabenFromRows([{ feldname: "  ", min: "1", max: "" }])).toEqual({});
  });

  it("verschiebt Schritt-IDs", () => {
    expect(moveSchrittIds(["s1", "s2", "s3"], 1, -1)).toEqual(["s2", "s1", "s3"]);
    expect(moveSchrittIds(["s1", "s2"], 0, -1)).toEqual(["s1", "s2"]);
    expect(moveSchrittIds(["s1", "s2"], 1, 1)).toEqual(["s1", "s2"]);
  });
});
