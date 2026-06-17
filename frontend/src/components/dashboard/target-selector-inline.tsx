import { useTranslation } from "react-i18next"
import { Globe } from "lucide-react"
import type { TargetSummaryResponse } from "@/lib/api/types.gen"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import cn from "@/lib/utils"

interface TargetSelectorInlineProps {
    targets: Array<TargetSummaryResponse>
    selectedTargetId: number | null
    onSelect: (targetId: number) => void
}

export function TargetSelectorInline({ targets, selectedTargetId, onSelect }: TargetSelectorInlineProps) {
    const { t } = useTranslation()

    return (
        <Select
            value={selectedTargetId?.toString() ?? ""}
            onValueChange={(val) => onSelect(parseInt(val, 10))}
            disabled={targets.length === 0}
        >
            <SelectTrigger className="w-full border-violet-200 hover:border-violet-300 focus:ring-violet-500 dark:border-violet-800 dark:hover:border-violet-600 dark:focus:ring-violet-400">
                <Globe className="size-4 text-violet-500 dark:text-violet-400 shrink-0" />
                <SelectValue placeholder={t('dashboard.targetSelector.selectPlaceholder')} />
            </SelectTrigger>
            <SelectContent className="min-w-[var(--radix-select-trigger-width)]">
                {targets.map((target) => {
                    const isActive = target.isActive
                    return (
                    <SelectItem key={target.id} value={String(target.id)}>
                        <span className="flex items-center justify-between w-full gap-2">
                            <span className="truncate">{target.name}</span>
                            <Badge
                                className={cn(
                                    "border-0",
                                    isActive
                                        ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                                        : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                                )}
                            >
                                {isActive
                                    ? t('dashboard.monitoredWebsites.active')
                                    : t('dashboard.monitoredWebsites.paused')}
                            </Badge>
                        </span>
                    </SelectItem>
                    )
                })}
            </SelectContent>
        </Select>
    )
}
