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

  it("erzeugt Blob-URL, öffnet per Anchor-Click und gibt URL nach Delay frei", () => {
    vi.useFakeTimers();
    const createObjectURL = vi.fn(() => "blob:protokoll-1");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL });

    const click = vi.fn();
    const anchor = {
      href: "",
      target: "",
      rel: "",
      click,
    } as unknown as HTMLAnchorElement;
    const createElement = vi.spyOn(document, "createElement").mockReturnValue(anchor);
    const appendChild = vi.spyOn(document.body, "appendChild").mockImplementation((node) => node);
    const removeChild = vi.spyOn(document.body, "removeChild").mockImplementation((node) => node);

    const blob = new Blob([new Uint8Array([1, 2, 3])], { type: "application/pdf" });
    openProtokollPdfInViewer(blob);

    expect(createObjectURL).toHaveBeenCalledWith(blob);
    expect(createElement).toHaveBeenCalledWith("a");
    expect(anchor.href).toBe("blob:protokoll-1");
    expect(anchor.target).toBe("_blank");
    expect(anchor.rel).toBe("noopener noreferrer");
    expect(appendChild).toHaveBeenCalledWith(anchor);
    expect(click).toHaveBeenCalledOnce();
    expect(removeChild).toHaveBeenCalledWith(anchor);
    expect(revokeObjectURL).not.toHaveBeenCalled();

    vi.advanceTimersByTime(60_000);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:protokoll-1");
    vi.useRealTimers();

    createElement.mockRestore();
    appendChild.mockRestore();
    removeChild.mockRestore();
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
