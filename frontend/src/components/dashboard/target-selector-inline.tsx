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
        >
            <SelectTrigger className="max-w-50 sm:max-w-full border-violet-200 hover:border-violet-300 focus:ring-violet-500">
                <Globe className="size-4 text-violet-500 shrink-0" />
                <SelectValue placeholder="Select a target" />
            </SelectTrigger>
            <SelectContent>
                {targets.map((target) => (
                    <SelectItem key={target.id} value={String(target.id)}>
                        <span className="flex items-center gap-2">
                            {target.name}
                            <Badge
                                className={cn(
                                    "border-0",
                                    target.isActive
                                        ? "bg-green-100 text-green-800"
                                        : "bg-gray-100 text-gray-600"
                                )}
                            >
                                {target.isActive
                                    ? t('dashboard.monitoredWebsites.active')
                                    : t('dashboard.monitoredWebsites.paused')}
                            </Badge>
                        </span>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    )
}
