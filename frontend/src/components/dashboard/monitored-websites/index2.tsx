import { useEffect, useState } from "react"
import { useTranslation } from "react-i18next"
import { Globe, Plus } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { SupportedWebsitesModal } from "./supported-websites-modal"
import type { OfferMonitor } from "@/types/dashboard"
import { getQuotaStatus, updateTargetName } from "@/lib/api/sdk.gen"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AddUrlDialog } from "@/components/dashboard/AddUrlDialog"
import { UrlCard2 } from "@/components/dashboard/UrlCard2"

interface MonitoredWebsitesProps {
  offerMonitor: OfferMonitor
}

export function MonitoredWebsites({ offerMonitor }: MonitoredWebsitesProps) {
  const { t } = useTranslation();
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false)
  const [isAddUrlDialogOpen, setIsAddUrlDialogOpen] = useState(false)
  const [targetName, setTargetName] = useState(offerMonitor.name)
  const [filterOpen, setFilterOpen] = useState<Record<number, boolean>>({})
  const [locationOpen, setLocationOpen] = useState<Record<number, boolean>>({})

  const queryClient = useQueryClient()

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

  // Handle sidebar's Add URL event
  useEffect(() => {
    const handleOpenAddUrl = () => {
      if (!isUrlQuotaExceeded) {
        setIsAddUrlDialogOpen(true)
      }
    }
    document.addEventListener('dashboard:open-add-url', handleOpenAddUrl)
    return () => document.removeEventListener('dashboard:open-add-url', handleOpenAddUrl)
  }, [isUrlQuotaExceeded])

  const updateNameMutation = useMutation({
    mutationFn: (newMonitorName: string) => {
      return updateTargetName({
        path: { target_id: offerMonitor.id },
        body: { name: newMonitorName },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['target'] });
      toast.success(t('dashboard.monitoredWebsites.toast.nameUpdated'));
    },
    onError: (err: Error) => {
      toast.error(t('dashboard.monitoredWebsites.toast.nameUpdateError'));
      console.error("Error updating target name:", err);
    },
  });

  const handleAddUrlDialogOpen = () => {
    if (!isUrlQuotaExceeded) {
      setIsAddUrlDialogOpen(true)
    }
  }

  const handleAddUrlSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['target'] });
  }

  const handleTargetNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTargetName(e.target.value)
  }

  const handleTargetNameSave = () => {
    updateNameMutation.mutate(targetName)
  }

  return (
    <>
      <Card className="bg-card border border-border animate-fade-in">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center text-lg font-medium">
                <Globe className="w-5 h-5 mr-3 text-primary" aria-hidden="true" />
                {t('dashboard.monitoredWebsites.title')}
              </CardTitle>
              <CardDescription className="text-sm text-muted-foreground">{t('dashboard.monitoredWebsites.description')}</CardDescription>
            </div>
            <Button
              size="sm"
              onClick={handleAddUrlDialogOpen}
              disabled={isUrlQuotaExceeded}
              className="transition-colors duration-200 ease-out-quart motion-reduce:transition-none"
            >
              <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
              {t('dashboard.monitoredWebsites.addWebsite')}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Target Name Update */}
          <div className="p-4 bg-secondary/30 rounded-lg border border-border">
            <div className="flex flex-col gap-4 md:flex-row md:items-center justify-between">
              <div className="flex-1">
                <h3 className="font-medium text-foreground">{t('dashboard.monitoredWebsites.targetName')}</h3>
                <p className="text-sm text-muted-foreground">{t('dashboard.monitoredWebsites.targetNameDescription')}</p>
              </div>
              <div className="flex sm:flex-row items-center gap-2">
                <Input
                  value={targetName}
                  placeholder={t('dashboard.monitoredWebsites.targetNamePlaceholder')}
                  onChange={handleTargetNameChange}
                  className="w-full"
                  disabled={updateNameMutation.isPending}
                />
                <Button
                  onClick={handleTargetNameSave}
                  disabled={updateNameMutation.isPending || targetName === offerMonitor.name}
                  variant="default"
                  size="icon"
                  className="transition-colors duration-200 ease-out-quart motion-reduce:transition-none"
                >
                  {updateNameMutation.isPending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin mr-2" />
                      <span className="sr-only">{t('dashboard.monitoredWebsites.saving')}</span>
                    </>
                  ) : (
                    <svg className="w-4 h-4" aria-hidden="true" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </Button>
              </div>
            </div>
          </div>

          {/* Quota Warning */}
          {isUrlQuotaExceeded && (
            <div className="flex items-center gap-2 text-warning-muted-foreground text-sm" role="status">
              <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{t('dashboard.monitoredWebsites.quotaExceededAction')}</span>
            </div>
          )}

          {/* URL List */}
          <div className="space-y-4" role="list" aria-label={t('dashboard.monitoredWebsites.title')}>
            {offerMonitor.urls.map((url) => (
              <UrlCard2
                key={url.id}
                url={url}
                targetId={offerMonitor.id}
                filterOpen={filterOpen[url.id] ?? false}
                locationOpen={locationOpen[url.id] ?? false}
                onToggleFilter={() => setFilterOpen((p) => ({ ...p, [url.id]: !p[url.id] }))}
                onToggleLocation={() => setLocationOpen((p) => ({ ...p, [url.id]: !p[url.id] }))}
              />
            ))}

            {offerMonitor.urls.length === 0 && (
              <div className="bg-card border border-border rounded-xl p-12 text-center animate-fade-in">
                <Globe className="w-12 h-12 mx-auto mb-4 text-muted-foreground" aria-hidden="true" />
                <p className="text-lg font-medium text-foreground mb-2">{t('dashboard.monitoredWebsites.noWebsitesTitle')}</p>
                <p className="text-sm text-muted-foreground mb-6">{t('dashboard.monitoredWebsites.noWebsitesDescription')}</p>
                <Button
                  size="lg"
                  onClick={handleAddUrlDialogOpen}
                  disabled={isUrlQuotaExceeded}
                  className="transition-colors duration-200 ease-out-quart motion-reduce:transition-none"
                >
                  <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
                  {t('dashboard.monitoredWebsites.addWebsite')}
                </Button>
              </div>
            )}
          </div>
        </CardContent>
        <SupportedWebsitesModal
          isOpen={isHelpModalOpen}
          onClose={() => setIsHelpModalOpen(false)}
        />
      </Card>

      <AddUrlDialog
        offerMonitor={offerMonitor}
        isOpen={isAddUrlDialogOpen}
        onClose={() => setIsAddUrlDialogOpen(false)}
        onSuccess={handleAddUrlSuccess}
      />
    </>
  )
}