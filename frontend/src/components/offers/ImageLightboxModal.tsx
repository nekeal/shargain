import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { ChevronLeft, ChevronRight, Images, X } from "lucide-react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export interface ImageLightboxModalProps {
  isOpen: boolean;
  onClose: () => void;
  images: Array<string>;
  activeIndex: number;
  onSelectIndex: (index: number) => void;
  title: string;
}

export function ImageLightboxModal({
  isOpen,
  onClose,
  images,
  activeIndex,
  onSelectIndex,
  title,
}: ImageLightboxModalProps) {
  const { t } = useTranslation();

  // Keyboard navigation when fullscreen lightbox is open
  useEffect(() => {
    if (!isOpen || images.length <= 1) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") {
        onSelectIndex((activeIndex - 1 + images.length) % images.length);
      } else if (e.key === "ArrowRight") {
        onSelectIndex((activeIndex + 1) % images.length);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, activeIndex, images.length, onSelectIndex]);

  if (!isOpen || images.length === 0) return null;

  const currentImage = images[activeIndex] || images[0];

  const handlePrev = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    onSelectIndex((activeIndex - 1 + images.length) % images.length);
  };

  const handleNext = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    onSelectIndex((activeIndex + 1) % images.length);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        className="fixed inset-0 top-0 left-0 translate-x-0 translate-y-0 w-screen h-screen max-w-none sm:max-w-none p-4 sm:p-6 bg-black/95 text-white border-0 rounded-none flex flex-col justify-between gap-0 z-50 m-0"
        showCloseButton={false}
      >
        <DialogTitle className="sr-only">
          {title} - {t("offers.gallery.openFullscreen")}
        </DialogTitle>

        {/* Lightbox Header */}
        <div className="flex items-center justify-between text-white z-10 w-full max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-neutral-800/80 text-xs font-mono text-neutral-200 border border-neutral-700">
              <Images className="w-3.5 h-3.5 text-neutral-400" />
              <span>
                {t("offers.gallery.photoCount", {
                  current: activeIndex + 1,
                  total: images.length,
                })}
              </span>
            </div>
            <span className="text-sm font-medium text-neutral-300 truncate max-w-md hidden sm:inline">
              {title}
            </span>
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="rounded-full bg-neutral-800/80 hover:bg-neutral-700 text-neutral-200 hover:text-white"
            title={t("offers.gallery.close")}
            aria-label={t("offers.gallery.close")}
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Lightbox Main Stage */}
        <div className="relative flex-1 flex items-center justify-center my-2 overflow-hidden w-full">
          {images.length > 1 && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handlePrev}
              className="absolute left-3 sm:left-8 top-1/2 -translate-y-1/2 z-30 w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-black/75 hover:bg-black/95 text-white backdrop-blur-md shadow-2xl border border-white/30 transition-all hover:scale-110 active:scale-95 cursor-pointer focus:outline-none focus:ring-2 focus:ring-white/70"
              title={t("offers.gallery.prevPhoto")}
              aria-label={t("offers.gallery.prevPhoto")}
            >
              <ChevronLeft className="w-7 h-7 sm:w-10 sm:h-10" />
            </Button>
          )}

          <div className="relative flex items-center justify-center max-h-[78vh] max-w-[85vw] select-none mx-auto">
            <img
              src={currentImage}
              alt={`${title} - ${t("offers.gallery.thumbnail", { index: activeIndex + 1 })}`}
              className="max-h-[78vh] max-w-[85vw] w-auto h-auto object-contain rounded-lg shadow-2xl transition-all"
              decoding="async"
              referrerPolicy="no-referrer"
            />
          </div>

          {images.length > 1 && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleNext}
              className="absolute right-3 sm:right-8 top-1/2 -translate-y-1/2 z-30 w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-black/75 hover:bg-black/95 text-white backdrop-blur-md shadow-2xl border border-white/30 transition-all hover:scale-110 active:scale-95 cursor-pointer focus:outline-none focus:ring-2 focus:ring-white/70"
              title={t("offers.gallery.nextPhoto")}
              aria-label={t("offers.gallery.nextPhoto")}
            >
              <ChevronRight className="w-7 h-7 sm:w-10 sm:h-10" />
            </Button>
          )}
        </div>

        {/* Lightbox Bottom Thumbnail strip */}
        {images.length > 1 && (
          <div className="flex items-center justify-center gap-2 overflow-x-auto py-2 z-10 scrollbar-thin w-full max-w-4xl mx-auto">
            {images.map((imgUrl, idx) => {
              const isSelected = idx === activeIndex;
              return (
                <button
                  key={`lb-thumb-${imgUrl}-${idx}`}
                  type="button"
                  onClick={() => onSelectIndex(idx)}
                  className={`relative shrink-0 w-16 h-12 rounded-md overflow-hidden border transition-all cursor-pointer ${
                    isSelected
                      ? "border-primary ring-2 ring-primary/60 scale-105"
                      : "border-neutral-700 opacity-50 hover:opacity-100 hover:border-neutral-500"
                  }`}
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
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
