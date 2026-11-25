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
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
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

  // Prototype variants for design exploration: A (Natural Hierarchy), B (Unified Single Bar), C (Popover Filters)
  const [prototypeVariant, setPrototypeVariant] = useState<"A" | "B" | "C">(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const v = params.get("variant")?.toUpperCase();
      if (v === "A" || v === "B" || v === "C") return v;
    }
    return "A";
  });

  const handleVariantChange = (v: "A" | "B" | "C") => {
    setPrototypeVariant(v);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      url.searchParams.set("variant", v);
      window.history.replaceState({}, "", url.toString());
    }
  };

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

  // Helper renderers for prototype variants
  const renderTabs = () => (
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
  );

  const renderTargetSelector = (className = "h-8 text-xs min-w-[150px] sm:min-w-[175px]") =>
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

  const renderSearch = (widthClass = "w-44 sm:w-52") => (
    <div className="relative flex items-center">
      <Search className="absolute left-2.5 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
      <Input
        ref={searchInputRef}
        value={searchInput}
        onChange={(event) => setSearchInput(event.target.value)}
        aria-label={t("offers.filters.searchLabel")}
        placeholder={t("offers.filters.searchPlaceholder")}
        className={`h-8 pl-8 pr-7 text-xs ${widthClass} bg-background/60 shadow-2xs focus-visible:bg-background transition-colors`}
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

  const renderPriceSegment = () => (
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
  );

  const renderPricePopover = () => {
    const isPriceActive = minPriceInput !== "" || maxPriceInput !== "";
    return (
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className={`h-8 text-xs gap-1.5 px-2.5 border rounded-lg cursor-pointer shadow-2xs ${
              isPriceActive
                ? "border-primary/50 bg-primary/10 text-primary font-semibold"
                : "border-border bg-background hover:bg-muted text-foreground"
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5 text-muted-foreground" />
            <span>
              {isPriceActive
                ? `${minPriceInput || "0"} – ${maxPriceInput || "∞"} zł`
                : t("offers.filters.priceLabel", "Cena")}
            </span>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-72 p-3 space-y-3" align="start">
          <div className="font-semibold text-xs text-foreground">
            {t("offers.filters.groupLabel", "Filtruj cenę")}
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 space-y-1">
              <span className="text-[10px] text-muted-foreground font-medium">Od</span>
              <Input
                value={minPriceInput}
                onChange={(e) => setMinPriceInput(e.target.value)}
                placeholder="0"
                inputMode="numeric"
                aria-label={t("offers.filters.minPriceLabel")}
                className="h-8 text-xs"
              />
            </div>
            <span className="text-muted-foreground mt-4">–</span>
            <div className="flex-1 space-y-1">
              <span className="text-[10px] text-muted-foreground font-medium">Do</span>
              <Input
                value={maxPriceInput}
                onChange={(e) => setMaxPriceInput(e.target.value)}
                placeholder="Max"
                inputMode="numeric"
                aria-label={t("offers.filters.maxPriceLabel")}
                className="h-8 text-xs"
              />
            </div>
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-border/50">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setMinPriceInput("");
                setMaxPriceInput("");
              }}
              className="h-7 text-xs px-2 text-muted-foreground cursor-pointer"
            >
              Resetuj
            </Button>
            <span className="text-[11px] text-muted-foreground">w zł (PLN)</span>
          </div>
        </PopoverContent>
      </Popover>
    );
  };

  const renderClearButton = () =>
    hasActiveFilters ? (
      <Button
        variant="ghost"
        size="sm"
        onClick={handleClearFilters}
        className="h-8 text-xs px-2 text-muted-foreground hover:text-foreground hover:bg-muted/80 rounded-lg gap-1 cursor-pointer shrink-0"
        title={t("offers.filters.clear")}
        aria-label={t("offers.filters.clear")}
      >
        <X className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">{t("offers.filters.clear")}</span>
      </Button>
    ) : null;

  const renderSortButton = () => (
    <Button
      variant="ghost"
      size="sm"
      onClick={() =>
        setOrdering(ordering === "oldest" ? "newest" : "oldest")
      }
      className="h-8 text-xs gap-1.5 px-2.5 border border-border bg-background hover:bg-muted text-foreground rounded-lg cursor-pointer shadow-2xs"
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

  const renderRefreshButton = (showText = false) => (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleRefresh}
      disabled={isBusy}
      className="h-8 text-xs gap-1.5 px-2.5 border border-border bg-background hover:bg-muted text-muted-foreground hover:text-foreground rounded-lg cursor-pointer shadow-2xs"
      title={t("offers.actions.refreshServer")}
      aria-label={t("offers.actions.refreshServer")}
    >
      <RefreshCw
        className={`w-3.5 h-3.5 ${
          isBusy ? "animate-spin text-primary" : ""
        }`}
      />
      {showText && <span className="hidden sm:inline">{t("offers.actions.refresh")}</span>}
    </Button>
  );

  const renderCountBadge = () => (
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
  );

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

          {/* Variants A & C: Target Selector belongs in header */}
          {(prototypeVariant === "A" || prototypeVariant === "C") && (
            <div className="shrink-0">{renderTargetSelector("h-8 text-xs min-w-[170px] sm:min-w-[200px]")}</div>
          )}
        </div>

        {/* VARIANT A: Natural Hierarchy (Linear/GitHub style) */}
        {prototypeVariant === "A" && (
          <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-xs flex flex-wrap items-center justify-between gap-2.5">
            {renderTabs()}
            <div
              role="group"
              aria-label={t("offers.filters.groupLabel")}
              className="flex flex-wrap items-center gap-2 sm:gap-2.5 ml-auto"
            >
              {renderSearch("w-44 sm:w-52 md:w-56")}
              {renderPriceSegment()}
              {renderClearButton()}
              <div className="h-4 w-px bg-border/80 self-center hidden sm:block mx-0.5" aria-hidden="true" />
              {renderCountBadge()}
              {renderSortButton()}
              {renderRefreshButton(false)}
              {priceInvalid && (
                <span id="offers-price-hint" className="text-[11px] font-medium text-destructive whitespace-nowrap animate-in fade-in">
                  {t("offers.filters.invalidPrice")}
                </span>
              )}
            </div>
          </div>
        )}

        {/* VARIANT B: Unified Single Bar (all in 1 continuous row with count) */}
        {prototypeVariant === "B" && (
          <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-xs flex flex-wrap items-center gap-2 sm:gap-2.5">
            {renderTabs()}
            {renderTargetSelector()}
            <div className="hidden md:block h-4 w-px bg-border/80 self-center mx-0.5" aria-hidden="true" />
            <div
              role="group"
              aria-label={t("offers.filters.groupLabel")}
              className="flex flex-wrap items-center gap-2"
            >
              {renderSearch("w-40 sm:w-48")}
              {renderPriceSegment()}
              {renderClearButton()}
              {priceInvalid && (
                <span id="offers-price-hint" className="text-[11px] font-medium text-destructive whitespace-nowrap animate-in fade-in">
                  {t("offers.filters.invalidPrice")}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 ml-auto">
              {renderCountBadge()}
              {renderSortButton()}
              {renderRefreshButton(true)}
            </div>
          </div>
        )}

        {/* VARIANT C: Minimalist Popover Filter */}
        {prototypeVariant === "C" && (
          <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-xs flex flex-wrap items-center justify-between gap-2.5">
            {renderTabs()}
            <div
              role="group"
              aria-label={t("offers.filters.groupLabel")}
              className="flex flex-wrap items-center gap-2 sm:gap-2.5 ml-auto"
            >
              {renderSearch("w-52 sm:w-64")}
              {renderPricePopover()}
              {renderClearButton()}
              <div className="h-4 w-px bg-border/80 self-center hidden sm:block mx-0.5" aria-hidden="true" />
              {renderSortButton()}
              {renderRefreshButton(false)}
            </div>
          </div>
        )}

        {/* Floating Prototype Switcher */}
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-neutral-900/90 dark:bg-neutral-100/90 text-white dark:text-neutral-900 backdrop-blur-md px-3.5 py-1.5 rounded-full shadow-2xl flex items-center gap-1.5 border border-white/20 text-xs font-medium select-none">
          <span className="text-[10px] uppercase tracking-wider font-bold opacity-60 mr-1.5">
            Wariant:
          </span>
          <button
            type="button"
            onClick={() => handleVariantChange("A")}
            className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
              prototypeVariant === "A"
                ? "bg-primary text-primary-foreground font-bold shadow-xs"
                : "opacity-75 hover:opacity-100 hover:bg-white/10 dark:hover:bg-black/10"
            }`}
          >
            A: Hierarchia (Linear)
          </button>
          <button
            type="button"
            onClick={() => handleVariantChange("B")}
            className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
              prototypeVariant === "B"
                ? "bg-primary text-primary-foreground font-bold shadow-xs"
                : "opacity-75 hover:opacity-100 hover:bg-white/10 dark:hover:bg-black/10"
            }`}
          >
            B: Jeden pasek
          </button>
          <button
            type="button"
            onClick={() => handleVariantChange("C")}
            className={`px-3 py-1 rounded-full transition-all cursor-pointer ${
              prototypeVariant === "C"
                ? "bg-primary text-primary-foreground font-bold shadow-xs"
                : "opacity-75 hover:opacity-100 hover:bg-white/10 dark:hover:bg-black/10"
            }`}
          >
            C: Popover ceny
          </button>
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
