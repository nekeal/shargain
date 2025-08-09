import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { MonitoredUrl, OfferMonitor } from "@/types/dashboard";
import { shargainPublicApiApiActivateScrapingUrl, shargainPublicApiApiAddUrlToTarget, shargainPublicApiApiDeactivateScrapingUrl, shargainPublicApiApiDeleteTargetUrl, shargainPublicApiApiGetMyTarget } from "@/lib/api";

export const useGetMyTarget = () => {
    return useQuery<OfferMonitor>({
        queryKey: ['myTarget'],
        queryFn: () => shargainPublicApiApiGetMyTarget().then(response => response.data as OfferMonitor),
    });
};

export const useAddUrlMutation = (targetId: number) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (newUrl: { url: string, name?: string }) => shargainPublicApiApiAddUrlToTarget({ path: { target_id: targetId }, body: { url: newUrl.url, name: newUrl.name} }),
        onMutate: async (newUrl) => {
            await queryClient.cancelQueries({ queryKey: ['myTarget'] });
            const previousTarget = queryClient.getQueryData<OfferMonitor>(['myTarget']);
            if (previousTarget) {
                const newUrls: Array<MonitoredUrl> = [...previousTarget.urls, { ...newUrl, id: -1, isActive: true, name: newUrl.name || newUrl.url }];
                queryClient.setQueryData<OfferMonitor>(['myTarget'], { ...previousTarget, urls: newUrls });
            }
            return { previousTarget };
        },
        onError: (err, _, context) => {
            if (context?.previousTarget) {
                queryClient.setQueryData<OfferMonitor>(['myTarget'], context.previousTarget);
            }
            // Here you can add your error handling logic, e.g., show a toast notification
            console.error("Error adding URL:", err);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['myTarget'] });
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
