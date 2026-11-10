import { useTranslation } from "react-i18next";
import { Check, Minus } from "lucide-react";
import type { OfferAttributeSchema } from "@/lib/api/types.gen";
import { Badge } from "@/components/ui/badge";

interface OfferAttributeBadgeProps {
  attribute: OfferAttributeSchema;
  compact?: boolean;
}

export function OfferAttributeBadge({
  attribute,
  compact = false,
}: OfferAttributeBadgeProps) {
  const { t } = useTranslation();
  const label = attribute.label || attribute.name;
  const isBoolean =
    attribute.type === "boolean" || typeof attribute.value === "boolean";
  const boolValue = Boolean(attribute.value);

  // Formatted display text using backend's display or value + unit
  const displayText =
    attribute.display ??
    (isBoolean
      ? boolValue
        ? t("offers.attributes.yes")
        : t("offers.attributes.no")
      : `${attribute.value}${attribute.unit ? ` ${attribute.unit}` : ""}`);

  if (compact) {
    if (isBoolean) {
      if (!boolValue) return null; // In compact mode, omit negative flags to save space
      return (
        <Badge
          variant="secondary"
          className="text-xs font-normal gap-1 px-2 py-0.5 bg-muted/80 text-foreground border border-border/50"
        >
          <Check className="w-3 h-3 text-emerald-500 shrink-0" />
          <span>{label}</span>
        </Badge>
      );
    }

    return (
      <Badge
        variant="secondary"
        className="text-xs font-normal gap-1 px-2 py-0.5 bg-muted/70 text-foreground border border-border/50"
      >
        <span className="text-muted-foreground">{label}:</span>
        <span className="font-medium">{displayText}</span>
      </Badge>
    );
  }

  // Clean paired row: borderless with subtle muted background, no heavy "cardception"
  return (
    <div className="flex flex-col justify-center py-1.5 px-2.5 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
      <span className="text-xs text-muted-foreground truncate">{label}</span>

      <div className="flex items-center gap-1.5 mt-0.5">
        {isBoolean ? (
          <span
            className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md ${
              boolValue
                ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {boolValue ? (
              <Check className="w-3 h-3" />
            ) : (
              <Minus className="w-3 h-3" />
            )}
            <span>{displayText}</span>
          </span>
        ) : (
          <span className="text-xs font-semibold text-foreground truncate">
            {displayText}
          </span>
        )}
      </div>
    </div>
  );
}
