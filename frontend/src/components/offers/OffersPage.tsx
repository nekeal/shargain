import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useQueryClient } from "@tanstack/react-query";
import {
  ArrowUpDown,
  CheckCircle2,
  Filter,
  Heart,
  Inbox,
  RefreshCw,
  Search,
  X,
} from "lucide-react";
import {
  useOffersQuery,
  useToggleLikeMutation,
  useToggleSeenMutation,
} from "./useOffers";
import { OfferSplitReader } from "./OfferSplitReader";
import { OffersSkeleton } from "./OffersSkeleton";
import type { PublicOfferSchema } from "@/lib/api/types.gen";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  loadStoredTargetId,
  saveStoredTargetId,
} from "@/components/dashboard/DashboardShared";
import {
  useGetMyTarget,
  useGetTargets,
} from "@/components/dashboard/monitored-websites/useMonitors";
import { TargetSelectorInline } from "@/components/dashboard/target-selector-inline";

export interface OffersPageProps {
  initialTargetId?: number;
  onTargetChange?: (targetId: number) => void;
}

// Postgres `price` is int4; anything above this cannot be a valid bound.
const MAX_PRICE = 2_147_483_647;

function parsePriceInput(raw: string): number | undefined {
  // Prices are whole zloty; tolerate grouping whitespace (incl. NBSP variants).
  const normalised = raw.replace(/[\s\u00a0\u202f\u2009]/g, "");
  if (!/^\d+$/.test(normalised)) return undefined;
  const value = Number(normalised);
  return Number.isSafeInteger(value) && value <= MAX_PRICE ? value : undefined;
}

function isPriceInputInvalid(raw: string): boolean {
  return raw.trim() !== "" && parsePriceInput(raw) === undefined;
}

export function OffersPage({
  initialTargetId,
  onTargetChange,
}: OffersPageProps) {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<"unseen" | "liked" | "all">("unseen");
  const [ordering, setOrdering] = useState<"oldest" | "newest">("oldest");
  const [limit, setLimit] = useState<number>(50);

  const [selectedTargetId, setSelectedTargetId] = useState<number | null>(
    initialTargetId ?? loadStoredTargetId(),
  );

  // Raw filter input state (debounced into applied values below)
  const [searchInput, setSearchInput] = useState("");
  const [minPriceInput, setMinPriceInput] = useState("");
  const [maxPriceInput, setMaxPriceInput] = useState("");

  const searchInputRef = useRef<HTMLInputElement>(null);

  const [search, setSearch] = useState<string | undefined>();
  const [minPrice, setMinPrice] = useState<number | undefined>();
  const [maxPrice, setMaxPrice] = useState<number | undefined>();

  const queryClient = useQueryClient();

  const { data: targets } = useGetTargets();
  const { data: myTarget } = useGetMyTarget();

  // Debounce raw filter inputs into applied query values
  useEffect(() => {
    const timer = setTimeout(() => {
      const trimmedSearch = searchInput.trim();
      setSearch(trimmedSearch === "" ? undefined : trimmedSearch);
      setMinPrice(parsePriceInput(minPriceInput));
      setMaxPrice(parsePriceInput(maxPriceInput));
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, minPriceInput, maxPriceInput]);

  const hasActiveFilters =
    searchInput !== "" || minPriceInput !== "" || maxPriceInput !== "";

  const minPriceInvalid = isPriceInputInvalid(minPriceInput);
  const maxPriceInvalid = isPriceInputInvalid(maxPriceInput);
  const priceInvalid = minPriceInvalid || maxPriceInvalid;

  const handleClearFilters = useCallback(() => {
    setSearchInput("");
    setMinPriceInput("");
    setMaxPriceInput("");
    // Apply immediately; the pending debounce timer re-applies undefined (no-op).
    setSearch(undefined);
    setMinPrice(undefined);
    setMaxPrice(undefined);
    // The unfiltered result may already be cached, so refresh it explicitly.
    queryClient.invalidateQueries({ queryKey: ["offers", selectedTargetId] });
    searchInputRef.current?.focus();
  }, [queryClient, selectedTargetId]);

  // Reset pagination limit when target, tab, ordering or filters change
  useEffect(() => {
    setLimit(50);
  }, [selectedTargetId, activeTab, ordering, search, minPrice, maxPrice]);

  // Sync initialTargetId if changed externally
  useEffect(() => {
    if (initialTargetId) {
      setSelectedTargetId(initialTargetId);
      saveStoredTargetId(initialTargetId);
    }
  }, [initialTargetId]);

  // Pick target ID
  useEffect(() => {
    if (selectedTargetId === null) {
      if (targets && targets.length > 0) {
        setSelectedTargetId(targets[0].id);
        saveStoredTargetId(targets[0].id);
      } else if (myTarget) {
        setSelectedTargetId(myTarget.id);
        saveStoredTargetId(myTarget.id);
      }
    }
  }, [selectedTargetId, targets, myTarget]);

  const handleSelectTarget = useCallback(
    (targetId: number) => {
      setSelectedTargetId(targetId);
      saveStoredTargetId(targetId);
      onTargetChange?.(targetId);
    },
    [onTargetChange],
  );

  // Live queries & mutations
  const {
    data: liveOffersPage,
    isLoading: liveLoading,
    isFetching,
  } = useOffersQuery({
    targetId: selectedTargetId,
    tab: activeTab,
    ordering,
    limit,
    search,
    minPrice,
    maxPrice,
  });

  const toggleLikeMutation = useToggleLikeMutation(selectedTargetId);
  const toggleSeenMutation = useToggleSeenMutation(selectedTargetId);

  const handleToggleLike = useCallback(
    (offerId: number, currentlyLiked: boolean) => {
      toggleLikeMutation.mutate({ offerId, currentlyLiked });
    },
    [toggleLikeMutation],
  );

  const handleToggleSeen = useCallback(
    (offerId: number, currentlySeen: boolean) => {
      toggleSeenMutation.mutate({ offerId, currentlySeen });
    },
    [toggleSeenMutation],
  );

  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    queryClient
      .invalidateQueries({
        queryKey: ["offers", selectedTargetId],
      })
      .finally(() => {
        setTimeout(() => setIsRefreshing(false), 400);
      });
  }, [queryClient, selectedTargetId]);

  const displayedOffers: Array<PublicOfferSchema> = liveOffersPage?.items ?? [];
  const totalCount = liveOffersPage?.count ?? displayedOffers.length;
  const hasMore = totalCount > displayedOffers.length;

  const handleLoadMore = useCallback(() => {
    setLimit((prev) => prev + 50);
  }, []);

  const isBusy = isRefreshing || liveLoading || isFetching;
  const isLoadingOffers =
    liveLoading || (isFetching && displayedOffers.length === 0);

  return (
    <div className="min-h-screen bg-secondary pb-3 flex flex-col">
      <main className="container mx-auto px-3 sm:px-4 py-2 sm:py-3 max-w-[1700px] space-y-2.5 flex-1 flex flex-col min-h-0">
        {/* Header with Title */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 bg-primary/10 text-primary rounded-lg shrink-0">
              <Inbox className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground leading-tight">
                {t("offers.title")}
              </h1>
              <p className="text-xs text-muted-foreground">
                {t("offers.subtitle")}
              </p>
            </div>
          </div>
        </div>

        {/* Filter Controls Bar (Consolidated with Target Selector) */}
        <div className="bg-card border border-border rounded-xl px-3 py-2 flex flex-wrap items-center justify-between gap-2.5 sm:gap-3 shadow-sm">
          {/* Group 1: Tabs + Target Selector */}
          <div className="flex flex-wrap items-center gap-2.5 sm:gap-3">
            <Tabs
              value={activeTab}
              onValueChange={(val) =>
                setActiveTab(val as "unseen" | "liked" | "all")
              }
            >
              <TabsList className="bg-muted/70 h-8">
                <TabsTrigger value="unseen" className="gap-1.5 text-xs h-7 px-2.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-primary" />
                  <span>{t("offers.tabs.unseen")}</span>
                </TabsTrigger>
                <TabsTrigger value="liked" className="gap-1.5 text-xs h-7 px-2.5">
                  <Heart className="w-3.5 h-3.5 text-red-500" />
                  <span>{t("offers.tabs.liked")}</span>
                </TabsTrigger>
                <TabsTrigger value="all" className="gap-1.5 text-xs h-7 px-2.5">
                  <Filter className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>{t("offers.tabs.all")}</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Target Selector Inline when multiple targets */}
            {targets && targets.length > 1 && (
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-muted-foreground whitespace-nowrap">
                  {t("offers.targetLabel")}
                </span>
                <TargetSelectorInline
                  targets={targets}
                  selectedTargetId={selectedTargetId}
                  onSelect={handleSelectTarget}
                />
              </div>
            )}
          </div>

          {/* Group 2: Inline title search & price range */}
          <div
            role="group"
            aria-label={t("offers.filters.groupLabel")}
            className="flex flex-wrap items-center gap-2"
          >
            <div className="relative flex items-center">
              <Search className="absolute left-2.5 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
              <Input
                ref={searchInputRef}
                value={searchInput}
                onChange={(event) => setSearchInput(event.target.value)}
                aria-label={t("offers.filters.searchLabel")}
                placeholder={t("offers.filters.searchPlaceholder")}
                className="h-8 pl-8 pr-2 text-xs w-full sm:w-48 md:w-56 lg:w-64"
              />
            </div>

            <div className="flex items-center gap-1.5">
              <Input
                value={minPriceInput}
                onChange={(event) => setMinPriceInput(event.target.value)}
                inputMode="numeric"
                aria-label={t("offers.filters.minPriceLabel")}
                aria-invalid={minPriceInvalid || undefined}
                aria-describedby={
                  minPriceInvalid ? "offers-price-hint" : undefined
                }
                placeholder={t("offers.filters.minPrice")}
                className={`h-8 w-24 sm:w-28 text-xs${
                  minPriceInvalid
                    ? " border-destructive ring-1 ring-destructive/40"
                    : ""
                }`}
              />
              <span aria-hidden="true" className="text-xs text-muted-foreground select-none">
                –
              </span>
              <Input
                value={maxPriceInput}
                onChange={(event) => setMaxPriceInput(event.target.value)}
                inputMode="numeric"
                aria-label={t("offers.filters.maxPriceLabel")}
                aria-invalid={maxPriceInvalid || undefined}
                aria-describedby={
                  maxPriceInvalid ? "offers-price-hint" : undefined
                }
                placeholder={t("offers.filters.maxPrice")}
                className={`h-8 w-24 sm:w-28 text-xs${
                  maxPriceInvalid
                    ? " border-destructive ring-1 ring-destructive/40"
                    : ""
                }`}
              />
              <span className="text-xs text-muted-foreground font-medium select-none">
                {t("offers.filters.currency", "zł")}
              </span>
            </div>

            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearFilters}
                className="h-8 text-xs px-2 text-muted-foreground hover:text-foreground cursor-pointer"
                title={t("offers.filters.clear")}
                aria-label={t("offers.filters.clear")}
              >
                <X className="w-3.5 h-3.5" />
              </Button>
            )}
            {priceInvalid && (
              <span
                id="offers-price-hint"
                className="text-[11px] text-destructive whitespace-nowrap"
              >
                {t("offers.filters.invalidPrice")}
              </span>
            )}
          </div>

          {/* Group 3: Ordering & Count & Refresh */}
          <div className="flex items-center gap-2.5 sm:gap-3 ml-auto sm:ml-0">
            <span className="text-xs text-muted-foreground">
              {totalCount > displayedOffers.length
                ? t("offers.resultsCountWithTotal", {
                    count: displayedOffers.length,
                    total: totalCount,
                  })
                : t("offers.resultsCount", {
                    count: displayedOffers.length,
                  })}
            </span>

            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setOrdering(ordering === "oldest" ? "newest" : "oldest")
              }
              className="h-8 text-xs gap-1.5 px-2.5 cursor-pointer"
            >
              <ArrowUpDown className="w-3 h-3 text-muted-foreground" />
              <span>
                {t("offers.ordering.label")}{" "}
                <strong className="text-foreground">
                  {ordering === "oldest"
                    ? t("offers.ordering.oldest")
                    : t("offers.ordering.newest")}
                </strong>
              </span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              className="h-8 text-xs gap-1.5 px-2.5 text-muted-foreground hover:text-foreground hover:border-primary/50 cursor-pointer"
              title={t("offers.actions.refreshServer")}
              aria-label={t("offers.actions.refreshServer")}
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${
                  isBusy ? "animate-spin text-primary" : ""
                }`}
              />
              <span className="hidden sm:inline">{t("offers.actions.refresh")}</span>
            </Button>
          </div>
        </div>

        {/* Loading skeleton while initial offers are loading */}
        {isLoadingOffers ? (
          <OffersSkeleton />
        ) : (
          /* Active SplitReader View */
          <div className="flex-1 min-h-0 flex flex-col">
            <OfferSplitReader
              offers={displayedOffers}
              onToggleLike={handleToggleLike}
              onToggleSeen={handleToggleSeen}
              onRefresh={handleRefresh}
              isRefreshing={isBusy}
              hasMore={hasMore}
              onLoadMore={handleLoadMore}
              isLoadingMore={isFetching && displayedOffers.length > 0}
              isLoading={isLoadingOffers}
              totalCount={totalCount}
            />
          </div>
        )}
      </main>
    </div>
  );
}
