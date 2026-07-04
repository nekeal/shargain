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
            <SelectTrigger className="w-full">
                <Globe className="size-4 text-primary shrink-0" aria-hidden="true" />
                <SelectValue placeholder={t('dashboard.targetSelector.selectPlaceholder')} />
            </SelectTrigger>
            <SelectContent className="min-w-[var(--radix-select-trigger-width)]">
                {targets.map((target: TargetSummaryResponse) => {
                    const isActive = target.isActive
                    return (
                    <SelectItem key={target.id} value={String(target.id)}>
                        <span className="flex items-center justify-between w-full gap-2">
                            <span className="truncate">{target.name}</span>
                            <Badge
                                variant={isActive ? "success" : "secondary"}
                                className="border-0"
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
