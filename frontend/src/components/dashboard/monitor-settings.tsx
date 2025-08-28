import { Plus, Send, Settings, Zap } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { OfferMonitor } from "@/types/dashboard"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { ConfigFormModal } from "@/components/notifications/config-form-modal"
import { generateTelegramToken, listNotificationConfigs, toggleTargetNotifications, updateTargetNotificationConfig } from "@/lib/api/sdk.gen"


interface MonitorSettingsProps {
  offerMonitor: OfferMonitor
  isVisible: boolean
}

export default function MonitorSettings({ offerMonitor, isVisible }: MonitorSettingsProps) {
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
      const previousOfferMonitor = queryClient.getQueryData(['myTarget']);
      queryClient.setQueryData(['myTarget'], (old: OfferMonitor | undefined) => {
        if (!old) return old;
        return { ...old, enableNotifications: newEnableStatus };
      });
      return { prev: previousOfferMonitor };
    },
    onError: (_err, _newEnableStatus, context) => {
      queryClient.setQueryData(['myTarget'], context?.prev);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['myTarget'] });
    }
  })

  const generateTokenMutation = useMutation({
    mutationFn: () =>
      generateTelegramToken({}),
    onSuccess: (data) => {
      window.open(data.data.telegramBotUrl, '_blank');
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
      queryClient.invalidateQueries({ queryKey: ['myTarget'] });
    },
    onError: (err: any) => {
      console.error("Error updating notification configuration:", err);
    },
  });


  return (
    <Card
      className={`border-0 bg-white/60 backdrop-blur-sm transition-all duration-700 delay-200 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
        }`}
    >
      <CardHeader>
        <CardTitle className="flex items-center text-2xl">
          <Settings className="w-6 h-6 mr-3 text-violet-600" />
          {t('dashboard.monitorSettings.title')}
        </CardTitle>
        <CardDescription>{t('dashboard.monitorSettings.description')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg">
          <div>
            <h3 className="font-medium text-gray-900">{t('dashboard.monitorSettings.enableNotifications')}</h3>
            <p className="text-sm text-gray-600">{t('dashboard.monitorSettings.enableNotificationsDescription')}</p>
          </div>
          <Switch
            checked={offerMonitor.enableNotifications}
            onCheckedChange={(checked: boolean) => toggleNotificationsMutation.mutate(checked)}
            className="data-[state=checked]:bg-violet-600"
            disabled={toggleNotificationsMutation.isPending}
          />
        </div>
        {offerMonitor.enableNotifications && (
          <>
            {(notificationConfigs?.data.configs ?? []).length === 0 ? (
              <div className="p-6 bg-gradient-to-br from-violet-100 to-sky-100 rounded-lg text-center shadow-lg">
                <Zap className="w-12 h-12 mx-auto text-violet-500 mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">{t('dashboard.monitorSettings.connectChannel.title')}</h3>
                <p className="text-md text-gray-600 mb-6">{t('dashboard.monitorSettings.connectChannel.description')}</p>
                <Button
                  onClick={() => generateTokenMutation.mutate()}
                  disabled={generateTokenMutation.isPending}
                  size="lg"
                >
                  <Send className="w-5 h-5 mr-3" />
                  {t('dashboard.monitorSettings.connectChannel.button')}
                </Button>
                <p className="text-sm text-gray-500 mt-3 mb-5">{t('dashboard.monitorSettings.connectChannel.note')}</p>
                <div className="my-4 flex items-center">
                  <div className="flex-grow border-t border-gray-300"></div>
                  <span className="flex-shrink mx-4 text-gray-500 text-sm">{t('dashboard.monitorSettings.connectChannel.or')}</span>
                  <div className="flex-grow border-t border-gray-300"></div>
                </div>
                <Button
                  variant="link"
                  onClick={() => setIsModalOpen(true)}
                  className="text-sm text-violet-600 hover:text-violet-800"
                >
                  {t('dashboard.monitorSettings.connectChannel.manual')}
                </Button>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-white/80">
                <h3 className="font-medium text-gray-900 mb-4 text-lg">{t('dashboard.monitorSettings.activeChannel')}</h3>
                <div className="flex items-center space-x-4">
                  <div className="flex-grow">
                    <Select
                      value={offerMonitor.notificationConfigId?.toString() || ""}
                      onValueChange={(value: string) => {
                        const configId = parseInt(value);
                        updateNotificationConfigMutation.mutate(configId);
                      }}
                    >
                      <SelectTrigger
                        id="notification-config"
                        className="w-full border-violet-200 hover:border-violet-300 focus:ring-violet-500"
                      >
                        <SelectValue placeholder={t('dashboard.monitorSettings.activeChannelPlaceholder')} />
                      </SelectTrigger>
                      <SelectContent>
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
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    {t('dashboard.monitorSettings.addChannel')}
                  </Button>
                </div>
                <div className="mt-4 flex items-center space-x-2">
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
