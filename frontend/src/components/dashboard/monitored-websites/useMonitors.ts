import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { OfferMonitor } from "@/types/dashboard";
import type { FiltersConfigSchema } from "@/lib/api/types.gen";
import { activateScrapingUrl, addUrlToTarget, deactivateScrapingUrl, deleteTargetUrl, getMyTarget, updateScrapingUrlFilters } from "@/lib/api/sdk.gen";

export const useGetMyTarget = () => {
    return useQuery<OfferMonitor>({
        queryKey: ['myTarget'],
        queryFn: () => getMyTarget().then(response => response.data as OfferMonitor),
    });
};

export const useAddUrlMutation = (
    targetId: number,
) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (newUrl: { url: string, name?: string }) => addUrlToTarget({ path: { target_id: targetId }, body: { url: newUrl.url, name: newUrl.name } }).then(response => response.data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
        },
    });
};

export const useRemoveUrlMutation = (targetId: number) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (urlId: number) => deleteTargetUrl({ path: { target_id: targetId, url_id: urlId } }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
        },
    });
};

export const useToggleUrlActiveMutation = (targetId: number) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ urlId, isActive }: { urlId: number, isActive: boolean }) => {
            if (isActive) {
                return deactivateScrapingUrl({ path: { target_id: targetId, url_id: urlId } });
            }
            return activateScrapingUrl({ path: { target_id: targetId, url_id: urlId } });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
        },
    });
};

export const useUpdateFiltersMutation = (targetId: number, urlId: number) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (filters: FiltersConfigSchema | null) => {
            return updateScrapingUrlFilters({
                path: { target_id: targetId, url_id: urlId },
                body: { filters },
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
        },
    });
}
