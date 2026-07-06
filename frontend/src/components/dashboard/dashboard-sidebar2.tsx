import { useEffect, useRef, useState } from "react"
import { useMutation, useQuery, useQueryClient  } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { Bell, CheckCircle, Loader, Target, Wifi, XCircle } from "lucide-react"
import type { OfferMonitor } from "@/types/dashboard"
import type { TargetSummaryResponse } from "@/lib/api/types.gen"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ProgressBar } from "@/components/ui/progress-bar"
import { getQuotaStatus, listNotificationConfigs, sendTargetTestNotification, toggleTargetNotifications, updateTargetNotificationConfig } from "@/lib/api/sdk.gen"
import { TargetSelectorInline } from "@/components/dashboard/target-selector-inline"

interface DashboardSidebarProps {
  offerMonitor: OfferMonitor
  targets?: Array<TargetSummaryResponse>
  selectedTargetId?: number
  onSelectTarget?: (targetId: number) => void
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

export default function DashboardSidebar({ offerMonitor, targets, selectedTargetId, onSelectTarget }: DashboardSidebarProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient()

  type Status = 'idle' | 'loading' | 'success' | 'error'
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const { data: quotaStatus } = useQuery({
    queryKey: ['quotaStatus'],
    queryFn: () => getQuotaStatus(),
    staleTime: 30_000,
  })

  const { data: notificationConfigs } = useQuery({
    queryKey: ['notificationConfigs'],
    queryFn: () => listNotificationConfigs(),
    staleTime: 30_000,
  });

  const quotaRows = quotaStatus?.data.quotas ?? []
  const scrapingUrlQuota = quotaRows.find(
    (row) => row.slug === "scraping_urls" && row.targetId === offerMonitor.id,
  )
  const currentTargetOffersQuota = quotaRows.find(
    (row) => row.slug === "offers" && row.targetId === offerMonitor.id,
  )

  const toggleNotificationsMutation = useMutation({
    mutationFn: (enable: boolean) =>
      toggleTargetNotifications({
        path: { target_id: offerMonitor.id },
        body: { enable },
        throwOnError: true
      }),
    onMutate: (newEnableStatus: boolean) => {
      const previousOfferMonitor = queryClient.getQueryData(['target', offerMonitor.id]);
      queryClient.setQueryData(['target', offerMonitor.id], (old: OfferMonitor | undefined) => {
        if (!old) return old;
        return { ...old, enableNotifications: newEnableStatus };
      });
      return { prev: previousOfferMonitor };
    },
    onError: (_err, _newEnableStatus, context) => {
      queryClient.setQueryData(['target', offerMonitor.id], context?.prev);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['target'] });
    }
  })

  const updateNotificationConfigMutation = useMutation({
    mutationFn: (configId: number | null) => {
      return updateTargetNotificationConfig({
        path: { target_id: offerMonitor.id },
        body: { notificationConfigId: configId },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['target'] });
    },
    onError: (err: Error) => {
      console.error("Error updating notification configuration:", err);
    },
  });

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

  const handleChannelChange = (configId: number | null) => {
    updateNotificationConfigMutation.mutate(configId)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with Target Name + Selector */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2 mb-3">
          <Target className="w-4 h-4 text-primary" aria-hidden="true" />
          <h2 className="font-semibold text-foreground text-sm">{t('dashboard.sidebar.header.monitor')}</h2>
        </div>
        {targets && targets.length > 1 && onSelectTarget && selectedTargetId && (
          <TargetSelectorInline
            targets={targets}
            selectedTargetId={selectedTargetId}
            onSelect={onSelectTarget}
          />
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Details */}
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground font-semibold">{t('dashboard.sidebar.status.title')}</Label>
          <div className="p-3 bg-secondary/50 rounded-lg space-y-2 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t('dashboard.sidebar.status.activeWebsites')}</span>
              <Badge variant="success" className="border-0">
                <Wifi className="w-3 h-3 mr-1" aria-hidden="true" />
                {offerMonitor.urls.filter((url) => url.isActive).length}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t('dashboard.sidebar.status.totalWebsites')}</span>
              <span className="font-medium">{offerMonitor.urls.length}</span>
            </div>
          </div>

          <Label htmlFor="sidebar-channel-select" className="text-xs text-muted-foreground font-semibold mt-3 block">{t('dashboard.sidebar.channel.title')}</Label>
          <Select
            value={offerMonitor.notificationConfigId?.toString() || ""}
            onValueChange={(value: string) => {
              const configId = value ? parseInt(value) : null;
              handleChannelChange(configId);
            }}
          >
            <SelectTrigger id="sidebar-channel-select" className="min-h-[44px] h-8 text-xs w-full">
              <SelectValue placeholder={t('dashboard.sidebar.channel.placeholder')} />
            </SelectTrigger>
            <SelectContent>
              {(notificationConfigs?.data.configs ?? []).map((config) => {
                return (
                  <SelectItem key={config.id} value={config.id.toString()}>
                    <span className="flex items-center gap-2 min-w-0">
                      <Bell className="w-3.5 h-3.5 text-muted-foreground shrink-0" aria-hidden="true" />
                      <span className="flex-1 min-w-0 truncate">{config.name || `${t('dashboard.monitorSettings.config')} ${config.id}`}</span>
                    </span>
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        </div>

        {/* Quota */}
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground font-semibold">{t('dashboard.sidebar.quotas.title')}</Label>
          <div className="space-y-2">
            {scrapingUrlQuota && (
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">{t('dashboard.sidebar.quotas.scrapingUrls')}</span>
                  <span className="font-medium">{scrapingUrlQuota.used}/{scrapingUrlQuota.limit}</span>
                </div>
                <ProgressBar
                  value={scrapingUrlQuota.used}
                  max={scrapingUrlQuota.limit}
                  variant={getQuotaProgressVariant(scrapingUrlQuota.used, scrapingUrlQuota.limit)}
                />
              </div>
            )}
            {currentTargetOffersQuota && (
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">{t('dashboard.sidebar.quotas.offers')}</span>
                  <span className="font-medium">{currentTargetOffersQuota.used}/{currentTargetOffersQuota.limit}</span>
                </div>
                <ProgressBar
                  value={currentTargetOffersQuota.used}
                  max={currentTargetOffersQuota.limit}
                  variant={getQuotaProgressVariant(currentTargetOffersQuota.used, currentTargetOffersQuota.limit)}
                />
                {currentTargetOffersQuota.periodEnd && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {t('dashboard.sidebar.quota.resetDate', { date: new Intl.DateTimeFormat().format(new Date(currentTargetOffersQuota.periodEnd)) })}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Settings */}
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground font-semibold">{t('dashboard.sidebar.settings.title')}</Label>
          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-muted-foreground">{t('dashboard.sidebar.settings.notificationsEnabled')}</span>
            <Switch
              checked={offerMonitor.enableNotifications}
              onCheckedChange={(checked: boolean) => toggleNotificationsMutation.mutate(checked)}
              disabled={toggleNotificationsMutation.isPending}
              aria-label={t('dashboard.sidebar.settings.notificationsEnabled')}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <Label className="text-xs text-muted-foreground font-semibold">{t('dashboard.sidebar.actions.title')}</Label>
          <Button
            variant="outline"
            size="sm"
            className="w-full justify-start text-xs transition-colors"
            onClick={handleTestNotification}
            disabled={status !== 'idle'}
            aria-busy={status === 'loading'}
          >
            <div aria-live="polite" aria-atomic="true" className="flex items-center">
              {status === 'loading' && (
                <Loader className="w-3.5 h-3.5 mr-2 animate-spin" aria-hidden="true" />
              )}
              {status === 'success' && (
                <CheckCircle className="w-3.5 h-3.5 mr-2 text-success" aria-hidden="true" />
              )}
              {status === 'error' && (
                <XCircle className="w-3.5 h-3.5 mr-2 text-destructive" aria-hidden="true" />
              )}
              {status === 'idle' && (
                <Bell className="w-3.5 h-3.5 mr-2" aria-hidden="true" />
              )}
              {message || `${t('dashboard.sidebar.quickActions.testNotifications')}…`}
            </div>
          </Button>
        </div>
    </div>
    </div>
  )
}
