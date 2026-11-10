import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { ChevronLeft, ChevronRight, Globe, Images, Maximize2 } from "lucide-react";
import { ImageLightboxModal } from "./ImageLightboxModal";

interface OfferImageGalleryProps {
  images?: Array<string>;
  mainImageUrl?: string | null;
  title: string;
}

export function OfferImageGallery({
  images,
  mainImageUrl,
  title,
}: OfferImageGalleryProps) {
  const { t } = useTranslation();

  // Aggregate images list: use provided images array, fallback to mainImageUrl
  const allImages =
    images && images.length > 0
      ? images
      : mainImageUrl
        ? [mainImageUrl]
        : [];

  const [activeIndex, setActiveIndex] = useState(0);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const firstImage = allImages[0] ?? null;

  // Reset active index when image set changes
  useEffect(() => {
    setActiveIndex(0);
  }, [firstImage]);

  if (allImages.length === 0) {
    return (
      <div className="relative rounded-xl overflow-hidden bg-muted/60 border border-border aspect-[16/10] flex flex-col items-center justify-center text-muted-foreground gap-2">
        <Globe className="w-10 h-10 stroke-[1.5] opacity-50" />
        <span className="text-xs">{t("offers.gallery.noImages")}</span>
      </div>
    );
  }

  const currentImage = allImages[activeIndex] || allImages[0];
  const MAX_PREVIEW_THUMBNAILS = 12;
  const previewImages = allImages.slice(0, MAX_PREVIEW_THUMBNAILS);
  const remainingThumbnails = allImages.length - MAX_PREVIEW_THUMBNAILS;

  const handlePrev = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    setActiveIndex((prev) => (prev - 1 + allImages.length) % allImages.length);
  };

  const handleNext = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    setActiveIndex((prev) => (prev + 1) % allImages.length);
  };

  return (
    <div className="space-y-2">
      {/* Main Preview with Semantic Button Trigger */}
      <div className="w-full relative rounded-xl overflow-hidden bg-neutral-950 aspect-[16/10] border border-border group select-none block">
        <button
          type="button"
          onClick={() => setIsLightboxOpen(true)}
          className="w-full h-full block cursor-zoom-in text-left focus:outline-none focus:ring-2 focus:ring-primary/50"
          title={t("offers.gallery.openFullscreen")}
          aria-label={t("offers.gallery.openFullscreen")}
        >
          <img
            src={currentImage}
            alt={`${title} - ${t("offers.gallery.thumbnail", { index: activeIndex + 1 })}`}
            className="w-full h-full object-cover"
            loading="eager"
            decoding="async"
            referrerPolicy="no-referrer"
          />

          {/* Hover zoom icon badge */}
          <div className="absolute top-2.5 left-2.5 p-1.5 rounded-md bg-neutral-900/70 hover:bg-neutral-900 text-white backdrop-blur-md opacity-0 group-hover:opacity-100 transition-opacity">
            <Maximize2 className="w-3.5 h-3.5" />
          </div>
        </button>

        {/* Multi-image indicators & navigation */}
        {allImages.length > 1 && (
          <>
            <button
              type="button"
              onClick={handlePrev}
              title={t("offers.gallery.prevPhoto")}
              className="absolute left-2.5 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-neutral-900/75 hover:bg-neutral-900 text-white backdrop-blur-md shadow-md opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100 focus:outline-none cursor-pointer"
              aria-label={t("offers.gallery.prevPhoto")}
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={handleNext}
              title={t("offers.gallery.nextPhoto")}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-neutral-900/75 hover:bg-neutral-900 text-white backdrop-blur-md shadow-md opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100 focus:outline-none cursor-pointer"
              aria-label={t("offers.gallery.nextPhoto")}
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            {/* Counter pill */}
            <div className="pointer-events-none absolute bottom-2.5 right-2.5 flex items-center gap-1 px-2 py-0.5 rounded-md bg-neutral-900/80 text-white text-xs font-mono backdrop-blur-md shadow border border-neutral-700/50">
              <Images className="w-3.5 h-3.5 text-neutral-400" />
              <span>
                {t("offers.gallery.photoCount", {
                  current: activeIndex + 1,
                  total: allImages.length,
                })}
              </span>
            </div>
          </>
        )}
      </div>

      {/* Thumbnail strip (when more than 1 image) */}
      {allImages.length > 1 && (
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 pt-0.5 scrollbar-thin">
          {previewImages.map((imgUrl, idx) => {
            const isSelected = idx === activeIndex;
            return (
              <button
                key={`${imgUrl}-${idx}`}
                type="button"
                onClick={() => setActiveIndex(idx)}
                className={`relative shrink-0 w-14 h-11 rounded-md overflow-hidden border transition-all cursor-pointer ${
                  isSelected
                    ? "border-primary ring-2 ring-primary/40 scale-102"
                    : "border-border/60 opacity-60 hover:opacity-100 hover:border-border"
                }`}
                title={t("offers.gallery.thumbnail", { index: idx + 1 })}
                aria-label={t("offers.gallery.thumbnail", { index: idx + 1 })}
              >
                <img
                  src={imgUrl}
                  alt={t("offers.gallery.thumbnail", { index: idx + 1 })}
                  className="w-full h-full object-cover"
                  loading="lazy"
                  decoding="async"
                  referrerPolicy="no-referrer"
                />
              </button>
            );
          })}

          {remainingThumbnails > 0 && (
            <button
              type="button"
              onClick={() => setIsLightboxOpen(true)}
              className="relative shrink-0 w-14 h-11 rounded-md overflow-hidden border border-border/80 bg-muted/60 hover:bg-muted text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center cursor-pointer"
              title={t("offers.gallery.openFullscreen")}
              aria-label={t("offers.gallery.openFullscreen")}
            >
              +{remainingThumbnails}
            </button>
          )}
        </div>
      )}

      {/* Fullscreen Lightbox Modal */}
      <ImageLightboxModal
        isOpen={isLightboxOpen}
        onClose={() => setIsLightboxOpen(false)}
        images={allImages}
        activeIndex={activeIndex}
        onSelectIndex={setActiveIndex}
        title={title}
      />
    </div>
  );
}
