import { Outlet } from "react-router-dom";

import { KatalogSetupBanner } from "@/components/katalog/KatalogSetupBanner";
import { KatalogSubNav } from "@/components/katalog/KatalogSubNav";

export function KatalogLayout() {
  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <KatalogSetupBanner />
      <KatalogSubNav />
      <Outlet />
    </div>
  );
}
