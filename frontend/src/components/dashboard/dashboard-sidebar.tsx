import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { AlertCircle, Bell, CheckCircle, Loader, XCircle } from "lucide-react"
import type { OfferMonitor } from "@/types/dashboard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { getQuotaStatus, sendTargetTestNotification } from "@/lib/api/sdk.gen"

interface DashboardSidebarProps {
  offerMonitor: OfferMonitor
  isVisible: boolean
}

export default function DashboardSidebar({ offerMonitor, isVisible }: DashboardSidebarProps) {
  const { t } = useTranslation();
  type Status = 'idle' | 'loading' | 'success' | 'error'
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const { data: quotaStatus } = useQuery({
    queryKey: ['quotaStatus'],
    queryFn: () => getQuotaStatus(),
    staleTime: 30_000,
  })
  const quotaRows = quotaStatus?.data.quotas ?? []
  const scrapingUrlQuota = quotaRows.find(
    (row) => row.slug === "scraping_urls" && row.targetId === offerMonitor.id,
  )
  const currentTargetOffersQuota = quotaRows.find(
    (row) => row.slug === "offers" && row.targetId === offerMonitor.id,
  )

  const handleTestNotification = async () => {
    setStatus('loading')
    setMessage('')

    try {
      await sendTargetTestNotification({
        path: { target_id: offerMonitor.id },
      })
      setStatus('success')
      setMessage(t('dashboard.sidebar.testNotification.success'))
    } catch (e) {
      setStatus('error')
      setMessage(t('dashboard.sidebar.testNotification.error'))
    }

    setTimeout(() => {
      setStatus('idle')
      setMessage('')
    }, 3000)
  }

  const getQuotaBadgeClassName = (used: number, limit: number) => {
    if (limit <= 0 || used >= limit) {
      return "bg-red-100 text-red-800 border-0"
    }
    if (used / limit >= 0.8) {
      return "bg-yellow-100 text-yellow-800 border-0"
    }
    return "bg-green-100 text-green-800 border-0"
  }

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card
        className={`border-0 bg-white/60 backdrop-blur-sm transition-all duration-700 delay-600 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
          }`}
      >
        <CardHeader>
          <CardTitle className="flex items-center text-lg">
            <AlertCircle className="w-5 h-5 mr-2 text-violet-600" />
            {t('dashboard.sidebar.status.title')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{t('dashboard.sidebar.status.activeWebsites')}</span>
            <Badge className="bg-green-100 text-green-800 border-0">
              {offerMonitor.urls.filter((url) => url.isActive).length}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{t('dashboard.sidebar.status.totalWebsites')}</span>
            <Badge className="bg-violet-100 text-violet-800 border-0">{offerMonitor.urls.length}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{t('dashboard.sidebar.status.notifications')}</span>
            <Badge
              className={`border-0 ${offerMonitor.enableNotifications ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"
                }`}
            >
              {offerMonitor.enableNotifications ? t('dashboard.sidebar.status.enabled') : t('dashboard.sidebar.status.disabled')}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Quota Card */}
      <Card
        className={`border-0 bg-white/60 backdrop-blur-sm transition-all duration-700 delay-700 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
          }`}
      >
        <CardHeader>
          <CardTitle className="text-lg">{t('dashboard.sidebar.quotas.title')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {scrapingUrlQuota ? (
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t('dashboard.sidebar.quotas.scrapingUrls')}</span>
                <Badge className={getQuotaBadgeClassName(scrapingUrlQuota.used, scrapingUrlQuota.limit)}>
                  {scrapingUrlQuota.used} / {scrapingUrlQuota.limit}
                </Badge>
              </div>
              {scrapingUrlQuota.used >= scrapingUrlQuota.limit ? (
                <p className="text-xs text-amber-700">{t('dashboard.sidebar.quotas.scrapingUrlsAction')}</p>
              ) : null}
            </div>
          ) : null}
          {currentTargetOffersQuota ? (
            <div
              key={`${currentTargetOffersQuota.slug}-${currentTargetOffersQuota.targetId ?? "unknown"}`}
              className="space-y-1"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm text-gray-600 truncate">{t('dashboard.sidebar.quotas.offers')}</span>
                <Badge className={getQuotaBadgeClassName(currentTargetOffersQuota.used, currentTargetOffersQuota.limit)}>
                  {currentTargetOffersQuota.used} / {currentTargetOffersQuota.limit}
                </Badge>
              </div>
              {currentTargetOffersQuota.used >= currentTargetOffersQuota.limit ? (
                <p className="text-xs text-amber-700">
                  {t('dashboard.sidebar.quotas.offersAction')}
                  {currentTargetOffersQuota.periodEnd
                    ? ` ${new Date(currentTargetOffersQuota.periodEnd).toLocaleDateString()}`
                    : ""}
                </p>
              ) : null}
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card
        className={`border-0 bg-white/60 backdrop-blur-sm transition-all duration-700 delay-800 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
          }`}
      >
        <CardHeader>
          <CardTitle className="text-lg">{t('dashboard.sidebar.quickActions.title')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button
            variant="outline"
            className="w-full justify-start border-violet-200 text-violet-600 hover:bg-violet-50 transition-all duration-300 hover:scale-105 bg-transparent"
            onClick={handleTestNotification}
            disabled={status !== 'idle'}
          >
            {status === 'loading' ? (
              <Loader className="w-4 h-4 mr-2 animate-spin" />
            ) : status === 'success' ? (
              <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
            ) : status === 'error' ? (
              <XCircle className="w-4 h-4 mr-2 text-red-500" />
            ) : (
              <Bell className="w-4 h-4 mr-2" />
            )}
            {message || t('dashboard.sidebar.quickActions.testNotifications')}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
