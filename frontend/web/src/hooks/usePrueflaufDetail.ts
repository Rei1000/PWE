import { useQuery } from "@tanstack/react-query";

import { fetchPrueflauf } from "@/adapters/api/prueflaeufe";
import { prueflaufQueryKey } from "@/lib/queryClient";

export function usePrueflaufDetail(prueflaufId: string) {
  return useQuery({
    queryKey: prueflaufQueryKey(prueflaufId),
    queryFn: () => fetchPrueflauf(prueflaufId),
    enabled: Boolean(prueflaufId),
  });
}
