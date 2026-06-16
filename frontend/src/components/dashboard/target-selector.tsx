import { useTranslation } from "react-i18next"
import { Globe } from "lucide-react"
import type { TargetSummaryResponse } from "@/lib/api/types.gen"
import { useAuth } from "@/context/auth"
import cn from "@/lib/utils"
import { Badge } from "@/components/ui/badge"

interface TargetSelectorProps {
    targets: Array<TargetSummaryResponse>
    selectedTargetId: number | null
    onSelect: (targetId: number) => void
}

export function TargetSelector({ targets, selectedTargetId, onSelect }: TargetSelectorProps) {
    const { t } = useTranslation()
    const { user } = useAuth()

    return (
        <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
            <div className="container mx-auto px-4 py-8 max-w-6xl">
                <div className="mb-8">
                    <h1 className="text-2xl font-semibold text-gray-900">{t('dashboard.greeting', { name: user?.username || '' })}</h1>
                    <p className="text-sm text-gray-500">{t('dashboard.subtitle')}</p>
                </div>

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {targets.map((target) => (
                        <button
                            key={target.id}
                            onClick={() => onSelect(target.id)}
                            className={cn(
                                "text-left bg-white/70 backdrop-blur-sm rounded-2xl p-6 border transition-all duration-300 hover:shadow-lg hover:scale-[1.02]",
                                selectedTargetId === target.id
                                    ? "border-violet-500 ring-2 ring-violet-200"
                                    : "border-gray-100 hover:border-violet-300"
                            )}
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <div className="p-2 bg-violet-100 rounded-lg">
                                    <Globe className="w-5 h-5 text-violet-600" />
                                </div>
                                <h3 className="font-semibold text-gray-900 truncate">{target.name}</h3>
                            </div>
                            <div className="flex items-center gap-2">
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
                                <span className="text-sm text-gray-500">
                                    {t('dashboard.targetSelector.urlCount', { count: target.urlCount })}
                                </span>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}
