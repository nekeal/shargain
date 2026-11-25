import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useQueryClient } from "@tanstack/react-query";
import {
  ArrowUpDown,
  CheckCircle2,
  ChevronDown,
  Filter,
  Heart,
  Inbox,
  RefreshCw,
  Search,
  SlidersHorizontal,
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
import cn from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Separator } from "@/components/ui/separator";
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
      setSearch(searchInput.trim() || undefined);
      setMinPrice(parsePriceInput(minPriceInput));
      setMaxPrice(parsePriceInput(maxPriceInput));
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, minPriceInput, maxPriceInput]);

  const minPriceInvalid = isPriceInputInvalid(minPriceInput);
  const maxPriceInvalid = isPriceInputInvalid(maxPriceInput);
  const priceInvalid = minPriceInvalid || maxPriceInvalid;

  const hasActiveFilters =
    searchInput !== "" || minPriceInput !== "" || maxPriceInput !== "";

  const handleClearFilters = useCallback(() => {
    setSearchInput("");
    setMinPriceInput("");
    setMaxPriceInput("");
    setSearch(undefined);
    setMinPrice(undefined);
    setMaxPrice(undefined);
    queryClient.invalidateQueries({ queryKey: ["offers", selectedTargetId] });
    searchInputRef.current?.focus();
  }, [queryClient, selectedTargetId]);

  const isPriceActive = minPriceInput !== "" || maxPriceInput !== "";

  const formattedPriceRange = useMemo(() => {
    if (minPriceInput !== "" && maxPriceInput !== "") {
      return `${minPriceInput} – ${maxPriceInput} zł`;
    }
    if (minPriceInput !== "") {
      return `od ${minPriceInput} zł`;
    }
    if (maxPriceInput !== "") {
      return `do ${maxPriceInput} zł`;
    }
    return t("offers.filters.priceLabel", "Cena");
  }, [minPriceInput, maxPriceInput, t]);

  const handleClearPrice = (e?: React.MouseEvent) => {
    e?.preventDefault();
    e?.stopPropagation();
    setMinPriceInput("");
    setMaxPriceInput("");
    setMinPrice(undefined);
    setMaxPrice(undefined);
  };

  // Sync prop changes into state
  useEffect(() => {
    if (initialTargetId !== undefined) {
      setSelectedTargetId(initialTargetId);
      saveStoredTargetId(initialTargetId);
    }
  }, [initialTargetId]);

  // Set default target if none is selected
  useEffect(() => {
    if (selectedTargetId === null && myTarget?.id) {
      setSelectedTargetId(myTarget.id);
      saveStoredTargetId(myTarget.id);
    }
  }, [selectedTargetId, myTarget]);

  // Reset pagination limit on tab / filter / ordering change
  useEffect(() => {
    setLimit(50);
  }, [activeTab, ordering, search, minPrice, maxPrice]);

  const handleSelectTarget = (targetId: number) => {
    setSelectedTargetId(targetId);
    saveStoredTargetId(targetId);
    setLimit(50);
    onTargetChange?.(targetId);
  };

  // Query live offers
  const {
    data: liveOffersPage,
    isLoading: liveLoading,
    isFetching,
    refetch: refetchOffers,
  } = useOffersQuery({
    targetId: selectedTargetId ?? 0,
    tab: activeTab,
    ordering,
    search,
    minPrice,
    maxPrice,
    limit,
    offset: 0,
  });

  // Mutations
  const toggleLikeMutation = useToggleLikeMutation(selectedTargetId ?? 0);
  const toggleSeenMutation = useToggleSeenMutation(selectedTargetId ?? 0);

  const [isRefreshing, setIsRefreshing] = useState(false);

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

  const handleRefresh = async () => {
    if (!selectedTargetId || isBusy) return;
    setIsRefreshing(true);
    try {
      await Promise.all([
        refetchOffers(),
        queryClient.invalidateQueries({
          queryKey: ["offers", selectedTargetId],
        }),
      ]);
    } finally {
      setIsRefreshing(false);
    }
  };

  const displayedOffers: Array<PublicOfferSchema> = liveOffersPage?.items ?? [];
  const totalCount = liveOffersPage?.count ?? displayedOffers.length;
  const hasMore = totalCount > displayedOffers.length;

  const handleLoadMore = useCallback(() => {
    setLimit((prev) => prev + 50);
  }, []);

  const isBusy = isRefreshing || liveLoading || isFetching;
  const isLoadingOffers =
    liveLoading || (isFetching && displayedOffers.length === 0);

  // Sub-component renderers
  const renderTabs = () => (
    <Tabs
      value={activeTab}
      onValueChange={(val) =>
        setActiveTab(val as "unseen" | "liked" | "all")
      }
    >
      <TabsList className="bg-muted/70 p-0.5 h-8">
        <TabsTrigger
          value="unseen"
          className="gap-1.5 text-xs h-7 px-2.5 font-medium cursor-pointer"
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-primary" />
          <span>{t("offers.tabs.unseen")}</span>
        </TabsTrigger>
        <TabsTrigger
          value="liked"
          className="gap-1.5 text-xs h-7 px-2.5 font-medium cursor-pointer"
        >
          <Heart
            className={cn(
              "w-3.5 h-3.5",
              activeTab === "liked"
                ? "fill-red-500 text-red-500"
                : "text-muted-foreground",
            )}
          />
          <span>{t("offers.tabs.liked")}</span>
        </TabsTrigger>
        <TabsTrigger
          value="all"
          className="gap-1.5 text-xs h-7 px-2.5 font-medium cursor-pointer"
        >
          <Filter className="w-3.5 h-3.5 text-muted-foreground" />
          <span>{t("offers.tabs.all")}</span>
        </TabsTrigger>
      </TabsList>
    </Tabs>
  );

  const renderTargetSelector = (
    className = "h-8 text-xs min-w-[150px] sm:min-w-[175px]",
  ) =>
    targets && targets.length > 1 ? (
      <div className="flex items-center gap-1.5">
        <span className="text-xs font-medium text-muted-foreground whitespace-nowrap hidden sm:inline">
          {t("offers.targetLabel")}
        </span>
        <TargetSelectorInline
          targets={targets}
          selectedTargetId={selectedTargetId}
          onSelect={handleSelectTarget}
          className={className}
        />
      </div>
    ) : null;

  const renderSearch = () => (
    <div className="relative flex items-center">
      <Search className="absolute left-2.5 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
      <Input
        ref={searchInputRef}
        value={searchInput}
        onChange={(event) => setSearchInput(event.target.value)}
        aria-label={t("offers.filters.searchLabel")}
        placeholder={t("offers.filters.searchPlaceholder")}
        className="h-8 pl-8 pr-7 text-xs w-48 sm:w-60 bg-background/60 shadow-2xs focus-visible:bg-background transition-colors"
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
  );

  const renderPricePopover = () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          aria-label={
            isPriceActive
              ? `${t("offers.filters.priceLabel", "Cena")}: ${formattedPriceRange}`
              : t("offers.filters.priceLabel", "Cena")
          }
          className={cn(
            "h-8 text-xs gap-1.5 px-2.5 border rounded-md cursor-pointer transition-colors shadow-2xs select-none",
            isPriceActive
              ? "border-primary/50 bg-primary/10 text-primary font-medium hover:bg-primary/15"
              : "border-input bg-background hover:bg-accent hover:text-accent-foreground text-foreground",
          )}
        >
          <SlidersHorizontal
            className={cn(
              "w-3.5 h-3.5",
              isPriceActive ? "text-primary" : "text-muted-foreground",
            )}
          />
          <span>{isPriceActive ? formattedPriceRange : t("offers.filters.priceLabel", "Cena")}</span>
          {isPriceActive ? (
            <span
              role="button"
              tabIndex={0}
              onClick={handleClearPrice}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  handleClearPrice(e as unknown as React.MouseEvent);
                }
              }}
              title={t("offers.filters.clearPrice", "Wyczyść filtr ceny")}
              aria-label={t("offers.filters.clearPrice", "Wyczyść filtr ceny")}
              className="ml-0.5 -mr-1 p-0.5 rounded-full hover:bg-primary/20 text-primary transition-colors cursor-pointer"
            >
              <X className="w-3 h-3" />
            </span>
          ) : (
            <ChevronDown className="w-3 h-3 text-muted-foreground opacity-60" />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="start"
        sideOffset={6}
        className="w-72 p-3 space-y-3 shadow-md border border-border bg-popover text-popover-foreground rounded-lg"
      >
        <div className="flex items-center justify-between pb-1.5 border-b border-border/60">
          <span className="text-xs font-semibold text-foreground">
            {t("offers.filters.priceRangeTitle", "Zakres cenowy")}
          </span>
          {isPriceActive && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleClearPrice}
              className="h-6 text-[11px] px-1.5 text-muted-foreground hover:text-destructive cursor-pointer"
            >
              {t("offers.filters.resetPrice", "Wyczyść")}
            </Button>
          )}
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          <div className="space-y-1">
            <Label
              htmlFor="offer-min-price"
              className="text-[11px] font-medium text-muted-foreground"
            >
              {t("offers.filters.minPriceLabel", "Cena od")}
            </Label>
            <div className="relative flex items-center">
              <Input
                id="offer-min-price"
                value={minPriceInput}
                onChange={(e) => setMinPriceInput(e.target.value)}
                inputMode="numeric"
                placeholder="0"
                aria-label={t("offers.filters.minPriceLabel")}
                aria-invalid={minPriceInvalid || undefined}
                aria-describedby={
                  minPriceInvalid ? "offers-price-hint" : undefined
                }
                className="h-8 text-xs pr-7 bg-background/60 focus-visible:bg-background"
              />
              <span className="absolute right-2 text-[11px] text-muted-foreground pointer-events-none select-none">
                zł
              </span>
            </div>
          </div>

          <div className="space-y-1">
            <Label
              htmlFor="offer-max-price"
              className="text-[11px] font-medium text-muted-foreground"
            >
              {t("offers.filters.maxPriceLabel", "Cena do")}
            </Label>
            <div className="relative flex items-center">
              <Input
                id="offer-max-price"
                value={maxPriceInput}
                onChange={(e) => setMaxPriceInput(e.target.value)}
                inputMode="numeric"
                placeholder="Max"
                aria-label={t("offers.filters.maxPriceLabel")}
                aria-invalid={maxPriceInvalid || undefined}
                aria-describedby={
                  maxPriceInvalid ? "offers-price-hint" : undefined
                }
                className="h-8 text-xs pr-7 bg-background/60 focus-visible:bg-background"
              />
              <span className="absolute right-2 text-[11px] text-muted-foreground pointer-events-none select-none">
                zł
              </span>
            </div>
          </div>
        </div>

        {priceInvalid && (
          <p
            id="offers-price-hint"
            role="alert"
            className="text-[11px] text-destructive leading-tight"
          >
            {t("offers.filters.invalidPrice")}
          </p>
        )}
      </PopoverContent>
    </Popover>
  );

  const renderClearButton = () =>
    hasActiveFilters ? (
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={handleClearFilters}
        className="h-8 text-xs px-2 text-muted-foreground hover:text-foreground hover:bg-accent rounded-md gap-1 cursor-pointer shrink-0"
        title={t("offers.filters.clear")}
        aria-label={t("offers.filters.clear")}
      >
        <X className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">{t("offers.filters.clear")}</span>
      </Button>
    ) : null;

  const renderSortButton = () => (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      onClick={() =>
        setOrdering(ordering === "oldest" ? "newest" : "oldest")
      }
      className="h-8 text-xs gap-1.5 px-2.5 border border-input bg-background hover:bg-accent hover:text-accent-foreground text-foreground rounded-md cursor-pointer shadow-2xs"
    >
      <ArrowUpDown className="w-3.5 h-3.5 text-muted-foreground" />
      <span>
        {t("offers.ordering.label")}{" "}
        <strong className="text-foreground font-semibold">
          {ordering === "oldest"
            ? t("offers.ordering.oldest")
            : t("offers.ordering.newest")}
        </strong>
      </span>
    </Button>
  );

  const renderRefreshButton = () => (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      onClick={handleRefresh}
      disabled={isBusy}
      className="h-8 text-xs gap-1.5 px-2.5 border border-input bg-background hover:bg-accent hover:text-accent-foreground text-muted-foreground hover:text-foreground rounded-md cursor-pointer shadow-2xs"
      title={t("offers.actions.refreshServer")}
      aria-label={t("offers.actions.refreshServer")}
    >
      <RefreshCw
        className={cn(
          "w-3.5 h-3.5",
          isBusy && "animate-spin text-primary",
        )}
      />
      <span className="hidden sm:inline">
        {t("offers.actions.refresh")}
      </span>
    </Button>
  );

  const renderCountBadge = () => (
    <Badge
      variant="outline"
      className="h-8 px-2.5 text-xs font-normal text-muted-foreground bg-muted/30 border-border whitespace-nowrap select-none rounded-md"
    >
      {totalCount > displayedOffers.length
        ? t("offers.resultsCountWithTotal", {
            count: displayedOffers.length,
            total: totalCount,
          })
        : t("offers.resultsCount", {
            count: displayedOffers.length,
          })}
    </Badge>
  );

  return (
    <div className="min-h-screen bg-secondary pb-3 flex flex-col">
      <main className="container mx-auto px-3 sm:px-4 py-2 sm:py-3 max-w-[1700px] space-y-2.5 flex-1 flex flex-col min-h-0">
        {/* Header with Title and Target Selector */}
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

          <div className="shrink-0">
            {renderTargetSelector("h-8 text-xs min-w-[170px] sm:min-w-[200px]")}
          </div>
        </div>

        {/* Polished Offers Filter Bar */}
        <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-xs flex flex-wrap items-center justify-between gap-2.5">
          {renderTabs()}
          <div
            role="group"
            aria-label={t("offers.filters.groupLabel")}
            className="flex flex-wrap items-center gap-2 sm:gap-2.5 ml-auto"
          >
            {renderSearch()}
            {renderPricePopover()}
            {renderClearButton()}
            <Separator
              orientation="vertical"
              className="h-4 self-center hidden sm:block mx-0.5"
              aria-hidden="true"
            />
            {renderCountBadge()}
            {renderSortButton()}
            {renderRefreshButton()}
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
