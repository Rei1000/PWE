import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createVorlage,
  deleteVorlage,
  listVorlagen,
  updateVorlage,
} from "@/adapters/api/bibliothek";
import type { VorlageCreateRequest, VorlageUpdateRequest } from "@/adapters/api/schemas/bibliothek";
import { katalogVorlagenKey } from "@/lib/katalogQueryKeys";

export function useVorlagenQuery() {
  return useQuery({
    queryKey: katalogVorlagenKey,
    queryFn: listVorlagen,
  });
}

export function useCreateVorlageMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: VorlageCreateRequest) => createVorlage(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogVorlagenKey }),
  });
}

export function useUpdateVorlageMutation(vorlageId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: VorlageUpdateRequest) => updateVorlage(vorlageId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogVorlagenKey }),
  });
}

export function useDeleteVorlageMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (vorlageId: string) => deleteVorlage(vorlageId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogVorlagenKey }),
  });
}
