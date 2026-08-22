import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  assignAutomatisierung,
  createEntwurf,
  createSchritt,
  deleteSchritt,
  getEntwurf,
  reorderSchritte,
  updateSchritt,
  veroeffentlichen,
} from "@/adapters/api/katalog";
import type {
  AutomatisierungZuweisenRequest,
  EntwurfAnlegenRequest,
  ReihenfolgeRequest,
  SchrittAktualisierenRequest,
  SchrittAnlegenRequest,
} from "@/adapters/api/schemas/katalog";
import { katalogEntwurfKey } from "@/lib/katalogQueryKeys";

export function useEntwurf(produktdefinitionId: string | undefined) {
  return useQuery({
    queryKey: katalogEntwurfKey(produktdefinitionId ?? ""),
    queryFn: () => getEntwurf(produktdefinitionId!),
    enabled: Boolean(produktdefinitionId),
  });
}

export function useEntwurfAnlegenMutation() {
  return useMutation({
    mutationFn: (body: EntwurfAnlegenRequest) => createEntwurf(body),
  });
}

export function useSchrittAnlegenMutation(produktdefinitionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: SchrittAnlegenRequest) => createSchritt(produktdefinitionId, body),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: katalogEntwurfKey(produktdefinitionId) }),
  });
}

export function useSchrittAktualisierenMutation(produktdefinitionId: string, schrittId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: SchrittAktualisierenRequest) =>
      updateSchritt(produktdefinitionId, schrittId, body),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: katalogEntwurfKey(produktdefinitionId) }),
  });
}

export function useSchrittLoeschenMutation(produktdefinitionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (schrittId: string) => deleteSchritt(produktdefinitionId, schrittId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: katalogEntwurfKey(produktdefinitionId) }),
  });
}

export function useSchritteReihenfolgeMutation(produktdefinitionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ReihenfolgeRequest) => reorderSchritte(produktdefinitionId, body),
    onSuccess: (data) => {
      queryClient.setQueryData(katalogEntwurfKey(produktdefinitionId), data);
    },
  });
}

export function useAutomatisierungZuweisenMutation(produktdefinitionId: string, schrittId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: AutomatisierungZuweisenRequest) =>
      assignAutomatisierung(produktdefinitionId, schrittId, body),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: katalogEntwurfKey(produktdefinitionId) }),
  });
}

export function useEntwurfVeroeffentlichenMutation(produktdefinitionId: string) {
  return useMutation({
    mutationFn: () => veroeffentlichen(produktdefinitionId),
  });
}
