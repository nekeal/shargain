import { useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { ChevronDown, Plus, Search, X } from "lucide-react";
import type { AvailableFieldSchema } from "@/lib/api/types.gen";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import cn from "@/lib/utils";

interface NotificationFieldsPickerProps {
  availableFields: Array<AvailableFieldSchema>;
  selectedFields: Array<string>;
  onChange: (next: Array<string>) => void;
}

export function NotificationFieldsPicker({
  availableFields,
  selectedFields,
  onChange,
}: NotificationFieldsPickerProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const searchRef = useRef<HTMLInputElement>(null);

  const matchesQuery = (field: AvailableFieldSchema, q: string) => {
    const needle = q.trim().toLowerCase();
    if (!needle) return true;
    return (
      field.label.toLowerCase().includes(needle) ||
      field.name.toLowerCase().includes(needle)
    );
  };

  const visibleFields = useMemo(
    () => availableFields.filter((field) => matchesQuery(field, query)),
    [availableFields, query],
  );

  const selectedSet = useMemo(() => new Set(selectedFields), [selectedFields]);
  const chips = useMemo(
    () => availableFields.filter((field) => selectedSet.has(field.name)),
    [availableFields, selectedSet],
  );
  const selectedCount = chips.length;

  const visibleSelectedCount = visibleFields.filter((f) => selectedSet.has(f.name)).length;
  const allVisibleSelected =
    visibleFields.length > 0 && visibleSelectedCount === visibleFields.length;

  const applySelection = (next: Set<string>) => {
    onChange(availableFields.map((field) => field.name).filter((name) => next.has(name)));
  };

  const toggleField = (name: string) => {
    const next = new Set(selectedSet);
    if (next.has(name)) {
      next.delete(name);
    } else {
      next.add(name);
    }
    applySelection(next);
  };

  const toggleAllVisible = () => {
    const visibleNames = visibleFields.map((field) => field.name);
    const next = new Set(selectedSet);
    visibleNames.forEach((name) => {
      if (allVisibleSelected) {
        next.delete(name);
      } else {
        next.add(name);
      }
    });
    applySelection(next);
  };

  const handleOpenChange = (nextOpen: boolean) => {
    setOpen(nextOpen);
    if (!nextOpen) setQuery("");
  };

  const preventTriggerToggle = (e: React.SyntheticEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  return (
    <Popover open={open} onOpenChange={handleOpenChange}>
      <PopoverTrigger asChild>
        <div
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              handleOpenChange(!open);
            }
          }}
          className={cn(
            "flex min-h-9 w-full cursor-pointer flex-wrap items-center gap-1.5 rounded-md border border-input bg-background px-2 py-1.5",
            "text-left text-sm transition-colors hover:border-primary/50",
            "focus:outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
          )}
        >
          {chips.length > 0 && (
            <div className="flex max-h-24 w-full flex-wrap gap-1.5 overflow-y-auto">
              {chips.map((field) => (
                <Badge key={field.name} variant="secondary" className="pr-1">
                  {field.label}
                  {field.unit && (
                    <span className="text-muted-foreground">({field.unit})</span>
                  )}
                  <button
                    type="button"
                    onClick={(e) => {
                      preventTriggerToggle(e);
                      toggleField(field.name);
                    }}
                    aria-label={t("urlSettings.removeField", { label: field.label })}
                    className="rounded-sm p-0.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}
          {chips.length === 0 ? (
            <span className="text-muted-foreground">
              {t("urlSettings.triggerPlaceholder")}
            </span>
          ) : (
            <span
              className="inline-flex h-5 items-center gap-0.5 rounded-md border border-dashed border-border px-1.5 text-xs text-muted-foreground"
              aria-hidden="true"
            >
              <Plus className="w-3 h-3" />
              {t("urlSettings.addFields")}
            </span>
          )}
          <span className="ml-auto flex shrink-0 items-center gap-1.5">
            <span className="text-xs font-medium text-muted-foreground">
              {selectedCount}/{availableFields.length}
            </span>
            <ChevronDown
              className={cn(
                "w-3.5 h-3.5 text-muted-foreground transition-transform duration-200",
                open && "rotate-180",
              )}
            />
          </span>
        </div>
      </PopoverTrigger>

      <PopoverContent
        align="start"
        sideOffset={4}
        className="w-[340px] p-0"
        onOpenAutoFocus={(e) => {
          e.preventDefault();
          searchRef.current?.focus();
        }}
      >
        <div className="flex items-center gap-2 border-b border-border px-3 py-2">
          <Search className="w-4 h-4 shrink-0 text-muted-foreground" />
          <Input
            ref={searchRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("urlSettings.searchPlaceholder")}
            aria-label={t("urlSettings.searchPlaceholder")}
            className="h-8 border-0 bg-transparent px-0 shadow-none focus-visible:ring-0"
          />
        </div>

        <div className="flex items-center justify-between border-b border-border px-3 py-1.5">
          <span className="text-xs text-muted-foreground">
            {t("urlSettings.selectedCount", {
              selected: selectedCount,
              total: availableFields.length,
            })}
          </span>
          {visibleFields.length > 0 && (
            <button
              type="button"
              onClick={toggleAllVisible}
              className="rounded-sm text-xs font-medium text-primary transition-colors hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {allVisibleSelected ? t("urlSettings.clear") : t("urlSettings.selectAll")}
            </button>
          )}
        </div>

        {visibleFields.length === 0 ? (
          <p className="px-3 py-3 text-xs text-muted-foreground">
            {t("urlSettings.noResults", { query })}
          </p>
        ) : (
          <div
            role="listbox"
            aria-label={t("urlSettings.notificationFields")}
            className="max-h-[min(280px,calc(var(--radix-popover-content-available-height)_-_76px))] overflow-y-auto p-1.5"
          >
            {visibleFields.map((field) => (
              <label
                key={field.name}
                className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 transition-colors hover:bg-accent"
              >
                <input
                  type="checkbox"
                  checked={selectedSet.has(field.name)}
                  onChange={() => toggleField(field.name)}
                  className="h-3.5 w-3.5 shrink-0 rounded border-border accent-primary"
                />
                <span className="text-sm">{field.label}</span>
                {field.unit && (
                  <span className="ml-auto text-xs text-muted-foreground">
                    ({field.unit})
                  </span>
                )}
              </label>
            ))}
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
