import { useState } from "react"
import { useTranslation } from "react-i18next"
import { AlertCircle, CheckCircle, ExternalLink, Eye, EyeOff, Globe, Plus, Save, Trash2 } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useRemoveUrlMutation, useToggleUrlActiveMutation } from "./useMonitors"
import { OfferFilters } from "./OfferFilters"
import { UrlNotificationSettings } from "./UrlNotificationSettings"
import type { OfferMonitor } from "@/types/dashboard"
import cn from "@/lib/utils"
import { getQuotaStatus, updateTargetName } from "@/lib/api/sdk.gen"
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { AddUrlDialog } from '@/components/dashboard/AddUrlDialog'

interface MonitoredWebsitesProps {
  offerMonitor: OfferMonitor
}

export function MonitoredWebsites({ offerMonitor }: MonitoredWebsitesProps) {
  const { t } = useTranslation();
  const [targetName, setTargetName] = useState(offerMonitor.name)
  const [updateSuccess, setUpdateSuccess] = useState(false)
  const [updateError, setUpdateError] = useState<string | null>(null)
  const [isAddUrlDialogOpen, setIsAddUrlDialogOpen] = useState(false)
  const [urlToRemove, setUrlToRemove] = useState<number | null>(null)

  const queryClient = useQueryClient()

  const removeUrlMutation = useRemoveUrlMutation(offerMonitor.id)
  const toggleUrlActiveMutation = useToggleUrlActiveMutation(offerMonitor.id)
  const { data: quotaStatus } = useQuery({
    queryKey: ['quotaStatus'],
    queryFn: () => getQuotaStatus(),
    staleTime: 30_000,
  })
  const currentTargetUrlQuota = quotaStatus?.data.quotas.find(
    (row) => row.slug === "scraping_urls" && row.targetId === offerMonitor.id,
  )
  const isUrlQuotaExceeded =
    !!currentTargetUrlQuota &&
    (currentTargetUrlQuota.limit <= 0 || currentTargetUrlQuota.used >= currentTargetUrlQuota.limit)

  const updateNameMutation = useMutation({
    mutationFn: (newMonitorName: string) => {
      setUpdateError(null);
      return updateTargetName({
        path: { target_id: offerMonitor.id },
        body: { name: newMonitorName },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setUpdateSuccess(true);
      queryClient.invalidateQueries({ queryKey: ['target'] });
      setTimeout(() => setUpdateSuccess(false), 2000);
    },
    onError: (err: any) => {
      setUpdateError(err.message || "An unexpected error occurred.");
    },
  });

  return (
    <Card className="bg-card border border-border">
      <CardHeader>
        <CardTitle className="flex items-center text-xl">
          <Globe className="w-6 h-6 mr-3 text-primary" />
          {t('dashboard.monitoredWebsites.title')}
        </CardTitle>
        <CardDescription>{t('dashboard.monitoredWebsites.description')}</CardDescription>
        <CardAction>
          <Button size="default" onClick={() => setIsAddUrlDialogOpen(true)} disabled={isUrlQuotaExceeded}>
            <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
            {t('dashboard.monitoredWebsites.addWebsite')}
          </Button>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Target Name Update */}
        <div className="p-4 bg-secondary/30 rounded-lg">
          <div className="flex flex-col gap-4 md:flex-row md:items-center justify-between">
            <div className="flex-1">
              <h3 className="font-medium text-foreground">{t('dashboard.monitoredWebsites.targetName')}</h3>
              <p className="text-sm text-muted-foreground">{t('dashboard.monitoredWebsites.targetNameDescription')}</p>
            </div>
            <div className="flex sm:flex-row items-center gap-2">
              <Input
                value={targetName}
                placeholder={t('dashboard.monitoredWebsites.targetNamePlaceholder')}
                onChange={(e) => {
                  setTargetName(e.target.value)
                  setUpdateError(null)
                }}
                className="w-full"
                disabled={updateNameMutation.isPending}
              />
              <Button
                onClick={() => updateNameMutation.mutate(targetName)}
                disabled={updateNameMutation.isPending || (targetName === offerMonitor.name && !updateError) || updateSuccess}
                variant="default"
                size="icon"
                aria-label={t('dashboard.monitoredWebsites.update')}
              >
                {updateNameMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin motion-reduce:animate-none mr-2" />
                    {t('dashboard.monitoredWebsites.saving')}
                  </>
                ) : updateSuccess ? (
                  <CheckCircle className="w-5 h-5 text-white" />
                ) : (
                  <>
                    <Save className="w-4 h-4 m-2" />
                    {/* {t('dashboard.monitoredWebsites.update')} */}
                  </>
                )}
              </Button>
            </div>
          </div>
          {updateError && (
            <div className="flex items-center mt-2 text-sm text-destructive">
              <AlertCircle className="w-4 h-4 mr-2" />
              {updateError}
            </div>
          )}
        </div>
        {/* URL List */}
        <div className="space-y-4">
          {offerMonitor.urls.map((url) => (
            <div
              key={url.id}
              className="p-4 bg-card/50 rounded-lg border border-border transition-shadow duration-200 motion-reduce:transition-none hover:shadow-md group"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between">
                <div className="flex-1">
                  <>
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-foreground">{url.name}</h4>
                      <Badge
                        variant={url.isActive ? "success" : "secondary"}
                        className="border-0"
                      >
                        {url.isActive ? t('dashboard.monitoredWebsites.active') : t('dashboard.monitoredWebsites.paused')}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <a
                        href={url.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="line-clamp-2 hover:text-primary transition-colors duration-200 break-all"
                      >
                        <ExternalLink className="w-4 h-4 mr-1" />
                        {url.url}
                      </a>
                    </div>
                    {/* Last checked time */}
                    <div className="mt-2 text-sm text-muted-foreground">
                      {url.lastCheckedAt ? (
                        <>
                          {t('dashboard.monitoredWebsites.lastChecked')}: {new Date(url.lastCheckedAt).toLocaleString()}
                        </>
                      ) : (
                        t('dashboard.monitoredWebsites.pending')
                      )}
                    </div>
                  </>
                </div>

                <div className="flex items-center space-x-2 mt-4 md:mt-0 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => toggleUrlActiveMutation.mutate({ urlId: url.id, isActive: url.isActive })}
                    aria-label={url.isActive ? t('dashboard.monitoredWebsites.pause') : t('dashboard.monitoredWebsites.resume')}
                    className={cn(url.isActive ? "text-muted-foreground hover:bg-accent" : "text-success hover:bg-success/10")}
                  >
                    {url.isActive ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => setUrlToRemove(url.id)}
                    aria-label={t('dashboard.monitoredWebsites.delete')}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Offer Filters Component */}
              <OfferFilters
                targetId={offerMonitor.id}
                urlId={url.id}
                initialFilters={url.filters ?? null}
              />

              {/* Notification Settings Component */}
              <UrlNotificationSettings
                targetId={offerMonitor.id}
                urlId={url.id}
                initialShowLocationMap={url.showLocationMapInNotifications ?? false}
                initialWaypoints={url.waypoints ?? []}
              />
            </div>
          ))}

          {offerMonitor.urls.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <Globe className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium text-foreground mb-2">{t('dashboard.monitoredWebsites.noWebsitesTitle')}</p>
              <p>{t('dashboard.monitoredWebsites.noWebsitesDescription')}</p>
            </div>
          )}
        </div>
      </CardContent>
      <AddUrlDialog
        offerMonitor={offerMonitor}
        isOpen={isAddUrlDialogOpen}
        onClose={() => setIsAddUrlDialogOpen(false)}
        onSuccess={() => queryClient.invalidateQueries({ queryKey: ['target'] })}
      />
      <Dialog open={urlToRemove !== null} onOpenChange={(open) => { if (!open) setUrlToRemove(null) }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('dashboard.monitoredWebsites.confirmRemoveTitle')}</DialogTitle>
            <DialogDescription>
              {t('dashboard.monitoredWebsites.confirmRemoveDescription')}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setUrlToRemove(null)}>
              {t('dashboard.monitoredWebsites.addUrlDialog.cancel')}
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (urlToRemove !== null) {
                  removeUrlMutation.mutate(urlToRemove)
                  setUrlToRemove(null)
                }
              }}
              disabled={removeUrlMutation.isPending}
            >
              {removeUrlMutation.isPending ? t('dashboard.monitoredWebsites.removing') : t('dashboard.monitoredWebsites.delete')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}
