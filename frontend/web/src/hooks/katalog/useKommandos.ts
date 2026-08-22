import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createKommando,
  deleteKommando,
  listKommandos,
  updateKommando,
} from "@/adapters/api/bibliothek";
import type { KommandoCreateRequest, KommandoUpdateRequest } from "@/adapters/api/schemas/bibliothek";
import { katalogKommandosKey } from "@/lib/katalogQueryKeys";

export function useKommandosQuery() {
  return useQuery({
    queryKey: katalogKommandosKey,
    queryFn: listKommandos,
  });
}

export function useCreateKommandoMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: KommandoCreateRequest) => createKommando(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogKommandosKey }),
  });
}

export function useUpdateKommandoMutation(kommandoId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: KommandoUpdateRequest) => updateKommando(kommandoId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogKommandosKey }),
  });
}

export function useDeleteKommandoMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (kommandoId: string) => deleteKommando(kommandoId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogKommandosKey }),
  });
}
