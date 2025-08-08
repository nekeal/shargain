import { Settings } from "lucide-react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
// import { NotificationConfigSelector } from "./NotificationConfigSelector"
import type { OfferMonitor } from "@/types/dashboard"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { shargainPublicApiApiToggleNotifications } from "@/lib/api";

interface MonitorSettingsProps {
  offerMonitor: OfferMonitor
  isVisible: boolean
}

export function MonitorSettings({ offerMonitor, isVisible }: MonitorSettingsProps) {
  const queryClient = useQueryClient()

  const toggleNotificationsMutation = useMutation({
    mutationFn: (enable: boolean) =>
      shargainPublicApiApiToggleNotifications({
        path: { target_id: offerMonitor.id },
        body: { enable }
      }),
    onSuccess: (_, checked) => {
      queryClient.setQueryData(['myTarget'], (old: OfferMonitor | undefined) => {
        if (!old) return old;
        return { ...old, enableNotifications: checked };
      });

      queryClient.invalidateQueries({ queryKey: ['myTarget'] });
      queryClient.refetchQueries({ queryKey: ['myTarget'] });
      console.log('Cache updated. New enableNotifications in cache:', checked);
    },
  })

  console.log('MonitorSettings re-rendered. enableNotifications:', offerMonitor.enableNotifications);

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
        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg">
          <div>
            <h3 className="font-medium text-gray-900">Notification Configuration</h3>
            <p className="text-sm text-gray-600">Choose how you want to receive notifications</p>
          </div>
          {/* <NotificationConfigSelector offerMonitor={offerMonitor} /> */}
        </div>
      </CardContent>
    </Card>
  )
}
