import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  aktivierenProfil,
  assignProfilZuBenutzer,
  createProfil,
  deaktivierenProfil,
  getProfil,
  listProfile,
  removeProfilVonBenutzer,
  updateProfil,
} from "@/adapters/api/identityQualification";
import type {
  ProfilAnlegenRequest,
  ProfilAktualisierenRequest,
} from "@/adapters/api/schemas/identity";
import {
  identityBenutzerProfileKey,
  identityProfilDetailKey,
  identityProfileKey,
} from "@/lib/identityQueryKeys";
import {
  loadBenutzerProfileIds,
  saveBenutzerProfileIds,
} from "@/lib/benutzerProfileCache";

export function useProfileQuery() {
  return useQuery({
    queryKey: identityProfileKey,
    queryFn: listProfile,
  });
}

export function useProfilDetailQuery(profilId: string) {
  return useQuery({
    queryKey: identityProfilDetailKey(profilId),
    queryFn: () => getProfil(profilId),
    enabled: Boolean(profilId),
  });
}

export function useCreateProfilMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ProfilAnlegenRequest) => createProfil(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: identityProfileKey }),
  });
}

export function useUpdateProfilMutation(profilId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ProfilAktualisierenRequest) => updateProfil(profilId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: identityProfileKey });
      queryClient.invalidateQueries({ queryKey: identityProfilDetailKey(profilId) });
    },
  });
}

export function useAktivierenProfilMutation(profilId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => aktivierenProfil(profilId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: identityProfileKey });
      queryClient.invalidateQueries({ queryKey: identityProfilDetailKey(profilId) });
    },
  });
}

export function useDeaktivierenProfilMutation(profilId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => deaktivierenProfil(profilId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: identityProfileKey });
      queryClient.invalidateQueries({ queryKey: identityProfilDetailKey(profilId) });
    },
  });
}

export function useBenutzerProfileIdsQuery(benutzerId: string) {
  return useQuery({
    queryKey: identityBenutzerProfileKey(benutzerId),
    queryFn: () => loadBenutzerProfileIds(benutzerId),
    enabled: Boolean(benutzerId),
    staleTime: Infinity,
  });
}

export function useAssignProfilMutation(benutzerId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (profilId: string) => assignProfilZuBenutzer(profilId, benutzerId),
    onSuccess: (_data, profilId) => {
      const key = identityBenutzerProfileKey(benutzerId);
      const current = queryClient.getQueryData<string[]>(key) ?? loadBenutzerProfileIds(benutzerId);
      const next = [...new Set([...current, profilId])];
      queryClient.setQueryData(key, next);
      saveBenutzerProfileIds(benutzerId, next);
    },
  });
}

export function useRemoveProfilMutation(benutzerId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (profilId: string) => removeProfilVonBenutzer(profilId, benutzerId),
    onSuccess: (_data, profilId) => {
      const key = identityBenutzerProfileKey(benutzerId);
      const current = queryClient.getQueryData<string[]>(key) ?? loadBenutzerProfileIds(benutzerId);
      const next = current.filter((id) => id !== profilId);
      queryClient.setQueryData(key, next);
      saveBenutzerProfileIds(benutzerId, next);
    },
  });
}
