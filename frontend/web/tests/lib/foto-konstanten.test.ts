import { describe, expect, it } from "vitest";

import { MAX_FOTO_GROESSE_BYTES, validateFotoDatei } from "@/lib/fotoKonstanten";

describe("validateFotoDatei", () => {
  it("akzeptiert JPEG", () => {
    const file = new File([new Uint8Array(100)], "f.jpg", { type: "image/jpeg" });
    expect(validateFotoDatei(file)).toBeNull();
  });

  it("lehnt zu große Datei ab", () => {
    const file = new File([new Uint8Array(10)], "f.jpg", { type: "image/jpeg" });
    Object.defineProperty(file, "size", { value: MAX_FOTO_GROESSE_BYTES + 1 });
    expect(validateFotoDatei(file)).toContain("5 MiB");
  });

  it("lehnt unbekannten MIME ab", () => {
    const file = new File(["x"], "f.gif", { type: "image/gif" });
    expect(validateFotoDatei(file)).toContain("JPEG");
  });
});
