import { Plus, Send, Settings, Zap } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { toast } from "sonner"
import type { OfferMonitor } from "@/types/dashboard"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { ConfigFormModal } from "@/components/notifications/config-form-modal"
import { generateTelegramToken, listNotificationConfigs, toggleTargetNotifications, updateTargetNotificationConfig } from "@/lib/api/sdk.gen"


interface MonitorSettingsProps {
  offerMonitor: OfferMonitor
}

export default function MonitorSettings({ offerMonitor }: MonitorSettingsProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
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
      toast.error(t('dashboard.monitorSettings.toast.enableError'));
    },
    onSuccess: () => {
      toast.success(t('dashboard.monitorSettings.toast.enableSuccess'));
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['target'] });
    }
  })

  const generateTokenMutation = useMutation({
    mutationFn: () =>
      generateTelegramToken({}),
    onSuccess: (data) => {
      window.open(data.data.telegramBotUrl, '_blank', 'noopener,noreferrer');
      toast.success(t('dashboard.monitorSettings.toast.telegramOpened'));
    },
    onError: () => {
      toast.error(t('dashboard.monitorSettings.toast.telegramError'));
    },
  })

  const { data: notificationConfigs } = useQuery({
    queryKey: ['notificationConfigs'],
    queryFn: () => listNotificationConfigs(),
  });

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
      toast.success(t('dashboard.monitorSettings.toast.channelUpdated'));
    },
    onError: (err: Error) => {
      toast.error(t('dashboard.monitorSettings.toast.channelError'));
      console.error("Error updating notification configuration:", err);
    },
  });


  return (
    <Card className="bg-card border border-border animate-fade-in">
      <CardHeader>
        <CardTitle className="flex items-center text-lg font-medium">
          <Settings className="w-5 h-5 mr-3 text-primary" aria-hidden="true" />
          {t('dashboard.monitorSettings.title')}
        </CardTitle>
        <CardDescription>{t('dashboard.monitorSettings.description')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg border border-border">
          <div>
            <h3 className="font-medium text-foreground">{t('dashboard.monitorSettings.enableNotifications')}</h3>
            <p className="text-sm text-muted-foreground">{t('dashboard.monitorSettings.enableNotificationsDescription')}</p>
          </div>
          <Switch
            checked={offerMonitor.enableNotifications}
            onCheckedChange={(checked: boolean) => toggleNotificationsMutation.mutate(checked)}
            disabled={toggleNotificationsMutation.isPending}
            aria-label={t('dashboard.monitorSettings.enableNotifications')}
          />
        </div>
        {offerMonitor.enableNotifications && (
          <>
            {(notificationConfigs?.data.configs ?? []).length === 0 ? (
              <div className="p-6 bg-secondary/30 rounded-lg text-center border border-border">
                <Zap className="w-12 h-12 mx-auto text-primary mb-4" aria-hidden="true" />
                <h3 className="text-lg font-semibold text-foreground mb-2">{t('dashboard.monitorSettings.connectChannel.title')}</h3>
                <p className="text-sm text-muted-foreground mb-6">{t('dashboard.monitorSettings.connectChannel.description')}</p>
                <Button
                  onClick={() => generateTokenMutation.mutate()}
                  disabled={generateTokenMutation.isPending}
                  size="lg"
                  className="transition-colors duration-200 ease-out-quart motion-reduce:transition-none"
                >
                  <Send className="w-5 h-5 mr-3" aria-hidden="true" />
                  {t('dashboard.monitorSettings.connectChannel.button')}
                </Button>
                <p className="text-sm text-muted-foreground mt-3 mb-5">{t('dashboard.monitorSettings.connectChannel.note')}</p>
                <div className="my-4 flex items-center">
                  <div className="flex-grow border-t border-border"></div>
                  <span className="flex-shrink mx-4 text-muted-foreground text-sm">{t('dashboard.monitorSettings.connectChannel.or')}</span>
                  <div className="flex-grow border-t border-border"></div>
                </div>
                <Button
                  variant="link"
                  onClick={() => setIsModalOpen(true)}
                  className="text-sm text-primary hover:text-primary/90 transition-colors duration-200 ease-out-quart motion-reduce:transition-none"
                >
                  {t('dashboard.monitorSettings.connectChannel.manual')}
                </Button>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-card border border-border">
                <h3 className="font-medium text-foreground mb-4 text-base">{t('dashboard.monitorSettings.activeChannel')}</h3>
                <div className="flex flex-wrap items-center sm:space-x-4 gap-y-2">
                  <div className="flex-grow w-full sm:w-auto">
                    <Select
                      value={offerMonitor.notificationConfigId?.toString() || ""}
                      onValueChange={(value: string) => {
                        const configId = parseInt(value);
                        updateNotificationConfigMutation.mutate(configId);
                      }}
                    >
                      <SelectTrigger id="notification-config" className="w-full sm:max-w-[300px] transition-colors duration-200 ease-out-quart motion-reduce:transition-none">
                        <SelectValue placeholder={t('dashboard.monitorSettings.activeChannelPlaceholder')} />
                      </SelectTrigger>
                      <SelectContent className="transition-colors duration-200 ease-out-quart motion-reduce:transition-none">
                        {(notificationConfigs?.data.configs ?? []).map((config) => (
                          <SelectItem key={config.id} value={config.id.toString()}>
                            {config.name || `${t('dashboard.monitorSettings.config')} ${config.id}`}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <Button
                    onClick={() => setIsModalOpen(true)}
                    variant="outline"
                    className="w-full sm:w-auto transition-colors duration-200 ease-out-quart motion-reduce:transition-none"
                  >
                    <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
                    {t('dashboard.monitorSettings.addChannel')}
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
      <ConfigFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        configToEdit={null}
        onSuccess={(configId) => {
          updateNotificationConfigMutation.mutate(configId);
        }}
      />
    </Card>
  )
}