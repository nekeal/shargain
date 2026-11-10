import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { TFunction } from "i18next";
import type {
  PublicOfferPageSchema,
} from "@/lib/api/types.gen";
import {
  getTargetOffers,
  likeOffer,
  markOfferSeen,
  markOfferUnseen,
  unlikeOffer,
} from "@/lib/api/sdk.gen";

export interface OfferFilters {
  tab?: "all" | "unseen" | "liked";
  ordering?: "oldest" | "newest";
  limit?: number;
  offset?: number;
}

export function useOffersQuery({
  targetId,
  tab = "unseen",
  ordering = "oldest",
  limit = 50,
  offset = 0,
  enabled = true,
}: {
  targetId: number | null;
  tab?: "all" | "unseen" | "liked";
  ordering?: "oldest" | "newest";
  limit?: number;
  offset?: number;
  enabled?: boolean;
}) {
  const seenParam = tab === "unseen" ? false : undefined;
  const likedParam = tab === "liked" ? true : undefined;

  return useQuery<PublicOfferPageSchema>({
    queryKey: ["offers", targetId, tab, ordering, limit, offset],
    queryFn: async () => {
      if (!targetId) {
        return { count: 0, items: [] };
      }
      const response = await getTargetOffers({
        path: { target_id: targetId },
        query: {
          seen: seenParam,
          liked: likedParam,
          ordering,
          limit,
          offset,
        },
      });
      return response.data;
    },
    enabled: enabled && targetId !== null,
    staleTime: 15_000,
  });
}

export function useToggleLikeMutation(targetId: number | null) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      offerId,
      currentlyLiked,
    }: {
      offerId: number;
      currentlyLiked: boolean;
    }) => {
      if (!targetId) return null;
      if (currentlyLiked) {
        const res = await unlikeOffer({
          path: { target_id: targetId, offer_id: offerId },
        });
        return res.data;
      } else {
        const res = await likeOffer({
          path: { target_id: targetId, offer_id: offerId },
        });
        return res.data;
      }
    },
    onMutate: async ({ offerId, currentlyLiked }) => {
      await queryClient.cancelQueries({ queryKey: ["offers"] });
      const previousData = queryClient.getQueriesData<PublicOfferPageSchema>({
        queryKey: ["offers", targetId],
      });

      queryClient.setQueriesData<PublicOfferPageSchema>(
        { queryKey: ["offers", targetId] },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.map((item) =>
              item.id === offerId
                ? {
                    ...item,
                    isLiked: !currentlyLiked,
                    likedAt: !currentlyLiked ? new Date().toISOString() : null,
                  }
                : item,
            ),
          };
        },
      );

      return { previousData };
    },
    onError: (_err, _vars, context) => {
      if (context?.previousData) {
        context.previousData.forEach(([key, data]) => {
          queryClient.setQueryData(key, data);
        });
      }
    },
  });
}

export function useToggleSeenMutation(targetId: number | null) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      offerId,
      currentlySeen,
    }: {
      offerId: number;
      currentlySeen: boolean;
    }) => {
      if (!targetId) return null;
      if (currentlySeen) {
        const res = await markOfferUnseen({
          path: { target_id: targetId, offer_id: offerId },
        });
        return res.data;
      } else {
        const res = await markOfferSeen({
          path: { target_id: targetId, offer_id: offerId },
        });
        return res.data;
      }
    },
    onMutate: async ({ offerId, currentlySeen }) => {
      await queryClient.cancelQueries({ queryKey: ["offers"] });
      const previousData = queryClient.getQueriesData<PublicOfferPageSchema>({
        queryKey: ["offers", targetId],
      });

      queryClient.setQueriesData<PublicOfferPageSchema>(
        { queryKey: ["offers", targetId] },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.map((item) =>
              item.id === offerId
                ? {
                    ...item,
                    isSeen: !currentlySeen,
                    seenAt: !currentlySeen ? new Date().toISOString() : null,
                  }
                : item,
            ),
          };
        },
      );

      return { previousData };
    },
    onError: (_err, _vars, context) => {
      if (context?.previousData) {
        context.previousData.forEach(([key, data]) => {
          queryClient.setQueryData(key, data);
        });
      }
    },
  });
}

const priceFormatters = new Map<string, Intl.NumberFormat>();
const dateFormatters = new Map<string, Intl.DateTimeFormat>();

function resolveLocale(t?: TFunction): string {
  if (t && "i18n" in t) {
    const i18nObj = (t as unknown as { i18n: { resolvedLanguage?: string; language?: string } }).i18n;
    const lang = i18nObj.resolvedLanguage || i18nObj.language;
    if (lang) {
      return lang.startsWith("en") ? "en-US" : "pl-PL";
    }
  }
  if (typeof window !== "undefined") {
    const stored = window.localStorage.getItem("i18nextLng");
    if (stored?.startsWith("en")) return "en-US";
  }
  return "pl-PL";
}

function getPriceFormatter(locale: string): Intl.NumberFormat {
  let formatter = priceFormatters.get(locale);
  if (!formatter) {
    formatter = new Intl.NumberFormat(locale, {
      style: "currency",
      currency: "PLN",
      maximumFractionDigits: 0,
    });
    priceFormatters.set(locale, formatter);
  }
  return formatter;
}

function getDateFormatter(locale: string): Intl.DateTimeFormat {
  let formatter = dateFormatters.get(locale);
  if (!formatter) {
    formatter = new Intl.DateTimeFormat(locale, {
      day: "numeric",
      month: "short",
    });
    dateFormatters.set(locale, formatter);
  }
  return formatter;
}

export function formatPrice(
  price: number | null | undefined,
  t?: TFunction,
): string {
  if (price === null || price === undefined) {
    return t ? t("offers.detail.unknownPrice") : "Zapytaj o cenę";
  }
  const locale = resolveLocale(t);
  return getPriceFormatter(locale).format(price);
}

export function formatTimeAgo(
  isoString: string,
  t?: TFunction,
): string {
  try {
    const date = new Date(isoString);
    const now = Date.now();
    const diffSec = Math.floor((now - date.getTime()) / 1000);

    if (diffSec < 60) return t ? t("offers.time.justNow") : "Przed chwilą";
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) {
      return t
        ? t("offers.time.minutesAgo", { count: diffMin })
        : `${diffMin} min temu`;
    }
    const diffHours = Math.floor(diffMin / 60);
    if (diffHours < 24) {
      return t
        ? t("offers.time.hoursAgo", { count: diffHours })
        : `${diffHours} godz. temu`;
    }
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) {
      return t
        ? t("offers.time.daysAgo", { count: diffDays })
        : `${diffDays} dni temu`;
    }

    const locale = resolveLocale(t);
    return getDateFormatter(locale).format(date);
  } catch {
    return isoString;
  }
}
