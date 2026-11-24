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
        <div className="bg-card border border-border rounded-xl p-2 sm:px-3 sm:py-2 shadow-xs flex flex-col xl:flex-row xl:items-center justify-between gap-2.5">
          {/* Left Area: View Triage (Tabs + Target Selector) + Filter Controls (Search + Price) */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-2.5 flex-1 min-w-0">
            {/* Tabs: Unseen, Liked, All */}
            <Tabs
              value={activeTab}
              onValueChange={(val) =>
                setActiveTab(val as "unseen" | "liked" | "all")
              }
            >
              <TabsList className="bg-muted/70 p-0.5 h-8">
                <TabsTrigger value="unseen" className="gap-1.5 text-xs h-7 px-2.5 font-medium cursor-pointer">
                  <CheckCircle2 className="w-3.5 h-3.5 text-primary" />
                  <span>{t("offers.tabs.unseen")}</span>
                </TabsTrigger>
                <TabsTrigger value="liked" className="gap-1.5 text-xs h-7 px-2.5 font-medium cursor-pointer">
                  <Heart
                    className={`w-3.5 h-3.5 ${
                      activeTab === "liked"
                        ? "fill-red-500 text-red-500"
                        : "text-muted-foreground"
                    }`}
                  />
                  <span>{t("offers.tabs.liked")}</span>
                </TabsTrigger>
                <TabsTrigger value="all" className="gap-1.5 text-xs h-7 px-2.5 font-medium cursor-pointer">
                  <Filter className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>{t("offers.tabs.all")}</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Target Selector Inline when multiple targets */}
            {targets && targets.length > 1 && (
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium text-muted-foreground whitespace-nowrap hidden sm:inline">
                  {t("offers.targetLabel")}
                </span>
                <TargetSelectorInline
                  targets={targets}
                  selectedTargetId={selectedTargetId}
                  onSelect={handleSelectTarget}
                  className="h-8 text-xs min-w-[150px] sm:min-w-[175px] max-w-[220px]"
                />
              </div>
            )}

            {/* Subtle separator between view scope and query filters */}
            <div
              className="hidden md:block h-4 w-px bg-border/80 self-center mx-0.5"
              aria-hidden="true"
            />

            {/* Query Filter Controls */}
            <div
              role="group"
              aria-label={t("offers.filters.groupLabel")}
              className="flex flex-wrap items-center gap-2"
            >
              {/* Title Search */}
              <div className="relative flex items-center">
                <Search className="absolute left-2.5 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
                <Input
                  ref={searchInputRef}
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  aria-label={t("offers.filters.searchLabel")}
                  placeholder={t("offers.filters.searchPlaceholder")}
                  className="h-8 pl-8 pr-7 text-xs w-44 sm:w-52 md:w-56 lg:w-60 bg-background/60 shadow-2xs focus-visible:bg-background transition-colors"
                />
                {searchInput !== "" && (
                  <button
                    type="button"
                    onClick={() => {
                      setSearchInput("");
                      setSearch(undefined);
                      searchInputRef.current?.focus();
                    }}
                    className="absolute right-2 p-0.5 rounded-full text-muted-foreground hover:text-foreground hover:bg-muted transition-colors cursor-pointer"
                    title={t("offers.filters.clearSearch")}
                    aria-label={t("offers.filters.clearSearch")}
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>

              {/* Price Range Segmented Group */}
              <div
                className={`flex items-center h-8 rounded-md border bg-background/60 px-2 shadow-2xs transition-[border-color,box-shadow] ${
                  priceInvalid
                    ? "border-destructive ring-1 ring-destructive/40"
                    : "border-input hover:border-input/80 focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/20 focus-within:bg-background"
                }`}
              >
                <span className="text-[11px] font-medium text-muted-foreground select-none mr-1.5 hidden sm:inline">
                  {t("offers.filters.priceLabel", "Cena:")}
                </span>
                <input
                  value={minPriceInput}
                  onChange={(event) => setMinPriceInput(event.target.value)}
                  inputMode="numeric"
                  aria-label={t("offers.filters.minPriceLabel")}
                  aria-invalid={minPriceInvalid || undefined}
                  aria-describedby={
                    minPriceInvalid ? "offers-price-hint" : undefined
                  }
                  placeholder={t("offers.filters.minPrice")}
                  className="h-full w-12 sm:w-14 bg-transparent text-xs text-foreground placeholder:text-muted-foreground/60 outline-none text-right font-medium"
                />
                <span
                  aria-hidden="true"
                  className="mx-1 text-xs text-muted-foreground/50 select-none"
                >
                  –
                </span>
                <input
                  value={maxPriceInput}
                  onChange={(event) => setMaxPriceInput(event.target.value)}
                  inputMode="numeric"
                  aria-label={t("offers.filters.maxPriceLabel")}
                  aria-invalid={maxPriceInvalid || undefined}
                  aria-describedby={
                    maxPriceInvalid ? "offers-price-hint" : undefined
                  }
                  placeholder={t("offers.filters.maxPrice")}
                  className="h-full w-12 sm:w-14 bg-transparent text-xs text-foreground placeholder:text-muted-foreground/60 outline-none text-left font-medium"
                />
                <span className="ml-1 text-[11px] font-medium text-muted-foreground select-none">
                  {t("offers.filters.currency", "zł")}
                </span>
              </div>

              {/* Clear All Filters Button */}
              {hasActiveFilters && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearFilters}
                  className="h-8 text-xs px-2.5 text-muted-foreground hover:text-foreground hover:bg-muted/80 rounded-lg gap-1.5 cursor-pointer shrink-0"
                  title={t("offers.filters.clear")}
                  aria-label={t("offers.filters.clear")}
                >
                  <X className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">
                    {t("offers.filters.clear")}
                  </span>
                </Button>
              )}

              {priceInvalid && (
                <span
                  id="offers-price-hint"
                  className="text-[11px] font-medium text-destructive whitespace-nowrap animate-in fade-in"
                >
                  {t("offers.filters.invalidPrice")}
                </span>
              )}
            </div>
          </div>

          {/* Right Area: Results Count, Ordering Toggle, Refresh */}
          <div className="flex items-center justify-between xl:justify-end gap-2 sm:gap-2.5 pt-1.5 xl:pt-0 border-t border-border/40 xl:border-t-0 shrink-0">
            <span className="text-xs text-muted-foreground font-medium px-2 py-1 rounded-md bg-muted/40 border border-border/40 whitespace-nowrap select-none">
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
              className="h-8 text-xs gap-1.5 px-2.5 cursor-pointer shadow-2xs hover:bg-accent hover:text-accent-foreground"
            >
              <ArrowUpDown className="w-3 h-3 text-muted-foreground" />
              <span>
                {t("offers.ordering.label")}{" "}
                <strong className="text-foreground font-semibold">
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
              disabled={isBusy}
              className="h-8 text-xs gap-1.5 px-2.5 text-muted-foreground hover:text-foreground hover:border-primary/50 cursor-pointer shadow-2xs"
              title={t("offers.actions.refreshServer")}
              aria-label={t("offers.actions.refreshServer")}
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${
                  isBusy ? "animate-spin text-primary" : ""
                }`}
              />
              <span className="hidden sm:inline">
                {t("offers.actions.refresh")}
              </span>
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
