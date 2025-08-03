import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Settings, MessageCircle, Mail } from "lucide-react"
import type { OfferMonitor } from "@/types/dashboard"

interface MonitorSettingsProps {
  offerMonitor: OfferMonitor
  setOfferMonitor: (updater: (prev: OfferMonitor) => OfferMonitor) => void
  isVisible: boolean
}

export function MonitorSettings({ offerMonitor, setOfferMonitor, isVisible }: MonitorSettingsProps) {
  return (
    <Card
      className={`border-0 bg-white/60 backdrop-blur-sm transition-all duration-700 delay-200 ${
        isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
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
        <div className="space-y-2">
          <Label htmlFor="monitor-name">Monitor Name</Label>
          <Input
            id="monitor-name"
            value={offerMonitor.name}
            onChange={(e) => setOfferMonitor((prev) => ({ ...prev, name: e.target.value }))}
            className="bg-white/50 border-violet-200 focus:border-violet-500 focus:ring-violet-500"
            placeholder="Enter a name for your monitor"
          />
        </div>

        <div className="flex items-center justify-between p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg">
          <div>
            <h3 className="font-medium text-gray-900">Enable Notifications</h3>
            <p className="text-sm text-gray-600">Receive alerts when new offers are found</p>
          </div>
          <Switch
            checked={offerMonitor.enable_notifications}
            onCheckedChange={(checked) => setOfferMonitor((prev) => ({ ...prev, enable_notifications: checked }))}
            className="data-[state=checked]:bg-violet-600"
          />
        </div>

        {offerMonitor.enable_notifications && (
          <div className="space-y-4 p-4 bg-white/50 rounded-lg border border-violet-100">
            <h4 className="font-medium text-gray-900">Notification Channels</h4>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <MessageCircle className="w-5 h-5 text-violet-600" />
                <div>
                  <p className="font-medium text-gray-900">Telegram</p>
                  <p className="text-sm text-gray-600">Instant notifications via Telegram bot</p>
                </div>
              </div>
              <Switch
                checked={offerMonitor.notification_config.telegram}
                onCheckedChange={(checked) =>
                  setOfferMonitor((prev) => ({
                    ...prev,
                    notification_config: { ...prev.notification_config, telegram: checked },
                  }))
                }
                className="data-[state=checked]:bg-violet-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-violet-600" />
                <div>
                  <p className="font-medium text-gray-900">Email</p>
                  <p className="text-sm text-gray-600">Detailed summaries via email</p>
                </div>
              </div>
              <Switch
                checked={offerMonitor.notification_config.email}
                onCheckedChange={(checked) =>
                  setOfferMonitor((prev) => ({
                    ...prev,
                    notification_config: { ...prev.notification_config, email: checked },
                  }))
                }
                className="data-[state=checked]:bg-violet-600"
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
