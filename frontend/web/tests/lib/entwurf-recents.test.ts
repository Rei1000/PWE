import { afterEach, describe, expect, it } from "vitest";

import {
  clearEntwurfRecentsForTests,
  loadEntwurfRecents,
  MAX_RECENTS,
  rememberEntwurfRecent,
} from "@/lib/entwurfRecents";

describe("entwurfRecents", () => {
  afterEach(() => {
    clearEntwurfRecentsForTests();
  });

  it("speichert nur Metadaten", () => {
    rememberEntwurfRecent({ produktdefinition_id: "pd-1", produktkodierung: "1234567890" });
    const recents = loadEntwurfRecents();
    expect(recents).toHaveLength(1);
    expect(recents[0]).toMatchObject({
      produktdefinition_id: "pd-1",
      produktkodierung: "1234567890",
    });
    expect(recents[0]?.zuletztGeoeffnet).toBeTruthy();
  });

  it("begrenzt Historie", () => {
    for (let i = 0; i < MAX_RECENTS + 2; i += 1) {
      rememberEntwurfRecent({
        produktdefinition_id: `pd-${i}`,
        produktkodierung: `kod-${i}`,
      });
    }
    expect(loadEntwurfRecents()).toHaveLength(MAX_RECENTS);
  });

  it("hebt Duplikate nach oben", () => {
    rememberEntwurfRecent({ produktdefinition_id: "pd-1", produktkodierung: "A" });
    rememberEntwurfRecent({ produktdefinition_id: "pd-2", produktkodierung: "B" });
    rememberEntwurfRecent({ produktdefinition_id: "pd-1", produktkodierung: "A" });
    const recents = loadEntwurfRecents();
    expect(recents[0]?.produktdefinition_id).toBe("pd-1");
    expect(recents).toHaveLength(2);
  });
});
