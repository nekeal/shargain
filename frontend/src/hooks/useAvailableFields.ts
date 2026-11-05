import { useQuery } from "@tanstack/react-query";
import type { AvailableFieldsResponse } from "@/lib/api/types.gen";
import { getAvailableFields } from "@/lib/api/sdk.gen";

export function useAvailableFields(urlId: number | null) {
    return useQuery<AvailableFieldsResponse>({
        queryKey: ['availableFields', urlId],
        queryFn: () => getAvailableFields({ path: { url_id: urlId! } }).then(r => r.data),
        enabled: urlId !== null,
        staleTime: 60_000,
    });
}
