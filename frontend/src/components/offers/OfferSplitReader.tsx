import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  CheckCircle2,
  PanelRightClose,
  PanelRightOpen,
  RefreshCw,
} from "lucide-react";
import { OfferDetailCockpit } from "./OfferDetailCockpit";
import { OfferExpandedCard, OfferQueueRow } from "./OfferQueueRow";
import { useOfferKeyboardTriage } from "./useOfferKeyboardTriage";
import type { PublicOfferSchema } from "@/lib/api/types.gen";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export interface OfferSplitReaderProps {
  offers: Array<PublicOfferSchema>;
  onToggleLike: (offerId: number, currentlyLiked: boolean) => void;
  onToggleSeen: (offerId: number, currentlySeen: boolean) => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  isLoadingMore?: boolean;
  totalCount?: number;
}

export function OfferSplitReader({
  offers,
  onToggleLike,
  onToggleSeen,
  onRefresh,
  isRefreshing,
  hasMore,
  onLoadMore,
  isLoadingMore,
  totalCount,
}: OfferSplitReaderProps) {
  const { t } = useTranslation();

  if (offers.length === 0) {
    return (
      <div className="p-16 text-center rounded-2xl border border-dashed border-border/80 bg-card/60 space-y-3">
        <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <h3 className="text-base font-semibold text-foreground">
          {t("offers.emptyState.title")}
        </h3>
        <p className="text-xs text-muted-foreground max-w-sm mx-auto">
          {t("offers.emptyState.description")}
        </p>
        {onRefresh && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            className="text-xs h-8 px-3 gap-1.5 mt-2 cursor-pointer"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin" : ""}`}
            />
            <span>{t("offers.emptyState.refreshButton")}</span>
          </Button>
        )}
      </div>
    );
  }

  return (
    <SplitReaderContent
      offers={offers}
      onToggleLike={onToggleLike}
      onToggleSeen={onToggleSeen}
      onRefresh={onRefresh}
      isRefreshing={isRefreshing}
      hasMore={hasMore}
      onLoadMore={onLoadMore}
      isLoadingMore={isLoadingMore}
      totalCount={totalCount}
    />
  );
}

function SplitReaderContent({
  offers,
  onToggleLike,
  onToggleSeen,
  onRefresh,
  isRefreshing,
  hasMore,
  onLoadMore,
  isLoadingMore,
  totalCount,
}: OfferSplitReaderProps) {
  const { t } = useTranslation();
  const [selectedOfferId, setSelectedOfferId] = useState<number>(offers[0].id);
  const [isDetailsOpen, setIsDetailsOpen] = useState(true);

  // Keep selected offer within bounds when list shrinks
  useEffect(() => {
    if (offers.length > 0 && !offers.some((o) => o.id === selectedOfferId)) {
      setSelectedOfferId(offers[0].id);
    }
  }, [offers, selectedOfferId]);

  const {
    activeIndex,
    activeOffer,
    handleNext,
    handlePrev,
    handleMarkSeenAndNext,
  } = useOfferKeyboardTriage({
    offers,
    selectedOfferId,
    setSelectedOfferId,
    isDetailsOpen,
    onToggleLike,
    onToggleSeen,
  });

  const handleSelectOffer = useCallback(
    (offerId: number) => {
      setSelectedOfferId(offerId);
      if (!isDetailsOpen) {
        setIsDetailsOpen(true);
      }
    },
    [isDetailsOpen],
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 items-stretch h-[calc(100vh-185px)] min-h-[540px]">
      {/* LEFT COLUMN: Queue / Master List */}
      <div
        className={`${
          isDetailsOpen ? "lg:col-span-4" : "lg:col-span-12"
        } bg-card border border-border rounded-xl flex flex-col h-full overflow-hidden shadow-sm`}
      >
        {/* Queue Header */}
        <div className="p-3 border-b border-border flex items-center justify-between gap-2 bg-muted/20 shrink-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-xs sm:text-sm text-foreground">
              {t("offers.queue.title")}
            </span>
            <Badge variant="secondary" className="text-[10px] font-mono px-1.5 py-0">
              {totalCount !== undefined && totalCount > offers.length
                ? `${offers.length} / ${totalCount}`
                : offers.length}
            </Badge>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsDetailsOpen((prev) => !prev)}
              className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground gap-1 cursor-pointer"
              title={
                isDetailsOpen
                  ? t("offers.actions.hideDetails")
                  : t("offers.actions.expandDetails")
              }
            >
              {isDetailsOpen ? (
                <>
                  <PanelRightClose className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">{t("offers.actions.hideDetails")}</span>
                </>
              ) : (
                <>
                  <PanelRightOpen className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">{t("offers.actions.expandDetails")}</span>
                </>
              )}
            </Button>

            {onRefresh && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRefresh}
                title={t("offers.actions.refreshOffers")}
                aria-label={t("offers.actions.refreshOffers")}
                className="h-6 w-6 p-0 text-muted-foreground hover:text-foreground ml-0.5 cursor-pointer"
              >
                <RefreshCw
                  className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin" : ""}`}
                />
              </Button>
            )}
          </div>
        </div>

        {/* Scrollable Items List */}
        <div
          className={`flex-1 overflow-y-auto divide-y divide-border/50 scrollbar-thin overscroll-contain [transform:translateZ(0)] ${
            !isDetailsOpen ? "grid sm:grid-cols-2 xl:grid-cols-3 divide-y-0 gap-3 p-3" : ""
          }`}
        >
          {offers.map((offer) => {
            const isSelected = offer.id === selectedOfferId;

            if (!isDetailsOpen) {
              return (
                <OfferExpandedCard
                  key={offer.id}
                  offer={offer}
                  isSelected={isSelected}
                  onSelect={handleSelectOffer}
                  onToggleLike={onToggleLike}
                />
              );
            }

            return (
              <OfferQueueRow
                key={offer.id}
                offer={offer}
                isSelected={isSelected}
                onSelect={handleSelectOffer}
                onToggleLike={onToggleLike}
              />
            );
          })}

          {/* Load More Pagination Button */}
          {hasMore && (
            <div className="p-3 text-center border-t border-border/50">
              <Button
                variant="outline"
                size="sm"
                onClick={onLoadMore}
                disabled={isLoadingMore}
                className="w-full text-xs gap-1.5 cursor-pointer"
              >
                {isLoadingMore ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-primary" />
                    <span>{t("offers.pagination.loading")}</span>
                  </>
                ) : (
                  <span>
                    {t("offers.pagination.loadMore", {
                      remaining: (totalCount ?? 0) - offers.length,
                    })}
                  </span>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Keyboard hints footer */}
        <div className="p-2 border-t border-border bg-muted/20 text-[11px] text-muted-foreground flex items-center justify-between px-3 shrink-0">
          <span>{t("offers.queue.shortcuts")}</span>
          <div className="flex items-center gap-1.5 font-mono text-[10px]">
            <span><kbd className="px-1 py-0.5 bg-muted rounded border border-border">J</kbd>/<kbd className="px-1 py-0.5 bg-muted rounded border border-border">K</kbd></span>
            <span><kbd className="px-1 py-0.5 bg-muted rounded border border-border">S</kbd></span>
            <span><kbd className="px-1 py-0.5 bg-muted rounded border border-border">L</kbd></span>
            <span><kbd className="px-1 py-0.5 bg-muted rounded border border-border">O</kbd></span>
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN: Full Inspection & Triage Cockpit */}
      {isDetailsOpen && activeOffer && (
        <OfferDetailCockpit
          activeOffer={activeOffer}
          activeIndex={activeIndex}
          totalOffers={offers.length}
          onNext={handleNext}
          onPrev={handlePrev}
          onMarkSeenAndNext={handleMarkSeenAndNext}
          onToggleLike={onToggleLike}
          onToggleSeen={onToggleSeen}
          onClose={() => setIsDetailsOpen(false)}
        />
      )}
    </div>
  );
}
