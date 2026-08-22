import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createRoutine,
  deleteRoutine,
  getRoutine,
  listRoutinen,
  updateRoutine,
} from "@/adapters/api/bibliothek";
import type { RoutineCreateRequest, RoutineUpdateRequest } from "@/adapters/api/schemas/bibliothek";
import { katalogRoutineKey, katalogRoutinenKey } from "@/lib/katalogQueryKeys";

export function useRoutinenQuery() {
  return useQuery({
    queryKey: katalogRoutinenKey,
    queryFn: listRoutinen,
  });
}

export function useRoutineQuery(routineId: string | undefined) {
  return useQuery({
    queryKey: katalogRoutineKey(routineId ?? ""),
    queryFn: () => getRoutine(routineId!),
    enabled: Boolean(routineId),
  });
}

export function useCreateRoutineMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: RoutineCreateRequest) => createRoutine(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogRoutinenKey }),
  });
}

export function useUpdateRoutineMutation(routineId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: RoutineUpdateRequest) => updateRoutine(routineId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: katalogRoutinenKey });
      queryClient.invalidateQueries({ queryKey: katalogRoutineKey(routineId) });
    },
  });
}

export function useDeleteRoutineMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (routineId: string) => deleteRoutine(routineId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: katalogRoutinenKey }),
  });
}
