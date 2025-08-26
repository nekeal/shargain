import { useState } from "react"
import { Link } from "@tanstack/react-router"
import { Bell, Monitor, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"


export default function DashboardHeader() {
  const [isSaving, setIsSaving] = useState(false)

  const saveMonitor = async () => {
    setIsSaving(true)
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setIsSaving(false)
  }

  return (
    <header className="border-b border-white/20 bg-white/10 backdrop-blur-xl sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3">
          <Bell className="h-8 w-8 text-violet-600" />
          <span className="text-2xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
            OfferAlert
          </span>
        </Link>

        <div className="flex items-center space-x-4">
          <Badge className="bg-gradient-to-r from-violet-100 to-purple-100 text-violet-800 border-0">
            <Monitor className="w-4 h-4 mr-2" />
            Dashboard
          </Badge>
          <Button
            onClick={saveMonitor}
            disabled={isSaving}
            className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 transition-all duration-300 hover:scale-105"
          >
            {isSaving ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </div>
    </header>
  )
}
