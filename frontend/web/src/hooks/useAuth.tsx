import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { ApiError } from "@/adapters/api/client";
import { fetchMe, type MeResponse } from "@/adapters/api/auth";

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
