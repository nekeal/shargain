import { useTranslation } from "react-i18next";
import { useEffect, useMemo, useState } from "react";
import { CheckCircle, ChevronDown, Filter, Plus, Save, X } from "lucide-react";
import { createFilterSchemas } from "./filterValidation";
import { useUpdateFiltersMutation } from "./useMonitors";
import type { FiltersConfigSchema, RuleGroupSchema } from "@/lib/api/types.gen";
import type { ZodIssue, z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import cn from "@/lib/utils";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface OfferFiltersProps {
  targetId: number;
  urlId: number;
  initialFilters: FiltersConfigSchema | null;
}

const createEmptyGroup = (): RuleGroupSchema => ({
  logic: "and",
  rules: [{ field: "title", operator: "contains", value: "", caseSensitive: false }],
});

export function OfferFilters({
  targetId,
  urlId,
  initialFilters,
}: OfferFiltersProps) {
  const { t } = useTranslation();
  const [filters, setFilters] = useState<FiltersConfigSchema | null>(initialFilters);
  const [isOpen, setIsOpen] = useState(false);
  const [validationErrors, setValidationErrors] = useState<z.ZodError | null>(null);

  const mutation = useUpdateFiltersMutation(targetId, urlId);

  useEffect(() => {
    setFilters(initialFilters);
  }, [initialFilters]);

  const { filtersConfigSchema } = useMemo(() => createFilterSchemas(t), [t]);

  const validateFilters = (currentFilters: FiltersConfigSchema | null): boolean => {
    if (!currentFilters || currentFilters.ruleGroups.length === 0) {
      setValidationErrors(null);
      return true;
    }

    const result = filtersConfigSchema.safeParse(currentFilters);

    if (!result.success) {
      setValidationErrors(result.error);
      return false;
    }

    setValidationErrors(null);
    return true;
  };

  const handleFiltersChange = (newFilters: FiltersConfigSchema | null) => {
    setFilters(newFilters);
    validateFilters(newFilters);
  };

  const getFieldError = (path: string): string | undefined => {
    if (!validationErrors) return undefined;
    const error = validationErrors.issues.find(
      (e: ZodIssue) =>
        e.path.join(".") === path || e.path.join(".").startsWith(path),
    );
    return error?.message;
  };

  const handleSave = () => {
    const normalizedFilters = normalizeFilters(filters);
    if (validateFilters(normalizedFilters)) {
      mutation.mutate(normalizedFilters);
    }
  };

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    // Auto-create first group when opening if no filters exist
    if (open && (!filters || filters.ruleGroups.length === 0)) {
      handleFiltersChange({ ruleGroups: [createEmptyGroup()] });
    }
  };

  // Only count rules that have actual values (not empty placeholders)
  const activeRulesCount = filters?.ruleGroups.reduce(
    (acc, g) => acc + g.rules.filter(r => r.value.trim().length > 0).length,
    0
  ) ?? 0;

  // Normalize filters for comparison and saving - empty filters become null
  const normalizeFilters = (f: FiltersConfigSchema | null): FiltersConfigSchema | null => {
    if (!f || f.ruleGroups.length === 0) return null;

    // Filter out rules with empty values, then filter out empty groups
    const cleanedGroups = f.ruleGroups
      .map(g => ({
        ...g,
        rules: g.rules.filter(r => r.value.trim().length > 0)
      }))
      .filter(g => g.rules.length > 0);

    return cleanedGroups.length > 0 ? { ruleGroups: cleanedGroups } : null;
  };

  const hasChanges = JSON.stringify(normalizeFilters(initialFilters)) !== JSON.stringify(normalizeFilters(filters));

  return (
    <Collapsible open={isOpen} onOpenChange={handleOpenChange}>
      {/* Accordion-style trigger */}
      <CollapsibleTrigger asChild>
        <button
          type="button"
          aria-label={isOpen ? t("filters.collapse") : t("filters.expand")}
          className={cn(
            "w-full mt-3 px-3 py-2 flex items-center justify-between",
            "text-sm text-gray-600 hover:text-gray-900",
            "bg-gray-50/80 hover:bg-gray-100/80 rounded-md",
            "transition-colors duration-150",
            "focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-1"
          )}
        >
          <span className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5" />
            <span className="font-medium">{t("filters.title")}</span>
            {activeRulesCount > 0 && !isOpen && (
              <span className="text-xs text-violet-600 bg-violet-100 px-1.5 py-0.5 rounded">
                {activeRulesCount}
              </span>
            )}
          </span>
          <ChevronDown
            className={cn(
              "w-4 h-4 text-gray-400 transition-transform duration-200",
              isOpen && "rotate-180"
            )}
          />
        </button>
      </CollapsibleTrigger>

      <CollapsibleContent className="mt-2">
        <div className="space-y-0">
          {filters?.ruleGroups.map((group, groupIndex) => (
            <div key={groupIndex}>
              {/* Group container - compact */}
              <div className="p-2.5 bg-gray-50/60 border border-gray-200 rounded-md">
                {/* Group header with logic toggle and delete */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-gray-500">
                      {t("filters.matchLabel", { defaultValue: "Match" })}
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        const newGroups = [...filters.ruleGroups];
                        newGroups[groupIndex].logic = group.logic === "and" ? "or" : "and";
                        handleFiltersChange({ ruleGroups: newGroups });
                      }}
                      aria-label={t("filters.toggleLogic", { current: group.logic === "and" ? t("filters.all") : t("filters.any") })}
                      className="inline-flex items-center h-6 p-0.5 bg-gray-200 rounded-md"
                    >
                      <span
                        className={cn(
                          "px-2 py-0.5 text-[11px] font-semibold rounded transition-all",
                          group.logic === "and"
                            ? "bg-white text-gray-900 shadow-sm"
                            : "text-gray-500"
                        )}
                      >
                        {t("filters.all", { defaultValue: "ALL" })}
                      </span>
                      <span
                        className={cn(
                          "px-2 py-0.5 text-[11px] font-semibold rounded transition-all",
                          group.logic === "or"
                            ? "bg-white text-gray-900 shadow-sm"
                            : "text-gray-500"
                        )}
                      >
                        {t("filters.any", { defaultValue: "ANY" })}
                      </span>
                    </button>
                    <span className="text-xs text-gray-500">
                      {t("filters.ofTheFollowing", { defaultValue: "of the following:" })}
                    </span>
                  </div>
                  {filters.ruleGroups.length > 1 && (
                    <button
                      type="button"
                      onClick={() => {
                        const newGroups = [...filters.ruleGroups];
                        newGroups.splice(groupIndex, 1);
                        handleFiltersChange({ ruleGroups: newGroups });
                      }}
                      aria-label={t("filters.deleteGroup", { index: groupIndex + 1 })}
                      className="p-0.5 text-gray-400 hover:text-red-500 transition-colors"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Rules - responsive layout */}
                <div className="space-y-2">
                  {group.rules.map((rule, ruleIndex) => (
                    <div
                      key={ruleIndex}
                      className="flex flex-col sm:flex-row sm:items-center gap-1.5 p-1.5 bg-white/50 rounded border border-gray-100"
                    >
                      <div className="flex items-center gap-1.5">
                        <Select
                          value={rule.field}
                          onValueChange={(value) => {
                            const newGroups = [...filters.ruleGroups];
                            newGroups[groupIndex].rules[ruleIndex].field = value as "title";
                            handleFiltersChange({ ruleGroups: newGroups });
                          }}
                        >
                          <SelectTrigger className="h-8 w-[90px] text-xs px-2 bg-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="title" className="text-xs">
                              {t("filters.field.title")}
                            </SelectItem>
                          </SelectContent>
                        </Select>

                        <Select
                          value={rule.operator}
                          onValueChange={(value) => {
                            const newGroups = [...filters.ruleGroups];
                            newGroups[groupIndex].rules[ruleIndex].operator = value as "contains" | "not_contains";
                            handleFiltersChange({ ruleGroups: newGroups });
                          }}
                        >
                          <SelectTrigger className="h-8 flex-1 sm:w-[150px] sm:flex-none text-xs px-2 bg-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="contains" className="text-xs">
                              {t("filters.operator.contains")}
                            </SelectItem>
                            <SelectItem value="not_contains" className="text-xs">
                              {t("filters.operator.not_contains")}
                            </SelectItem>
                          </SelectContent>
                        </Select>

                        {group.rules.length > 1 && (
                          <button
                            type="button"
                            onClick={() => {
                              const newGroups = [...filters.ruleGroups];
                              newGroups[groupIndex].rules.splice(ruleIndex, 1);
                              handleFiltersChange({ ruleGroups: newGroups });
                            }}
                            aria-label={t("filters.deleteRule")}
                            className="p-1.5 text-gray-400 hover:text-red-500 transition-colors sm:hidden"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>

                      <div className="flex items-center gap-1.5 flex-1">
                        <Input
                          value={rule.value}
                          placeholder={t("filters.valuePlaceholder", { defaultValue: "Enter text..." })}
                          onChange={(e) => {
                            const newGroups = [...filters.ruleGroups];
                            newGroups[groupIndex].rules[ruleIndex].value = e.target.value;
                            handleFiltersChange({ ruleGroups: newGroups });
                          }}
                          className={cn(
                            "h-8 text-xs px-2 bg-white flex-1",
                            getFieldError(`ruleGroups.${groupIndex}.rules.${ruleIndex}.value`) &&
                              "border-red-400 focus:border-red-500 focus:ring-red-500/20"
                          )}
                        />
                        {group.rules.length > 1 && (
                          <button
                            type="button"
                            onClick={() => {
                              const newGroups = [...filters.ruleGroups];
                              newGroups[groupIndex].rules.splice(ruleIndex, 1);
                              handleFiltersChange({ ruleGroups: newGroups });
                            }}
                            aria-label={t("filters.deleteRule")}
                            className="p-1.5 text-gray-400 hover:text-red-500 transition-colors hidden sm:block"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>

                      {getFieldError(`ruleGroups.${groupIndex}.rules.${ruleIndex}.value`) && (
                        <p className="text-[11px] text-red-500 sm:hidden">
                          {getFieldError(`ruleGroups.${groupIndex}.rules.${ruleIndex}.value`)}
                        </p>
                      )}
                    </div>
                  ))}
                </div>

                {/* Add rule button - subtle */}
                <button
                  type="button"
                  onClick={() => {
                    const newGroups = [...filters.ruleGroups];
                    newGroups[groupIndex].rules.push({
                      field: "title",
                      operator: "contains",
                      value: "",
                      caseSensitive: false,
                    });
                    handleFiltersChange({ ruleGroups: newGroups });
                  }}
                  className="mt-2 flex items-center gap-1 text-xs text-gray-500 hover:text-violet-600 transition-colors"
                >
                  <Plus className="w-3 h-3" />
                  {t("filters.addRule")}
                </button>
              </div>

              {/* Logic divider between groups */}
              {groupIndex < filters.ruleGroups.length - 1 && (
                <div className="flex items-center justify-center py-1.5">
                  <div className="flex-1 h-px bg-gray-200" />
                  <Select
                    value={group.logicWithNext || "or"}
                    onValueChange={(value) => {
                      const newGroups = [...filters.ruleGroups];
                      newGroups[groupIndex].logicWithNext = value as "and" | "or";
                      handleFiltersChange({ ruleGroups: newGroups });
                    }}
                  >
                    <SelectTrigger className="h-6 w-14 mx-2 text-[10px] font-semibold px-2 bg-white border-gray-200 text-gray-600">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="and" className="text-xs">{t("filters.logic.and")}</SelectItem>
                      <SelectItem value="or" className="text-xs">{t("filters.logic.or")}</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex-1 h-px bg-gray-200" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Add group button */}
        <button
          type="button"
          onClick={() => {
            const newGroups = [
              ...(filters?.ruleGroups || []),
              createEmptyGroup(),
            ];
            // Set logicWithNext on the previous last group
            if (newGroups.length > 1) {
              newGroups[newGroups.length - 2].logicWithNext = "or";
            }
            handleFiltersChange({ ruleGroups: newGroups });
          }}
          className="w-full mt-2 py-1.5 flex items-center justify-center gap-1.5 text-xs text-gray-500 hover:text-violet-600 border border-dashed border-gray-300 hover:border-violet-400 rounded-md transition-colors"
        >
          <Plus className="w-3 h-3" />
          {t("filters.addGroup")}
        </button>

        {/* Error alert */}
        {mutation.isError && (
          <Alert variant="destructive" className="mt-3 py-2">
            <AlertTitle className="text-sm">{t("filters.errors.saveFailed")}</AlertTitle>
            <AlertDescription className="text-xs">
              {mutation.error.message || "An error occurred."}
            </AlertDescription>
          </Alert>
        )}

        {/* Save button - compact footer */}
        <div className="flex justify-end mt-3 pt-2 border-t border-gray-100">
          <Button
            size="sm"
            onClick={handleSave}
            disabled={mutation.isPending || !hasChanges || !!validationErrors}
            className="h-7 text-xs px-3"
          >
            {mutation.isPending ? (
              <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin mr-1.5" />
            ) : mutation.isSuccess ? (
              <CheckCircle className="w-3 h-3 mr-1.5" />
            ) : (
              <Save className="w-3 h-3 mr-1.5" />
            )}
            {t("filters.save")}
          </Button>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
