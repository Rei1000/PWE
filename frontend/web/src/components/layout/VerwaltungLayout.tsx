import { Outlet } from "react-router-dom";

import { IdentitySubNav } from "@/components/identity/IdentitySubNav";

export function VerwaltungLayout() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Verwaltung</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Benutzer, Berechtigungsprofile und Einweisungen.
        </p>
      </div>
      <IdentitySubNav />
      <Outlet />
    </div>
  );
}
