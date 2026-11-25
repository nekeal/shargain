import { useTranslation } from "react-i18next";

export function OffersSkeleton() {
  const { t } = useTranslation();

  return (
    <div
      role="status"
      aria-live="polite"
      aria-busy="true"
      className="grid grid-cols-1 lg:grid-cols-12 gap-3 items-stretch flex-1 min-h-0 animate-pulse motion-reduce:animate-none"
    >
      <span className="sr-only">{t("offers.loadingFromBackend")}</span>

      {/* Left column: Queue skeleton */}
      <div className="lg:col-span-4 bg-card border border-border rounded-xl flex flex-col h-full overflow-hidden shadow-sm">
        {/* Header */}
        <div className="p-3 border-b border-border flex items-center justify-between gap-2 bg-muted/20 shrink-0">
          <div className="h-4 w-28 bg-muted rounded" />
          <div className="h-5 w-12 bg-muted rounded-full" />
        </div>

        {/* List items */}
        <div className="flex-1 p-2 space-y-2 overflow-hidden">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              className="p-2.5 rounded-lg bg-muted/15 border border-border/30 flex items-stretch gap-2.5"
            >
              <div className="w-16 h-16 bg-muted rounded-md shrink-0" />
              <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
                <div className="flex items-center justify-between gap-2">
                  <div className="h-4 w-24 bg-muted rounded" />
                  <div className="h-3.5 w-14 bg-muted rounded" />
                </div>
                <div className="h-3.5 w-4/5 bg-muted rounded my-1" />
                <div className="flex items-center justify-between gap-2">
                  <div className="h-3 w-28 bg-muted rounded" />
                  <div className="h-3 w-12 bg-muted rounded" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-2 border-t border-border bg-muted/20 flex items-center justify-between px-3 shrink-0">
          <div className="h-3 w-20 bg-muted rounded" />
          <div className="h-3 w-28 bg-muted rounded" />
        </div>
      </div>

      {/* Right column: Detail Cockpit skeleton */}
      <div className="hidden lg:flex lg:col-span-8 bg-card border border-border rounded-xl flex-col h-full overflow-hidden shadow-sm">
        {/* Command bar */}
        <div className="p-3 border-b border-border flex items-center justify-between gap-3 bg-muted/25 shrink-0">
          <div className="flex items-center gap-2">
            <div className="h-8 w-36 bg-muted rounded-md" />
            <div className="h-8 w-28 bg-muted rounded-md" />
            <div className="h-8 w-24 bg-muted rounded-md" />
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-8 w-24 bg-muted rounded-md" />
            <div className="h-8 w-16 bg-muted rounded-md" />
            <div className="h-8 w-8 bg-muted rounded-md" />
          </div>
        </div>

        {/* Cockpit body */}
        <div className="flex-1 overflow-hidden p-5 space-y-5">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="h-8 w-36 bg-muted rounded" />
              <div className="flex gap-2">
                <div className="h-5 w-20 bg-muted rounded" />
                <div className="h-5 w-16 bg-muted rounded" />
              </div>
            </div>
            <div className="h-5 w-3/4 bg-muted rounded" />
            <div className="h-4 w-32 bg-muted rounded" />
          </div>

          <div className="grid grid-cols-2 gap-4 pt-1 border-t border-border/60">
            <div className="h-44 bg-muted rounded-xl" />
            <div className="space-y-3">
              <div className="h-3.5 w-24 bg-muted rounded" />
              <div className="grid grid-cols-2 gap-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-10 bg-muted/60 rounded-lg" />
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-border/60">
            <div className="h-3.5 w-24 bg-muted rounded" />
            <div className="h-40 bg-muted rounded-xl" />
          </div>
        </div>
      </div>
    </div>
  );
}
