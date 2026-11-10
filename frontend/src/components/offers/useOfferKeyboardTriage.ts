import { useCallback, useEffect, useRef } from "react";
import type { PublicOfferSchema } from "@/lib/api/types.gen";

export interface UseOfferKeyboardTriageOptions {
  offers: Array<PublicOfferSchema>;
  selectedOfferId: number;
  setSelectedOfferId: React.Dispatch<React.SetStateAction<number>>;
  isDetailsOpen: boolean;
  onToggleLike: (offerId: number, currentlyLiked: boolean) => void;
  onToggleSeen: (offerId: number, currentlySeen: boolean) => void;
}

export function useOfferKeyboardTriage({
  offers,
  selectedOfferId,
  setSelectedOfferId,
  isDetailsOpen,
  onToggleLike,
  onToggleSeen,
}: UseOfferKeyboardTriageOptions) {
  const activeIndex = offers.findIndex((o) => o.id === selectedOfferId);
  const activeOffer = offers[activeIndex >= 0 ? activeIndex : 0];

  const offersRef = useRef(offers);
  useEffect(() => {
    offersRef.current = offers;
  }, [offers]);

  const selectedOfferIdRef = useRef(selectedOfferId);
  useEffect(() => {
    selectedOfferIdRef.current = selectedOfferId;
  }, [selectedOfferId]);

  // Auto-mark offer as seen after 1 second of inspection ONLY when details panel is open
  useEffect(() => {
    if (!isDetailsOpen || activeOffer.isSeen) return;

    const timer = setTimeout(() => {
      onToggleSeen(activeOffer.id, false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [activeOffer.id, activeOffer.isSeen, isDetailsOpen, onToggleSeen]);

  // Preload adjacent offers' main images in background for instant switching
  useEffect(() => {
    if (activeIndex < 0) return;

    const candidateOffers = [
      offers[activeIndex + 1],
      offers[activeIndex + 2],
      offers[activeIndex - 1],
    ].filter((o): o is PublicOfferSchema => Boolean(o));

    candidateOffers.forEach((candidate) => {
      if (candidate.mainImageUrl) {
        const img = new Image();
        img.decoding = "async";
        img.referrerPolicy = "no-referrer";
        img.src = candidate.mainImageUrl;
      }
    });
  }, [activeIndex, offers]);

  // Synchronous functional updates prevent state desync during rapid keyboard triage
  const handleNext = useCallback(() => {
    setSelectedOfferId((currentId) => {
      const currentOffers = offersRef.current;
      const currentIndex = currentOffers.findIndex((o) => o.id === currentId);
      if (currentIndex >= 0 && currentIndex < currentOffers.length - 1) {
        return currentOffers[currentIndex + 1].id;
      }
      return currentId;
    });
  }, [setSelectedOfferId]);

  const handlePrev = useCallback(() => {
    setSelectedOfferId((currentId) => {
      const currentOffers = offersRef.current;
      const currentIndex = currentOffers.findIndex((o) => o.id === currentId);
      if (currentIndex > 0) {
        return currentOffers[currentIndex - 1].id;
      }
      return currentId;
    });
  }, [setSelectedOfferId]);

  const handleMarkSeenAndNext = useCallback(() => {
    setSelectedOfferId((currentId) => {
      const currentOffers = offersRef.current;
      const currentIndex = currentOffers.findIndex((o) => o.id === currentId);
      if (currentIndex >= 0) {
        const currentOffer = currentOffers[currentIndex];
        if (!currentOffer.isSeen) {
          onToggleSeen(currentOffer.id, false);
        }
        if (currentIndex < currentOffers.length - 1) {
          return currentOffers[currentIndex + 1].id;
        }
      }
      return currentId;
    });
  }, [onToggleSeen, setSelectedOfferId]);

  // Global keyboard shortcuts (Vim / Gmail / Supabase style)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeEl = document.activeElement;
      if (
        activeEl &&
        (activeEl.tagName === "INPUT" ||
          activeEl.tagName === "TEXTAREA" ||
          (activeEl as HTMLElement).isContentEditable)
      ) {
        return;
      }

      // Check if any modal dialog is currently open (e.g. ImageLightboxModal)
      if (document.querySelector('[role="dialog"]') != null) {
        return;
      }

      if (offersRef.current.length === 0) return;

      const currentId = selectedOfferIdRef.current;
      const currentOffer =
        offersRef.current.find((o) => o.id === currentId) ?? offersRef.current[0];

      if (e.key === "j" || e.key === "J") {
        e.preventDefault();
        handleMarkSeenAndNext();
      } else if (e.key === "k" || e.key === "K") {
        e.preventDefault();
        handlePrev();
      } else if (e.key === "s" || e.key === "S") {
        e.preventDefault();
        onToggleSeen(currentOffer.id, currentOffer.isSeen);
      } else if (e.key === "l" || e.key === "L") {
        e.preventDefault();
        onToggleLike(currentOffer.id, currentOffer.isLiked);
      } else if (e.key === "o" || e.key === "O") {
        e.preventDefault();
        window.open(currentOffer.url, "_blank", "noopener,noreferrer");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    handleMarkSeenAndNext,
    handlePrev,
    onToggleLike,
    onToggleSeen,
  ]);

  return {
    activeIndex: activeIndex >= 0 ? activeIndex : 0,
    activeOffer,
    handleNext,
    handlePrev,
    handleMarkSeenAndNext,
  };
}
