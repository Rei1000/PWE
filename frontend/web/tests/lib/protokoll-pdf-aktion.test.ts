import { afterEach, describe, expect, it, vi } from "vitest";

import {
  downloadProtokollPdfBlob,
  openProtokollPdfInViewer,
} from "@/lib/protokollPdfAktion";

describe("openProtokollPdfInViewer", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("erzeugt Blob-URL, öffnet Tab und gibt URL nach Delay frei", () => {
    vi.useFakeTimers();
    const createObjectURL = vi.fn(() => "blob:protokoll-1");
    const revokeObjectURL = vi.fn();
    const open = vi.fn(() => ({ closed: false }));
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL });
    vi.stubGlobal("window", { ...window, open });

    const blob = new Blob([new Uint8Array([1, 2, 3])], { type: "application/pdf" });
    const result = openProtokollPdfInViewer(blob);

    expect(result.ok).toBe(true);
    expect(createObjectURL).toHaveBeenCalledWith(blob);
    expect(open).toHaveBeenCalledWith("blob:protokoll-1", "_blank", "noopener,noreferrer");
    expect(revokeObjectURL).not.toHaveBeenCalled();

    vi.advanceTimersByTime(60_000);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:protokoll-1");
    vi.useRealTimers();
  });

  it("revoked sofort und meldet Fehler wenn Popup blockiert", () => {
    const createObjectURL = vi.fn(() => "blob:blocked");
    const revokeObjectURL = vi.fn();
    const open = vi.fn(() => null);
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL });
    vi.stubGlobal("window", { ...window, open });

    const blob = new Blob([new Uint8Array([1])], { type: "application/pdf" });
    const result = openProtokollPdfInViewer(blob);

    expect(result.ok).toBe(false);
    expect(result.reason).toBe("popup_blocked");
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:blocked");
  });
});

describe("downloadProtokollPdfBlob", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("erzeugt Download-Link und revoked Blob-URL", () => {
    const createObjectURL = vi.fn(() => "blob:download-1");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL });

    const click = vi.fn();
    const anchor = {
      href: "",
      download: "",
      click,
    } as unknown as HTMLAnchorElement;
    const createElement = vi.spyOn(document, "createElement").mockReturnValue(anchor);

    const blob = new Blob([new Uint8Array([9])], { type: "application/pdf" });
    downloadProtokollPdfBlob(blob, "protokoll-abc.pdf");

    expect(createObjectURL).toHaveBeenCalledWith(blob);
    expect(anchor.href).toBe("blob:download-1");
    expect(anchor.download).toBe("protokoll-abc.pdf");
    expect(click).toHaveBeenCalledOnce();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:download-1");
    createElement.mockRestore();
  });
});
