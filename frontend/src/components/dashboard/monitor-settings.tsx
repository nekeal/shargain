import { AlertCircle, CheckCircle, Plus, Save, Settings } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import type { OfferMonitor } from "@/types/dashboard"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select"
import { ConfigFormModal } from "@/components/notifications/config-form-modal"
import { generateTelegramToken, listNotificationConfigs, toggleTargetNotifications, updateTargetName, updateTargetNotificationConfig } from "@/lib/api/sdk.gen"

interface MonitorSettingsProps {
  offerMonitor: OfferMonitor
  isVisible: boolean
}

export default function MonitorSettings({ offerMonitor, isVisible }: MonitorSettingsProps) {
  const queryClient = useQueryClient()
  const [telegramBotUrl, setTelegramBotUrl] = useState<string | null>(null)
  const [targetName, setTargetName] = useState(offerMonitor.name)
  const [updateSuccess, setUpdateSuccess] = useState(false)
  const [updateError, setUpdateError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const selectedNotificationConfig = offerMonitor.notificationConfigId

  useEffect(() => {
    setTargetName(offerMonitor.name)
  }, [offerMonitor.name])

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
      generateTelegramToken({
        throwOnError: true,
      }),
    onSuccess: (data) => {
      setTelegramBotUrl(data.data.telegramBotUrl)
    },
  })

  const updateNameMutation = useMutation({
    mutationFn: (newName: string) => {
      setUpdateError(null);
      return updateTargetName({
        path: { target_id: offerMonitor.id },
        body: { name: newName },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setUpdateSuccess(true);
      queryClient.invalidateQueries({ queryKey: ['myTarget'] });
      setTimeout(() => setUpdateSuccess(false), 2000);
    },
    onError: (err: any) => {
      setUpdateError(err.message || "An unexpected error occurred.");
    },
  });

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
          Monitor Settings
        </CardTitle>
        <CardDescription>Configure your offer monitoring preferences</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Target Name</h3>
              <p className="text-sm text-gray-600">Update the name of your scraping target.</p>
            </div>
            <div className="flex items-center space-x-2">
              <Input
                value={targetName}
                onChange={(e) => {
                  setTargetName(e.target.value)
                  setUpdateError(null)
                }}
                className="w-48"
                disabled={updateNameMutation.isPending}
              />
              <Button
                onClick={() => updateNameMutation.mutate(targetName)}
                disabled={updateNameMutation.isPending || (targetName === offerMonitor.name && !updateError) || updateSuccess}
                className="w-32 justify-center bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 transition-all duration-300 hover:scale-105"
              >
                {updateNameMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    Saving...
                  </>
                ) : updateSuccess ? (
                  <CheckCircle className="w-5 h-5 text-white" />
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Update
                  </>
                )}
              </Button>
            </div>
          </div>
          {updateError && (
            <div className="flex items-center mt-2 text-sm text-red-600">
              <AlertCircle className="w-4 h-4 mr-2" />
              {updateError}
            </div>
          )}
        </div>
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg">
          <div>
            <h3 className="font-medium text-gray-900">Enable Notifications</h3>
            <p className="text-sm text-gray-600">Receive alerts when new offers are found</p>
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
            {(notificationConfigs?.data.configs ?? []).length > 0 && (
              <div className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <h3 className="font-medium text-gray-900">Notification Configuration</h3>
                    <p className="text-sm text-gray-600 sm:hidden">
                      Select a notification configuration for this target
                    </p>
                  </div>
                  <div className="flex items-center space-x-2 w-full sm:w-auto">
                    <div className="flex-1 min-w-0">
                      <Label htmlFor="notification-config" className="sr-only">
                        Notification Configuration
                      </Label>
                      <Select
                        value={selectedNotificationConfig?.toString() || ""}
                        onValueChange={(value) => {
                          const configId = parseInt(value);
                          updateNotificationConfigMutation.mutate(configId);
                        }}
                      >
                        <SelectTrigger id="notification-config">
                          <SelectValue placeholder="Select configuration" />
                        </SelectTrigger>
                        <SelectContent>
                          {notificationConfigs?.data.configs.map((config) => (
                            <SelectItem key={config.id} value={config.id.toString()}>
                              {config.name || `Config ${config.id}`} ({config.channel})
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => setIsModalOpen(true)}
                      className="h-10 w-10 p-0 flex-shrink-0"
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-gray-600 hidden sm:block mt-1">
                  Select a notification configuration for this target
                </p>
              </div>
            )}
            {!selectedNotificationConfig && (
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
                <div>
                  <h3 className="font-medium text-gray-900">Telegram Notifications</h3>
                  <p className="text-sm text-gray-600">
                    {offerMonitor.notificationConfigId
                      ? "Telegram notifications are configured."
                      : "Enable notifications on telegram."}
                  </p>
                </div>
                {!offerMonitor.notificationConfigId && (
                  <Button
                    onClick={() => generateTokenMutation.mutate()}
                    disabled={generateTokenMutation.isPending}
                  >
                    Configure
                  </Button>
                )}
              </div>
            )}
            {telegramBotUrl && (
              <div className="flex items-center justify-between p-4 bg-gray-100 rounded-lg">
                <p className="text-sm text-gray-700 truncate">{telegramBotUrl}</p>
                <Button
                  onClick={() => navigator.clipboard.writeText(telegramBotUrl)}
                  variant="outline"
                >
                  Copy
                </Button>
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
