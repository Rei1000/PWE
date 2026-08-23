import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { ApiError } from "@/adapters/api/client";
import { fetchMe, type MeResponse } from "@/adapters/api/auth";
import { darfIdentityLesen } from "@/lib/identityRoles";

export const ME_QUERY_KEY = ["auth", "me"] as const;

export function useCurrentUser() {
  return useQuery({
    queryKey: ME_QUERY_KEY,
    queryFn: fetchMe,
    retry: false,
    staleTime: 30_000,
  });
}

export function useInvalidateSession() {
  const qc = useQueryClient();
  return () => qc.removeQueries({ queryKey: ME_QUERY_KEY });
}

/** Nur eingeloggt / nicht eingeloggt — keine Rollen-Guards (Gate 8.1a). */
export function RequireAuth() {
  const location = useLocation();
  const { data, isLoading, isError, error } = useCurrentUser();

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Sitzung wird geladen…</p>;
  }

  const unauthorized =
    isError && error instanceof ApiError && (error.status === 401 || error.status === 403);

  if (unauthorized || !data) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet context={{ user: data satisfies MeResponse }} />;
}

/** Blockiert alle Routen außer Passwort-Änderung bei erzwungenem Passwortwechsel. */
export function RequireNoForceChange() {
  const location = useLocation();
  const { data } = useCurrentUser();

  if (data?.passwortwechsel_erforderlich) {
    return <Navigate to="/passwort-aendern" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}

/** Verwaltungsbereich — nur Admin, QM, Abteilungsleiter (ADR-0025). */
export function RequireIdentityAccess() {
  const { data } = useCurrentUser();

  if (!darfIdentityLesen(data)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
