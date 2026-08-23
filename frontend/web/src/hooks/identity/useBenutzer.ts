import { QueryClient, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  aktivierenBenutzer,
  archivierenBenutzer,
  createBenutzer,
  entsperrenBenutzer,
  getBenutzer,
  listBenutzer,
  resetBenutzerPasswort,
  setBenutzerRollen,
  sperrenBenutzer,
  wiederherstellenBenutzer,
} from "@/adapters/api/identity";
import type { BenutzerAnlegenRequest } from "@/adapters/api/schemas/identity";
import {
  identityBenutzerDetailKey,
  identityBenutzerKey,
} from "@/lib/identityQueryKeys";

export function useBenutzerQuery() {
  return useQuery({
    queryKey: identityBenutzerKey,
    queryFn: listBenutzer,
  });
}

export function useBenutzerDetailQuery(benutzerId: string) {
  return useQuery({
    queryKey: identityBenutzerDetailKey(benutzerId),
    queryFn: () => getBenutzer(benutzerId),
    enabled: Boolean(benutzerId),
  });
}

function invalidateBenutzer(queryClient: QueryClient, benutzerId?: string) {
  queryClient.invalidateQueries({ queryKey: identityBenutzerKey });
  if (benutzerId) {
    queryClient.invalidateQueries({ queryKey: identityBenutzerDetailKey(benutzerId) });
  }
}

export function useCreateBenutzerMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: BenutzerAnlegenRequest) => createBenutzer(body),
    onSuccess: () => invalidateBenutzer(queryClient),
  });
}

function useBenutzerActionMutation(benutzerId: string, action: (id: string) => Promise<unknown>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => action(benutzerId),
    onSuccess: () => invalidateBenutzer(queryClient, benutzerId),
  });
}

export function useAktivierenBenutzerMutation(benutzerId: string) {
  return useBenutzerActionMutation(benutzerId, aktivierenBenutzer);
}

export function useSperrenBenutzerMutation(benutzerId: string) {
  return useBenutzerActionMutation(benutzerId, sperrenBenutzer);
}

export function useEntsperrenBenutzerMutation(benutzerId: string) {
  return useBenutzerActionMutation(benutzerId, entsperrenBenutzer);
}

export function useArchivierenBenutzerMutation(benutzerId: string) {
  return useBenutzerActionMutation(benutzerId, archivierenBenutzer);
}

export function useWiederherstellenBenutzerMutation(benutzerId: string) {
  return useBenutzerActionMutation(benutzerId, wiederherstellenBenutzer);
}

export function useSetBenutzerRollenMutation(benutzerId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (rollen: string[]) => setBenutzerRollen(benutzerId, { rollen }),
    onSuccess: () => invalidateBenutzer(queryClient, benutzerId),
  });
}

export function useResetBenutzerPasswortMutation(benutzerId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (passwort: string) => resetBenutzerPasswort(benutzerId, passwort),
    onSuccess: () => invalidateBenutzer(queryClient, benutzerId),
  });
}
