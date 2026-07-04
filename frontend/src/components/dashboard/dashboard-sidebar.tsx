import { useEffect, useRef, useState } from "react"
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
}

function getQuotaProgressVariant(used: number, limit: number): "success" | "warning" | "destructive" {
  if (limit <= 0 || used >= limit) {
    return "destructive"
  }
  if (used / limit >= 0.8) {
    return "warning"
  }
  return "success"
}

export default function DashboardSidebar({ offerMonitor }: DashboardSidebarProps) {
  const { t } = useTranslation();
  type Status = 'idle' | 'loading' | 'success' | 'error'
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
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

  useEffect(() => {
    return () => clearTimeout(timerRef.current);
  }, []);

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

    timerRef.current = setTimeout(() => {
      setStatus('idle')
      setMessage('')
    }, 3000)
  }

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card className="bg-card border border-border">
        <CardHeader>
          <CardTitle className="flex items-center text-base font-medium">
            <AlertCircle className="w-4 h-4 mr-2 text-primary" aria-hidden="true" />
            {t('dashboard.sidebar.status.title')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('dashboard.sidebar.status.activeWebsites')}</span>
            <Badge variant="success" className="border-0">
              {offerMonitor.urls.filter((url) => url.isActive).length}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('dashboard.sidebar.status.totalWebsites')}</span>
            <Badge variant="default" className="border-0">{offerMonitor.urls.length}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{t('dashboard.sidebar.status.notifications')}</span>
            <Badge variant={offerMonitor.enableNotifications ? "success" : "secondary"} className="border-0">
              {offerMonitor.enableNotifications ? t('dashboard.sidebar.status.enabled') : t('dashboard.sidebar.status.disabled')}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Quota Card */}
      <Card className="bg-card border border-border">
        <CardHeader>
          <CardTitle className="text-base font-medium">{t('dashboard.sidebar.quotas.title')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {scrapingUrlQuota ? (
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{t('dashboard.sidebar.quotas.scrapingUrls')}</span>
                <Badge variant={getQuotaProgressVariant(scrapingUrlQuota.used, scrapingUrlQuota.limit)}>
                  {scrapingUrlQuota.used} / {scrapingUrlQuota.limit}
                </Badge>
              </div>
              {scrapingUrlQuota.used >= scrapingUrlQuota.limit ? (
                <p className="text-xs text-warning">{t('dashboard.sidebar.quotas.scrapingUrlsAction')}</p>
              ) : null}
            </div>
          ) : null}
          {currentTargetOffersQuota ? (
            <div
              key={`${currentTargetOffersQuota.slug}-${currentTargetOffersQuota.targetId ?? "unknown"}`}
              className="space-y-1"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm text-muted-foreground truncate">{t('dashboard.sidebar.quotas.offers')}</span>
                <Badge variant={getQuotaProgressVariant(currentTargetOffersQuota.used, currentTargetOffersQuota.limit)}>
                  {currentTargetOffersQuota.used} / {currentTargetOffersQuota.limit}
                </Badge>
              </div>
              {currentTargetOffersQuota.used >= currentTargetOffersQuota.limit ? (
                <p className="text-xs text-warning">
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
      <Card className="bg-card border border-border">
        <CardHeader>
          <CardTitle className="text-base font-medium">{t('dashboard.sidebar.quickActions.title')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button
            variant="outline"
            className="w-full justify-start"
            onClick={handleTestNotification}
            disabled={status !== 'idle'}
          >
            {status === 'loading' && (
              <Loader className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
            )}
            {status === 'success' && (
              <CheckCircle className="w-4 h-4 mr-2 text-success" aria-hidden="true" />
            )}
            {status === 'error' && (
              <XCircle className="w-4 h-4 mr-2 text-destructive" aria-hidden="true" />
            )}
            {status === 'idle' && (
              <Bell className="w-4 h-4 mr-2" aria-hidden="true" />
            )}
            {message || t('dashboard.sidebar.quickActions.testNotifications')}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
