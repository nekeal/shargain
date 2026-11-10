import { memo } from "react";
import { useTranslation } from "react-i18next";
import {
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Eye,
  EyeOff,
  FileText,
  Heart,
  Layers,
  MapPin,
  X,
} from "lucide-react";
import { formatPrice, formatTimeAgo } from "./useOffers";
import { extractDomain } from "./OfferQueueRow";
import { OfferAttributeBadge } from "./OfferAttributeBadge";
import { OfferImageGallery } from "./OfferImageGallery";
import { OfferLocationMap } from "./OfferLocationMap";
import type { PublicOfferSchema } from "@/lib/api/types.gen";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export interface OfferDetailCockpitProps {
  activeOffer: PublicOfferSchema;
  activeIndex: number;
  totalOffers: number;
  onNext: () => void;
  onPrev: () => void;
  onMarkSeenAndNext: () => void;
  onToggleLike: (offerId: number, currentlyLiked: boolean) => void;
  onToggleSeen: (offerId: number, currentlySeen: boolean) => void;
  onClose: () => void;
}

export const OfferDetailCockpit = memo(function OfferDetailCockpit({
  activeOffer,
  activeIndex,
  totalOffers,
  onNext,
  onPrev,
  onMarkSeenAndNext,
  onToggleLike,
  onToggleSeen,
  onClose,
}: OfferDetailCockpitProps) {
  const { t } = useTranslation();
  const domain = extractDomain(activeOffer.url);

  return (
    <div className="lg:col-span-8 bg-card border border-border rounded-xl flex flex-col h-full overflow-hidden shadow-sm">
      {/* Sticky Command Bar */}
      <div className="p-3 border-b border-border flex flex-wrap items-center justify-between gap-3 bg-muted/25 shrink-0">
        <div className="flex items-center gap-2">
          <Button
            onClick={onMarkSeenAndNext}
            size="sm"
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold gap-1.5 shadow-sm text-xs h-8 px-3 cursor-pointer"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{t("offers.actions.markSeenAndNext")}</span>
          </Button>

          <Button
            variant={activeOffer.isSeen ? "secondary" : "outline"}
            size="sm"
            onClick={() => onToggleSeen(activeOffer.id, activeOffer.isSeen)}
            className="gap-1.5 text-xs h-8 px-3 cursor-pointer"
          >
            {activeOffer.isSeen ? (
              <>
                <EyeOff className="w-3.5 h-3.5 text-muted-foreground" />
                <span>{t("offers.actions.markUnseen")}</span>
              </>
            ) : (
              <>
                <Eye className="w-3.5 h-3.5 text-primary" />
                <span>{t("offers.actions.markSeen")}</span>
              </>
            )}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onToggleLike(activeOffer.id, activeOffer.isLiked)}
            className={`gap-1.5 text-xs h-8 px-3 cursor-pointer ${
              activeOffer.isLiked
                ? "text-red-600 border-red-300 dark:border-red-900 bg-red-50 dark:bg-red-950/30"
                : ""
            }`}
          >
            <Heart
              className={`w-3.5 h-3.5 ${
                activeOffer.isLiked ? "fill-red-500 text-red-500" : ""
              }`}
            />
            <span>
              {activeOffer.isLiked
                ? t("offers.actions.liked")
                : t("offers.actions.likeShortcut")}
            </span>
          </Button>
        </div>

        <div className="flex items-center gap-1.5">
          <Button
            asChild
            variant="outline"
            size="sm"
            className="text-xs h-8 gap-1.5 px-3 cursor-pointer"
          >
            <a
              href={activeOffer.url}
              target="_blank"
              rel="noopener noreferrer"
              title={t("offers.actions.openOriginal")}
            >
              <span>{t("offers.actions.openOriginalShortcut")}</span>
              <ExternalLink className="w-3 h-3 text-muted-foreground" />
            </a>
          </Button>

          <div className="flex items-center border border-border rounded-lg overflow-hidden ml-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={onPrev}
              disabled={activeIndex === 0}
              className="h-8 w-8 rounded-none border-r border-border disabled:opacity-40 cursor-pointer"
              title={t("offers.actions.prev")}
              aria-label={t("offers.actions.prev")}
            >
              <ChevronUp className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onNext}
              disabled={activeIndex === totalOffers - 1}
              className="h-8 w-8 rounded-none disabled:opacity-40 cursor-pointer"
              title={t("offers.actions.next")}
              aria-label={t("offers.actions.next")}
            >
              <ChevronDown className="w-4 h-4" />
            </Button>
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-muted-foreground hover:text-foreground cursor-pointer"
            title={t("offers.actions.hideDetails")}
            aria-label={t("offers.actions.hideDetails")}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Scrollable Detail Body */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-5 scrollbar-thin overscroll-contain [transform:translateZ(0)]">
        {/* Header info */}
        <div className="space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl sm:text-3xl font-extrabold text-foreground tracking-tight">
                {formatPrice(activeOffer.price, t)}
              </span>
              {!activeOffer.isSeen && (
                <Badge className="bg-primary text-primary-foreground text-xs font-semibold">
                  {t("offers.queue.unreadDot")}
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs uppercase font-mono">
                {domain}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {formatTimeAgo(activeOffer.createdAt, t)}
              </span>
            </div>
          </div>

          <h2 className="text-base font-bold text-foreground leading-snug line-clamp-2">
            {activeOffer.title}
          </h2>

          {activeOffer.scrapingUrlName && (
            <div className="flex items-center gap-1.5 text-xs text-primary font-medium">
              <Layers className="w-3.5 h-3.5" />
              <span>
                {t("offers.queue.sourceUrl", { name: activeOffer.scrapingUrlName })}
              </span>
            </div>
          )}
        </div>

        {/* Gallery & Attributes side-by-side row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start pt-1 border-t border-border/60">
          {/* Gallery preview */}
          <div className="space-y-2 min-w-0">
            <OfferImageGallery
              key={activeOffer.id}
              images={activeOffer.images}
              mainImageUrl={activeOffer.mainImageUrl}
              title={activeOffer.title}
            />
          </div>

          {/* Structured Attributes Grid */}
          <div className="space-y-2 min-w-0">
            <span className="text-xs font-semibold uppercase text-muted-foreground tracking-wider block">
              {t("offers.detail.parameters")}
            </span>

            <div className="grid grid-cols-2 gap-2">
              {activeOffer.attributes.length > 0 ? (
                activeOffer.attributes.map((attr) => (
                  <OfferAttributeBadge key={attr.name} attribute={attr} />
                ))
              ) : (
                <div className="col-span-full text-xs text-muted-foreground py-2 italic">
                  {t("offers.detail.noParameters")}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Large Location Map Section */}
        <div className="space-y-2.5 pt-2 border-t border-border/60">
          <span className="text-xs font-semibold uppercase text-muted-foreground tracking-wider flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-primary" />
            {t("offers.detail.map")}
          </span>

          <OfferLocationMap
            location={activeOffer.location}
            interactiveMap={true}
            mapHeightClassName="h-[300px] sm:h-[360px]"
          />
        </div>

        {/* Description Section */}
        <div className="space-y-2 pt-2 border-t border-border/60">
          <span className="text-xs font-semibold uppercase text-muted-foreground tracking-wider flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-primary" />
            {t("offers.detail.description")}
          </span>

          {activeOffer.description ? (
            <div className="bg-muted/20 border border-border/60 rounded-xl p-4 text-xs sm:text-sm text-foreground/90 leading-relaxed whitespace-pre-line">
              {activeOffer.description}
            </div>
          ) : (
            <div className="p-4 rounded-xl border border-border/60 bg-muted/20 text-xs text-muted-foreground italic text-center">
              {t("offers.detail.noDescription")}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});
