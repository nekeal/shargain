import { memo, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Heart, Images, Layers, MapPin } from "lucide-react";
import { formatPrice, formatTimeAgo } from "./useOffers";
import { OfferAttributeBadge } from "./OfferAttributeBadge";
import type { PublicOfferSchema } from "@/lib/api/types.gen";
import { Badge } from "@/components/ui/badge";

export function extractDomain(url: string): string {
  try {
    const match = url.match(/^https?:\/\/(?:www\.)?([^/?#]+)/i);
    return match ? match[1] : "link";
  } catch {
    return "link";
  }
}

interface OfferThumbnailProps {
  offer: PublicOfferSchema;
  size?: "sm" | "md";
}

export const OfferThumbnail = memo(function OfferThumbnail({
  offer,
  size = "sm",
}: OfferThumbnailProps) {
  const { t } = useTranslation();
  const photoCount = offer.images?.length || (offer.mainImageUrl ? 1 : 0);
  const sizeClasses =
    size === "sm" ? "w-16 h-16 rounded-md" : "w-20 h-20 rounded-lg";

  return (
    <div
      className={`relative ${sizeClasses} overflow-hidden bg-muted shrink-0 border border-border/40`}
    >
      {offer.mainImageUrl ? (
        <img
          src={offer.mainImageUrl}
          alt={offer.title}
          className="w-full h-full object-cover"
          loading="lazy"
          decoding="async"
          referrerPolicy="no-referrer"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center text-muted-foreground/50">
          <Layers className={size === "sm" ? "w-5 h-5" : "w-6 h-6"} />
        </div>
      )}

      {!offer.isSeen && (
        <span
          title={t("offers.queue.unreadDot")}
          className="absolute top-1 left-1 w-2.5 h-2.5 rounded-full bg-primary ring-2 ring-background shadow-sm"
        />
      )}

      {photoCount > 1 && (
        <span className="absolute bottom-0.5 right-0.5 flex items-center gap-0.5 px-1 rounded bg-neutral-900/80 text-[10px] text-white font-mono">
          <Images className="w-2.5 h-2.5" />
          {photoCount}
        </span>
      )}
    </div>
  );
});

interface OfferSourceBadgesProps {
  offer: PublicOfferSchema;
  domain: string;
}

export const OfferSourceBadges = memo(function OfferSourceBadges({
  offer,
  domain,
}: OfferSourceBadgesProps) {
  const { t } = useTranslation();

  return (
    <div className="flex items-center gap-1 shrink-0">
      {offer.scrapingUrlName && (
        <Badge
          variant="secondary"
          className="text-[9px] px-1 py-0 max-w-[110px] truncate bg-primary/10 text-primary border-primary/20 font-medium"
          title={t("offers.queue.sourceUrl", { name: offer.scrapingUrlName })}
        >
          <span className="truncate">{offer.scrapingUrlName}</span>
        </Badge>
      )}

      <Badge
        variant="outline"
        className="text-[9px] px-1 py-0 uppercase border-border/80 font-mono text-muted-foreground"
      >
        {domain}
      </Badge>
    </div>
  );
});

export interface OfferQueueRowProps {
  offer: PublicOfferSchema;
  isSelected: boolean;
  onSelect: (id: number) => void;
  onToggleLike: (id: number, currentlyLiked: boolean) => void;
}

export const OfferQueueRow = memo(function OfferQueueRow({
  offer,
  isSelected,
  onSelect,
  onToggleLike,
}: OfferQueueRowProps) {
  const { t } = useTranslation();
  const domain = extractDomain(offer.url);
  const rowRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (isSelected) {
      rowRef.current?.scrollIntoView({ block: "nearest", behavior: "auto" });
    }
  }, [isSelected]);

  return (
    <div
      ref={rowRef}
      className={`p-2.5 flex items-stretch gap-2.5 relative transition-colors ${
        isSelected
          ? "bg-violet-500/10 dark:bg-violet-500/20 border-l-4 border-primary"
          : "hover:bg-muted/40"
      }`}
    >
      <button
        type="button"
        onClick={() => onSelect(offer.id)}
        className="flex flex-1 gap-2.5 text-left min-w-0 cursor-pointer focus:outline-none"
        aria-label={offer.title}
      >
        <OfferThumbnail offer={offer} size="sm" />

        <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
          <div className="flex items-baseline justify-between gap-1.5">
            <span className="font-bold text-sm text-foreground truncate">
              {formatPrice(offer.price, t)}
            </span>
            <OfferSourceBadges offer={offer} domain={domain} />
          </div>

          <p className="text-xs text-foreground/90 font-medium line-clamp-1 leading-snug my-0.5">
            {offer.title}
          </p>

          <div className="flex items-center justify-between gap-1 text-[11px] text-muted-foreground">
            <span className="truncate max-w-[140px]">
              {offer.location?.name || t("offers.queue.unknownLocation")}
            </span>
            <span className="shrink-0 text-[10px]">
              {formatTimeAgo(offer.createdAt, t)}
            </span>
          </div>
        </div>
      </button>

      <div className="flex items-start pt-0.5 shrink-0">
        <button
          type="button"
          onClick={() => onToggleLike(offer.id, offer.isLiked)}
          className="p-1 rounded hover:bg-muted text-muted-foreground transition-colors cursor-pointer"
          title={offer.isLiked ? t("offers.actions.unlike") : t("offers.actions.like")}
          aria-label={offer.isLiked ? t("offers.actions.unlike") : t("offers.actions.like")}
        >
          <Heart
            className={`w-3.5 h-3.5 ${
              offer.isLiked
                ? "fill-red-500 text-red-500"
                : "hover:text-red-500 text-muted-foreground/60"
            }`}
          />
        </button>
      </div>
    </div>
  );
});

export const OfferExpandedCard = memo(function OfferExpandedCard({
  offer,
  isSelected,
  onSelect,
  onToggleLike,
}: OfferQueueRowProps) {
  const { t } = useTranslation();
  const domain = extractDomain(offer.url);
  const rowRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (isSelected) {
      rowRef.current?.scrollIntoView({ block: "nearest", behavior: "auto" });
    }
  }, [isSelected]);

  return (
    <div
      ref={rowRef}
      className={`p-3.5 rounded-xl border flex flex-col justify-between gap-3 text-left relative transition-colors ${
        isSelected
          ? "border-primary bg-primary/5 shadow-md"
          : "border-border/70 hover:border-border hover:shadow-sm bg-card"
      }`}
    >
      <div className="flex items-start gap-3">
        <button
          type="button"
          onClick={() => onSelect(offer.id)}
          className="flex flex-1 gap-3 text-left min-w-0 cursor-pointer focus:outline-none"
          aria-label={offer.title}
        >
          <OfferThumbnail offer={offer} size="md" />

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-1 mb-1">
              <span className="font-bold text-base text-foreground truncate">
                {formatPrice(offer.price, t)}
              </span>
              <OfferSourceBadges offer={offer} domain={domain} />
            </div>

            <p className="text-xs sm:text-sm font-medium text-foreground line-clamp-2 leading-snug mb-1.5">
              {offer.title}
            </p>

            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span className="truncate max-w-[170px] flex items-center gap-1">
                <MapPin className="w-3 h-3 shrink-0 text-muted-foreground/70" />
                <span>{offer.location?.name || t("offers.queue.unknownLocation")}</span>
              </span>
              <span className="shrink-0 text-[11px]">
                {formatTimeAgo(offer.createdAt, t)}
              </span>
            </div>
          </div>
        </button>

        <button
          type="button"
          onClick={() => onToggleLike(offer.id, offer.isLiked)}
          className="p-1.5 rounded-md hover:bg-muted text-muted-foreground transition-colors shrink-0 cursor-pointer"
          title={offer.isLiked ? t("offers.actions.unlike") : t("offers.actions.like")}
          aria-label={offer.isLiked ? t("offers.actions.unlike") : t("offers.actions.like")}
        >
          <Heart
            className={`w-4 h-4 ${
              offer.isLiked
                ? "fill-red-500 text-red-500"
                : "hover:text-red-500 text-muted-foreground/60"
            }`}
          />
        </button>
      </div>

      {offer.attributes.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1 border-t border-border/50">
          {offer.attributes.slice(0, 4).map((attr) => (
            <OfferAttributeBadge key={attr.name} attribute={attr} compact={true} />
          ))}
        </div>
      )}
    </div>
  );
});
