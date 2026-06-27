import { useQuery } from "@tanstack/react-query";

import { fetchHealth } from "@/adapters/api/health";

export function useHealthQuery(refetchIntervalMs?: number) {
  return useQuery({
    queryKey: ["health", refetchIntervalMs],
    queryFn: fetchHealth,
    refetchInterval: refetchIntervalMs,
  });
}
