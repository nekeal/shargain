import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { OfferMonitor } from "@/types/dashboard";
import { shargainPublicApiApiActivateScrapingUrl, shargainPublicApiApiAddUrlToTarget, shargainPublicApiApiDeactivateScrapingUrl, shargainPublicApiApiDeleteTargetUrl, shargainPublicApiApiGetMyTarget } from "@/lib/api";

export const useGetMyTarget = () => {
    return useQuery<OfferMonitor>({
        queryKey: ['myTarget'],
        queryFn: () => shargainPublicApiApiGetMyTarget().then(response => response.data as OfferMonitor),
    });
};

export const useAddUrlMutation = (
    targetId: number,
) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (newUrl: { url: string, name?: string }) => shargainPublicApiApiAddUrlToTarget({ path: { target_id: targetId }, body: { url: newUrl.url, name: newUrl.name } }).then(response => {
            if (response.error) {
                console.error("Error adding URL:", response.error);
                return Promise.reject(response.error);
            }
            return response.data;
        }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
        },
        onError(error) {
            console.error("Error adding URL:", error);
        },
    });
};

export const useRemoveUrlMutation = (targetId: number) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (urlId: number) => shargainPublicApiApiDeleteTargetUrl({ path: { target_id: targetId, url_id: urlId } }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
        },
        onError: (err) => {
            console.error("Error removing URL:", err);
        }
    });
};

export const useToggleUrlActiveMutation = (targetId: number) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ urlId, isActive }: { urlId: number, isActive: boolean }) => {
            if (isActive) {
                return shargainPublicApiApiDeactivateScrapingUrl({ path: { target_id: targetId, url_id: urlId } });
            }
            return shargainPublicApiApiActivateScrapingUrl({ path: { target_id: targetId, url_id: urlId } });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
        },
        onError: (err) => {
            console.error("Error toggling URL active state:", err);
        }
    });
};
