import { useEffect, useMemo, useRef, useState } from "react"
import { Plus, X } from "lucide-react"
import { baseFiltersConfigSchema } from "./monitored-websites/filterValidation"
import type { FiltersConfigSchema, RuleGroupSchema } from "@/lib/api/types.gen"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import cn from "@/lib/utils"

interface FilterEditorProps {
  initialData: FiltersConfigSchema | null
  onSave: (data: FiltersConfigSchema | null) => void
}

const emptyGroup = (): RuleGroupSchema => ({
  logic: "and",
  rules: [{ field: "title", operator: "contains", value: "", caseSensitive: false }],
})

export function FilterEditor({ initialData, onSave }: FilterEditorProps) {
  const [groups, setGroups] = useState<Array<RuleGroupSchema>>(
    () => initialData?.ruleGroups ?? []
  )
  const [snapshot, setSnapshot] = useState(() => JSON.stringify(groups))
  const [status, setStatus] = useState<"idle" | "applied" | "fading">("idle")
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  // Sync local state when initialData changes (e.g., after parent mutation)
  useEffect(() => {
    const newGroups = initialData?.ruleGroups ?? []
    setGroups(newGroups)
    setSnapshot(JSON.stringify(newGroups))
    setStatus("idle")
  }, [initialData])

  const isDirty = JSON.stringify(groups) !== snapshot
  const totalRules = groups.reduce((a, g) => a + g.rules.length, 0)
  const isFading = status === "fading"

  const validationError = useMemo(() => {
    if (!isDirty) return null
    const cleaned = groups
      .map((g) => ({ ...g, rules: g.rules.filter((r) => r.value.trim()) }))
      .filter((g) => g.rules.length > 0)
    const result = cleaned.length > 0 ? { ruleGroups: cleaned } : null
    const validation = baseFiltersConfigSchema.safeParse(result)
    if (!validation.success) {
      const errors = validation.error.flatten()
      return errors.formErrors.length > 0 ? errors.formErrors.join("; ") : "Invalid filter configuration"
    }
    return null
  }, [groups, isDirty])

  const handleApply = () => {
    const cleaned = groups
      .map((g) => ({ ...g, rules: g.rules.filter((r) => r.value.trim()) }))
      .filter((g) => g.rules.length > 0)
    const result = cleaned.length > 0 ? { ruleGroups: cleaned } : null

    // Validate against backend constraints
    const validation = baseFiltersConfigSchema.safeParse(result)
    if (!validation.success) {
      console.warn("Filter validation failed:", validation.error.flatten())
    }

    setSnapshot(JSON.stringify(groups))
    setStatus("applied")
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      setStatus("fading")
      setTimeout(() => setStatus("idle"), 300)
    }, 2000)

    onSave(result)
  }

  const addRule = (gIdx: number) => {
    setGroups((prev) =>
      prev.map((g, i) =>
        i !== gIdx
          ? g
          : {
              ...g,
              rules: [
                ...g.rules,
                { field: "title", operator: "contains", value: "", caseSensitive: false },
              ],
            }
      )
    )
  }

  const removeRule = (gIdx: number, rIdx: number) => {
    setGroups((prev) =>
      prev.map((g, i) =>
        i !== gIdx ? g : { ...g, rules: g.rules.filter((_, j) => j !== rIdx) }
      )
    )
  }

  const updateRule = (gIdx: number, rIdx: number, field: string, val: string) => {
    setGroups((prev) =>
      prev.map((g, i) =>
        i !== gIdx
          ? g
          : {
              ...g,
              rules: g.rules.map((r, j) => (j !== rIdx ? r : { ...r, [field]: val })),
            }
      )
    )
  }

  const addGroup = () => {
    setGroups((prev) => [...prev, emptyGroup()])
  }

  return (
    <div>
      <div className="space-y-3">
        <div className="text-xs text-muted-foreground">
          {totalRules} rule{totalRules !== 1 ? "s" : ""} &middot; {groups.length} group
          {groups.length !== 1 ? "s" : ""}
        </div>

        {groups.map((group, gIdx) => (
          <div key={gIdx} className="bg-secondary/30 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-2.5 py-1.5">
              <span className="text-xs font-medium text-muted-foreground">
                Group {gIdx + 1} <span className="text-muted-foreground/50">(AND)</span>
              </span>
              {groups.length > 1 && (
                <button
                  onClick={() => setGroups(groups.filter((_, i) => i !== gIdx))}
                  className="p-0.5 rounded text-muted-foreground/40 hover:text-destructive hover:bg-destructive/10 transition-colors"
                  aria-label={`Delete group ${gIdx + 1}`}
                >
                  <X className="w-3 h-3" aria-hidden="true" />
                </button>
              )}
            </div>

            <div className="px-2.5 pb-2 space-y-1">
              {group.rules.map((rule, rIdx) => (
                <div key={rIdx} className="space-y-1.5">
                  {/* Row 1: Field + Operator */}
                  <div className="flex gap-1.5 w-full">
                    <Select
                      defaultValue={rule.field}
                      onValueChange={(v) => updateRule(gIdx, rIdx, "field", v)}
                    >
                      <SelectTrigger className="flex-1 min-w-0 h-9 text-sm px-2 gap-1 [&>svg]:w-3.5 [&>svg]:h-3.5 [&>svg]:shrink-0 sm:w-[96px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="title" className="text-xs">
                          Title
                        </SelectItem>
                        <SelectItem value="price" className="text-xs">
                          Price
                        </SelectItem>
                        <SelectItem value="description" className="text-xs">
                          Desc.
                        </SelectItem>
                        <SelectItem value="location" className="text-xs">
                          Loc.
                        </SelectItem>
                      </SelectContent>
                    </Select>

                    <Select
                      defaultValue={rule.operator}
                      onValueChange={(v) => updateRule(gIdx, rIdx, "operator", v)}
                    >
                      <SelectTrigger className="flex-1 min-w-0 h-9 text-sm px-2 gap-1 [&>svg]:w-3.5 [&>svg]:h-3.5 [&>svg]:shrink-0 sm:w-[120px]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="contains" className="text-xs">
                          Contains
                        </SelectItem>
                        <SelectItem value="not_contains" className="text-xs">
                          Excludes
                        </SelectItem>
                        <SelectItem value="equals" className="text-xs">
                          Equals
                        </SelectItem>
                        <SelectItem value="less_than" className="text-xs">
                          Under
                        </SelectItem>
                        <SelectItem value="greater_than" className="text-xs">
                          Over
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Row 2: Value + Delete button */}
                  <div className="flex items-center gap-1.5 w-full">
                    <Input
                      defaultValue={rule.value}
                      className="flex-1 min-w-0 h-9 text-sm"
                      placeholder="Value"
                      onChange={(e) => updateRule(gIdx, rIdx, "value", e.target.value)}
                    />

                    {group.rules.length > 1 && (
                      <button
                        onClick={() => removeRule(gIdx, rIdx)}
                        className="p-0.5 rounded text-muted-foreground/30 hover:text-destructive hover:bg-destructive/10 transition-colors shrink-0"
                        aria-label="Delete rule"
                      >
                        <X className="w-3 h-3" aria-hidden="true" />
                      </button>
                    )}
                  </div>
                </div>
              ))}

              <button
                onClick={() => addRule(gIdx)}
                className="flex items-center gap-1 text-xs text-primary/60 hover:text-primary py-1 transition-colors"
              >
                <Plus className="w-3 h-3" aria-hidden="true" /> Add rule
              </button>
            </div>
          </div>
        ))}

        <button
          onClick={addGroup}
          className="w-full flex items-center justify-center gap-1.5 text-xs text-muted-foreground hover:text-foreground py-2 border border-dashed border-border/60 hover:border-border rounded-lg transition-colors"
        >
          <Plus className="w-3 h-3" aria-hidden="true" /> Add group (OR)
        </button>
      </div>

      {/* Apply bar */}
      {isDirty && status === "idle" && (
        <div className="sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10">
          <span className="text-xs flex items-center gap-1.5 text-warning-muted-foreground">
            <span className="w-1.5 h-1.5 rounded-full bg-warning" />
            Unsaved changes
          </span>
          <div className="flex items-center gap-2">
            {validationError && (
              <span className="text-xs text-destructive max-w-[200px] truncate" title={validationError} role="alert">
                {validationError}
              </span>
            )}
            <Button size="sm" className="h-7 text-xs" onClick={handleApply} disabled={!!validationError}>
              Apply
            </Button>
          </div>
        </div>
      )}
{status === "applied" && (
        <div
          className={cn(
            "sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10 transition-opacity duration-300",
            isFading && "opacity-0"
          )}
        >
          <span className="text-xs flex items-center gap-1.5 text-success-muted-foreground">
            <svg
              className="w-3.5 h-3.5 text-success"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Applied
          </span>
          <span className="text-xs text-muted-foreground">
            {totalRules} rule{totalRules !== 1 ? "s" : ""}
          </span>
        </div>
      )}
    </div>
  )
}
