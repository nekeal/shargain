import { Link } from "@tanstack/react-router"
import { AlertCircle, Bell, Globe } from "lucide-react"
import type { OfferMonitor } from "types/dashboard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface DashboardSidebarProps {
  offerMonitor: OfferMonitor
  isVisible: boolean
}

export function DashboardSidebar({ offerMonitor, isVisible }: DashboardSidebarProps) {
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
            Monitor Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Active Websites</span>
            <Badge className="bg-green-100 text-green-800 border-0">
              {offerMonitor.urls.filter((url) => url.isActive).length}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total Websites</span>
            <Badge className="bg-violet-100 text-violet-800 border-0">{offerMonitor.urls.length}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Notifications</span>
            <Badge
              className={`border-0 ${offerMonitor.enableNotifications ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"
                }`}
            >
              {offerMonitor.enableNotifications ? "Enabled" : "Disabled"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card
        className={`border-0 bg-white/60 backdrop-blur-sm transition-all duration-700 delay-800 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
          }`}
      >
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button
            variant="outline"
            className="w-full justify-start border-violet-200 text-violet-600 hover:bg-violet-50 transition-all duration-300 hover:scale-105 bg-transparent"
          >
            <Bell className="w-4 h-4 mr-2" />
            Test Notifications
          </Button>
          <Button
            variant="outline"
            className="w-full justify-start border-violet-200 text-violet-600 hover:bg-violet-50 transition-all duration-300 hover:scale-105 bg-transparent"
          >
            <Globe className="w-4 h-4 mr-2" />
            Check All URLs
          </Button>
          <Link to="/">
            <Button
              variant="outline"
              className="w-full justify-start border-gray-200 text-gray-600 hover:bg-gray-50 transition-all duration-300 hover:scale-105 bg-transparent"
            >
              ← Back to Home
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* Tips Card */}
      <Card
        className={`border-0 bg-gradient-to-br from-violet-50 to-purple-50 transition-all duration-700 delay-1000 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
          }`}
      >
        <CardHeader>
          <CardTitle className="text-lg text-violet-800">💡 Pro Tips</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-violet-700">
          <p>• Use specific URLs like /deals or /sales pages for better results</p>
          <p>• Give descriptive names to easily identify your monitored sites</p>
          <p>• Enable both Telegram and email for important deals</p>
          <p>• Pause monitoring temporarily instead of deleting URLs</p>
        </CardContent>
      </Card>
    </div>
  )
}
